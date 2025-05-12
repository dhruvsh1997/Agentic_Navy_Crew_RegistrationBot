import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import ChatbotForm
from .utils import supergraph
from datetime import datetime
import json
from langgraph.errors import InvalidUpdateError

# Set up logger
logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"New user registered and logged in: {user.username}")
            return redirect('Navy_registrar:chatbot')
        else:
            logger.warning("Registration form is invalid.")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User logged in: {user.username}")
            return redirect('Navy_registrar:chatbot')
        else:
            logger.warning("Login form is invalid.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def user_logout(request):
    logger.info(f"User logged out: {request.user.username}")
    logout(request)
    return redirect('Navy_registrar:login')

@login_required
def chatbot(request):
    if request.method == 'POST':
        form = ChatbotForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data['user_input']
            user_id = request.user.username
            logger.debug(f"Chatbot input from {user_id}: {user_input}")
            initial_state = {
                "query": user_input,
                "data": {},
                "memory": {},
                "uid": user_id,
                "error": None,
                "output": {'question_answer': {'questions': [], 'answers': []}},
                "questions": [],
                "answers": [],
                "ISIC": "",
                "ICIA": "",
                "IPIA": "",
                "next": None
            }
            try:
                final_state = supergraph.invoke(
                    initial_state,
                    config={"configurable": {"thread_id": str(datetime.now().timestamp())}}
                )
                logger.debug(f"Final state for {user_id}: {final_state}")
            except InvalidUpdateError as e:
                logger.error(f"LangGraph concurrent update error: {e}", exc_info=True)
                final_state = {"error": "Internal workflow error: concurrent state update"}
            except Exception as e:
                logger.error(f"Exception in supergraph.invoke: {e}", exc_info=True)
                final_state = {"error": str(e)}
            response = {}
            if final_state["error"]:
                response["message"] = f"Error: {final_state['error']}"
                logger.error(f"Error in chatbot response for {user_id}: {final_state['error']}")
            else:
                response["data"] = final_state["data"]
                if final_state.get("ISIC"):
                    response["mission_priority"] = final_state["ISIC"]
                if final_state.get("ICIA"):
                    response["crew_readiness"] = final_state["ICIA"]
                if final_state.get("IPIA"):
                    response["strategic_advantage"] = final_state["IPIA"]
                if final_state.get("questions") and final_state.get("answers"):
                    response["questions_answers"] = [
                        {"question": q, "answer": a}
                        for q, a in zip(final_state["questions"], final_state["answers"])
                    ]
                logger.info(f"Chatbot processed response for {user_id}")
            # Handle AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'response': json.dumps(response, indent=2)})
            # Handle regular POST
            return render(request, 'chatbot.html', {'form': form, 'response': json.dumps(response, indent=2)})
    else:
        form = ChatbotForm()
    return render(request, 'chatbot.html', {'form': form})