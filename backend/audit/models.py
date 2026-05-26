from django.db import models
from clients.models import User
from normalization.models import NormalizedRecord

class AuditLog(models.Model):
    record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    before_state = models.JSONField(help_text="Record state before edit")
    after_state = models.JSONField(help_text="Record state after edit")
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"Audit log {self.id} for Record {self.record.id}"
