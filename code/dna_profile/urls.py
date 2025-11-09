from django.urls import path
from .views import (
    health,
    DNAKitTypeListView, DNAKitTypeDetailView,
    DNAKitOrderCreateView, DNAKitOrderListView, DNAKitOrderDetailView,
    DNAKitOrderStatusUpdateView,  # New view
    activate_dna_kit,
    DNAResultListView, DNAResultDetailView,
    DNAReportListView, DNAReportDetailView,
    DNAConsentView,
    dna_dashboard,
    DNAResultCreateView, DNAResultUpdateView,
    DNAReportCreateView, DNAReportUpdateView,
    update_order_status,
    DNAPDFUploadCreateView, DNAPDFUploadListView, DNAPDFUploadDetailView,
    process_extracted_data, ExtractedDNADataListView
)

app_name = 'dna_profile'

urlpatterns = [
    # Health check
    path('health/', health, name='health'),
    
    # DNA Kit Types (Public endpoints)
    path('kit-types/', DNAKitTypeListView.as_view(), name='kit-types-list'),
    path('kit-types/<int:pk>/', DNAKitTypeDetailView.as_view(), name='kit-type-detail'),
    
    # DNA Kit Orders (User endpoints)
    path('orders/', DNAKitOrderListView.as_view(), name='orders-list'),
    path('orders/create/', DNAKitOrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', DNAKitOrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', DNAKitOrderStatusUpdateView.as_view(), name='order-status-update'),
    
    # DNA Kit Management
    path('kits/activate/', activate_dna_kit, name='kit-activate'),
    
    # DNA Results (User endpoints)
    path('results/', DNAResultListView.as_view(), name='results-list'),
    path('results/<int:pk>/', DNAResultDetailView.as_view(), name='result-detail'),
    
    # DNA Reports (User endpoints)
    path('reports/', DNAReportListView.as_view(), name='reports-list'),
    path('reports/<int:pk>/', DNAReportDetailView.as_view(), name='report-detail'),
    
    # Consent Management
    path('consent/', DNAConsentView.as_view(), name='consent'),
    
    # Dashboard
    path('dashboard/', dna_dashboard, name='dashboard'),
    
    # PDF Upload and Processing
    path('pdf/upload/', DNAPDFUploadCreateView.as_view(), name='pdf-upload'),
    path('pdf/uploads/', DNAPDFUploadListView.as_view(), name='pdf-uploads-list'),
    path('pdf/uploads/<int:pk>/', DNAPDFUploadDetailView.as_view(), name='pdf-upload-detail'),
    
    # Lab/Admin endpoints (should be restricted in production)
    path('lab/results/create/', DNAResultCreateView.as_view(), name='lab-result-create'),
    path('lab/results/<int:pk>/update/', DNAResultUpdateView.as_view(), name='lab-result-update'),
    path('lab/reports/create/', DNAReportCreateView.as_view(), name='lab-report-create'),
    path('lab/reports/<int:pk>/update/', DNAReportUpdateView.as_view(), name='lab-report-update'),
    path('lab/orders/<uuid:order_id>/status/', update_order_status, name='lab-order-status'),
    path('lab/extracted-data/', ExtractedDNADataListView.as_view(), name='lab-extracted-data-list'),
    path('lab/process-extracted-data/', process_extracted_data, name='lab-process-extracted-data'),
]
