# DNA Profile System - Complete Guide

## Overview

The Aevum Health DNA Profile System is a comprehensive platform for managing DNA kit ordering, sample processing, genetic analysis, and result delivery. This system handles the entire lifecycle from kit ordering to personalized health insights.

## 🧬 System Architecture

### Core Models

1. **DNAKitType** - Available DNA test packages
2. **DNAKitOrder** - User orders for DNA kits
3. **DNAKit** - Physical kits with unique barcodes
4. **DNAResult** - Individual genetic analysis results
5. **DNAReport** - Comprehensive analysis reports
6. **DNAConsent** - User consent for data usage

### Key Features

- ✅ Professional DNA kit ordering system
- ✅ Complete order tracking and status management
- ✅ Secure result storage and delivery
- ✅ Comprehensive admin interface
- ✅ User consent management
- ✅ Lab workflow integration
- ✅ Professional reporting system

## 🔗 API Endpoints

### Public Endpoints (No Authentication Required)

#### DNA Kit Types
```http
GET /api/dna-profile/kit-types/
GET /api/dna-profile/kit-types/{id}/
```

**Query Parameters:**
- `category`: Filter by kit category (ANCESTRY, HEALTH, FITNESS, etc.)
- `search`: Search in name and description
- `ordering`: Sort by name, price, category

**Example Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Health Insights Pro",
      "category": "HEALTH",
      "description": "Comprehensive health risk assessment...",
      "price": "199.00",
      "processing_time_days": 28,
      "features": [
        "Disease risk assessment (150+ conditions)",
        "Genetic predispositions",
        "Carrier status screening"
      ],
      "is_active": true,
      "requires_prescription": false
    }
  ]
}
```

### User Endpoints (Authentication Required)

#### Kit Ordering
```http
POST /api/dna-profile/orders/create/
GET /api/dna-profile/orders/
GET /api/dna-profile/orders/{id}/
```

**Order Creation Example:**
```json
{
  "kit_type": 1,
  "quantity": 1,
  "shipping_method": "EXPRESS",
  "shipping_address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94105",
    "country": "USA"
  },
  "special_instructions": "Leave at front door"
}
```

#### Kit Activation
```http
POST /api/dna-profile/kits/activate/
```

**Request:**
```json
{
  "kit_id": "AEVUM-A1B2C3D4",
  "activation_code": "optional_code"
}
```

#### Results & Reports
```http
GET /api/dna-profile/results/
GET /api/dna-profile/results/{id}/
GET /api/dna-profile/reports/
GET /api/dna-profile/reports/{id}/
```

**Query Parameters for Results:**
- `category`: Filter by result category
- `confidence`: Filter by confidence level
- `search`: Search in trait names

#### Dashboard
```http
GET /api/dna-profile/dashboard/
```

**Response:**
```json
{
  "total_orders": 3,
  "active_orders": 1,
  "completed_orders": 2,
  "pending_results": 1,
  "recent_orders": [...],
  "latest_results": [...],
  "ancestry_results_count": 45,
  "health_results_count": 23,
  "fitness_results_count": 12,
  "consent_status": {
    "ANALYSIS": true,
    "RESEARCH": false
  }
}
```

#### Consent Management
```http
GET /api/dna-profile/consent/
POST /api/dna-profile/consent/
```

### Lab/Admin Endpoints (Restricted Access)

#### Create DNA Results
```http
POST /api/dna-profile/lab/results/create/
```

**Request:**
```json
{
  "kit_id": "AEVUM-A1B2C3D4",
  "category": "HEALTH_RISK",
  "subcategory": "Cardiovascular",
  "trait_name": "Type 2 Diabetes Risk",
  "result_value": "Slightly increased risk (1.3x average)",
  "confidence_level": "HIGH",
  "risk_score": 65.5,
  "genetic_markers": ["rs7903146", "rs12255372"],
  "methodology": "Polygenic Risk Score",
  "clinical_significance": "MODERATE",
  "recommendations": "Maintain healthy diet and regular exercise",
  "requires_followup": true,
  "reviewed_by": "Dr. Jane Smith"
}
```

#### Update DNA Results
```http
PUT /api/dna-profile/lab/results/{id}/update/
PATCH /api/dna-profile/lab/results/{id}/update/
```

#### Create DNA Reports
```http
POST /api/dna-profile/lab/reports/create/
```

**Request:**
```json
{
  "kit_id": "AEVUM-A1B2C3D4",
  "report_type": "COMPREHENSIVE",
  "summary": "Your genetic analysis reveals important insights about your health predispositions...",
  "key_findings": [
    "Increased risk for Type 2 Diabetes",
    "Normal risk for Heart Disease",
    "Carrier for Cystic Fibrosis"
  ],
  "recommendations": "Based on your results, we recommend regular health screenings...",
  "report_file_url": "https://reports.aevumhealth.com/reports/ABC123.pdf",
  "raw_data_url": "https://data.aevumhealth.com/raw/ABC123.txt",
  "quality_score": 98.5,
  "validated_by": "Dr. John Doe"
}
```

#### Update DNA Reports
```http
PUT /api/dna-profile/lab/reports/{id}/update/
PATCH /api/dna-profile/lab/reports/{id}/update/
```

#### Update Order Status
```http
PATCH /api/dna-profile/lab/orders/{order_id}/status/
```

**Request:**
```json
{
  "status": "SAMPLE_RECEIVED",
  "tracking_number": "1Z999AA1234567890"
}
```

## 📋 Order Workflow

### 1. Kit Ordering Process
```
User Browse Kits → Select Kit → Provide Shipping → Place Order → Payment → Order Confirmed
```

### 2. Fulfillment Process
```
Order Confirmed → Kit Prepared → Kit Shipped → Kit Delivered → Kit Activated → Sample Collected
```

### 3. Lab Processing
```
Sample Received → Quality Check → DNA Extraction → Analysis → Results Generated → Report Created
```

### 4. Result Delivery
```
Results Reviewed → Report Finalized → User Notified → Results Available → Dashboard Updated
```

## 🔒 Order Status Flow

| Status | Description | Next Status |
|--------|-------------|-------------|
| PENDING | Order placed, awaiting confirmation | CONFIRMED |
| CONFIRMED | Order confirmed, preparing for shipment | SHIPPED |
| SHIPPED | Kit shipped to customer | DELIVERED |
| DELIVERED | Kit delivered, awaiting activation | SAMPLE_RECEIVED |
| SAMPLE_RECEIVED | Sample received at lab | PROCESSING |
| PROCESSING | Sample being analyzed | COMPLETED |
| COMPLETED | Results ready | - |
| CANCELLED | Order cancelled | - |
| FAILED | Processing failed | - |

## 🧪 Result Categories

### ANCESTRY
- Ethnicity breakdown
- Geographic origins
- Migration patterns
- DNA relative matching

### HEALTH_RISK
- Disease predispositions
- Risk factors
- Genetic variants
- Clinical significance

### CARRIER_STATUS
- Recessive conditions
- Inheritance patterns
- Family planning insights

### PHARMACOGENOMICS
- Drug response
- Metabolism rates
- Dosage recommendations
- Drug interactions

### TRAITS
- Physical characteristics
- Behavioral traits
- Sensory preferences

### FITNESS
- Exercise response
- Muscle composition
- Injury risk
- Recovery patterns

### WELLNESS
- Sleep patterns
- Stress response
- Nutritional needs

## 🎛️ Admin Interface Features

### DNA Kit Types Management
- Create/edit kit types
- Set pricing and features
- Manage availability
- Track popularity

### Order Management
- View all orders
- Update order status
- Track shipments
- Manage payments

### Kit Tracking
- Monitor kit lifecycle
- Quality control notes
- Sample status tracking

### Results Management
- Review lab results
- Quality assurance
- Result validation
- Clinical annotations

### User Consent Tracking
- Monitor consent status
- Legal compliance
- Data usage permissions

## 🛠️ Management Commands

### Populate Sample Data
```bash
python manage.py populate_dna_kits
python manage.py populate_dna_kits --clear  # Clear existing first
```

### Data Maintenance
```bash
# Clean up old orders (custom command - to be implemented)
python manage.py cleanup_old_orders --days 365

# Generate reports (custom command - to be implemented)
python manage.py generate_monthly_reports
```

## 🔐 Security & Privacy

### Data Protection
- All genetic data encrypted at rest
- Secure API authentication required
- User consent tracking
- GDPR compliance ready

### Access Controls
- User can only access their own data
- Lab staff permissions for result updates
- Admin controls for system management

### Audit Trail
- All data changes logged
- User consent history tracked
- Result review history maintained

## 📊 Sample Data Structure

### DNA Result Example
```json
{
  "id": 123,
  "result_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "category": "HEALTH_RISK",
  "subcategory": "Cardiovascular",
  "trait_name": "Type 2 Diabetes Risk",
  "result_value": "Slightly increased risk (1.3x average)",
  "confidence_level": "HIGH",
  "risk_score": 65.5,
  "genetic_markers": ["rs7903146", "rs12255372"],
  "methodology": "Polygenic Risk Score",
  "clinical_significance": "MODERATE",
  "recommendations": "Maintain healthy diet and regular exercise...",
  "requires_followup": true
}
```

### Shipping Address Format
```json
{
  "street": "123 Main Street, Apt 4B",
  "city": "San Francisco",
  "state": "CA",
  "zip_code": "94105",
  "country": "USA",
  "phone": "+1-555-123-4567"
}
```

## 🚀 Integration Points

### Payment Processing
- Integrate with Stripe/PayPal
- Handle recurring subscriptions
- Manage refunds and cancellations

### Shipping Integration
- Connect with FedEx/UPS APIs
- Real-time tracking updates
- Delivery confirmations

### Lab Information Systems
- LIMS integration for sample tracking
- Automated result importing
- Quality control workflows

### Notification System
- Email notifications for status updates
- SMS alerts for important milestones
- In-app notifications

## 📈 Monitoring & Analytics

### Key Metrics to Track
- Order conversion rates
- Processing times
- Customer satisfaction
- Result accuracy
- System performance

### Health Checks
- API endpoint monitoring
- Database performance
- Queue processing status
- Error rate tracking

## 🔧 Development & Testing

### Test Data Creation
```python
# Create test user and order
from django.contrib.auth.models import User
from dna_profile.models import DNAKitType, DNAKitOrder

user = User.objects.create_user('testuser', 'test@example.com', 'password')
kit_type = DNAKitType.objects.first()
order = DNAKitOrder.objects.create(
    user=user,
    kit_type=kit_type,
    total_amount=kit_type.price,
    shipping_address={...}
)
```

### API Testing
```bash
# Test kit types endpoint
curl -X GET "http://localhost:8000/api/dna-profile/kit-types/"

# Test authenticated endpoints
curl -X GET "http://localhost:8000/api/dna-profile/dashboard/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🎯 Future Enhancements

### Planned Features
- [ ] Mobile app integration
- [ ] Telemedicine consultations
- [ ] AI-powered health insights
- [ ] Family sharing features
- [ ] Subscription-based testing
- [ ] International shipping
- [ ] Multi-language support

### Technical Improvements
- [ ] GraphQL API option
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Machine learning insights
- [ ] Blockchain data integrity

## 📞 Support & Maintenance

### Regular Tasks
- Monitor order processing
- Review result quality
- Update kit types and pricing
- Manage user consent
- System performance optimization

### Troubleshooting
- Check logs for API errors
- Monitor database performance
- Verify payment processing
- Validate result data integrity

---

**Note:** This system handles sensitive genetic and health data. Always ensure compliance with relevant privacy laws (HIPAA, GDPR, etc.) and maintain the highest security standards. 