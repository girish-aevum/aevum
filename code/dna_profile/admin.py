from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    DNAKitType, DNAKitOrder, DNAKit, DNAResult, 
    DNAReport, DNAConsent, DNAPDFUpload, ExtractedDNAData
)


@admin.register(DNAKitType)
class DNAKitTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'processing_time_days', 'is_active', 'requires_prescription')
    list_filter = ('category', 'is_active', 'requires_prescription')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Processing', {
            'fields': ('price', 'processing_time_days')
        }),
        ('Features & Options', {
            'fields': ('features', 'is_active', 'requires_prescription')
        }),
    )


class DNAKitInline(admin.StackedInline):
    model = DNAKit
    extra = 0
    readonly_fields = ('kit_id', 'created_at', 'updated_at')


@admin.register(DNAKitOrder)
class DNAKitOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id_short', 'user', 'kit_type', 'status', 
        'total_amount', 'order_date', 'estimated_completion_date'
    )
    list_filter = ('status', 'shipping_method', 'payment_status', 'kit_type__category')
    search_fields = ('order_id', 'user__username', 'user__email', 'kit_type__name')
    readonly_fields = ('order_id', 'order_date', 'created_at', 'updated_at')
    ordering = ('-order_date',)
    
    inlines = [DNAKitInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'kit_type', 'status', 'quantity')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'payment_status', 'payment_reference')
        }),
        ('Shipping Information', {
            'fields': ('shipping_method', 'shipping_address', 'tracking_number')
        }),
        ('Important Dates', {
            'fields': (
                'order_date', 'shipped_date', 'delivered_date', 
                'sample_received_date', 'estimated_completion_date'
            )
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'lab_notes'),
            'classes': ('collapse',)
        }),
    )
    
    def order_id_short(self, obj):
        return str(obj.order_id)[:8]
    order_id_short.short_description = 'Order ID'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'kit_type')


class DNAResultInline(admin.TabularInline):
    model = DNAResult
    extra = 0
    readonly_fields = ('result_id', 'created_at')
    fields = ('category', 'trait_name', 'result_value', 'confidence_level', 'requires_followup')


class DNAReportInline(admin.TabularInline):
    model = DNAReport
    extra = 0
    readonly_fields = ('report_id', 'generated_date')
    fields = ('report_type', 'status', 'version', 'quality_score')


@admin.register(DNAKit)
class DNAKitAdmin(admin.ModelAdmin):
    list_display = (
        'kit_id', 'order_link', 'user_name', 'is_activated', 
        'sample_collected', 'sample_quality', 'created_at'
    )
    list_filter = ('is_activated', 'sample_collected', 'sample_quality')
    search_fields = ('kit_id', 'order__user__username', 'order__user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    inlines = [DNAResultInline, DNAReportInline]
    
    fieldsets = (
        ('Kit Information', {
            'fields': ('kit_id', 'order')
        }),
        ('Activation Status', {
            'fields': ('is_activated', 'activation_date')
        }),
        ('Sample Collection', {
            'fields': ('sample_collected', 'collection_date', 'collection_method')
        }),
        ('Quality Control', {
            'fields': ('sample_quality', 'quality_notes')
        }),
    )
    
    def order_link(self, obj):
        url = reverse('admin:dna_profile_dnakitorder_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.order.order_id)[:8])
    order_link.short_description = 'Order'
    
    def user_name(self, obj):
        return obj.order.user.username
    user_name.short_description = 'User'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order__user')


@admin.register(DNAResult)
class DNAResultAdmin(admin.ModelAdmin):
    list_display = (
        'trait_name', 'category', 'kit_link', 'user_name', 
        'confidence_level', 'risk_score', 'requires_followup', 'analysis_date'
    )
    list_filter = ('category', 'confidence_level', 'requires_followup', 'clinical_significance')
    search_fields = ('trait_name', 'kit__kit_id', 'kit__order__user__username')
    readonly_fields = ('result_id', 'created_at', 'updated_at')
    ordering = ('-analysis_date',)
    
    fieldsets = (
        ('Result Identification', {
            'fields': ('result_id', 'kit', 'category', 'subcategory', 'trait_name')
        }),
        ('Result Data', {
            'fields': ('result_value', 'confidence_level', 'risk_score')
        }),
        ('Scientific Information', {
            'fields': ('genetic_markers', 'methodology', 'reference_population')
        }),
        ('Clinical Information', {
            'fields': ('clinical_significance', 'recommendations', 'requires_followup')
        }),
        ('Metadata', {
            'fields': ('analysis_date', 'reviewed_by'),
            'classes': ('collapse',)
        }),
    )
    
    def kit_link(self, obj):
        url = reverse('admin:dna_profile_dnakit_change', args=[obj.kit.pk])
        return format_html('<a href="{}">{}</a>', url, obj.kit.kit_id)
    kit_link.short_description = 'Kit'
    
    def user_name(self, obj):
        return obj.kit.order.user.username
    user_name.short_description = 'User'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('kit__order__user')


@admin.register(DNAReport)
class DNAReportAdmin(admin.ModelAdmin):
    list_display = (
        'report_id_short', 'kit_link', 'user_name', 'report_type', 
        'status', 'version', 'quality_score', 'generated_date'
    )
    list_filter = ('report_type', 'status')
    search_fields = ('report_id', 'kit__kit_id', 'kit__order__user__username')
    readonly_fields = ('report_id', 'generated_date', 'created_at', 'updated_at')
    ordering = ('-generated_date',)
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_id', 'kit', 'report_type', 'status', 'version')
        }),
        ('Report Content', {
            'fields': ('summary', 'key_findings', 'recommendations')
        }),
        ('File Storage', {
            'fields': ('report_file_url', 'raw_data_url')
        }),
        ('Quality & Validation', {
            'fields': ('quality_score', 'validated_by', 'validation_date')
        }),
        ('Delivery Information', {
            'fields': ('generated_date', 'delivered_date')
        }),
    )
    
    def report_id_short(self, obj):
        return str(obj.report_id)[:8]
    report_id_short.short_description = 'Report ID'
    
    def kit_link(self, obj):
        url = reverse('admin:dna_profile_dnakit_change', args=[obj.kit.pk])
        return format_html('<a href="{}">{}</a>', url, obj.kit.kit_id)
    kit_link.short_description = 'Kit'
    
    def user_name(self, obj):
        return obj.kit.order.user.username
    user_name.short_description = 'User'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('kit__order__user')


@admin.register(DNAConsent)
class DNAConsentAdmin(admin.ModelAdmin):
    """Admin configuration for DNA Consent"""
    
    list_display = (
        'user', 
        'order', 
        'consent_type', 
        'consented', 
        'consent_date'
    )
    
    list_filter = (
        'consent_type', 
        'consented', 
        'created_at'
    )
    
    search_fields = (
        'user__username', 
        'user__email', 
        'order__order_id'
    )
    
    readonly_fields = (
        'created_at', 
        'updated_at'
    )
    
    fieldsets = (
        ('Consent Information', {
            'fields': ('user', 'order', 'consent_type', 'consented')
        }),
        ('Consent Dates', {
            'fields': ('consent_date', 'withdrawal_date', 'consent_version')
        }),
        ('Additional Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'order')


@admin.register(DNAPDFUpload)
class DNAPDFUploadAdmin(admin.ModelAdmin):
    list_display = (
        'upload_id_short', 'kit_link', 'user_name', 'original_filename',
        'status', 'file_size_mb', 'extraction_confidence', 'results_created_count',
        'uploaded_at'
    )
    list_filter = ('status', 'uploaded_at')
    search_fields = ('upload_id', 'kit__kit_id', 'kit__order__user__username', 'original_filename')
    readonly_fields = ('upload_id', 'file_size', 'uploaded_at')
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('Upload Information', {
            'fields': ('upload_id', 'kit', 'pdf_file', 'original_filename', 'file_size')
        }),
        ('Processing Status', {
            'fields': ('status', 'processing_started_at', 'processing_completed_at')
        }),
        ('Extraction Results', {
            'fields': ('extraction_confidence', 'results_created_count', 'extracted_text')
        }),
        ('Processing Notes', {
            'fields': ('processing_notes', 'processed_by'),
            'classes': ('collapse',)
        }),
        ('Upload Metadata', {
            'fields': ('uploaded_by', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def upload_id_short(self, obj):
        return str(obj.upload_id)[:8]
    upload_id_short.short_description = 'Upload ID'
    
    def kit_link(self, obj):
        url = reverse('admin:dna_profile_dnakit_change', args=[obj.kit.pk])
        return format_html('<a href="{}">{}</a>', url, obj.kit.kit_id)
    kit_link.short_description = 'Kit'
    
    def user_name(self, obj):
        return obj.kit.order.user.username
    user_name.short_description = 'User'
    
    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024 * 1024):.2f} MB" if obj.file_size else "N/A"
    file_size_mb.short_description = 'File Size'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('kit__order__user')


class ExtractedDNADataInline(admin.TabularInline):
    model = ExtractedDNAData
    extra = 0
    readonly_fields = ('created_at', 'extraction_confidence')
    fields = ('trait_name', 'category', 'result_value', 'confidence_level', 'is_processed', 'extraction_confidence')


@admin.register(ExtractedDNAData)
class ExtractedDNADataAdmin(admin.ModelAdmin):
    list_display = (
        'trait_name', 'category', 'pdf_upload_short', 'kit_id', 
        'confidence_level', 'extraction_confidence', 'is_processed', 'created_at'
    )
    list_filter = ('category', 'confidence_level', 'is_processed', 'created_at')
    search_fields = ('trait_name', 'pdf_upload__kit__kit_id', 'result_value')
    readonly_fields = ('created_at', 'extraction_confidence')
    ordering = ['-created_at']
    
    fieldsets = (
        ('Extracted Information', {
            'fields': ('pdf_upload', 'trait_name', 'category', 'subcategory')
        }),
        ('Result Data', {
            'fields': ('result_value', 'confidence_level', 'risk_score', 'genetic_markers')
        }),
        ('Scientific Details', {
            'fields': ('methodology', 'recommendations')
        }),
        ('Extraction Metadata', {
            'fields': ('extraction_confidence', 'page_number', 'text_position'),
            'classes': ('collapse',)
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'dna_result', 'processing_notes')
        }),
    )
    
    def pdf_upload_short(self, obj):
        return str(obj.pdf_upload.upload_id)[:8]
    pdf_upload_short.short_description = 'PDF Upload'
    
    def kit_id(self, obj):
        return obj.pdf_upload.kit.kit_id
    kit_id.short_description = 'Kit ID'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pdf_upload__kit')


# Update existing DNAKit admin to include PDF uploads
class DNAPDFUploadInline(admin.TabularInline):
    model = DNAPDFUpload
    extra = 0
    readonly_fields = ('upload_id', 'status', 'uploaded_at')
    fields = ('pdf_file', 'original_filename', 'status', 'extraction_confidence', 'uploaded_at')

# Add the inline to existing DNAKitAdmin
DNAKitAdmin.inlines.append(DNAPDFUploadInline)


# Custom admin site customization
admin.site.site_header = "Aevum Health - DNA Profile Administration"
admin.site.site_title = "DNA Profile Admin"
admin.site.index_title = "DNA Profile Management"
