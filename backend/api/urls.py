from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngestionJobViewSet, NormalizedRecordViewSet, IngestFileView, AuditLogListView, DashboardSummaryView

router = DefaultRouter()
router.register(r'jobs', IngestionJobViewSet)
router.register(r'records', NormalizedRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ingest/<str:source_type>/', IngestFileView.as_view(), name='ingest'),
    path('audit/<int:record_id>/', AuditLogListView.as_view(), name='audit_log'),
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard_summary'),
]
