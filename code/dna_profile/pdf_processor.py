"""
DNA PDF Processing Utilities

This module handles the extraction of structured DNA result data from PDF files.
It uses various techniques including OCR, text extraction, and pattern matching
to identify and extract relevant genetic information.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.utils import timezone

logger = logging.getLogger(__name__)

# Try to import PDF processing libraries
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    logger.warning("PyPDF2 not installed. PDF text extraction will be limited.")

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    logger.warning("pdfplumber not installed. Advanced PDF processing unavailable.")

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    logger.warning("OCR libraries not installed. Image-based PDF processing unavailable.")


class DNAPDFProcessor:
    """Main class for processing DNA result PDFs"""
    
    # Common DNA result patterns
    TRAIT_PATTERNS = [
        r'(?i)(Type\s+2\s+Diabetes|Diabetes\s+Risk)',
        r'(?i)(Heart\s+Disease|Cardiovascular\s+Risk)',
        r'(?i)(Alzheimer\'s\s+Disease|Alzheimer\s+Risk)',
        r'(?i)(Breast\s+Cancer|BRCA\d+)',
        r'(?i)(Lactose\s+Intolerance)',
        r'(?i)(Caffeine\s+Metabolism)',
        r'(?i)(Muscle\s+Fiber\s+Type)',
        r'(?i)(Exercise\s+Response)',
        r'(?i)(European\s+Ancestry|African\s+Ancestry|Asian\s+Ancestry)',
        r'(?i)(Carrier\s+Status)',
    ]
    
    RISK_PATTERNS = [
        r'(?i)(increased\s+risk|elevated\s+risk|higher\s+risk)',
        r'(?i)(decreased\s+risk|lower\s+risk|reduced\s+risk)',
        r'(?i)(normal\s+risk|average\s+risk|typical\s+risk)',
        r'(?i)(\d+\.?\d*x\s+(?:higher|lower|average))',
        r'(?i)(\d+\.?\d*%\s+(?:risk|chance))',
    ]
    
    CONFIDENCE_PATTERNS = [
        r'(?i)(high\s+confidence|high\s+certainty)',
        r'(?i)(medium\s+confidence|moderate\s+confidence)',
        r'(?i)(low\s+confidence|low\s+certainty)',
    ]
    
    GENETIC_MARKER_PATTERNS = [
        r'(rs\d+)',  # SNP identifiers
        r'([A-Z]+\d+[A-Z]*)',  # Gene names like BRCA1, APOE4
        r'([A-Z]{2,})',  # Gene symbols
    ]
    
    def __init__(self, pdf_upload):
        self.pdf_upload = pdf_upload
        self.extracted_text = ""
        self.confidence_score = 0.0
        self.processing_notes = []
    
    def process_pdf(self) -> Dict:
        """Main processing method that extracts and structures data from PDF"""
        try:
            # Update status to processing
            self.pdf_upload.status = 'PROCESSING'
            self.pdf_upload.processing_started_at = timezone.now()
            self.pdf_upload.save()
            
            # Extract text from PDF
            self.extracted_text = self._extract_text_from_pdf()
            
            if not self.extracted_text:
                raise Exception("No text could be extracted from PDF")
            
            # Parse structured data
            extracted_data = self._parse_dna_data()
            
            # Calculate overall confidence
            self.confidence_score = self._calculate_confidence_score(extracted_data)
            
            # Update PDF upload record
            self.pdf_upload.extracted_text = self.extracted_text
            self.pdf_upload.extraction_confidence = Decimal(str(self.confidence_score))
            self.pdf_upload.status = 'COMPLETED'
            self.pdf_upload.processing_completed_at = timezone.now()
            self.pdf_upload.processing_notes = '\n'.join(self.processing_notes)
            self.pdf_upload.processed_by = 'AI_PROCESSOR_v1.0'
            self.pdf_upload.save()
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'confidence_score': self.confidence_score,
                'processing_notes': self.processing_notes
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed for {self.pdf_upload.upload_id}: {str(e)}")
            
            # Update status to failed
            self.pdf_upload.status = 'FAILED'
            self.pdf_upload.processing_completed_at = timezone.now()
            self.pdf_upload.processing_notes = f"Processing failed: {str(e)}\n" + '\n'.join(self.processing_notes)
            self.pdf_upload.save()
            
            return {
                'success': False,
                'error': str(e),
                'processing_notes': self.processing_notes
            }
    
    def _extract_text_from_pdf(self) -> str:
        """Extract text from PDF using available libraries"""
        text = ""
        
        # Try pdfplumber first (most reliable)
        if HAS_PDFPLUMBER:
            try:
                text = self._extract_with_pdfplumber()
                if text:
                    self.processing_notes.append("Successfully extracted text using pdfplumber")
                    return text
            except Exception as e:
                self.processing_notes.append(f"pdfplumber extraction failed: {str(e)}")
        
        # Fallback to PyPDF2
        if HAS_PYPDF2:
            try:
                text = self._extract_with_pypdf2()
                if text:
                    self.processing_notes.append("Successfully extracted text using PyPDF2")
                    return text
            except Exception as e:
                self.processing_notes.append(f"PyPDF2 extraction failed: {str(e)}")
        
        # Last resort: OCR (if available)
        if HAS_OCR:
            try:
                text = self._extract_with_ocr()
                if text:
                    self.processing_notes.append("Successfully extracted text using OCR")
                    return text
            except Exception as e:
                self.processing_notes.append(f"OCR extraction failed: {str(e)}")
        
        self.processing_notes.append("All text extraction methods failed")
        return ""
    
    def _extract_with_pdfplumber(self) -> str:
        """Extract text using pdfplumber"""
        import pdfplumber
        
        text = ""
        with pdfplumber.open(self.pdf_upload.pdf_file.path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
        
        return text.strip()
    
    def _extract_with_pypdf2(self) -> str:
        """Extract text using PyPDF2"""
        import PyPDF2
        
        text = ""
        with open(self.pdf_upload.pdf_file.path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
        
        return text.strip()
    
    def _extract_with_ocr(self) -> str:
        """Extract text using OCR (last resort for image-based PDFs)"""
        # This is a simplified OCR implementation
        # In production, you might want more sophisticated OCR processing
        self.processing_notes.append("OCR extraction not fully implemented yet")
        return ""
    
    def _parse_dna_data(self) -> List[Dict]:
        """Parse structured DNA data from extracted text"""
        extracted_data = []
        
        # Split text into sections/paragraphs
        sections = self._split_into_sections(self.extracted_text)
        
        for section_num, section in enumerate(sections):
            # Look for traits in this section
            traits = self._extract_traits_from_section(section, section_num)
            extracted_data.extend(traits)
        
        return extracted_data
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split text into logical sections for processing"""
        # Split by page markers first
        pages = re.split(r'--- PAGE \d+ ---', text)
        
        sections = []
        for page in pages:
            if not page.strip():
                continue
            
            # Further split by paragraphs or sections
            paragraphs = re.split(r'\n\s*\n', page.strip())
            sections.extend([p.strip() for p in paragraphs if p.strip()])
        
        return sections
    
    def _extract_traits_from_section(self, section: str, section_num: int) -> List[Dict]:
        """Extract DNA traits from a text section"""
        traits = []
        
        # Look for trait names
        for pattern in self.TRAIT_PATTERNS:
            matches = re.finditer(pattern, section)
            for match in matches:
                trait_data = self._extract_trait_details(section, match, section_num)
                if trait_data:
                    traits.append(trait_data)
        
        return traits
    
    def _extract_trait_details(self, section: str, trait_match, section_num: int) -> Optional[Dict]:
        """Extract detailed information for a specific trait"""
        trait_name = trait_match.group(1).strip()
        
        # Get the surrounding context (e.g., 200 characters before and after)
        start = max(0, trait_match.start() - 200)
        end = min(len(section), trait_match.end() + 200)
        context = section[start:end]
        
        # Extract various components
        result_value = self._extract_result_value(context)
        confidence_level = self._extract_confidence_level(context)
        risk_score = self._extract_risk_score(context)
        genetic_markers = self._extract_genetic_markers(context)
        category = self._categorize_trait(trait_name)
        
        # Only return if we have meaningful data
        if result_value or risk_score or genetic_markers:
            return {
                'trait_name': trait_name,
                'category': category,
                'result_value': result_value,
                'confidence_level': confidence_level,
                'risk_score': risk_score,
                'genetic_markers': genetic_markers,
                'extraction_confidence': self._calculate_trait_confidence(context),
                'page_number': section_num + 1,
                'text_position': {
                    'start': trait_match.start(),
                    'end': trait_match.end(),
                    'context': context[:100] + '...' if len(context) > 100 else context
                }
            }
        
        return None
    
    def _extract_result_value(self, context: str) -> Optional[str]:
        """Extract the result value from context"""
        # Look for risk descriptions
        for pattern in self.RISK_PATTERNS:
            match = re.search(pattern, context)
            if match:
                return match.group(0).strip()
        
        # Look for percentage values
        percent_match = re.search(r'\d+\.?\d*%', context)
        if percent_match:
            return f"Risk: {percent_match.group(0)}"
        
        # Look for fold changes
        fold_match = re.search(r'\d+\.?\d*x', context)
        if fold_match:
            return f"Risk multiplier: {fold_match.group(0)}"
        
        return None
    
    def _extract_confidence_level(self, context: str) -> Optional[str]:
        """Extract confidence level from context"""
        for pattern in self.CONFIDENCE_PATTERNS:
            match = re.search(pattern, context)
            if match:
                if 'high' in match.group(0).lower():
                    return 'HIGH'
                elif 'medium' in match.group(0).lower() or 'moderate' in match.group(0).lower():
                    return 'MEDIUM'
                elif 'low' in match.group(0).lower():
                    return 'LOW'
        
        return None
    
    def _extract_risk_score(self, context: str) -> Optional[float]:
        """Extract numerical risk score from context"""
        # Look for percentages
        percent_match = re.search(r'(\d+\.?\d*)%', context)
        if percent_match:
            return float(percent_match.group(1))
        
        # Look for fold changes and convert to percentage
        fold_match = re.search(r'(\d+\.?\d*)x', context)
        if fold_match:
            fold_value = float(fold_match.group(1))
            # Convert to percentage (rough approximation)
            return min(100, fold_value * 20)  # 1x = 20%, 2x = 40%, etc.
        
        return None
    
    def _extract_genetic_markers(self, context: str) -> List[str]:
        """Extract genetic markers from context"""
        markers = []
        
        for pattern in self.GENETIC_MARKER_PATTERNS:
            matches = re.findall(pattern, context)
            markers.extend(matches)
        
        # Remove duplicates and filter out common false positives
        markers = list(set(markers))
        markers = [m for m in markers if len(m) > 1 and not m.isdigit()]
        
        return markers[:10]  # Limit to 10 markers
    
    def _categorize_trait(self, trait_name: str) -> str:
        """Categorize trait based on its name"""
        trait_lower = trait_name.lower()
        
        if any(word in trait_lower for word in ['diabetes', 'heart', 'cancer', 'disease', 'alzheimer']):
            return 'HEALTH_RISK'
        elif any(word in trait_lower for word in ['ancestry', 'european', 'african', 'asian']):
            return 'ANCESTRY'
        elif any(word in trait_lower for word in ['muscle', 'exercise', 'fitness', 'metabolism']):
            return 'FITNESS'
        elif any(word in trait_lower for word in ['carrier', 'recessive']):
            return 'CARRIER_STATUS'
        elif any(word in trait_lower for word in ['drug', 'medication', 'warfarin', 'caffeine']):
            return 'PHARMACOGENOMICS'
        else:
            return 'TRAITS'
    
    def _calculate_trait_confidence(self, context: str) -> float:
        """Calculate confidence score for a specific trait extraction"""
        confidence = 50.0  # Base confidence
        
        # Boost confidence based on various factors
        if re.search(r'\d+\.?\d*%', context):
            confidence += 15  # Has percentage
        if re.search(r'\d+\.?\d*x', context):
            confidence += 10  # Has fold change
        if re.search(r'rs\d+', context):
            confidence += 20  # Has SNP identifier
        if any(word in context.lower() for word in ['high', 'medium', 'low']):
            confidence += 10  # Has confidence indicator
        if len(context) > 100:
            confidence += 5  # Rich context
        
        return min(100.0, confidence)
    
    def _calculate_confidence_score(self, extracted_data: List[Dict]) -> float:
        """Calculate overall confidence score for the extraction"""
        if not extracted_data:
            return 0.0
        
        # Average of individual trait confidences
        trait_confidences = [item.get('extraction_confidence', 0) for item in extracted_data]
        average_confidence = sum(trait_confidences) / len(trait_confidences)
        
        # Adjust based on number of traits found
        trait_count_bonus = min(20, len(extracted_data) * 2)
        
        # Adjust based on text quality
        text_quality_bonus = 10 if len(self.extracted_text) > 1000 else 5
        
        total_confidence = average_confidence + trait_count_bonus + text_quality_bonus
        
        return min(100.0, total_confidence)


def process_dna_pdf(pdf_upload):
    """Convenience function to process a DNA PDF upload"""
    processor = DNAPDFProcessor(pdf_upload)
    return processor.process_pdf() 