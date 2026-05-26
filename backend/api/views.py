from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Count, Sum
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS

class IsAnalystOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'ANALYST'

class LoginView(APIView):
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'role': user.role, 'username': user.username})
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
from .serializers import *
from ingestion.models import IngestionJob
from normalization.models import NormalizedRecord
from review.models import ReviewEvent
from audit.models import AuditLog
from clients.models import Client, User
from ingestion.services import process_file
import threading

class IngestionJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IngestionJob.objects.all().order_by('-ingested_at')
    serializer_class = IngestionJobSerializer

class IngestFileView(APIView):
    permission_classes = [IsAnalystOrReadOnly]
    
    def post(self, request, source_type, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        file_content = file.read().decode('utf-8')
        
        # Get first client for prototype
        client = Client.objects.first()
        if not client:
            client = Client.objects.create(name="Demo Client")
            
        try:
            source_enum = IngestionJob.SourceType[source_type.upper()]
        except KeyError:
            return Response({"error": "Invalid source type"}, status=status.HTTP_400_BAD_REQUEST)
            
        job = IngestionJob.objects.create(
            client=client,
            source_type=source_enum,
            file_ref=file.name
        )
        
        # Process in background thread for prototype (celery in prod)
        thread = threading.Thread(target=process_file, args=(job, client, file_content))
        thread.start()
        
        return Response(IngestionJobSerializer(job).data, status=status.HTTP_201_CREATED)

class NormalizedRecordViewSet(viewsets.ModelViewSet):
    queryset = NormalizedRecord.objects.all().order_by('-created_at')
    serializer_class = NormalizedRecordSerializer
    permission_classes = [IsAnalystOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        job_id = self.request.query_params.get('job', None)
        status = self.request.query_params.get('status', None)
        scope = self.request.query_params.get('scope', None)
        
        if job_id:
            queryset = queryset.filter(raw_record__job_id=job_id)
        if status:
            queryset = queryset.filter(status=status)
        if scope:
            queryset = queryset.filter(scope=scope)
            
        return queryset
        
    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_state = model_to_dict(old_instance)
        
        # Convert date to string for JSON serialization
        if old_state.get('reporting_date'):
             old_state['reporting_date'] = old_state['reporting_date'].isoformat()
        
        # Convert Decimals to string for JSON serialization
        for key, value in old_state.items():
             import decimal
             if isinstance(value, decimal.Decimal):
                  old_state[key] = str(value)
        
        new_instance = serializer.save()
        
        # Recalculate emissions if quantity changed
        if new_instance.emission_factor and new_instance.normalized_quantity:
            new_instance.calculated_emissions_kg = new_instance.normalized_quantity * new_instance.emission_factor.factor_value
            if new_instance.status == 'FLAGGED':
                 new_instance.status = 'PENDING'
                 new_instance.anomaly_reason = ''
            new_instance.save()
            
        new_state = model_to_dict(new_instance)
        
        if new_state.get('reporting_date'):
             new_state['reporting_date'] = new_state['reporting_date'].isoformat()
             
        for key, value in new_state.items():
             import decimal
             if isinstance(value, decimal.Decimal):
                  new_state[key] = str(value)
        
        # Log Audit
        AuditLog.objects.create(
            record=new_instance,
            user=self.request.user if self.request.user.is_authenticated else User.objects.first(),
            before_state=old_state,
            after_state=new_state,
            reason="Manual edit via API"
        )
        
        # Log Review Event
        ReviewEvent.objects.create(
            record=new_instance,
            user=self.request.user if self.request.user.is_authenticated else User.objects.first(),
            action=ReviewEvent.Action.EDITED,
            note="Record edited"
        )

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        record = self.get_object()
        if record.status == NormalizedRecord.Status.LOCKED:
            return Response({"error": "Record is locked"}, status=status.HTTP_400_BAD_REQUEST)
            
        record.status = NormalizedRecord.Status.APPROVED
        record.save()
        
        ReviewEvent.objects.create(
            record=record,
            user=self.request.user if self.request.user.is_authenticated else User.objects.first(),
            action=ReviewEvent.Action.APPROVED
        )
        return Response(self.get_serializer(record).data)
        
    @action(detail=True, methods=['patch'])
    def flag(self, request, pk=None):
        record = self.get_object()
        reason = request.data.get('reason', 'Manually flagged')
        
        record.status = NormalizedRecord.Status.FLAGGED
        record.anomaly_reason = reason
        record.save()
        
        ReviewEvent.objects.create(
            record=record,
            user=self.request.user if self.request.user.is_authenticated else User.objects.first(),
            action=ReviewEvent.Action.FLAGGED,
            note=reason
        )
        return Response(self.get_serializer(record).data)

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    
    def get_queryset(self):
        record_id = self.kwargs['record_id']
        return AuditLog.objects.filter(record_id=record_id).order_by('-timestamp')

class DashboardSummaryView(APIView):
    def get(self, request, format=None):
        records = NormalizedRecord.objects.all()
        
        total_records = records.count()
        pending = records.filter(status=NormalizedRecord.Status.PENDING).count()
        flagged = records.filter(status=NormalizedRecord.Status.FLAGGED).count()
        approved = records.filter(status=NormalizedRecord.Status.APPROVED).count()
        locked = records.filter(status=NormalizedRecord.Status.LOCKED).count()
        
        scope_counts = {
            'SCOPE_1': records.filter(scope='SCOPE_1').count(),
            'SCOPE_2': records.filter(scope='SCOPE_2').count(),
            'SCOPE_3': records.filter(scope='SCOPE_3').count(),
        }
        
        emissions_by_scope = list(records.values('scope').annotate(total=Sum('calculated_emissions_kg')))
        
        recent_jobs = IngestionJobSerializer(IngestionJob.objects.all().order_by('-ingested_at')[:5], many=True).data
        
        return Response({
            "total_records": total_records,
            "pending": pending,
            "flagged": flagged,
            "approved": approved,
            "locked": locked,
            "scope_counts": scope_counts,
            "emissions_by_scope": emissions_by_scope,
            "recent_jobs": recent_jobs
        })
