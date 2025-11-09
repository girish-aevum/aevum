import uuid
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone
from datetime import timedelta, datetime
import random
import string

User = get_user_model()


def dna_pdf_upload_path(instance, filename):
    """Generate upload path for DNA result PDFs"""
    ext = filename.split('.')[-1].lower()
    filename = f"dna_result_{instance.kit.kit_id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('dna_results', 'pdfs', filename)


class DNAKitType(models.Model):
    """Different types of DNA kits available for ordering"""
    
    KIT_CATEGORIES = [
        ('ANCESTRY', 'Ancestry & Genealogy'),
        ('HEALTH', 'Health & Wellness'),
        ('FITNESS', 'Fitness & Nutrition'),
        ('COMPREHENSIVE', 'Comprehensive Analysis'),
        ('PHARMACOGENOMICS', 'Drug Response'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=KIT_CATEGORIES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    processing_time_days = models.PositiveIntegerField(default=21, help_text="Expected processing time in days")
    features = models.JSONField(default=list, help_text="List of features included in this kit")
    is_active = models.BooleanField(default=True)
    requires_prescription = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class DNAKitOrder(models.Model):
    """DNA Kit order tracking"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Order Pending'),
        ('CONFIRMED', 'Order Confirmed'),
        ('SHIPPED', 'Kit Shipped'),
        ('DELIVERED', 'Kit Delivered'),
        ('SAMPLE_RECEIVED', 'Sample Received at Lab'),
        ('PROCESSING', 'Sample Processing'),
        ('COMPLETED', 'Results Ready'),
        ('RESULTS_GENERATED', 'Results Generated'),
        ('CANCELLED', 'Order Cancelled'),
        ('FAILED', 'Processing Failed'),
    ]
    
    SHIPPING_METHODS = [
        ('STANDARD', 'Standard Shipping (5-7 days)'),
        ('EXPRESS', 'Express Shipping (2-3 days)'),
        ('OVERNIGHT', 'Overnight Shipping (1 day)'),
    ]
    
    # Order identification
    order_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_reference = models.CharField(max_length=50, unique=True, blank=True, null=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dna_orders')
    kit_type = models.ForeignKey(DNAKitType, on_delete=models.PROTECT)
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping information
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHODS, default='STANDARD')
    shipping_address = models.JSONField(help_text="Complete shipping address")
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Important dates
    order_date = models.DateTimeField(auto_now_add=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    sample_received_date = models.DateTimeField(null=True, blank=True)
    estimated_completion_date = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    payment_status = models.CharField(max_length=20, default='PENDING')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional information
    special_instructions = models.TextField(blank=True, null=True)
    lab_notes = models.TextField(blank=True, null=True, help_text="Internal lab notes")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Generate human-readable order reference if not exists
        if not self.order_reference:
            current_date = datetime.now()
            random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.order_reference = f"AEVUM-{current_date.strftime('%Y%m')}-{random_chars}"
        
        # Generate tracking number if not exists (regardless of status for now)
        if not self.tracking_number:
            current_date = datetime.now()
            random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.tracking_number = f"DNAKIT-{current_date.strftime('%Y%m')}-{random_chars}"
        
        # Auto-calculate estimated completion date
        if self.sample_received_date and not self.estimated_completion_date:
            self.estimated_completion_date = self.sample_received_date + timedelta(days=self.kit_type.processing_time_days)
        
        # Set shipped date when status is SHIPPED
        if self.status == 'SHIPPED' and not self.shipped_date:
            self.shipped_date = datetime.now()

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_id} - {self.user.username} - {self.kit_type.name}"
    
    @property
    def is_completed(self):
        return self.status == 'COMPLETED'
    
    @property
    def can_be_cancelled(self):
        return self.status in ['PENDING', 'CONFIRMED']


class DNAKit(models.Model):
    """Physical DNA kit with unique barcode"""
    
    kit_id = models.CharField(max_length=50, unique=True, help_text="Unique kit barcode/ID")
    order = models.OneToOneField(DNAKitOrder, on_delete=models.CASCADE, related_name='kit')
    
    # Kit status
    is_activated = models.BooleanField(default=False)
    activation_date = models.DateTimeField(null=True, blank=True)
    
    # Sample collection
    sample_collected = models.BooleanField(default=False)
    collection_date = models.DateTimeField(null=True, blank=True)
    collection_method = models.CharField(max_length=50, blank=True, null=True)
    
    # Quality control
    sample_quality = models.CharField(max_length=20, blank=True, null=True)
    quality_notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Kit {self.kit_id} - Order {self.order.order_id}"


class DNAResult(models.Model):
    """DNA analysis results"""
    
    RESULT_CATEGORIES = [
        ('ANCESTRY', 'Ancestry & Ethnicity'),
        ('HEALTH_RISK', 'Health Risk Factors'),
        ('CARRIER_STATUS', 'Carrier Status'),
        ('PHARMACOGENOMICS', 'Drug Response'),
        ('TRAITS', 'Physical Traits'),
        ('FITNESS', 'Fitness & Nutrition'),
        ('WELLNESS', 'Wellness Insights'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('HIGH', 'High Confidence (>95%)'),
        ('MEDIUM', 'Medium Confidence (80-95%)'),
        ('LOW', 'Low Confidence (<80%)'),
    ]
    
    # Result identification
    result_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    kit = models.ForeignKey(DNAKit, on_delete=models.CASCADE, related_name='results')
    
    # Result classification
    category = models.CharField(max_length=20, choices=RESULT_CATEGORIES)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    trait_name = models.CharField(max_length=200)
    
    # Result data
    result_value = models.TextField(help_text="The actual result/finding")
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Risk score if applicable (0-100)")
    
    # Scientific information
    genetic_markers = models.JSONField(default=list, help_text="List of genetic markers analyzed")
    methodology = models.CharField(max_length=100, blank=True, null=True)
    reference_population = models.CharField(max_length=100, blank=True, null=True)
    
    # Clinical relevance
    clinical_significance = models.CharField(max_length=20, blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    requires_followup = models.BooleanField(default=False)
    
    # Metadata
    analysis_date = models.DateTimeField(default=timezone.now)
    reviewed_by = models.CharField(max_length=100, blank=True, null=True, help_text="Lab technician/geneticist")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'trait_name']
        unique_together = ['kit', 'category', 'trait_name']
    
    def __str__(self):
        return f"{self.trait_name} - {self.kit.kit_id}"


class DNAReport(models.Model):
    """Comprehensive DNA analysis report"""
    
    REPORT_TYPES = [
        ('PRELIMINARY', 'Preliminary Report'),
        ('COMPREHENSIVE', 'Comprehensive Report'),
        ('UPDATED', 'Updated Report'),
        ('CLINICAL', 'Clinical Report'),
    ]
    
    REPORT_STATUS = [
        ('GENERATING', 'Report Generating'),
        ('READY', 'Report Ready'),
        ('DELIVERED', 'Report Delivered'),
        ('ARCHIVED', 'Report Archived'),
    ]
    
    # Report identification
    report_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    kit = models.ForeignKey(DNAKit, on_delete=models.CASCADE, related_name='reports')
    
    # Report details
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='GENERATING')
    version = models.PositiveIntegerField(default=1)
    
    # Report content
    summary = models.TextField(blank=True, null=True)
    key_findings = models.JSONField(default=list)
    recommendations = models.TextField(blank=True, null=True)
    
    # File storage
    report_file_url = models.URLField(blank=True, null=True, help_text="URL to PDF report")
    raw_data_url = models.URLField(blank=True, null=True, help_text="URL to raw genetic data")
    
    # Quality and validation
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    validated_by = models.CharField(max_length=100, blank=True, null=True)
    validation_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    generated_date = models.DateTimeField(default=timezone.now)
    delivered_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-generated_date']
        unique_together = ['kit', 'report_type', 'version']
    
    def __str__(self):
        return f"{self.get_report_type_display()} v{self.version} - {self.kit.kit_id}"


class DNAConsent(models.Model):
    """User consent for DNA analysis and data usage"""
    
    CONSENT_TYPES = [
        ('ANALYSIS', 'DNA Analysis Consent'),
        ('RESEARCH', 'Research Participation'),
        ('DATA_SHARING', 'Data Sharing Consent'),
        ('STORAGE', 'Sample Storage Consent'),
        ('FAMILY_MATCHING', 'Family Matching Consent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dna_consents')
    order = models.OneToOneField(
        DNAKitOrder, 
        on_delete=models.CASCADE, 
        related_name='consent', 
        null=True,  # Make order nullable
        blank=True  # Allow blank in forms
    )
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    
    # Consent details
    consented = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    withdrawal_date = models.DateTimeField(null=True, blank=True)
    
    # Legal information
    consent_version = models.CharField(max_length=10, default='1.0')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'consent_type']
    
    def __str__(self):
        status = "Consented" if self.consented else "Not Consented"
        return f"{self.user.username} - {self.get_consent_type_display()} - {status}"


class DNAPDFUpload(models.Model):
    """DNA result PDF upload and processing tracking"""
    
    PROCESSING_STATUS = [
        ('UPLOADED', 'PDF Uploaded'),
        ('PROCESSING', 'Extracting Data'),
        ('COMPLETED', 'Processing Complete'),
        ('FAILED', 'Processing Failed'),
        ('MANUAL_REVIEW', 'Requires Manual Review'),
    ]
    
    # Upload identification
    upload_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    kit = models.ForeignKey(DNAKit, on_delete=models.CASCADE, related_name='pdf_uploads')
    
    # File information
    pdf_file = models.FileField(
        upload_to=dna_pdf_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="DNA result PDF file"
    )
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    
    # Processing status
    status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='UPLOADED')
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Extraction results
    extracted_text = models.TextField(blank=True, null=True, help_text="Raw text extracted from PDF")
    extraction_confidence = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Confidence score for extraction (0-100)"
    )
    
    # Processing metadata
    results_created_count = models.PositiveIntegerField(default=0, help_text="Number of DNA results created from this PDF")
    processing_notes = models.TextField(blank=True, null=True, help_text="Processing notes and errors")
    processed_by = models.CharField(max_length=100, blank=True, null=True, help_text="System or user who processed")
    
    # Upload metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"PDF Upload {self.upload_id} - {self.kit.kit_id} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if self.pdf_file:
            self.file_size = self.pdf_file.size
            if not self.original_filename:
                self.original_filename = self.pdf_file.name
        super().save(*args, **kwargs)
    
    @property
    def is_processing_complete(self):
        return self.status in ['COMPLETED', 'FAILED', 'MANUAL_REVIEW']
    
    @property
    def processing_duration(self):
        if self.processing_started_at and self.processing_completed_at:
            return self.processing_completed_at - self.processing_started_at
        return None


class ExtractedDNAData(models.Model):
    """Structured data extracted from PDF before creating DNAResult"""
    
    pdf_upload = models.ForeignKey(DNAPDFUpload, on_delete=models.CASCADE, related_name='extracted_data')
    
    # Extracted fields
    trait_name = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=20, blank=True, null=True)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    result_value = models.TextField(blank=True, null=True)
    confidence_level = models.CharField(max_length=10, blank=True, null=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    genetic_markers = models.JSONField(default=list, blank=True)
    methodology = models.CharField(max_length=100, blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    
    # Extraction metadata
    extraction_confidence = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Confidence score for this specific extraction"
    )
    page_number = models.PositiveIntegerField(null=True, blank=True)
    text_position = models.JSONField(default=dict, blank=True, help_text="Position in PDF where data was found")
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    dna_result = models.OneToOneField(DNAResult, on_delete=models.SET_NULL, null=True, blank=True)
    processing_notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['page_number', 'trait_name']
    
    def __str__(self):
        return f"Extracted: {self.trait_name or 'Unknown'} from {self.pdf_upload.upload_id}"
