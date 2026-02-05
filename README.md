# Aevum Health Platform

## 🏥 Overview

Aevum Health is a comprehensive digital health platform that provides personalized healthcare solutions through advanced technology integration. The platform combines genetic analysis, mental wellness tracking, AI-powered health insights, personalized healthcare management, and advanced quality assurance systems.

The platform consists of three main components:
- **Backend API** - Django REST Framework API server
- **Web Frontend** - React-based web application
- **Mobile App** - Native Android application

## 📁 Project Structure

```
aevum/
├── code/              # Django Backend API
│   ├── aevum/         # Django project settings
│   ├── authentication/    # User authentication & management
│   ├── ai_companion/       # AI health assistant
│   ├── mental_wellness/    # Mood tracking & wellness
│   ├── dna_profile/        # DNA analysis & profiling
│   ├── smart_journal/      # AI-powered journaling
│   ├── dashboard/          # Health dashboard
│   ├── healthcare/         # Medical records
│   ├── nutrition/          # Nutrition tracking
│   └── tests/              # Test suites
│
├── frontend/          # React Web Application
│   ├── src/           # React source code
│   ├── public/       # Static assets
│   └── package.json  # Dependencies
│
├── android/          # Android Mobile App
│   ├── app/          # Android app module
│   └── gradle/       # Gradle configuration
│
└── env/              # Python Virtual Environment
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** - For Django backend
- **Node.js 18+** - For React frontend
- **Android Studio** - For Android app development
- **PostgreSQL** (optional) - For production database
- **Git** - Version control

### 1. Backend Setup (Django)

```bash
# Navigate to backend directory
cd code

# Create and activate virtual environment (if not exists)
python3 -m venv ../env
source ../env/bin/activate  # On Windows: ..\env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp env.example .env

# Edit .env file with your configuration
# Set SECRET_KEY, DATABASE_URL, GROQ_API_KEY, etc.

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8080
```

**Backend will be available at:** `http://localhost:8080`

**API Documentation:**
- Swagger UI: `http://localhost:8080/api/docs/`
- ReDoc: `http://localhost:8080/api/redoc/`

### 2. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

**Frontend will be available at:** `http://localhost:3000`

The React app is configured to proxy API requests to `http://127.0.0.1:8080` (see `package.json`).

### 3. Android App Setup

```bash
# Navigate to android directory
cd android

# Open in Android Studio
# File > Open > Select the android folder
```

**Detailed Android Setup:**
- See [`android/ANDROID_STUDIO_SETUP.md`](./android/ANDROID_STUDIO_SETUP.md) for step-by-step instructions
- See [`android/README.md`](./android/README.md) for comprehensive documentation

**Quick Steps:**
1. Open Android Studio
2. Open the `android` folder
3. Wait for Gradle sync
4. Configure API URL in `gradle.properties`
5. Start emulator or connect device
6. Run the app

## 🏗️ Architecture

### Backend (Django REST Framework)

**Technology Stack:**
- **Framework**: Django 5.2.6 + Django REST Framework 3.16.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT with SimpleJWT and token blacklisting
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **AI Integration**: Groq API with llama3-70b-8192 model
- **File Processing**: PDF extraction, OCR, image handling
- **Email System**: Django email with HTML templates

**Key Features:**
- RESTful APIs with comprehensive OpenAPI documentation
- JWT-based authentication with refresh tokens
- AI-powered health insights with quality assurance
- Secure file upload and processing
- Real-time analytics and trend analysis
- Professional admin interface
- Modular architecture for easy scaling

**API Endpoints:** 50+ endpoints across 8 modules

### Frontend (React)

**Technology Stack:**
- **Framework**: React 18.2.0
- **Routing**: React Router DOM 6.15.0
- **HTTP Client**: Axios 1.4.0
- **Styling**: Tailwind CSS 3.3.3
- **Icons**: Heroicons, React Icons
- **Charts**: Recharts 2.7.2
- **Animations**: Framer Motion 10.15.0

**Key Features:**
- Modern, responsive UI with Tailwind CSS
- JWT token management with auto-refresh
- Protected routes and authentication
- Real-time data visualization
- Beautiful animations and transitions
- Mobile-responsive design

### Android App (Kotlin)

**Technology Stack:**
- **Language**: Kotlin
- **Architecture**: MVVM (Model-View-ViewModel)
- **HTTP Client**: Retrofit 2.9.0
- **JSON Parsing**: Gson 2.9.0
- **Async**: Kotlin Coroutines 1.7.3
- **Storage**: DataStore 1.0.0
- **UI**: Material Design 3

**Key Features:**
- Native Android experience
- Secure token storage using DataStore
- Material Design 3 components
- Repository pattern for data access
- Comprehensive error handling
- Offline-ready architecture

## 📱 Applications & Features

### 🔐 Authentication System
- User registration and login
- JWT token management
- Email verification
- Password reset workflow
- Profile management
- Subscription management

### 🧬 DNA Profile System
- DNA kit ordering and tracking
- PDF upload with AI-powered extraction
- Lab management for results
- Genetic insights and recommendations
- Order status tracking

### 🧠 Mental Wellness
- Mood logging and tracking
- Emotion categorization
- Activity and trigger tracking
- AI-powered insights
- Analytics and trends
- Pattern recognition

### 🤖 AI Companion
- Intelligent health assistant
- Chat interface with threads
- QA testing and feedback systems
- Knowledge base integration
- RAG (Retrieval-Augmented Generation)
- Response quality monitoring

### 📔 Smart Journal
- AI-powered personal journaling
- Entry categorization
- Insights and analytics
- Search and filtering
- Privacy controls

### 📊 Dashboard
- Centralized health data visualization
- Health summary and statistics
- Quick access to all modules
- Real-time updates

### 🏥 Healthcare Module
- Medical records management
- Provider integration
- Health history tracking

### 🥗 Nutrition Tracking
- Dietary analysis
- Meal logging
- Nutritional recommendations

## 🔧 Configuration

### Backend Configuration

Create a `.env` file in the `code/` directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# AI Integration
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama3-70b-8192

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# RAG Settings
RAG_ENABLED=True
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Frontend Configuration

The frontend is configured to proxy API requests to the backend. Update `package.json` if needed:

```json
{
  "proxy": "http://127.0.0.1:8080"
}
```

### Android Configuration

Update `android/gradle.properties`:

```properties
# For Android Emulator
AEVUM_API_BASE_URL=http://10.0.2.2:8080

# For Physical Device (use your computer's IP)
AEVUM_API_BASE_URL=http://192.168.1.XXX:8080
```

## 🧪 Testing

### Backend Tests

```bash
cd code

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test authentication
python manage.py test ai_companion

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

### Android Tests

```bash
cd android

# Unit tests
./gradlew test

# Instrumented tests
./gradlew connectedAndroidTest
```

## 📚 Documentation

### Backend Documentation
- **Main README**: [`code/README.md`](./code/README.md)
- **API Documentation**: `http://localhost:8080/api/docs/`
- **Module Guides**: See individual app folders in `code/`

### Frontend Documentation
- **README**: [`frontend/README.md`](./frontend/README.md)
- **React Documentation**: https://reactjs.org/

### Android Documentation
- **Main README**: [`android/README.md`](./android/README.md)
- **Setup Guide**: [`android/ANDROID_STUDIO_SETUP.md`](./android/ANDROID_STUDIO_SETUP.md)
- **Quick Setup**: [`android/SETUP_GUIDE.md`](./android/SETUP_GUIDE.md)
- **Project Summary**: [`android/PROJECT_SUMMARY.md`](./android/PROJECT_SUMMARY.md)

## 🚀 Development Workflow

### Starting All Services

**Terminal 1 - Backend:**
```bash
cd code
source ../env/bin/activate
python manage.py runserver 0.0.0.0:8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Android Studio - Mobile App:**
- Open `android` folder in Android Studio
- Run the app on emulator or device

### Development Tips

1. **Backend Development:**
   - Use Django admin at `http://localhost:8080/admin/`
   - Check API docs at `http://localhost:8080/api/docs/`
   - Use Django shell: `python manage.py shell`

2. **Frontend Development:**
   - Hot reload is enabled by default
   - Check browser console for errors
   - Use React DevTools extension

3. **Android Development:**
   - Use Logcat in Android Studio for debugging
   - Enable USB debugging on physical devices
   - Use Android Emulator for testing

## 🔐 Security

### Backend Security
- JWT tokens with refresh mechanism
- Token blacklisting on logout
- Password hashing with Django's PBKDF2
- CORS configuration for API access
- Secure file upload validation
- SQL injection protection (Django ORM)

### Frontend Security
- JWT token storage in localStorage
- Automatic token refresh
- Protected routes
- XSS protection (React's built-in escaping)

### Android Security
- Secure token storage using DataStore
- HTTPS support (configure for production)
- Certificate pinning (recommended for production)

## 🐛 Troubleshooting

### Backend Issues

**Database errors:**
```bash
cd code
python manage.py migrate
```

**Import errors:**
```bash
source ../env/bin/activate
pip install -r requirements.txt
```

**Port already in use:**
```bash
# Use a different port
python manage.py runserver 0.0.0.0:8081
```

### Frontend Issues

**Dependencies not installing:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
- Verify backend is running on port 8080
- Check `package.json` proxy configuration
- Check browser console for CORS errors

### Android Issues

**Gradle sync failed:**
- Check internet connection
- Invalidate caches: `File > Invalidate Caches / Restart`
- Clean project: `Build > Clean Project`

**Cannot connect to API:**
- Verify backend is running
- Check API URL in `gradle.properties`
- For physical device, ensure same network
- Check firewall settings

**App crashes:**
- Check Logcat in Android Studio
- Verify API URL configuration
- Ensure backend is accessible

## 📦 Deployment

### Backend Deployment

1. **Set up production database (PostgreSQL)**
2. **Configure environment variables**
3. **Collect static files**: `python manage.py collectstatic`
4. **Run migrations**: `python manage.py migrate`
5. **Set up WSGI server** (Gunicorn, uWSGI)
6. **Configure reverse proxy** (Nginx, Apache)

### Frontend Deployment

```bash
cd frontend
npm run build
# Deploy the build/ folder to your web server
```

### Android Deployment

1. Generate signed APK in Android Studio
2. Update API URL to production endpoint
3. Test on physical devices
4. Upload to Google Play Store

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Write tests** for new features
5. **Run tests** to ensure everything works
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Code Style

- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: Follow React best practices
- **Android**: Follow Kotlin style guide

## 📄 License

[Add your license here]

## 📞 Support

For issues, questions, or contributions:
- Check the documentation in each module
- Review API documentation at `/api/docs/`
- Check individual README files in each directory

## 🎯 Roadmap

### Completed ✅
- Backend API with all modules
- Web frontend with React
- Android mobile app foundation
- Authentication system
- AI Companion integration
- Mental Wellness tracking
- DNA Profile system
- Smart Journal

### In Progress 🚧
- Enhanced mobile app features
- Offline mode support
- Push notifications
- Advanced analytics

### Planned 📋
- iOS mobile app
- Advanced AI features
- Integration with health devices
- Telemedicine features

---

**Built with ❤️ for better health management**

For detailed documentation, see:
- Backend: [`code/README.md`](./code/README.md)
- Frontend: [`frontend/README.md`](./frontend/README.md)
- Android: [`android/README.md`](./android/README.md)

