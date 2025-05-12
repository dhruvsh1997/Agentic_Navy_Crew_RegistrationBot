from django.db import models
from django.contrib.auth.models import User
import uuid

class ShipInformation(models.Model):
    ship_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ship_name = models.CharField(max_length=255)
    ship_type = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Ship Information"
        verbose_name_plural = "Ship Information"

class CrewInformation(models.Model):
    ship = models.ForeignKey(ShipInformation, on_delete=models.CASCADE, related_name='crew')
    crew_size = models.IntegerField()
    commander_name = models.CharField(max_length=255)
    commander_rank = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Crew Information"
        verbose_name_plural = "Crew Information"

class MissionInformation(models.Model):
    ship = models.ForeignKey(ShipInformation, on_delete=models.CASCADE, related_name='missions')
    mission_type = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Mission Information"
        verbose_name_plural = "Mission Information"

class PortInformation(models.Model):
    ship = models.ForeignKey(ShipInformation, on_delete=models.CASCADE, related_name='ports')
    home_port = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Port Information"
        verbose_name_plural = "Port Information"

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} for {self.user.username}"

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"