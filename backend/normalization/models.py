from django.db import models
from clients.models import Client
from ingestion.models import RawRecord

class EmissionFactor(models.Model):
    class Scope(models.TextChoices):
        SCOPE_1 = 'SCOPE_1', 'Scope 1'
        SCOPE_2 = 'SCOPE_2', 'Scope 2'
        SCOPE_3 = 'SCOPE_3', 'Scope 3'

    substance = models.CharField(max_length=100) # e.g., Diesel, Grid Electricity
    scope = models.CharField(max_length=10, choices=Scope.choices)
    factor_value = models.DecimalField(max_digits=12, decimal_places=6, help_text="kg CO2e per unit")
    unit = models.CharField(max_length=20) # e.g., L, kWh, km
    source = models.CharField(max_length=100) # e.g., EPA, DEFRA
    version = models.CharField(max_length=20)
    valid_from = models.DateField()
    
    def __str__(self):
        return f"{self.substance} ({self.version})"

class NormalizedRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        FLAGGED = 'FLAGGED', 'Flagged'
        APPROVED = 'APPROVED', 'Approved'
        LOCKED = 'LOCKED', 'Locked'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='normalized_records')
    raw_record = models.OneToOneField(RawRecord, on_delete=models.CASCADE, related_name='normalized_record')
    
    # Categorization
    scope = models.CharField(max_length=10, choices=EmissionFactor.Scope.choices)
    category = models.CharField(max_length=100, blank=True)
    source_type = models.CharField(max_length=50) # SAP, UTILITY, TRAVEL
    
    # Normalized Data
    reporting_date = models.DateField()
    activity_type = models.CharField(max_length=100) # e.g., Diesel, Electricity, Flight
    
    # Original Quantity (preserved)
    original_quantity = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    original_unit = models.CharField(max_length=20, blank=True)
    
    # Normalized Quantity (SI base units: L/m3 -> m3, MWh -> kWh, miles -> km)
    normalized_quantity = models.DecimalField(max_digits=15, decimal_places=4)
    normalized_unit = models.CharField(max_length=20)
    
    # Calculated Emissions (Applied at review time ideally, but cached here for sorting)
    emission_factor = models.ForeignKey(EmissionFactor, on_delete=models.SET_NULL, null=True, blank=True)
    calculated_emissions_kg = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Review State
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    anomaly_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.activity_type} - {self.reporting_date} ({self.status})"
