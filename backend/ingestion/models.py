from django.db import models
from clients.models import Client

class IngestionJob(models.Model):
    class SourceType(models.TextChoices):
        SAP = 'SAP', 'SAP (Fuel & Procurement)'
        UTILITY = 'UTILITY', 'Utility Data (Electricity)'
        TRAVEL = 'TRAVEL', 'Corporate Travel'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ingestion_jobs')
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    file_ref = models.CharField(max_length=500, help_text="Path or URL to the uploaded file")
    ingested_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Job {self.id} - {self.source_type} ({self.status})"

class RawRecord(models.Model):
    job = models.ForeignKey(IngestionJob, on_delete=models.CASCADE, related_name='raw_records')
    raw_data = models.JSONField(help_text="Original data exactly as received")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RawRecord {self.id} for Job {self.job.id}"
