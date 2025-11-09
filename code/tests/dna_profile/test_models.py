"""
DNA Profile Models Tests
Tests for DNA profile models including kit types, orders, kits, results, and reports
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from decimal import Decimal

from dna_profile.models import (
    DNAKitType, DNAKitOrder, DNAKit, DNAResult, DNAReport, 
    DNAConsent, DNAPDFUpload, ExtractedDNAData
)


class DNAProfileModelTests(TestCase):
    """Test cases for DNA Profile models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a DNA kit type
        self.kit_type = DNAKitType.objects.create(
            name='Health & Wellness Kit',
            category='HEALTH',
            description='Comprehensive health analysis',
            price=Decimal('199.99'),
            processing_time_days=21,
            features=['Health Risk Analysis', 'Carrier Status', 'Drug Response'],
            is_active=True
        )
        
    def test_dna_kit_type_creation(self):
        """Test DNAKitType model creation"""
        self.assertEqual(self.kit_type.name, 'Health & Wellness Kit')
        self.assertEqual(self.kit_type.category, 'HEALTH')
        self.assertEqual(self.kit_type.price, Decimal('199.99'))
        self.assertTrue(self.kit_type.is_active)
        self.assertIn('Health Risk Analysis', self.kit_type.features)
        self.assertEqual(str(self.kit_type), 'Health & Wellness Kit (Health & Wellness)')
    
    def test_dna_kit_order_creation(self):
        """Test DNAKitOrder model creation"""
        order = DNAKitOrder.objects.create(
            user=self.user,
            kit_type=self.kit_type,
            quantity=1,
            total_amount=self.kit_type.price,  # Required field
            shipping_address={
                'street': '123 Main St',
                'city': 'Test City',
                'state': 'TS',
                'zip_code': '12345',
                'country': 'USA'
            },
            shipping_method='STANDARD'
        )
        
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.kit_type, self.kit_type)
        self.assertEqual(order.quantity, 1)
        self.assertEqual(order.status, 'PENDING')
        self.assertEqual(order.shipping_method, 'STANDARD')
        self.assertIsNotNone(order.order_id)
    
    def test_dna_kit_creation(self):
        """Test DNAKit model creation"""
        order = DNAKitOrder.objects.create(
            user=self.user,
            kit_type=self.kit_type,
            quantity=1,
            total_amount=self.kit_type.price,
            shipping_address={'street': '123 Main St', 'city': 'Test City', 'state': 'TS', 'zip_code': '12345', 'country': 'USA'}
        )
        
        kit = DNAKit.objects.create(
            order=order,
            kit_id='TEST-KIT-001',
            is_activated=True
        )
        
        self.assertEqual(kit.order, order)
        self.assertEqual(kit.kit_id, 'TEST-KIT-001')
        self.assertTrue(kit.is_activated)
        self.assertIn(str(kit.order.order_id), str(kit))
    
    def test_dna_result_creation(self):
        """Test DNAResult model creation"""
        order = DNAKitOrder.objects.create(
            user=self.user,
            kit_type=self.kit_type,
            quantity=1,
            total_amount=self.kit_type.price,
            shipping_address={'street': '123 Main St', 'city': 'Test City', 'state': 'TS', 'zip_code': '12345', 'country': 'USA'}
        )
        
        kit = DNAKit.objects.create(order=order, kit_id='TEST-KIT-002', sample_collected=True)
        
        result = DNAResult.objects.create(
            kit=kit,
            category='HEALTH_RISK',
            trait_name='Type 2 Diabetes Risk',
            result_value='Increased risk',
            confidence_level='HIGH',
            risk_score=Decimal('75.5'),
            genetic_markers=['rs7903146', 'rs12255372'],
            methodology='SNP Analysis',
            recommendations='Regular exercise and healthy diet recommended'
        )
        
        self.assertEqual(result.kit, kit)
        self.assertEqual(result.category, 'HEALTH_RISK')
        self.assertEqual(result.trait_name, 'Type 2 Diabetes Risk')
        self.assertEqual(result.confidence_level, 'HIGH')
        self.assertEqual(result.risk_score, Decimal('75.5'))
        self.assertIn('rs7903146', result.genetic_markers)
    
    def test_dna_report_creation(self):
        """Test DNAReport model creation"""
        order = DNAKitOrder.objects.create(
            user=self.user,
            kit_type=self.kit_type,
            quantity=1,
            total_amount=self.kit_type.price,
            shipping_address={'street': '123 Main St', 'city': 'Test City', 'state': 'TS', 'zip_code': '12345', 'country': 'USA'}
        )
        
        kit = DNAKit.objects.create(order=order, kit_id='TEST-KIT-003', sample_collected=True)
        
        report = DNAReport.objects.create(
            kit=kit,
            report_type='COMPREHENSIVE',
            status='READY',
            summary='Comprehensive genetic analysis completed',
            key_findings=['High diabetes risk', 'Normal heart disease risk'],
            recommendations='Follow personalized health recommendations'
        )
        
        self.assertEqual(report.kit, kit)
        self.assertEqual(report.report_type, 'COMPREHENSIVE')
        self.assertEqual(report.status, 'READY')
        self.assertEqual(report.version, 1)
        self.assertIn('High diabetes risk', report.key_findings)
    
    def test_dna_consent_creation(self):
        """Test DNAConsent model creation"""
        order = DNAKitOrder.objects.create(
            user=self.user,
            kit_type=self.kit_type,
            quantity=1,
            total_amount=self.kit_type.price,
            shipping_address={'street': '123 Main St', 'city': 'Test City', 'state': 'TS', 'zip_code': '12345', 'country': 'USA'}
        )
        
        consent = DNAConsent.objects.create(
            user=self.user,
            order=order,
            consent_type='ANALYSIS',
            consented=True,
            consent_date=timezone.now(),
            consent_version='1.0'
        )
        
        self.assertEqual(consent.user, self.user)
        self.assertEqual(consent.order, order)
        self.assertEqual(consent.consent_type, 'ANALYSIS')
        self.assertTrue(consent.consented)
        self.assertIn('Consented', str(consent))
    
    def test_dna_pdf_upload_creation(self):
        """Test DNAPDFUpload model creation"""
        order = DNAKitOrder.objects.create(
            user=self.user,
            kit_type=self.kit_type,
            quantity=1,
            total_amount=self.kit_type.price,
            shipping_address={'street': '123 Main St', 'city': 'Test City', 'state': 'TS', 'zip_code': '12345', 'country': 'USA'}
        )
        
        kit = DNAKit.objects.create(order=order, kit_id='TEST-KIT-004', sample_collected=True)
        
        # Create a simple PDF file for testing
        pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        pdf_file = SimpleUploadedFile('test_results.pdf', pdf_content, content_type='application/pdf')
        
        pdf_upload = DNAPDFUpload.objects.create(
            kit=kit,
            pdf_file=pdf_file,
            original_filename='test_results.pdf',
            status='UPLOADED'
        )
        
        self.assertEqual(pdf_upload.kit, kit)
        self.assertEqual(pdf_upload.original_filename, 'test_results.pdf')
        self.assertEqual(pdf_upload.status, 'UPLOADED')
        self.assertIsNotNone(pdf_upload.upload_id)
        self.assertGreater(pdf_upload.file_size, 0)  # File size is auto-calculated
    
    def test_extracted_dna_data_creation(self):
        """Test ExtractedDNAData model creation"""
        order = DNAKitOrder.objects.create(
            user=self.user,
            kit_type=self.kit_type,
            quantity=1,
            total_amount=self.kit_type.price,
            shipping_address={'street': '123 Main St', 'city': 'Test City', 'state': 'TS', 'zip_code': '12345', 'country': 'USA'}
        )
        
        kit = DNAKit.objects.create(order=order, kit_id='TEST-KIT-005', sample_collected=True)
        
        pdf_content = b'%PDF-1.4\nTest content'
        pdf_file = SimpleUploadedFile('test.pdf', pdf_content, content_type='application/pdf')
        
        pdf_upload = DNAPDFUpload.objects.create(
            kit=kit,
            pdf_file=pdf_file,
            original_filename='test.pdf',
            status='PROCESSING'
        )
    
        extracted_data = ExtractedDNAData.objects.create(
            pdf_upload=pdf_upload,
            trait_name='Eye Color',
            category='TRAITS',
            result_value='Brown',
            confidence_level='HIGH',
            genetic_markers=['rs12913832'],
            extraction_confidence=Decimal('95.5'),
            page_number=1
        )
        
        self.assertEqual(extracted_data.pdf_upload, pdf_upload)
        self.assertEqual(extracted_data.trait_name, 'Eye Color')
        self.assertEqual(extracted_data.category, 'TRAITS')
        self.assertEqual(extracted_data.result_value, 'Brown')
        self.assertEqual(extracted_data.confidence_level, 'HIGH')
        self.assertFalse(extracted_data.is_processed)
        self.assertIn('Eye Color', str(extracted_data))
