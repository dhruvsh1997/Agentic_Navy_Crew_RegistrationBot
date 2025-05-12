from django.contrib import admin
from .models import ShipInformation, CrewInformation, MissionInformation, PortInformation, Conversation

@admin.register(ShipInformation)
class ShipInformationAdmin(admin.ModelAdmin):
    list_display = ('ship_id', 'ship_name', 'ship_type')

@admin.register(CrewInformation)
class CrewInformationAdmin(admin.ModelAdmin):
    list_display = ('ship', 'crew_size', 'commander_name', 'commander_rank')

@admin.register(MissionInformation)
class MissionInformationAdmin(admin.ModelAdmin):
    list_display = ('ship', 'mission_type')

@admin.register(PortInformation)
class PortInformationAdmin(admin.ModelAdmin):
    list_display = ('ship', 'home_port')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp')
    list_filter = ('user', 'timestamp')