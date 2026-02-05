# Aevum Health - Android Mobile App

## 📱 Overview

This is the Android mobile application for the Aevum Health platform. Built with Kotlin and Android Studio, it provides a native Android experience for accessing all Aevum Health features including authentication, mental wellness tracking, AI companion, DNA profiling, and more.

## 🏗️ Project Structure

```
android/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/aevum/health/
│   │       │   ├── MainActivity.kt
│   │       │   ├── data/
│   │       │   │   ├── models/          # Data models (User, AuthResponse, etc.)
│   │       │   │   └── local/           # Local storage (AuthPreferences)
│   │       │   ├── network/             # API services (Retrofit)
│   │       │   ├── repository/          # Repository pattern (AuthRepository)
│   │       │   └── ui/
│   │       │       ├── auth/            # Login, Register activities
│   │       │       └── dashboard/       # Dashboard activity
│   │       ├── res/                     # Resources (layouts, strings, colors)
│   │       └── AndroidManifest.xml
│   └── build.gradle.kts
├── build.gradle.kts
├── settings.gradle.kts
└── gradle.properties
```

## 🚀 Setup Instructions

### Prerequisites

1. **Android Studio** - Download and install [Android Studio Hedgehog (2023.1.1)](https://developer.android.com/studio) or later
2. **JDK 17** - Android Studio includes JDK 17, or install separately
3. **Android SDK** - Minimum SDK 24 (Android 7.0), Target SDK 34 (Android 14)
4. **Django Backend** - Ensure your Django backend is running (see backend README)

### Installation Steps

1. **Open Project in Android Studio**
   ```bash
   # Navigate to the android directory
   cd aevum/aevum/android
   
   # Open in Android Studio
   # File > Open > Select the android folder
   ```

2. **Sync Gradle**
   - Android Studio will automatically sync Gradle dependencies
   - If not, click "Sync Now" or go to `File > Sync Project with Gradle Files`

3. **Configure API Base URL**
   - Open `gradle.properties` file
   - Update `AEVUM_API_BASE_URL` with your backend URL:
     ```properties
     # For Android Emulator (localhost)
     AEVUM_API_BASE_URL=http://10.0.2.2:8080
     
     # For Physical Device (replace with your computer's IP)
     AEVUM_API_BASE_URL=http://192.168.1.XXX:8080
     ```
   - **Note**: 
     - `10.0.2.2` is the special IP address that points to `localhost` on the host machine when using Android Emulator
     - For physical devices, use your computer's local IP address (find it with `ipconfig` on Windows or `ifconfig` on Linux/Mac)

4. **Build and Run**
   - Connect an Android device or start an emulator
   - Click the "Run" button (green play icon) or press `Shift + F10`
   - Select your device/emulator
   - The app will build and install automatically

## 🔧 Configuration

### API Configuration

The API base URL is configured in `gradle.properties`:

```properties
AEVUM_API_BASE_URL=http://10.0.2.2:8080
```

This value is automatically injected into `BuildConfig.API_BASE_URL` during build.

### Network Security

For development, the app allows cleartext traffic (HTTP). For production, you should:
1. Use HTTPS
2. Update `AndroidManifest.xml` to remove `android:usesCleartextTraffic="true"`
3. Add network security configuration

## 📚 Key Features

### ✅ Implemented

- **Authentication**
  - User login with email/password
  - User registration
  - JWT token management
  - Secure token storage using DataStore
  - Auto-logout on token expiration

- **User Interface**
  - Material Design 3 components
  - Login screen
  - Registration screen
  - Dashboard screen
  - Responsive layouts

- **API Integration**
  - Retrofit for HTTP requests
  - Gson for JSON parsing
  - OkHttp with logging interceptor
  - Error handling and network error management

### 🚧 To Be Implemented

- Mental Wellness tracking
- AI Companion chat interface
- DNA Profile management
- Smart Journal entries
- Health dashboard with charts
- Push notifications
- Offline mode support

## 🏛️ Architecture

The app follows **MVVM (Model-View-ViewModel)** architecture pattern:

- **Model**: Data models and API responses (`data/models/`)
- **View**: Activities and Fragments (`ui/`)
- **ViewModel**: (To be implemented) ViewModels for data binding
- **Repository**: Data access layer (`repository/`)
- **Network**: API service layer (`network/`)

### Key Components

1. **RetrofitClient**: Singleton Retrofit instance for API calls
2. **AuthRepository**: Handles authentication logic
3. **AuthPreferences**: Secure storage for tokens using DataStore
4. **ApiService**: Retrofit interface defining API endpoints

## 🔐 Security

- **Token Storage**: Tokens are stored securely using Android DataStore Preferences
- **HTTPS Ready**: App is configured to work with HTTPS (update API URL)
- **Token Refresh**: Automatic token refresh on expiration (to be implemented)
- **Secure Logout**: Clears all stored authentication data

## 🧪 Testing

### Running Tests

```bash
# Unit tests
./gradlew test

# Instrumented tests
./gradlew connectedAndroidTest
```

### Manual Testing

1. **Login Flow**
   - Enter valid credentials
   - Verify successful login and navigation to dashboard
   - Test with invalid credentials

2. **Registration Flow**
   - Fill registration form
   - Verify successful registration
   - Test validation (password mismatch, empty fields)

3. **Logout Flow**
   - Click logout button
   - Verify navigation to login screen
   - Verify tokens are cleared

## 📦 Dependencies

### Core Libraries

- **Retrofit 2.9.0** - HTTP client
- **Gson 2.9.0** - JSON parsing
- **OkHttp 4.12.0** - HTTP client implementation
- **Coroutines 1.7.3** - Asynchronous programming
- **DataStore 1.0.0** - Data storage
- **Material Design 3** - UI components
- **Navigation Component 2.7.6** - Navigation between screens

See `app/build.gradle.kts` for complete dependency list.

## 🐛 Troubleshooting

### Build Issues

1. **Gradle Sync Failed**
   - Check internet connection
   - Invalidate caches: `File > Invalidate Caches / Restart`
   - Clean project: `Build > Clean Project`

2. **API Connection Failed**
   - Verify backend is running
   - Check API URL in `gradle.properties`
   - For physical device, ensure device and computer are on same network
   - Check firewall settings

3. **Emulator Issues**
   - Ensure Android Emulator is running
   - Check emulator network settings
   - Try restarting emulator

### Runtime Issues

1. **Login Fails**
   - Verify backend is accessible
   - Check API URL configuration
   - Verify backend CORS settings allow mobile app

2. **Token Expired**
   - Token refresh is not yet implemented
   - User needs to login again

## 🔄 Integration with Backend

The Android app connects to the Django REST API backend. Ensure:

1. **Backend is Running**
   ```bash
   cd aevum/aevum/code
   python manage.py runserver 0.0.0.0:8080
   ```

2. **CORS Configuration** (if needed)
   - Django backend should allow requests from Android app
   - Update `ALLOWED_HOSTS` in Django settings

3. **API Endpoints**
   - All endpoints match the backend API structure
   - Base URL: `http://YOUR_IP:8080/api/`

## 📱 Building for Production

1. **Generate Signed APK**
   - `Build > Generate Signed Bundle / APK`
   - Create keystore if needed
   - Select release build variant

2. **Update API URL**
   - Change to production API URL
   - Use HTTPS endpoint

3. **Remove Debug Features**
   - Disable logging interceptor
   - Remove debug flags

## 🤝 Contributing

When adding new features:

1. Follow MVVM architecture
2. Use Kotlin coroutines for async operations
3. Add proper error handling
4. Update this README
5. Test on both emulator and physical device

## 📄 License

Same as main Aevum Health project.

## 📞 Support

For issues or questions:
- Check backend API documentation
- Review Django backend README
- Check Android Studio logs for errors

---

**Note**: This is an initial setup. More features will be added incrementally to match the React frontend functionality.

