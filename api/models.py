from datetime import datetime
from django.db import models

# Create your models here.
class CDD_Users(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'CDD_Users'


    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'



class Handover(models.Model):
    handover_id = models.CharField(primary_key=True, editable=False, max_length=60)
    date = models.DateField()
    shift = models.CharField(max_length=20)
    region = models.CharField(max_length=10)
    dispatcher_name = models.CharField(max_length=100)
    chief_duty_name = models.CharField(max_length=100)
    shift_highlights = models.TextField()
    non_standard_flights = models.JSONField(default=list, blank=True, null=True)
    naifr = models.JSONField(default=list, blank=True, null=True)
    aog = models.JSONField(default=list, blank=True, null=True)
    comat = models.JSONField(default=list, blank=True, null=True)
    fob_co_notam_created = models.BooleanField(default=False)
    comat_request_created = models.BooleanField(default=False)
    fuel_payload_critical_flights = models.JSONField(default=list, blank=True, null=True)
    weather_issues = models.JSONField(default=list, blank=True, null=True)
    operational_notams = models.JSONField(default=list, blank=True, null=True)
    performance_mels = models.JSONField(default=list, blank=True, null=True)
    nvb_tickets = models.JSONField(default=list, blank=True, null=True)
    tmi = models.JSONField(default=list, blank=True, null=True)
    enroute_weather_pirep = models.TextField(blank=True, null=True)
    cdd_followup = models.TextField(blank=True, null=True)
    misc = models.TextField(blank=True, null=True)
    it_issues = models.TextField(blank=True, null=True)
    procedural_changes = models.TextField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Handovers'


    def save(self, *args, **kwargs):
        if not self.handover_id:
            format_date = self.date.strftime('%Y-%m-%d')
            self.handover_id = f"{format_date}-{self.shift}-{self.region}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.handover_id}'

