from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import generics, status, filters
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from aevum.pagination import StandardResultsPagination, LargeResultsPagination, SmallResultsPagination
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import serializers
from django.db import transaction

logger = logging.getLogger(__name__)

from .models import (
    DNAKitType, DNAKitOrder, DNAKit, DNAResult, 
    DNAReport, DNAConsent, DNAPDFUpload, ExtractedDNAData
)
from .serializers import (
    DNAKitTypeSerializer, DNAKitOrderCreateSerializer, 
    DNAKitOrderListSerializer, DNAKitOrderDetailSerializer,
    DNAKitOrderUpdateSerializer,
    DNAKitActivationSerializer, DNAResultCreateSerializer, DNAResultUpdateSerializer, 
    DNAResultSerializer,
    DNAReportSerializer,  # Add this line
    DNAReportCreateSerializer, DNAResultSummarySerializer, DNAPDFUploadSerializer,
    DNAPDFUploadDetailSerializer, ExtractedDNADataSerializer, ProcessExtractedDataSerializer,
    DNAConsentSerializer, DNAPDFUploadResponseSerializer
)
from dashboard.email_utils import (
    send_dna_kit_order_user_notification,
    send_dna_kit_order_admin_notification
)


# Using centralized pagination classes from aevum.pagination


# Health check endpoint
@extend_schema(tags=['DNA Profile'])
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "app": "dna_profile"})


# DNA Kit Types (Public - for browsing available kits)
@extend_schema(
    tags=['DNA Profile'],
    summary='List Available DNA Kit Types',
    description='Get all available DNA kit types for ordering'
)
class DNAKitTypeListView(generics.ListAPIView):
    serializer_class = DNAKitTypeSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'price', 'category']
    ordering = ['category', 'name']
    pagination_class = SmallResultsPagination
    
    def get_queryset(self):
        queryset = DNAKitType.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


# DNA Kit Type Detail
@extend_schema(
    tags=['DNA Profile'],
    summary='Get DNA Kit Type Details',
    description='Get detailed information about a specific DNA kit type'
)
class DNAKitTypeDetailView(generics.RetrieveAPIView):
    serializer_class = DNAKitTypeSerializer
    permission_classes = [AllowAny]
    queryset = DNAKitType.objects.filter(is_active=True)


# DNA Kit Order Creation
@extend_schema(
    tags=['DNA Profile'],
    summary='Order DNA Kit',
    description='Place an order for a DNA analysis kit'
)
class DNAKitOrderCreateView(generics.CreateAPIView):
    serializer_class = DNAKitOrderCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Additional logic can be added here (e.g., payment processing)
        # Explicitly set the user for the order
        order = serializer.save(user=self.request.user)
        
        # Create associated DNA Kit with unique ID
        import uuid
        kit_id = f"AEVUM-{str(uuid.uuid4())[:8].upper()}"
        DNAKit.objects.create(
            kit_id=kit_id,
            order=order
        )
        
        # Send email notifications
        try:
            # Send user confirmation email
            send_dna_kit_order_user_notification(order)
            
            # Send admin notification email
            send_dna_kit_order_admin_notification(order)
        except Exception as e:
            # Log email sending errors without interrupting order creation
            logger.error(f"Failed to send DNA kit order emails: {e}")


# User's DNA Kit Orders List
@extend_schema(
    tags=['DNA Profile'],
    summary='List My DNA Kit Orders',
    description='Get all DNA kit orders for the authenticated user'
)
class DNAKitOrderListView(generics.ListAPIView):
    serializer_class = DNAKitOrderListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order_date', 'status']
    ordering = ['-order_date']
    
    def get_queryset(self):
        return DNAKitOrder.objects.filter(user=self.request.user).select_related('kit')


# DNA Kit Order Detail
@extend_schema(
    tags=['DNA Profile'],
    summary='Get DNA Kit Order Details',
    description='Get detailed information about a specific DNA kit order'
)
class DNAKitOrderDetailView(generics.RetrieveAPIView):
    serializer_class = DNAKitOrderDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DNAKitOrder.objects.filter(user=self.request.user)


# DNA Kit Activation
@extend_schema(
    tags=['DNA Profile'],
    summary='Activate DNA Kit',
    description='Activate a DNA kit using the kit ID'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_dna_kit(request):
    serializer = DNAKitActivationSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        kit_id = serializer.validated_data['kit_id']
        kit = DNAKit.objects.get(kit_id=kit_id)
        
        # Activate the kit
        kit.is_activated = True
        kit.activation_date = timezone.now()
        kit.save()
        
        # Update order status
        kit.order.status = 'DELIVERED'
        kit.order.delivered_date = timezone.now()
        kit.order.save()
        
        return Response({
            'message': 'DNA kit activated successfully',
            'kit_id': kit_id,
            'activation_date': kit.activation_date
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# DNA Results List
@extend_schema(
    tags=['DNA Profile'],
    summary='List My DNA Results',
    description='Get all DNA analysis results for the authenticated user'
)
class DNAResultListView(generics.ListAPIView):
    serializer_class = DNAResultSummarySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['trait_name', 'category', 'subcategory']
    ordering_fields = ['category', 'trait_name', 'analysis_date']
    ordering = ['category', 'trait_name']
    
    def get_queryset(self):
        user_kits = DNAKit.objects.filter(order__user=self.request.user)
        queryset = DNAResult.objects.filter(kit__in=user_kits)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # Filter by confidence level
        confidence = self.request.query_params.get('confidence')
        if confidence:
            queryset = queryset.filter(confidence_level=confidence)
            
        return queryset


# DNA Result Detail
@extend_schema(
    tags=['DNA Profile'],
    summary='Get DNA Result Details',
    description='Get detailed information about a specific DNA analysis result'
)
class DNAResultDetailView(generics.RetrieveAPIView):
    serializer_class = DNAResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_kits = DNAKit.objects.filter(order__user=self.request.user)
        return DNAResult.objects.filter(kit__in=user_kits)


# DNA Reports List
@extend_schema(
    tags=['DNA Profile'],
    summary='List My DNA Reports',
    description='Get all DNA analysis reports for the authenticated user'
)
class DNAReportListView(generics.ListAPIView):
    serializer_class = DNAReportSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-generated_date']
    
    def get_queryset(self):
        user_kits = DNAKit.objects.filter(order__user=self.request.user)
        return DNAReport.objects.filter(kit__in=user_kits, status='READY')


# DNA Report Detail
@extend_schema(
    tags=['DNA Profile'],
    summary='Get DNA Report Details',
    description='Get detailed information about a specific DNA analysis report'
)
class DNAReportDetailView(generics.RetrieveAPIView):
    serializer_class = DNAReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_kits = DNAKit.objects.filter(order__user=self.request.user)
        return DNAReport.objects.filter(kit__in=user_kits)


# DNA Consent Management
@extend_schema(
    tags=['DNA Profile'],
    summary='Manage DNA Consent',
    description='View and update DNA analysis and data usage consent'
)
class DNAConsentView(generics.ListCreateAPIView):
    serializer_class = DNAConsentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DNAConsent.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            consent_date=timezone.now() if serializer.validated_data.get('consented') else None,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


# DNA Dashboard
@extend_schema(
    tags=['DNA Profile'],
    summary='DNA Profile Dashboard',
    description='Get comprehensive dashboard data for DNA profile management'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dna_dashboard(request):
    user = request.user
    
    # Order statistics
    orders = DNAKitOrder.objects.filter(user=user)
    total_orders = orders.count()
    active_orders = orders.exclude(status__in=['COMPLETED', 'CANCELLED']).count()
    completed_orders = orders.filter(status='COMPLETED').count()
    
    # Result statistics
    user_kits = DNAKit.objects.filter(order__user=user)
    all_results = DNAResult.objects.filter(kit__in=user_kits)
    pending_results = user_kits.filter(order__status__in=['PROCESSING', 'SAMPLE_RECEIVED']).count()
    
    # Recent data
    recent_orders = orders.order_by('-order_date')[:5]
    latest_results = all_results.order_by('-analysis_date')[:10]
    
    # Result counts by category
    result_stats = all_results.values('category').annotate(count=Count('id'))
    ancestry_count = next((item['count'] for item in result_stats if item['category'] == 'ANCESTRY'), 0)
    health_count = next((item['count'] for item in result_stats if item['category'] == 'HEALTH_RISK'), 0)
    fitness_count = next((item['count'] for item in result_stats if item['category'] == 'FITNESS'), 0)
    
    # Consent status
    consents = DNAConsent.objects.filter(user=user)
    consent_status = {consent.consent_type: consent.consented for consent in consents}
    
    dashboard_data = {
        'total_orders': total_orders,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'pending_results': pending_results,
        'recent_orders': DNAKitOrderListSerializer(recent_orders, many=True).data,
        'latest_results': DNAResultSummarySerializer(latest_results, many=True).data,
        'ancestry_results_count': ancestry_count,
        'health_results_count': health_count,
        'fitness_results_count': fitness_count,
        'consent_status': consent_status
    }
    
    serializer = DNADashboardSerializer(dashboard_data)
    return Response(serializer.data)


# Lab/Admin endpoints for managing results (restricted access)
@extend_schema(
    tags=['DNA Profile'],
    summary='Create DNA Results (Lab Use)',
    description='Create new DNA analysis results - restricted to lab personnel'
)
class DNAResultCreateView(generics.CreateAPIView):
    serializer_class = DNAResultCreateSerializer
    permission_classes = [IsAuthenticated]  # Should be restricted to lab staff
    
    def perform_create(self, serializer):
        # Additional validation or processing can be added here
        serializer.save()


@extend_schema(
    tags=['DNA Profile'],
    summary='Update DNA Results (Lab Use)',
    description='Update DNA analysis results - restricted to lab personnel'
)
class DNAResultUpdateView(generics.UpdateAPIView):
    serializer_class = DNAResultUpdateSerializer
    permission_classes = [IsAuthenticated]  # Should be restricted to lab staff
    queryset = DNAResult.objects.all()
    
    # Note: In production, this should have proper lab staff permissions


@extend_schema(
    tags=['DNA Profile'],
    summary='Create DNA Report (Lab Use)',
    description='Create new DNA analysis report - restricted to lab personnel'
)
class DNAReportCreateView(generics.CreateAPIView):
    serializer_class = DNAReportCreateSerializer
    permission_classes = [IsAuthenticated]  # Should be restricted to lab staff
    
    def perform_create(self, serializer):
        # Additional validation or processing can be added here
        serializer.save()


@extend_schema(
    tags=['DNA Profile'],
    summary='Update DNA Report (Lab Use)', 
    description='Update DNA analysis report - restricted to lab personnel'
)
class DNAReportUpdateView(generics.UpdateAPIView):
    serializer_class = DNAReportSerializer
    permission_classes = [IsAuthenticated]  # Should be restricted to lab staff
    queryset = DNAReport.objects.all()


# Order status update (Lab/Admin use)
@extend_schema(
    tags=['DNA Profile'],
    summary='Update Order Status (Lab Use)',
    description='Update DNA kit order status - restricted to lab personnel'
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  # Should be restricted to lab staff
def update_order_status(request, order_id):
    try:
        order = DNAKitOrder.objects.get(order_id=order_id)
    except DNAKitOrder.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    if new_status not in [choice[0] for choice in DNAKitOrder.STATUS_CHOICES]:
        return Response({
            'error': 'Invalid status'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update status and relevant dates
    order.status = new_status
    
    if new_status == 'SHIPPED':
        order.shipped_date = timezone.now()
        order.tracking_number = request.data.get('tracking_number', '')
    elif new_status == 'SAMPLE_RECEIVED':
        order.sample_received_date = timezone.now()
    elif new_status == 'COMPLETED':
        # Mark completion and generate report if not exists
        pass
    
    order.save()
    
    return Response({
        'message': f'Order status updated to {new_status}',
        'order_id': str(order.order_id),
        'status': new_status
    })


# DNA Kit Order Status Update
@extend_schema(
    tags=['DNA Profile'],
    summary='Update DNA Kit Order Status',
    description='Update the status of a DNA kit order (e.g., mark as shipped)'
)
class DNAKitOrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = DNAKitOrderUpdateSerializer
    permission_classes = [IsAdminUser]  # Only admin can update order status
    
    def get_queryset(self):
        return DNAKitOrder.objects.all()


# PDF Upload and Processing Endpoints
# PDF Upload Endpoint
@extend_schema(
    tags=['DNA Profile'],
    summary='Upload DNA Result PDF',
    description='Upload a PDF file for a specific DNA kit',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'kit_id': {
                    'type': 'string', 
                    'description': 'Unique DNA Kit ID (e.g., AEVUM-ABC12345)',
                    'example': 'AEVUM-ABC12345'
                },
                'pdf_file': {
                    'type': 'string', 
                    'format': 'binary', 
                    'description': 'PDF file containing DNA results (max 10MB)'
                }
            },
            'required': ['kit_id', 'pdf_file']
        }
    },
    responses={
        201: DNAPDFUploadResponseSerializer,
        400: {
            'description': 'Bad Request',
            'content': {
                'application/json': {
                    'example': {
                        'error': 'DNA Kit with ID \'INVALID_ID\' does not exist.'
                    }
                }
            }
        }
    }
)
class DNAPDFUploadCreateView(generics.CreateAPIView):
    serializer_class = DNAPDFUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle PDF upload with kit ID
        """
        # Log the entire request data for debugging
        logger.info(f"PDF Upload Request Data: {request.data}")
        logger.info(f"PDF Upload Files: {request.FILES}")

        # Get the uploaded file first
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            logger.error("No PDF file uploaded")
            return Response(
                {"error": "No PDF file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size
        max_size = 10 * 1024 * 1024  # 10 MB
        if pdf_file.size > max_size:
            logger.error(f"File size too large: {pdf_file.size} bytes")
            return Response(
                {"error": "File size must be under 10 MB"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        if not pdf_file.name.lower().endswith('.pdf'):
            logger.error(f"Invalid file type: {pdf_file.name}")
            return Response(
                {"error": "Only PDF files are allowed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get kit_id from POST data (not FILES)
        kit_id = request.POST.get('kit_id')
        if not kit_id:
            logger.error("No kit_id provided")
            return Response(
                {"error": "kit_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare data for serializer
        data = {
            'kit_id': kit_id,
            'pdf_file': pdf_file.name
        }
        
        # Use serializer for validation
        serializer = self.get_serializer(data=data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            logger.error(f"Serializer validation failed: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the upload
        pdf_upload = serializer.save()
        
        # Trigger PDF processing
        try:
            from .pdf_processor import process_dna_pdf
            
            # Process PDF synchronously (in production, use async task)
            logger.info(f"Starting PDF processing for upload {pdf_upload.upload_id}")
            result = process_dna_pdf(pdf_upload)
            
            logger.info(f"PDF processing result: {result}")
            
            if result['success']:
                # Use transaction to ensure data consistency
                with transaction.atomic():
                    # Create extracted data objects
                    extracted_data_list = self._create_extracted_data_objects(pdf_upload, result['extracted_data'])
                    logger.info(f"Created {len(extracted_data_list)} extracted data objects")
                    
                    # Create DNA results from extracted data
                    dna_results = self._create_dna_results_from_extracted_data(pdf_upload, extracted_data_list)
                    logger.info(f"Created {len(dna_results)} DNA results")
                    
                    # Create DNA report
                    dna_report = self._create_dna_report(pdf_upload, dna_results)
                    if dna_report:
                        logger.info(f"Created DNA report: {dna_report.report_id}")
                    else:
                        logger.warning("Failed to create DNA report")
                    
                    # Update order status to completed if not already
                    self._update_order_status_after_results(pdf_upload.kit.order, dna_results, dna_report)
                    
                    # Send notification to user about results being ready
                    if dna_report:
                        self._notify_user_results_ready(pdf_upload.kit.order, dna_report)
                    
                    # Update upload status
                    pdf_upload.status = 'COMPLETED'
                    pdf_upload.processing_completed_at = timezone.now()
                    pdf_upload.results_created_count = len(dna_results)
                    pdf_upload.save()
                    
                    logger.info(f"PDF processing completed: {len(dna_results)} results created, report generated")
            else:
                # Mark as failed if processing unsuccessful
                pdf_upload.status = 'FAILED'
                pdf_upload.processing_notes = result.get('error', 'Unknown processing error')
                pdf_upload.save()
                logger.error(f"PDF processing failed: {pdf_upload.processing_notes}")
        except Exception as e:
            # Log and mark as failed
            logger.error(f"PDF processing failed with exception: {str(e)}", exc_info=True)
            pdf_upload.status = 'FAILED'
            pdf_upload.processing_notes = f"Processing error: {str(e)}"
            pdf_upload.save()
        
        # Prepare response
        response_data = {
            'upload_id': pdf_upload.upload_id,
            'kit_id': pdf_upload.kit.kit_id,
            'status': pdf_upload.status,
            'original_filename': pdf_upload.original_filename
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def _create_extracted_data_objects(self, pdf_upload, extracted_data):
        """Create ExtractedDNAData objects from processed data"""
        created_extracted_data = []
        for data in extracted_data:
            extracted_data_obj = ExtractedDNAData.objects.create(
                pdf_upload=pdf_upload,
                trait_name=data.get('trait_name'),
                category=data.get('category'),
                subcategory=data.get('subcategory'),
                result_value=data.get('result_value'),
                confidence_level=data.get('confidence_level'),
                risk_score=data.get('risk_score'),
                genetic_markers=data.get('genetic_markers', []),
                methodology=data.get('methodology'),
                recommendations=data.get('recommendations'),
                extraction_confidence=data.get('extraction_confidence'),
                page_number=data.get('page_number'),
                text_position=data.get('text_position', {})
            )
            created_extracted_data.append(extracted_data_obj)
        return created_extracted_data

    def _create_dna_results_from_extracted_data(self, pdf_upload, extracted_data_list):
        """Create DNAResult objects from ExtractedDNAData objects."""
        created_dna_results = []
        for extracted_data in extracted_data_list:
            try:
                # Determine confidence level
                confidence_mapping = {
                    'HIGH': 'HIGH',
                    'MEDIUM': 'MEDIUM',
                    'LOW': 'LOW'
                }
                confidence_level = confidence_mapping.get(
                    extracted_data.confidence_level, 
                    'MEDIUM'
                )
                
                # Determine risk score
                try:
                    risk_score = float(extracted_data.risk_score) if extracted_data.risk_score is not None else None
                except (TypeError, ValueError):
                    risk_score = None
                
                # Check if a result already exists
                existing_result = DNAResult.objects.filter(
                    kit=extracted_data.pdf_upload.kit,
                    category=extracted_data.category or 'GENERAL',
                    trait_name=extracted_data.trait_name or 'Unknown Trait'
                ).first()
                
                # If result exists, update it instead of creating a new one
                if existing_result:
                    logger.info(f"Updating existing result for trait: {existing_result.trait_name}")
                    existing_result.result_value = str(extracted_data.result_value) if extracted_data.result_value is not None else 'N/A'
                    existing_result.confidence_level = confidence_level
                    existing_result.risk_score = risk_score
                    existing_result.genetic_markers = extracted_data.genetic_markers or []
                    existing_result.methodology = extracted_data.methodology or 'Automated PDF Extraction'
                    existing_result.recommendations = extracted_data.recommendations or 'No specific recommendations available.'
                    existing_result.reviewed_by = 'Automated PDF Processing System'
                    existing_result.save()
                    
                    dna_result = existing_result
                    
                    # Check if this extracted_data is already linked to a different result
                    if extracted_data.dna_result and extracted_data.dna_result != existing_result:
                        # If linked to a different result, unlink it first
                        extracted_data.dna_result = None
                        extracted_data.save()
                    
                    # Only link if not already linked to this result
                    if extracted_data.dna_result != existing_result:
                        # Check if another ExtractedDNAData is already linked to this result
                        existing_link = ExtractedDNAData.objects.filter(dna_result=existing_result).first()
                        if existing_link and existing_link != extracted_data:
                            # Unlink the existing one
                            existing_link.dna_result = None
                            existing_link.save()
                        
                        # Link this extracted_data to the result
                        extracted_data.dna_result = existing_result
                else:
                    # Create new result if no existing result found
                    dna_result = DNAResult.objects.create(
                        kit=extracted_data.pdf_upload.kit,
                        category=extracted_data.category or 'GENERAL',
                        subcategory=extracted_data.subcategory or 'UNSPECIFIED',
                        trait_name=extracted_data.trait_name or 'Unknown Trait',
                        result_value=str(extracted_data.result_value) if extracted_data.result_value is not None else 'N/A',
                        confidence_level=confidence_level,
                        risk_score=risk_score,
                        genetic_markers=extracted_data.genetic_markers or [],
                        methodology=extracted_data.methodology or 'Automated PDF Extraction',
                        recommendations=extracted_data.recommendations or 'No specific recommendations available.',
                        reviewed_by='Automated PDF Processing System',
                        clinical_significance=None  # You might want to add logic to determine this
                    )
                    
                    # Link the extracted_data to the new result
                    extracted_data.dna_result = dna_result
                
                # Mark the extracted data as processed and save
                extracted_data.is_processed = True
                extracted_data.processing_notes = 'Successfully converted to DNAResult'
                extracted_data.save()
                
                created_dna_results.append(dna_result)
            
            except Exception as e:
                logger.error(f"Error processing extracted data for result: {e}", exc_info=True)
                # Continue processing other extracted data even if one fails
                continue
        
        return created_dna_results

    def _create_dna_report(self, pdf_upload, dna_results):
        """Create DNAReport from DNAResult objects."""
        # Validate inputs
        if not dna_results:
            logger.warning(f"No DNA results to create report for upload {pdf_upload.upload_id}")
            return None

        # Generate summary from results
        summary_parts = []
        key_findings = []
        recommendations_parts = []
        
        for result in dna_results:
            try:
                if result.trait_name:
                    summary_parts.append(f"{result.trait_name}: {result.result_value}")
                    
                    # Add to key findings
                    key_findings.append({
                        'trait': result.trait_name or 'Unknown Trait',
                        'value': str(result.result_value) or 'N/A',
                        'confidence': result.confidence_level or 'UNKNOWN',
                        'risk_score': float(result.risk_score) if result.risk_score is not None else None,
                        'category': result.category or 'GENERAL'
                    })
                    
                    # Add recommendations if available
                    if result.recommendations:
                        recommendations_parts.append(f"{result.trait_name}: {result.recommendations}")
            except Exception as e:
                logger.error(f"Error processing result for report: {e}")
        
        # Get the file URL for the uploaded PDF
        try:
            # Assuming the PDF is stored in a way that allows generating a URL
            report_file_url = self.request.build_absolute_uri(pdf_upload.pdf_file.url) if pdf_upload.pdf_file else None
        except Exception as e:
            logger.error(f"Error generating report file URL: {e}")
            report_file_url = None
        
        # Prepare summary and recommendations
        summary = (f"DNA analysis report generated from uploaded PDF. " +
                   f"Analyzed {len(dna_results)} genetic traits. " + 
                   ". ".join(summary_parts[:3]) + 
                   ("..." if len(summary_parts) > 3 else ""))
        
        recommendations = "\n".join(recommendations_parts) if recommendations_parts else "No specific recommendations available."
        
        # Create the report
        try:
            # Check if a report already exists for this kit
            existing_report = DNAReport.objects.filter(
                kit=pdf_upload.kit, 
                report_type='COMPREHENSIVE'
            ).first()
            
            if existing_report:
                # Update existing report
                logger.info(f"Updating existing report: {existing_report.report_id}")
                existing_report.summary = summary
                existing_report.key_findings = key_findings
                existing_report.recommendations = recommendations
                existing_report.report_file_url = report_file_url
                existing_report.raw_data_url = report_file_url
                existing_report.status = 'READY'
                existing_report.validation_date = timezone.now()
                existing_report.save()
                
                dna_report = existing_report
            else:
                # Create new report
                dna_report = DNAReport.objects.create(
                    kit=pdf_upload.kit,
                    report_type='COMPREHENSIVE',
                    status='READY',
                    summary=summary,
                    key_findings=key_findings,
                    recommendations=recommendations,
                    quality_score=85.0,  # Default quality score
                    validated_by='Automated PDF Processing System',
                    validation_date=timezone.now(),
                    generated_date=timezone.now(),
                    report_file_url=report_file_url,
                    raw_data_url=report_file_url
                )
            
            logger.info(f"DNA Report created/updated: {dna_report.report_id} for kit {pdf_upload.kit.kit_id}")
            return dna_report
        
        except Exception as e:
            logger.error(f"Failed to create/update DNA report: {e}", exc_info=True)
            return None

    def _update_order_status_after_results(self, order, dna_results, dna_report):
        """Update order status after processing results"""
        try:
            if not order:
                logger.warning("No order provided for status update")
                return False
            
            if dna_results and dna_report:
                # Mark order as results generated
                order.status = 'RESULTS_GENERATED'
                order.estimated_completion_date = timezone.now()
                order.save()
                
                logger.info(f"Order {order.order_id} status updated to RESULTS_GENERATED")
                return True
            
            logger.warning(f"Cannot update order {order.order_id} status - missing results or report")
            return False
        
        except Exception as e:
            logger.error(f"Error updating order status: {e}", exc_info=True)
            return False

    def _notify_user_results_ready(self, order, dna_report):
        """Send notification to user that DNA results are ready."""
        if not dna_report:
            logger.warning(f"Cannot send notification - no DNA report for order {order.order_id}")
            return
        
        try:
            from dashboard.email_utils import send_dna_results_ready_notification
            
            # Validate required data
            if not order or not order.user or not order.user.email:
                logger.error(f"Invalid order or user data for order {order.order_id}")
                return
            
            # Send notification
            result = send_dna_results_ready_notification(order, dna_report)
            
            if result:
                logger.info(f"DNA results ready notification sent for order {order.order_id}")
            else:
                logger.error(f"Failed to send DNA results ready notification for order {order.order_id}")
        
        except ImportError:
            # If email utils don't exist, just log
            logger.warning(f"Email notification system not configured for order {order.order_id}")
        except Exception as e:
            logger.error(f"Unexpected error sending DNA results notification: {e}", exc_info=True)


@extend_schema(
    tags=['DNA Profile'],
    summary='List PDF Uploads',
    description='List all DNA PDF uploads for the authenticated user'
)
class DNAPDFUploadListView(generics.ListAPIView):
    serializer_class = DNAPDFUploadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['uploaded_at', 'status']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        user_kits = DNAKit.objects.filter(order__user=self.request.user)
        return DNAPDFUpload.objects.filter(kit__in=user_kits)


@extend_schema(
    tags=['DNA Profile'],
    summary='Get PDF Upload Details',
    description='Get detailed information about a specific PDF upload including extracted data'
)
class DNAPDFUploadDetailView(generics.RetrieveAPIView):
    serializer_class = DNAPDFUploadDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_kits = DNAKit.objects.filter(order__user=self.request.user)
        return DNAPDFUpload.objects.filter(kit__in=user_kits)


@extend_schema(
    tags=['DNA Profile'],
    summary='Process Extracted Data (Lab Use)',
    description='Convert extracted PDF data into DNA results - restricted to lab personnel'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Should be restricted to lab staff
def process_extracted_data(request):
    serializer = ProcessExtractedDataSerializer(data=request.data)
    
    if serializer.is_valid():
        extracted_data_ids = serializer.validated_data['extracted_data_ids']
        reviewed_by = serializer.validated_data.get('reviewed_by', 'Lab Staff')
        
        created_results = []
        
        # Process each extracted data item
        for data_id in extracted_data_ids:
            try:
                extracted_data = ExtractedDNAData.objects.get(id=data_id)
                
                # Create DNAResult from extracted data
                dna_result = DNAResult.objects.create(
                    kit=extracted_data.pdf_upload.kit,
                    category=extracted_data.category or 'TRAITS',
                    subcategory=extracted_data.subcategory,
                    trait_name=extracted_data.trait_name,
                    result_value=extracted_data.result_value,
                    confidence_level=extracted_data.confidence_level or 'MEDIUM',
                    risk_score=extracted_data.risk_score,
                    genetic_markers=extracted_data.genetic_markers,
                    methodology=extracted_data.methodology,
                    recommendations=extracted_data.recommendations,
                    reviewed_by=reviewed_by
                )
                
                # Mark extracted data as processed
                extracted_data.is_processed = True
                extracted_data.dna_result = dna_result
                extracted_data.processing_notes = f"Processed by {reviewed_by}"
                extracted_data.save()
                
                # Update PDF upload results count
                pdf_upload = extracted_data.pdf_upload
                pdf_upload.results_created_count += 1
                pdf_upload.save()
                
                created_results.append({
                    'extracted_data_id': data_id,
                    'dna_result_id': dna_result.id,
                    'trait_name': dna_result.trait_name
                })
                
            except ExtractedDNAData.DoesNotExist:
                continue
            except Exception as e:
                logger.error(f"Error processing extracted data {data_id}: {str(e)}")
                continue
        
        return Response({
            'message': f'Successfully processed {len(created_results)} extracted data items',
            'created_results': created_results
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['DNA Profile'],
    summary='List Extracted Data (Lab Use)',
    description='List extracted data from PDF uploads - restricted to lab personnel'
)
class ExtractedDNADataListView(generics.ListAPIView):
    serializer_class = ExtractedDNADataSerializer
    permission_classes = [IsAuthenticated]  # Should be restricted to lab staff
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['trait_name', 'category', 'pdf_upload__kit__kit_id']
    ordering_fields = ['created_at', 'extraction_confidence']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = ExtractedDNAData.objects.all()
        
        # Filter by processing status
        is_processed = self.request.query_params.get('is_processed')
        if is_processed is not None:
            queryset = queryset.filter(is_processed=is_processed.lower() == 'true')
        
        # Filter by PDF upload
        upload_id = self.request.query_params.get('upload_id')
        if upload_id:
            queryset = queryset.filter(pdf_upload__upload_id=upload_id)
        
        return queryset
