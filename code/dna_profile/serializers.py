from rest_framework import serializers
from django.contrib.auth.models import User
from decimal import Decimal
import random
import string
from datetime import datetime
import uuid
from django.utils import timezone

from .models import (
    DNAKitType, DNAKitOrder, DNAKit, DNAResult, 
    DNAReport, DNAConsent, DNAPDFUpload, ExtractedDNAData
)


class DNAKitTypeSerializer(serializers.ModelSerializer):
    """Serializer for DNA Kit Types"""
    
    class Meta:
        model = DNAKitType
        fields = [
            'id', 'name', 'category', 'description', 'price',
            'processing_time_days', 'features', 'is_active',
            'requires_prescription', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class DNAConsentSerializer(serializers.ModelSerializer):
    """Serializer for DNA Consent"""
    
    class Meta:
        model = DNAConsent
        fields = [
            'id', 'order', 'user', 'consent_type', 'status',
            'is_data_processing_consent', 'is_research_consent', 
            'is_medical_insights_consent', 'is_genetic_counseling_consent',
            'consent_given_at', 'consent_version', 'additional_notes'
        ]
        read_only_fields = ['id', 'order', 'user', 'consent_given_at']

class DNAKitOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DNA Kit Orders"""
    
    # Add consent fields as write-only fields that won't be passed to the model
    consented = serializers.BooleanField(write_only=True, required=True)
    consent_type = serializers.ChoiceField(
        choices=DNAConsent.CONSENT_TYPES, 
        write_only=True, 
        default='ANALYSIS'
    )
    
    class Meta:
        model = DNAKitOrder
        fields = [
            # Only actual model fields
            'kit_type', 'quantity', 'shipping_method', 'shipping_address',
            'special_instructions',
            # Write-only consent fields
            'consented', 'consent_type'
        ]
        extra_kwargs = {
            'quantity': {'required': False, 'default': 1},
            'shipping_method': {'required': False, 'default': 'STANDARD'},
            'special_instructions': {'required': False, 'allow_blank': True}
        }
    
    def validate(self, data):
        """Validate consent is given"""
        # Ensure consented is explicitly passed and is True
        if not data.get('consented'):
            raise serializers.ValidationError({
                'consented': 'Consent is mandatory to proceed with the order.'
            })
        
        # Validate consent type
        if 'consent_type' not in data:
            data['consent_type'] = 'ANALYSIS'
        
        return data
    
    def create(self, validated_data):
        """Create order and associated consent"""
        # Store consent data before removing from validated_data
        consented = validated_data.get('consented', False)
        consent_type = validated_data.get('consent_type', 'ANALYSIS')
        
        # Remove consent fields completely from validated_data
        validated_data.pop('consented', None)
        validated_data.pop('consent_type', None)
        
        # Calculate total amount based on kit type and quantity
        kit_type = validated_data['kit_type']
        quantity = validated_data.get('quantity', 1)
        total_amount = kit_type.price * Decimal(str(quantity))
        
        # Add shipping cost based on method
        shipping_costs = {
            'STANDARD': Decimal('0.00'),
            'EXPRESS': Decimal('15.00'),
            'OVERNIGHT': Decimal('35.00')
        }
        
        shipping_method = validated_data.get('shipping_method', 'STANDARD')
        total_amount += shipping_costs.get(shipping_method, Decimal('0.00'))
        
        validated_data['total_amount'] = total_amount
        
        # Create the order using only valid model fields
        order = DNAKitOrder.objects.create(**validated_data)
        
        # Create consent record
        DNAConsent.objects.create(
            user=order.user,
            order=order,
            consent_type=consent_type,
            consented=consented,
            consent_date=timezone.now()
        )
        
        return order
    
    def validate_shipping_address(self, value):
        """Validate shipping address has required fields"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Shipping address must be a valid object")
        
        required_fields = {
            'street': 'Street address',
            'city': 'City',
            'state': 'State/Province', 
            'zip_code': 'ZIP/Postal code',
            'country': 'Country'
        }
        
        missing_fields = []
        for field, display_name in required_fields.items():
            if field not in value or not value[field] or str(value[field]).strip() == '':
                missing_fields.append(display_name)
        
        if missing_fields:
            if len(missing_fields) == 1:
                raise serializers.ValidationError(f"Shipping address is missing: {missing_fields[0]}")
            else:
                raise serializers.ValidationError(f"Shipping address is missing: {', '.join(missing_fields)}")
        
        # Optional validation for reasonable field lengths
        if len(value['street']) > 200:
            raise serializers.ValidationError("Street address is too long (max 200 characters)")
        if len(value['city']) > 100:
            raise serializers.ValidationError("City name is too long (max 100 characters)")
        if len(value['zip_code']) > 20:
            raise serializers.ValidationError("ZIP/Postal code is too long (max 20 characters)")
            
        return value


class DNAKitSerializer(serializers.ModelSerializer):
    """Serializer for DNA Kit details"""
    
    class Meta:
        model = DNAKit
        fields = [
            'id', 'kit_id', 'is_activated', 'activation_date',
            'sample_collected', 'collection_date', 'collection_method',
            'sample_quality', 'quality_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class DNAKitOrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for DNA Kit Orders with nested relationships"""
    
    kit_type = DNAKitTypeSerializer(read_only=True)
    kit = DNAKitSerializer(read_only=True)
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = DNAKitOrder
        fields = [
            'id', 'order_id', 'order_reference', 'tracking_id', 'tracking_number',
            'user_info', 'kit_type', 'kit', 'status', 'quantity', 'total_amount', 
            'shipping_method', 'shipping_address', 'order_date', 'shipped_date', 
            'delivered_date', 'sample_received_date', 'estimated_completion_date', 
            'payment_status', 'payment_reference', 'special_instructions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_id', 'order_reference', 'tracking_id', 'tracking_number', 'created_at', 'updated_at']
    
    def get_user_info(self, obj):
        """Get basic user information"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': f"{obj.user.first_name} {obj.user.last_name}".strip(),
            'email': obj.user.email
        }


class DNAResultSerializer(serializers.ModelSerializer):
    """Detailed serializer for DNA Results"""
    
    kit_type_name = serializers.CharField(source='kit.order.kit_type.name', read_only=True)
    kit_order_id = serializers.CharField(source='kit.order.order_id', read_only=True)
    
    class Meta:
        model = DNAResult
        fields = [
            'id', 'kit_type_name', 'kit_order_id', 
            'category', 'subcategory', 'trait_name',
            'result_value', 'confidence_level', 'risk_score',
            'genetic_markers', 'methodology', 'reference_population',
            'clinical_significance', 'recommendations', 'requires_followup',
            'reviewed_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DNAReportSerializer(serializers.ModelSerializer):
    """Detailed serializer for DNA Reports"""
    
    kit_type_name = serializers.CharField(source='kit.order.kit_type.name', read_only=True)
    kit_order_id = serializers.CharField(source='kit.order.order_id', read_only=True)
    
    class Meta:
        model = DNAReport
        fields = [
            'id', 'kit_type_name', 'kit_order_id',
            'report_type', 'status', 'generated_date', 
            'report_file_url', 'raw_data_url', 
            'summary', 'key_findings', 'recommendations',
            'quality_score', 'validated_by', 'validation_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DNAConsentSerializer(serializers.ModelSerializer):
    """Serializer for DNA Consent management"""
    
    class Meta:
        model = DNAConsent
        fields = [
            'id', 'consent_type', 'consented', 'consent_date',
            'withdrawal_date', 'consent_version', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class DNAKitOrderListSerializer(serializers.ModelSerializer):
    """Serializer for listing DNA Kit Orders"""
    
    kit_type_name = serializers.SerializerMethodField()
    kit_category = serializers.SerializerMethodField()
    kit_id = serializers.SerializerMethodField()
    report_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DNAKitOrder
        fields = [
            'id', 'order_id', 'kit_type', 'kit_type_name', 'kit_category', 
            'kit_id', 'status', 'quantity', 'total_amount', 
            'order_date', 'estimated_completion_date', 
            'shipping_method', 'shipping_address', 
            'report_url'
        ]
    
    def get_kit_type_name(self, obj):
        return obj.kit_type.name if obj.kit_type else None
    
    def get_kit_category(self, obj):
        return obj.kit_type.category if obj.kit_type else None
    
    def get_kit_id(self, obj):
        # Assuming there's a related DNAKit for this order
        try:
            return obj.kit.kit_id if hasattr(obj, 'kit') else None
        except:
            return None
    
    def get_report_url(self, obj):
        # Try to get the report URL from the latest DNA report
        try:
            latest_report = obj.kit.reports.order_by('-created_at').first()
            return latest_report.report_file_url if latest_report else None
        except:
            return None


class DNAResultSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for DNA Results by category"""
    
    class Meta:
        model = DNAResult
        fields = [
            'id', 'category', 'trait_name', 'result_value',
            'confidence_level', 'risk_score', 'requires_followup'
        ]


class DNADashboardSerializer(serializers.Serializer):
    """Comprehensive dashboard data for DNA profile"""
    
    total_orders = serializers.IntegerField()
    active_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    pending_results = serializers.IntegerField()
    
    recent_orders = DNAKitOrderListSerializer(many=True)
    latest_results = DNAResultSummarySerializer(many=True)
    
    # Result statistics by category
    ancestry_results_count = serializers.IntegerField()
    health_results_count = serializers.IntegerField()
    fitness_results_count = serializers.IntegerField()
    
    # Consent status
    consent_status = serializers.DictField()


class DNAKitActivationSerializer(serializers.Serializer):
    """Serializer for DNA Kit activation"""
    
    kit_id = serializers.CharField(max_length=50)
    activation_code = serializers.CharField(max_length=20, required=False)
    
    def validate_kit_id(self, value):
        """Validate kit exists and belongs to user"""
        try:
            kit = DNAKit.objects.get(kit_id=value)
            if kit.order.user != self.context['request'].user:
                raise serializers.ValidationError("This kit does not belong to you.")
            if kit.is_activated:
                raise serializers.ValidationError("This kit is already activated.")
            return value
        except DNAKit.DoesNotExist:
            raise serializers.ValidationError("Invalid kit ID.")


class DNAResultCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DNA results (lab use)"""
    
    kit_id = serializers.CharField(write_only=True, help_text="DNA Kit ID")
    
    class Meta:
        model = DNAResult
        fields = [
            'kit_id', 'category', 'subcategory', 'trait_name',
            'result_value', 'confidence_level', 'risk_score',
            'genetic_markers', 'methodology', 'reference_population',
            'clinical_significance', 'recommendations', 'requires_followup',
            'reviewed_by'
        ]
    
    def validate_kit_id(self, value):
        """Validate kit exists"""
        try:
            kit = DNAKit.objects.get(kit_id=value)
            return value
        except DNAKit.DoesNotExist:
            raise serializers.ValidationError(f"DNA Kit with ID '{value}' does not exist.")
    
    def validate_risk_score(self, value):
        """Validate risk score is within valid range"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Risk score must be between 0 and 100.")
        return value
    
    def create(self, validated_data):
        """Create result with kit lookup"""
        kit_id = validated_data.pop('kit_id')
        kit = DNAKit.objects.get(kit_id=kit_id)
        validated_data['kit'] = kit
        return super().create(validated_data)


class DNAResultUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating DNA results (lab use)"""
    
    class Meta:
        model = DNAResult
        fields = [
            'result_value', 'confidence_level', 'risk_score',
            'genetic_markers', 'methodology', 'reference_population',
            'clinical_significance', 'recommendations', 'requires_followup',
            'reviewed_by'
        ]
    
    def validate_risk_score(self, value):
        """Validate risk score is within valid range"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Risk score must be between 0 and 100.")
        return value


class DNAReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DNA reports (lab use)"""
    
    kit_id = serializers.CharField(write_only=True, help_text="DNA Kit ID")
    
    class Meta:
        model = DNAReport
        fields = [
            'kit_id', 'report_type', 'summary', 'key_findings',
            'recommendations', 'report_file_url', 'raw_data_url',
            'quality_score', 'validated_by'
        ]
    
    def validate_kit_id(self, value):
        """Validate kit exists"""
        try:
            kit = DNAKit.objects.get(kit_id=value)
            return value
        except DNAKit.DoesNotExist:
            raise serializers.ValidationError(f"DNA Kit with ID '{value}' does not exist.")
    
    def validate_quality_score(self, value):
        """Validate quality score is within valid range"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Quality score must be between 0 and 100.")
        return value
    
    def create(self, validated_data):
        """Create report with kit lookup"""
        kit_id = validated_data.pop('kit_id')
        kit = DNAKit.objects.get(kit_id=kit_id)
        validated_data['kit'] = kit
        return super().create(validated_data)


class DNAPDFUploadResponseSerializer(serializers.Serializer):
    """
    Response serializer for PDF upload
    """
    upload_id = serializers.UUIDField(help_text="Unique upload identifier")
    kit_id = serializers.CharField(help_text="DNA Kit ID")
    status = serializers.CharField(help_text="Processing status")
    original_filename = serializers.CharField(help_text="Original filename of uploaded PDF")


class DNAPDFUploadSerializer(serializers.Serializer):
    """
    Serializer for DNA PDF Upload with separate kit ID and file upload
    """
    kit_id = serializers.CharField(
        required=True, 
        help_text="Unique DNA Kit ID for which results are being uploaded"
    )
    pdf_file = serializers.CharField(
        required=True, 
        help_text="Filename of the uploaded PDF"
    )
    
    def validate_kit_id(self, value):
        """
        Validate that the kit ID exists and belongs to the user
        """
        try:
            # Find the kit by its unique identifier
            kit = DNAKit.objects.get(kit_id=value)
            
            # Validate kit ownership and status
            request = self.context.get('request')
            if not request or not request.user.is_authenticated:
                raise serializers.ValidationError("Authentication required.")
            
            if kit.order.user != request.user:
                raise serializers.ValidationError("You can only upload results for your own DNA kits.")
            
            if kit.order.status != 'COMPLETED':
                raise serializers.ValidationError("You can only upload results for completed orders.")
            
            return value
        except DNAKit.DoesNotExist:
            raise serializers.ValidationError(f"DNA Kit with ID '{value}' does not exist.")
    
    def validate_pdf_file(self, value):
        """
        Validate PDF filename
        """
        # Check file type
        if not value.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        
        return value
    
    def create(self, validated_data):
        """
        Create PDF upload with kit lookup
        """
        # Find the kit
        kit = DNAKit.objects.get(kit_id=validated_data['kit_id'])
        
        # Get the uploaded file from request
        request = self.context.get('request')
        pdf_file = request.FILES.get('pdf_file')
        
        if not pdf_file:
            raise serializers.ValidationError("No PDF file uploaded.")
        
        # Create PDF upload with all required fields
        pdf_upload = DNAPDFUpload.objects.create(
            kit=kit,
            pdf_file=pdf_file,
            uploaded_by=request.user,
            original_filename=pdf_file.name,
            file_size=pdf_file.size,
            status='PENDING',
            processing_started_at=timezone.now()
        )
        
        return pdf_upload


class ExtractedDNADataSerializer(serializers.ModelSerializer):
    """Serializer for extracted DNA data"""
    
    class Meta:
        model = ExtractedDNAData
        fields = [
            'id', 'trait_name', 'category', 'subcategory', 'result_value',
            'confidence_level', 'risk_score', 'genetic_markers', 'methodology',
            'recommendations', 'extraction_confidence', 'page_number',
            'text_position', 'is_processed', 'processing_notes', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')


class DNAPDFUploadDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for DNA PDF uploads with extracted data"""
    
    kit_info = serializers.SerializerMethodField()
    extracted_data = ExtractedDNADataSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()
    processing_duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = DNAPDFUpload
        fields = [
            'upload_id', 'kit_info', 'pdf_file', 'file_url', 'original_filename',
            'file_size', 'status', 'processing_started_at', 'processing_completed_at',
            'processing_duration_seconds', 'extracted_text', 'extraction_confidence',
            'results_created_count', 'processing_notes', 'processed_by',
            'uploaded_at', 'extracted_data'
        ]
    
    def get_kit_info(self, obj):
        """Get kit information"""
        return {
            'kit_id': obj.kit.kit_id,
            'order_id': str(obj.kit.order.order_id),
            'user': obj.kit.order.user.username
        }
    
    def get_file_url(self, obj):
        """Get the URL of the uploaded PDF file"""
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None
    
    def get_processing_duration_seconds(self, obj):
        """Get processing duration in seconds"""
        duration = obj.processing_duration
        return duration.total_seconds() if duration else None


class ProcessExtractedDataSerializer(serializers.Serializer):
    """Serializer for processing extracted data into DNA results"""
    
    extracted_data_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of ExtractedDNAData IDs to process into DNAResult objects"
    )
    reviewed_by = serializers.CharField(
        max_length=100, 
        required=False,
        help_text="Name of the person reviewing and approving the data"
    )
    
    def validate_extracted_data_ids(self, value):
        """Validate that all extracted data IDs exist and are not already processed"""
        if not value:
            raise serializers.ValidationError("At least one extracted data ID must be provided.")
        
        # Check that all IDs exist
        existing_ids = ExtractedDNAData.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_ids)
        if missing_ids:
            raise serializers.ValidationError(f"Extracted data IDs not found: {list(missing_ids)}")
        
        # Check that none are already processed
        already_processed = ExtractedDNAData.objects.filter(
            id__in=value, 
            is_processed=True
        ).values_list('id', flat=True)
        
        if already_processed:
            raise serializers.ValidationError(f"Some data is already processed: {list(already_processed)}")
        
        return value 


class DNAKitOrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating DNA Kit Orders"""
    
    class Meta:
        model = DNAKitOrder
        fields = ['status', 'tracking_number']
        read_only_fields = ['tracking_number']
    
    def update(self, instance, validated_data):
        """Generate tracking number when order is shipped"""
        # Check if status is being changed to 'SHIPPED'
        if validated_data.get('status') == 'SHIPPED' and not instance.tracking_number:
            # Generate tracking number
            current_date = datetime.now()
            random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            validated_data['tracking_number'] = f"DNAKIT-{current_date.strftime('%Y%m')}-{random_chars}"
            
            # Set shipped date
            validated_data['shipped_date'] = current_date
        
        return super().update(instance, validated_data) 