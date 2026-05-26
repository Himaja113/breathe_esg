from rest_framework import serializers
from ingestion.models import IngestionJob, RawRecord
from normalization.models import NormalizedRecord, EmissionFactor
from review.models import ReviewEvent
from audit.models import AuditLog

class IngestionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionJob
        fields = '__all__'

class EmissionFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionFactor
        fields = '__all__'

class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = '__all__'

class NormalizedRecordSerializer(serializers.ModelSerializer):
    raw_data = serializers.JSONField(source='raw_record.raw_data', read_only=True)
    calculated_emissions_kg = serializers.DecimalField(max_digits=15, decimal_places=4, read_only=True)
    
    class Meta:
        model = NormalizedRecord
        fields = '__all__'

class ReviewEventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ReviewEvent
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
