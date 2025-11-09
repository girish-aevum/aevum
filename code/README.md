# Aevum Health Platform

## 🏥 Overview

Aevum Health is a comprehensive digital health platform that provides personalized healthcare solutions through advanced technology integration. The platform combines genetic analysis, mental wellness tracking, AI-powered health insights, personalized healthcare management, and advanced quality assurance systems.

## 🚀 **Current Status: FULLY OPERATIONAL & ENHANCED**

- ✅ **Authentication System** - Complete user management with JWT, email verification, password reset
- ✅ **DNA Profile System** - Comprehensive genetic analysis with PDF processing and lab management  
- ✅ **Mental Wellness** - Advanced mood logging with AI insights and analytics
- ✅ **AI Companion** - Intelligent health assistant with QA testing and feedback systems
- ✅ **Smart Journal** - AI-powered personal journaling with insights and analytics
- ✅ **Dashboard** - Centralized health data visualization and analytics
- ✅ **Healthcare Module** - Medical records and provider integration
- ✅ **Nutrition Tracking** - Dietary analysis and recommendations
- ✅ **QA Testing System** - Comprehensive quality assurance for AI responses
- ✅ **Feedback System** - User feedback collection and QA review workflows

## 📊 **Enhanced System Statistics**

- **Total API Endpoints**: 50+ endpoints across all modules
- **Database Models**: 18+ comprehensive models with QA enhancements
- **Apps**: 8 specialized Django apps
- **Authentication**: JWT-based with refresh tokens and blacklisting
- **Quality Assurance**: Complete QA testing and feedback system
- **Documentation**: Comprehensive guides for each module + API documentation
- **Testing**: Complete test suites, management commands, and QA workflows

## 🏗️ **Architecture**

### **Backend Stack**
- **Framework**: Django 5.2.6 + Django REST Framework 3.16.1
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: JWT with SimpleJWT and token blacklisting
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **File Processing**: PDF extraction, OCR, image handling
- **Email System**: Django email with HTML templates
- **AI Integration**: Groq API with llama3-70b-8192 model
- **Quality Assurance**: Built-in QA testing and feedback systems

### **Enhanced Key Features**
- **RESTful APIs** with comprehensive OpenAPI documentation
- **Configurable Pagination** with environment-based settings
- **AI-Powered Insights** for health analysis with quality monitoring
- **Secure File Upload** with validation and processing
- **Real-time Analytics** and trend analysis
- **Professional Admin Interface** with custom dashboards and QA tools
- **Modular Architecture** for easy scaling
- **Quality Assurance System** for AI response monitoring
- **User Feedback Collection** with analytics and reporting
- **Management Commands** for automated QA processes

## 📱 **Applications & Features**

### 🔐 **Authentication** (`/api/authentication/`)
Complete user management system with advanced security features.

**Key Features:**
- JWT-based authentication with refresh tokens and blacklisting
- Email verification and password reset workflows
- Profile management with image upload
- Beautiful HTML email templates
- Token management and cleanup
- User session management

**API Endpoints:**
- `POST /login/` - User authentication
- `POST /logout/` - Secure logout with token blacklisting
- `POST /register/` - User registration with email verification
- `POST /password-reset/` - Password reset request
- `POST /password-reset-confirm/` - Password reset confirmation
- `GET /profile/` - User profile retrieval
- `PUT /profile/` - Profile updates

**Documentation:** [`authentication/`](./authentication/) folder
- `PASSWORD_RESET_GUIDE.md` - Password reset implementation
- `EMAIL_SYSTEM_GUIDE.md` - Email system setup and templates
- `SCHEMA_REFACTORING_GUIDE.md` - Authentication schema design

### 🧬 **DNA Profile** (`/api/dna-profile/`)
Comprehensive genetic analysis platform with lab management and AI-powered processing.

**Key Features:**
- DNA kit ordering and tracking system
- PDF upload with AI-powered data extraction using OCR
- Lab management for results and reports
- Genetic insights and recommendations
- Professional admin interface with bulk operations
- Order status tracking and notifications

**API Endpoints (23+ endpoints):**
- Kit ordering and management
- PDF upload and processing
- Lab result management
- Genetic data analysis
- Order tracking and status updates

**Documentation:** [`dna_profile/`](./dna_profile/) folder
- `DNA_PROFILE_SYSTEM_GUIDE.md` - Complete system overview
- `DNA_PDF_UPLOAD_SYSTEM.md` - PDF processing capabilities

### 🧠 **Mental Wellness** (`/api/mental-wellness/`)
Advanced mood logging and mental health analytics with AI-powered insights.

**Key Features:**
- Comprehensive mood tracking (mood, energy, anxiety, stress levels)
- AI-generated insights and pattern recognition
- Activity and trigger correlation analysis
- Dashboard with trends and statistics
- Professional mental health monitoring
- Mood analytics and reporting

**API Endpoints (15+ endpoints):**
- Mood logging and tracking
- Emotion management
- Analytics and insights
- Trend analysis
- Mental health reporting

**Documentation:** [`mental_wellness/`](./mental_wellness/) folder
- `MENTAL_WELLNESS_MOOD_LOGGING.md` - Complete mood logging system

### 🤖 **AI Companion** (`/api/ai-companion/`)
Intelligent health assistant with advanced QA testing and user feedback systems.

**Key Features:**
- **Chat System**: Thread-based conversations like ChatGPT
- **AI Integration**: Groq API with llama3-70b-8192 model
- **Quality Assurance**: Complete QA testing system for AI responses
- **User Feedback**: Thumbs up/down with detailed comments
- **Thread Management**: Favorites, archiving, categorization
- **Smart Suggestions**: AI-generated conversation suggestions
- **Analytics**: Response time, token usage, helpfulness tracking
- **QA Workflow**: Random message selection and systematic review

**AI Companion API Endpoints:**
- `GET /threads/` - List user's chat threads
- `GET /threads/{id}/` - Get thread details with messages
- `POST /chat/` - Send message and get AI response
- `POST /messages/react/` - React to AI messages (👍/👎)
- `POST /threads/{id}/favorite/` - Toggle thread favorite status
- `POST /threads/{id}/archive/` - Archive/unarchive threads
- `GET /suggestions/` - Get smart thread suggestions
- `POST /suggestions/handle/` - Use or dismiss suggestions
- `GET /stats/` - User's AI companion usage statistics

**Feedback System API Endpoints:**
- `POST /feedback/user/` - Submit user feedback on AI messages
- `GET /feedback/user/history/` - Get user's feedback history
- `POST /feedback/qa/` - Submit QA team reviews (Staff only)
- `GET /qa/messages/` - Get QA messages list (Staff only)
- `GET /qa-stats/` - QA statistics and analytics (Staff only)

**QA Testing Features:**
- Random message selection for quality review
- Scoring system (0.0-10.0) with automatic letter grades (A+ to F)
- Multiple review statuses (Pending, Approved, Needs Improvement, Rejected, Skipped)
- QA reviewer tracking and performance metrics
- Comprehensive analytics and reporting
- Management commands for automated QA workflows

**Documentation:** [`ai_companion/`](./ai_companion/) folder
- `QA_TESTING_SYSTEM.md` - Complete QA system guide
- `FEEDBACK_API_GUIDE.md` - Feedback API documentation

### 📝 **Smart Journal** (`/api/smart-journal/`)
AI-powered personal journaling system with insights and analytics.

**Key Features:**
- Personal journaling with AI insights
- Entry analytics and pattern recognition
- Mood correlation with journal entries
- Privacy-focused personal reflection
- AI-generated suggestions and prompts

### 📊 **Dashboard** (`/api/dashboard/`)
Centralized health data visualization and analytics platform.

**Key Features:**
- Comprehensive health data visualization
- Cross-module analytics integration
- Early access request management
- Contact form handling
- User engagement tracking

### 🏥 **Healthcare** (`/api/healthcare/`)
Medical records, provider integration, and health management system.

**Key Features:**
- Medical record management
- Healthcare provider integration
- Appointment tracking
- Health data aggregation
- Clinical insights and reporting

### 🥗 **Nutrition** (`/api/nutrition/`)
Dietary tracking, analysis, and nutritional recommendations system.

**Key Features:**
- Food intake tracking
- Nutritional analysis
- Dietary recommendations
- Meal planning assistance
- Nutrition goal tracking

## 🔧 **Quality Assurance System**

### **QA Testing Features**
- **Random Selection**: Automated selection of AI messages for review
- **Scoring System**: 0.0-10.0 scale with automatic letter grades
- **Review Workflow**: Multiple status levels for systematic review
- **Analytics**: Comprehensive QA metrics and reporting
- **Management Tools**: Command-line tools for QA operations

### **Management Commands**
```bash
# Select messages for QA testing
python manage.py select_messages_for_qa --count 10 --min-length 50

# Interactive QA review session
python manage.py qa_review_messages --reviewer username --batch-size 5

# Generate AI suggestions
python manage.py generate_suggestions

# Populate AI personalities
python manage.py populate_ai_personalities
```

### **QA Workflow**
1. **Selection**: Random AI messages selected for review
2. **Review**: QA team scores and provides feedback
3. **Analytics**: Performance tracking and reporting
4. **Improvement**: Insights used for AI model enhancement

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Navigate to project
cd /path/to/aevum/code

# Activate virtual environment (Python 3.12.3)
source ../env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Environment Configuration**
```bash
# Copy environment template
cp env.example .env

# Configure essential settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# AI Configuration
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama3-70b-8192

# Email Configuration (optional for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### **3. Database Setup**
```bash
# Run all migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Populate sample data (optional)
python manage.py populate_dna_kits
python manage.py populate_mood_data
python manage.py populate_ai_personalities
```

### **4. Start Development Server**
```bash
# Start server on port 8080
python manage.py runserver 8080
```

### **5. Access the Platform**
- **API Documentation**: http://localhost:8080/api/docs/
- **Admin Interface**: http://localhost:8080/admin/
- **API Base URL**: http://localhost:8080/api/
- **OpenAPI Schema**: http://localhost:8080/api/schema/

## 📚 **Comprehensive API Documentation**

### **Interactive Documentation**
- **Swagger UI**: http://localhost:8080/api/docs/
- **ReDoc**: http://localhost:8080/api/redoc/
- **OpenAPI Schema**: http://localhost:8080/api/schema/

### **Authentication**
All user-specific endpoints require JWT authentication:
```bash
# Get access token
POST /api/authentication/login/
{
  "username": "your_username",
  "password": "your_password"
}

# Use in requests
Authorization: Bearer <your_access_token>
```

### **Complete API Endpoints Summary**
```
Authentication:       /api/authentication/     (7 endpoints)
DNA Profile:          /api/dna-profile/        (23+ endpoints)
Mental Wellness:      /api/mental-wellness/    (15+ endpoints)
AI Companion:         /api/ai-companion/       (13+ endpoints)
  ├── Chat System:    /chat/, /threads/, /messages/
  ├── User Feedback:  /feedback/user/, /feedback/user/history/
  ├── QA System:      /feedback/qa/, /qa/messages/, /qa-stats/
Smart Journal:        /api/smart-journal/      (8+ endpoints)
Dashboard:            /api/dashboard/          (5+ endpoints)
Healthcare:           /api/healthcare/         (6+ endpoints)
Nutrition:            /api/nutrition/          (6+ endpoints)
```

### **Enhanced Pagination**
All listing APIs support advanced pagination:
```bash
# Standard pagination
GET /api/ai-companion/threads/?page=1&page_size=20

# With filtering and sorting
GET /api/ai-companion/threads/?category=MENTAL_HEALTH&is_favorite=true&page=1

# QA message filtering
GET /api/ai-companion/qa/messages/?status=PENDING&reviewed=false&limit=10
```

**Pagination Response Format:**
```json
{
  "pagination": {
    "count": 45,
    "total_pages": 5,
    "current_page": 1,
    "page_size": 10,
    "has_next": true,
    "has_previous": false,
    "next_page": 2,
    "previous_page": null
  },
  "results": [...]
}
```

## 🧪 **Testing & Quality Assurance**

### **Automated Testing**
```bash
# Run Django tests
python manage.py test

# Test specific apps
python manage.py test ai_companion
python manage.py test authentication

# Check system integrity
python manage.py check
```

### **QA Testing Workflow**
```bash
# Select 10 AI messages for QA review
python manage.py select_messages_for_qa --count 10

# Start interactive QA review session
python manage.py qa_review_messages --reviewer qa_username --batch-size 5

# View QA statistics
curl -H "Authorization: Bearer <staff_token>" http://localhost:8080/api/ai-companion/qa-stats/
```

### **Example Data & Testing**
Each app includes comprehensive testing resources:
- JSON payload examples
- API usage demonstrations
- Test scripts and validation tools
- QA workflow examples

## 🔧 **Development & Architecture**

### **Enhanced Project Structure**
```
aevum/
├── aevum/                    # Django project settings & configuration
├── authentication/          # User management & JWT authentication
├── dna_profile/             # Genetic analysis & lab management
├── mental_wellness/         # Mood tracking & mental health analytics
├── ai_companion/            # AI chat system with QA & feedback
│   ├── management/commands/ # QA automation commands
│   ├── QA_TESTING_SYSTEM.md # QA system documentation
│   └── FEEDBACK_API_GUIDE.md # Feedback API guide
├── smart_journal/           # AI-powered personal journaling
├── dashboard/               # Data visualization & analytics
├── healthcare/              # Medical records & provider integration
├── nutrition/               # Dietary tracking & recommendations
├── templates/               # Email & HTML templates
├── media/                   # User uploads & file storage
├── static/                  # Static assets
├── requirements.txt         # Python dependencies
├── env.example             # Environment configuration template
├── manage.py               # Django management commands
└── README.md               # This comprehensive guide
```

### **Database Architecture**
- **18+ Models** with comprehensive relationships
- **Advanced Indexing** for optimal query performance
- **QA Enhancement Fields** for quality assurance tracking
- **User Feedback Tracking** with analytics support
- **Migration System** with version control

### **Key Design Patterns**
- **RESTful API Design** with consistent patterns
- **Permission-Based Access Control** with role management
- **Modular App Architecture** for maintainability
- **Quality Assurance Integration** throughout the system
- **Comprehensive Logging** and error tracking

### **Adding New Features**
1. Create models in appropriate app with proper relationships
2. Add serializers with comprehensive validation
3. Implement views with proper permissions and error handling
4. Add URL patterns with clear naming conventions
5. Update admin interface with custom displays
6. Write comprehensive tests and documentation
7. Add QA considerations if AI-related features

## 🚀 **Production Deployment**

### **Environment Variables**
```bash
# Core Django Settings
DEBUG=False
SECRET_KEY=your_production_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SITE_URL=https://yourdomain.com/

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/aevum_production

# JWT Token Configuration
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@domain.com
EMAIL_HOST_PASSWORD=your_secure_app_password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
CONTACT_EMAIL=support@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

# AI Configuration
GROQ_API_KEY=your_production_groq_api_key
GROQ_MODEL=llama3-70b-8192

# Pagination Configuration
PAGE_SIZE=20
MAX_PAGE_SIZE=100
LARGE_PAGE_SIZE=50
MAX_LARGE_PAGE_SIZE=200
SMALL_PAGE_SIZE=10
MAX_SMALL_PAGE_SIZE=50

# File Upload Configuration
MAX_UPLOAD_SIZE=52428800  # 50MB

# API Rate Limiting
API_RATE_LIMIT=100  # requests per minute

# Logging Configuration
LOG_LEVEL=INFO

# Analytics & SEO
GOOGLE_ANALYTICS_ID=your_ga_id
```

### **Production Checklist**
- [ ] Set `DEBUG=False` and configure secure settings
- [ ] Configure PostgreSQL database with connection pooling
- [ ] Set up email service (SendGrid, AWS SES, etc.)
- [ ] Configure static file serving with CDN
- [ ] Set up SSL/HTTPS with proper certificates
- [ ] Configure logging with log rotation
- [ ] Set up monitoring and alerting
- [ ] Implement backup strategy for database and media files
- [ ] Configure Groq API for AI features
- [ ] Set up QA review workflow and team access
- [ ] Configure rate limiting and security headers
- [ ] Set up error tracking (Sentry, etc.)

### **Performance Optimization**
- Database query optimization with select_related/prefetch_related
- Redis caching for frequently accessed data
- API response caching for static content
- Database connection pooling
- Asynchronous task processing for heavy operations
- CDN integration for static and media files

## 👥 **Team & Workflow Management**

### **QA Team Setup**
```bash
# Create QA reviewer accounts
python manage.py createsuperuser  # For QA team leads
python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.create_user('qa_reviewer1', 'qa1@company.com', 'password', is_staff=True)
User.objects.create_user('qa_reviewer2', 'qa2@company.com', 'password', is_staff=True)
"

# Start QA workflow
python manage.py select_messages_for_qa --count 20
python manage.py qa_review_messages --reviewer qa_reviewer1
```

### **Development Workflow**
1. **Feature Development**: Create feature branch from main
2. **Implementation**: Develop with comprehensive tests
3. **QA Integration**: Add QA considerations for AI features
4. **Documentation**: Update relevant documentation
5. **Testing**: Run full test suite including QA workflows
6. **Review**: Code review with focus on security and quality
7. **Deployment**: Staged deployment with monitoring

### **Code Standards & Quality**
- **Python**: Follow PEP 8 with Black formatting
- **API Design**: RESTful principles with consistent patterns
- **Documentation**: Comprehensive docstrings and API docs
- **Testing**: Minimum 80% code coverage
- **Security**: Regular security audits and updates
- **QA Integration**: Quality checks for all AI-related features

## 📊 **Monitoring & Analytics**

### **System Monitoring**
- **Health Checks**: Automated endpoint monitoring
- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Comprehensive error logging and alerts
- **QA Metrics**: AI response quality tracking
- **User Engagement**: Feedback and usage analytics

### **QA Analytics Dashboard**
- **Coverage Metrics**: Percentage of AI responses reviewed
- **Quality Trends**: Score distributions over time
- **Reviewer Performance**: Individual and team metrics
- **User Satisfaction**: Correlation between QA scores and user feedback
- **Improvement Tracking**: Before/after quality measurements

## 🔒 **Security & Compliance**

### **Security Features**
- **JWT Authentication** with secure token management
- **Permission-Based Access Control** with role separation
- **Input Validation** and sanitization
- **SQL Injection Protection** via Django ORM
- **XSS Protection** with proper output encoding
- **CSRF Protection** for state-changing operations
- **Rate Limiting** to prevent abuse
- **Secure File Upload** with validation and scanning

### **Privacy & Compliance**
- **Data Encryption** at rest and in transit
- **User Data Privacy** with consent management
- **HIPAA Considerations** for health data handling
- **Audit Trails** for all critical operations
- **Data Retention Policies** with automated cleanup
- **QA Data Security** with reviewer access controls

## 📞 **Support & Documentation**

### **Comprehensive Documentation**
- **API Documentation**: Interactive Swagger/OpenAPI docs
- **Module Guides**: Detailed documentation in each app folder
- **QA System Guide**: Complete quality assurance documentation
- **Feedback API Guide**: User and QA feedback system documentation
- **Deployment Guide**: Production deployment instructions
- **Troubleshooting**: Common issues and solutions

### **Getting Help**
- **Documentation First**: Check app-specific documentation
- **API Reference**: Use interactive API documentation
- **Error Logs**: Check Django logs for detailed error information
- **QA Issues**: Refer to QA system documentation
- **Database Issues**: Verify migrations are current
- **Dependencies**: Ensure all requirements are installed

### **Common Issues & Solutions**
```bash
# Migration issues
python manage.py showmigrations
python manage.py migrate --fake-initial

# QA system issues
python manage.py shell -c "from ai_companion.models import Message; print(Message.objects.filter(is_selected_for_qa=True).count())"

# Permission issues
python manage.py shell -c "from django.contrib.auth.models import User; print([u.username for u in User.objects.filter(is_staff=True)])"

# API testing
curl -H "Authorization: Bearer <token>" http://localhost:8080/api/ai-companion/stats/
```

## 📄 **License & Legal**

This project is proprietary software developed for Aevum Health. All rights reserved.

**Third-Party Dependencies:**
- Django and related packages (BSD License)
- Groq API integration (Commercial License)
- Various Python packages (See requirements.txt for details)

---

## 🎉 **Platform Status: PRODUCTION READY**

### **✅ FULLY OPERATIONAL SYSTEMS**
- **🔐 Authentication**: Complete JWT system with security features
- **🧬 DNA Analysis**: Full genetic analysis platform with lab management
- **🧠 Mental Wellness**: Advanced mood tracking with AI insights
- **🤖 AI Companion**: Intelligent assistant with comprehensive QA system
- **📝 Smart Journal**: AI-powered personal journaling
- **📊 Dashboard**: Centralized analytics and visualization
- **🏥 Healthcare**: Medical records and provider integration
- **🥗 Nutrition**: Dietary tracking and recommendations
- **🔍 QA System**: Complete quality assurance for AI responses
- **💬 Feedback System**: User feedback collection and analysis

### **📈 ENHANCED CAPABILITIES**
- **50+ API Endpoints** with comprehensive documentation
- **18+ Database Models** with advanced relationships
- **Complete QA Workflow** with automated testing and review
- **User Feedback Integration** with analytics and reporting
- **AI Quality Monitoring** with performance tracking
- **Professional Admin Interface** with QA management tools
- **Management Commands** for automated operations
- **Comprehensive Documentation** with usage guides

### **🚀 READY FOR PRODUCTION**
- **Scalable Architecture** designed for growth
- **Security-First Approach** with comprehensive protection
- **Quality Assurance Integration** for AI response monitoring
- **Professional Documentation** for development and operations
- **Complete Testing Suite** with QA workflow validation
- **Production Deployment Guide** with best practices
- **Monitoring & Analytics** for system health and quality tracking

**The Aevum Health Platform is now a comprehensive, production-ready digital health solution with advanced AI capabilities and quality assurance systems. Ready for user onboarding and scaling!** 🚀

---

*For detailed information about specific modules, check the documentation in each app's folder. For QA system details, see `ai_companion/QA_TESTING_SYSTEM.md`. For feedback API usage, see `ai_companion/FEEDBACK_API_GUIDE.md`.* 