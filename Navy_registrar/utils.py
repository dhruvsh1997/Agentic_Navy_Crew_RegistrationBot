import os
import json
import uuid
from datetime import datetime
from typing import TypedDict, Sequence, Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from django.contrib.auth.models import User
from django.db import transaction
from .models import ShipInformation, CrewInformation, MissionInformation, PortInformation, Conversation
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Initialize LLM
groq_llm = ChatGroq(
    api_key=os.environ.get('GROQ_API_KEY'),
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

# State Definitions
class AgentState(TypedDict):
    query: str
    data: dict
    memory: dict
    error: str
    messages: Sequence[BaseMessage]
    user_id: str

class SuperAgentState(TypedDict):
    query: str
    data: dict
    memory: dict
    uid: str
    error: str
    output: Optional[dict]
    questions: list
    answers: list
    ISIC: str
    ICIA: str
    IPIA: str
    next: Optional[str]

# Conversation Management
def get_conversation_context(user_id: str) -> dict:
    try:
        user = User.objects.get(username=user_id)
        latest_conversation = Conversation.objects.filter(user=user).order_by('-timestamp').first()
        return latest_conversation.data if latest_conversation else {}
    except User.DoesNotExist:
        return {}

def add_conversation(user_id: str, data: dict):
    try:
        user = User.objects.get(username=user_id)
        Conversation.objects.create(user=user, data=data)
    except User.DoesNotExist:
        pass

# Analysis Prompt
analysis_prompt = """You are an analysis agent specialized in parsing naval and military queries. Your primary function is to:

1. Extract structured information from natural language queries
2. Maintain context from previous conversations
3. Update information based on new inputs

Current Conversation Context: {context_str}

Output Format Requirements:
- Response must be a valid JSON dictionary enclosed in curly braces {{}}
- Example: {{"ship_name": "USS Example", "ship_type": "Destroyer", ...}}
1. Mandatory Parameters:
   - ship_name
   - ship_type
   - crew_size
   - commander_name
   - commander_rank
   - either mission_type OR home_port
   - question (as list of strings)

2. Optional Parameters:
   - commission_date
   - decommission_date

Rules:
1. Maintain consistency with previous conversation context
2. Update fields only when new information is provided
3. Preserve existing information when not explicitly changed
4. Numbers should be integers
5. Names and proper nouns should maintain their case
6. Do not include any text outside the JSON dictionary
"""

# Utility Functions
def extract_dict_from_string(text: str) -> Optional[dict]:
    logger.debug(f"Raw LLM response: {text}")
    start_index = text.find('{')
    end_index = text.rfind('}')
    if start_index == -1 or end_index == -1 or start_index >= end_index:
        logger.error("No valid JSON object found in response")
        return None
    json_string = text[start_index:end_index+1]
    try:
        json_data = json.loads(json_string)
        logger.debug(f"Parsed JSON: {json_data}")
        return json_data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        return None

def format_context(context: dict) -> str:
    return json.dumps(context, indent=2) if context else "{}"

# Analysis Node
def analysis_node(state: AgentState) -> AgentState:
    user_id = state["user_id"]
    context = get_conversation_context(user_id)
    context_str = format_context(context)
    try:
        prompt_content = analysis_prompt.format(context_str=context_str)
        logger.debug(f"Formatted prompt for user {user_id}: {prompt_content[:500]}...")
    except Exception as e:
        logger.error(f"Error formatting prompt for user {user_id}: {e}", exc_info=True)
        return {**state, "error": f"Prompt formatting failed: {e}", "data": {}}

    messages = [
        SystemMessage(content=prompt_content),
        HumanMessage(content=state["query"])
    ]
    try:
        response = groq_llm.invoke(messages)
        logger.debug(f"LLM response for user {user_id}: {response.content}")
    except Exception as e:
        logger.error(f"Error during LLM invocation: {e}", exc_info=True)
        return {**state, "error": f"LLM invocation failed: {e}", "data": {}}

    parsed_data = extract_dict_from_string(response.content)
    if not parsed_data:
        logger.error("Failed to parse structured data from LLM response")
        return {**state, "error": "Failed to parse response", "data": {}}

    parsed_data["commander_name"] = None if str(parsed_data.get("commander_name", "")) == str(parsed_data.get("commander_rank", "")) else str(parsed_data.get("commander_name", ""))
    parsed_data["ship_name"] = None if str(parsed_data.get("ship_name", "")) == str(parsed_data.get("ship_type", "")) else str(parsed_data.get("ship_name", ""))

    if context:
        for key, value in context.items():
            if not parsed_data.get(key):
                parsed_data[key] = value

    add_conversation(user_id, parsed_data)

    mandatory_params = ["ship_name", "ship_type", "crew_size", "commander_name", "commander_rank"]
    if not (parsed_data.get("mission_type") or parsed_data.get("home_port")):
        logger.warning(f"Missing mission_type or home_port for user {user_id}")
        return {
            **state,
            "error": "Please provide either mission_type or home_port",
            "data": parsed_data
        }

    missing_params = [param for param in mandatory_params if not parsed_data.get(param)]
    if missing_params:
        logger.warning(f"Missing parameters for user {user_id}: {missing_params}")
        return {
            **state,
            "error": f"Please provide: {', '.join(missing_params)}",
            "data": parsed_data
        }

    logger.info(f"Successfully parsed data for user {user_id}: {parsed_data}")
    return {**state, "data": parsed_data, "error": None}

# Analysis Workflow
analysis_workflow = StateGraph(AgentState)
analysis_workflow.add_node("analysis", analysis_node)
analysis_workflow.set_entry_point("analysis")
analysis_workflow.add_edge("analysis", END)
analysis_graph = analysis_workflow.compile()

# Supergraph Nodes
def payload_maker(state: SuperAgentState) -> SuperAgentState:
    user_input = state["query"]
    user_id = state["uid"]
    logger.debug(f"Payload maker processing input for {user_id}: {user_input}")
    initial_agent_state = {
        "query": user_input,
        "data": {},
        "memory": {},
        "error": None,
        "messages": [HumanMessage(content=user_input)],
        "user_id": user_id
    }
    final_agent_state = analysis_graph.invoke(initial_agent_state)
    if final_agent_state["error"]:
        logger.error(f"Error during analysis: {final_agent_state['error']}")
        state["error"] = final_agent_state["error"]
        state["next"] = "END"
    else:
        state["data"] = final_agent_state["data"]
        state["next"] = "router"
    return state

def router_node(state: SuperAgentState) -> SuperAgentState:
    data = state['data']
    if 'ship_id' not in data:
        data['ship_id'] = str(uuid.uuid4())
    state['data'] = data
    logger.debug(f"Router node assigned ship_id: {data['ship_id']}")
    return state

def insert_ship_info_and_calculate_priority(state: SuperAgentState) -> SuperAgentState:
    data = state['data']
    try:
        with transaction.atomic():
            ship, created = ShipInformation.objects.get_or_create(
                ship_id=data['ship_id'],
                defaults={'ship_name': data['ship_name'], 'ship_type': data['ship_type']}
            )
            if not created:
                ship.ship_name = data['ship_name']
                ship.ship_type = data['ship_type']
                ship.save()
            MissionInformation.objects.create(
                ship=ship,
                mission_type=data['mission_type']
            )
    except Exception as e:
        logger.error(f"Error saving ship info for ship_id {data['ship_id']}: {e}", exc_info=True)
        state['error'] = f"Failed to save ship information: {e}"
        state['next'] = "END"
        return state

    messages = [
        SystemMessage(content="You are a tactical advisor for naval missions. Determine the priority of the mission based on the ship type and mission type."),
        HumanMessage(content=f"Ship Type: {data['ship_type']}, Mission Type: {data['mission_type']}. What is the priority of this mission? Provide answer under 10 words.")
    ]
    try:
        response = groq_llm.invoke(messages)
        state['ISIC'] = f"Mission Priority: {response.content}"
        logger.info(f"Mission priority calculated for ship {data['ship_name']}: {response.content}")
    except Exception as e:
        logger.error(f"Error calculating mission priority: {e}", exc_info=True)
        state['error'] = f"Failed to calculate mission priority: {e}"
        state['next'] = "END"
    return state

def insert_crew_info_and_assess_readiness(state: SuperAgentState) -> SuperAgentState:
    data = state['data']
    try:
        ship = ShipInformation.objects.get(ship_id=data['ship_id'])
    except ShipInformation.DoesNotExist:
        logger.error(f"ShipInformation not found for ship_id {data['ship_id']}")
        state['error'] = "Ship information not found"
        state['next'] = "END"
        return state

    try:
        with transaction.atomic():
            CrewInformation.objects.create(
                ship=ship,
                crew_size=data['crew_size'],
                commander_name=data['commander_name'],
                commander_rank=data['commander_rank']
            )
    except Exception as e:
        logger.error(f"Error saving crew info for ship_id {data['ship_id']}: {e}", exc_info=True)
        state['error'] = f"Failed to save crew information: {e}"
        state['next'] = "END"
        return state

    messages = [
        SystemMessage(content="You are a naval operations analyst. Assess the readiness of the crew based on the crew size and commander's rank."),
        HumanMessage(content=f"Crew Size: {data['crew_size']}, Commander Rank: {data['commander_rank']}. Is the crew ready for the mission? Provide answer under 10 words.")
    ]
    try:
        response = groq_llm.invoke(messages)
        state['ICIA'] = f"Crew Readiness Assessment: {response.content}"
        logger.info(f"Crew readiness assessed for ship {data['ship_name']}: {response.content}")
    except Exception as e:
        logger.error(f"Error assessing crew readiness: {e}", exc_info=True)
        state['error'] = f"Failed to assess crew readiness: {e}"
        state['next'] = "END"
    return state

def insert_port_info_and_determine_strategic_advantage(state: SuperAgentState) -> SuperAgentState:
    data = state['data']
    try:
        ship = ShipInformation.objects.get(ship_id=data['ship_id'])
    except ShipInformation.DoesNotExist:
        logger.error(f"ShipInformation not found for ship_id {data['ship_id']}")
        state['error'] = "Ship information not found"
        state['next'] = "END"
        return state

    try:
        with transaction.atomic():
            PortInformation.objects.create(
                ship=ship,
                home_port=data['home_port']
            )
    except Exception as e:
        logger.error(f"Error saving port info for ship_id {data['ship_id']}: {e}", exc_info=True)
        state['error'] = f"Failed to save port information: {e}"
        state['next'] = "END"
        return state

    messages = [
        SystemMessage(content="You are a strategic advisor for naval operations. Determine the strategic advantage of the home port for the mission."),
        HumanMessage(content=f"Home Port: {data['home_port']}. What is the strategic advantage of this port for the mission? Provide answer under 10 words.")
    ]
    try:
        response = groq_llm.invoke(messages)
        state['IPIA'] = f"Strategic Advantage: {response.content}"
        logger.info(f"Strategic advantage determined for port {data['home_port']}: {response.content}")
    except Exception as e:
        logger.error(f"Error determining strategic advantage: {e}", exc_info=True)
        state['error'] = f"Failed to determine strategic advantage: {e}"
        state['next'] = "END"
        return state

    qa = data.get("question", [])
    state["next"] = "END" if isinstance(qa, list) and len(qa) == 0 else "answer_questions_node"
    return state

def answer_questions_node(state: SuperAgentState) -> SuperAgentState:
    questions = state.get('data', {}).get('question', [])
    answers = []
    for question in questions:
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=question)
        ]
        try:
            response = groq_llm.invoke(messages)
            answers.append(response.content)
        except Exception as e:
            logger.error(f"Error answering question '{question}': {e}", exc_info=True)
            answers.append(f"Error: {e}")
    state['questions'] = questions
    state['answers'] = answers
    logger.info(f"Answered {len(questions)} questions for user {state['uid']}")
    return state

def Q_router_node(state: SuperAgentState) -> SuperAgentState:
    home_port = state.get("data", {}).get("home_port")
    state["next"] = "answer_questions_node" if not home_port else "IPIA_node"
    logger.debug(f"Q_router directing to {'answer_questions_node' if not home_port else 'IPIA_node'}")
    return state

def deqoute_node(state: SuperAgentState) -> SuperAgentState:
    logger.debug(f"Deqoute node output: {state.get('output', {})} | IPIA: {state.get('IPIA', '')}")
    return state

# Supergraph Workflow
superflow = StateGraph(SuperAgentState)
superflow.add_node("payload", payload_maker)
superflow.add_node("router", router_node)
superflow.add_node("ISIC_node", insert_ship_info_and_calculate_priority)
superflow.add_node("ICIA_node", insert_crew_info_and_assess_readiness)
superflow.add_node("IPIA_node", insert_port_info_and_determine_strategic_advantage)
superflow.add_node("answer_questions_node", answer_questions_node)
superflow.add_node("Q_router", Q_router_node)
superflow.add_node("deqoute_node", deqoute_node)

# Define edges
superflow.set_entry_point("payload")
superflow.add_conditional_edges(
    "payload",
    lambda x: x["next"],
    {"router": "router", "END": END}
)
superflow.add_edge("router", "ISIC_node")
superflow.add_edge("ISIC_node", "ICIA_node")
superflow.add_edge("ICIA_node", "Q_router")
superflow.add_conditional_edges(
    "Q_router",
    lambda x: x["next"],
    {"answer_questions_node": "answer_questions_node", "IPIA_node": "IPIA_node"}
)
superflow.add_conditional_edges(
    "IPIA_node",
    lambda x: x["next"],
    {"answer_questions_node": "answer_questions_node", "END": END}
)
superflow.add_edge("IPIA_node", "deqoute_node")
superflow.add_edge("answer_questions_node", "deqoute_node")
superflow.add_edge("deqoute_node", END)

# Compile graph
checkpointer = MemorySaver()
supergraph = superflow.compile(checkpointer=checkpointer)