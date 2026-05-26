from django.db import models
from clients.models import User
from normalization.models import NormalizedRecord

class ReviewEvent(models.Model):
    class Action(models.TextChoices):
        APPROVED = 'APPROVED', 'Approved'
        FLAGGED = 'FLAGGED', 'Flagged'
        EDITED = 'EDITED', 'Edited'
        UNLOCKED = 'UNLOCKED', 'Unlocked'

    record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE, related_name='review_events')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.record.id} by {self.user.username if self.user else 'System'}"
