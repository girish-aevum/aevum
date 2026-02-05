# Quick Setup Guide - Aevum Health Android App

## 🚀 Quick Start (5 minutes)

### Step 1: Install Android Studio
1. Download [Android Studio](https://developer.android.com/studio)
2. Install with default settings
3. Open Android Studio and let it complete setup

### Step 2: Open the Project
1. Open Android Studio
2. Click `File > Open`
3. Navigate to: `aevum/aevum/android`
4. Select the `android` folder and click `OK`
5. Wait for Gradle sync to complete (first time may take 5-10 minutes)

### Step 3: Configure API URL
1. Open `gradle.properties` file
2. Update the API URL:
   ```properties
   # For Android Emulator (use this if testing on emulator)
   AEVUM_API_BASE_URL=http://10.0.2.2:8080
   
   # For Physical Device (replace XXX with your computer's IP)
   # Find your IP: Windows (ipconfig) or Linux/Mac (ifconfig)
   AEVUM_API_BASE_URL=http://192.168.1.XXX:8080
   ```

### Step 4: Start Backend Server
```bash
cd aevum/aevum/code
python manage.py runserver 0.0.0.0:8080
```

### Step 5: Run the App
1. **Option A: Android Emulator**
   - Click `Tools > Device Manager`
   - Click `Create Device`
   - Select a device (e.g., Pixel 5)
   - Download a system image (API 34 recommended)
   - Click `Finish` and start the emulator
   - Click the green ▶️ Run button in Android Studio

2. **Option B: Physical Device**
   - Enable Developer Options on your Android device
   - Enable USB Debugging
   - Connect device via USB
   - Allow USB debugging when prompted
   - Click the green ▶️ Run button in Android Studio
   - Select your device from the list

## ✅ Verify Setup

1. App should launch and show Login screen
2. Try registering a new account
3. Login with your credentials
4. You should see the Dashboard screen

## 🐛 Common Issues

### "Gradle sync failed"
- **Solution**: Check internet connection, then `File > Invalidate Caches / Restart`

### "Cannot connect to API"
- **Solution**: 
  - Verify backend is running: `http://localhost:8080/api/authentication/health/`
  - For emulator: Use `http://10.0.2.2:8080`
  - For physical device: Use your computer's IP address

### "Build failed"
- **Solution**: 
  - `Build > Clean Project`
  - `Build > Rebuild Project`
  - Check Android Studio logs for specific errors

### "App crashes on launch"
- **Solution**: 
  - Check Logcat in Android Studio for error messages
  - Verify API URL is correct
  - Ensure backend is running

## 📱 Testing Checklist

- [ ] App launches successfully
- [ ] Registration works
- [ ] Login works
- [ ] Dashboard displays user info
- [ ] Logout works
- [ ] App remembers login (close and reopen)

## 🔧 Next Steps

Once basic setup works:
1. Explore the code structure
2. Check `README.md` for detailed documentation
3. Start adding features (Mental Wellness, AI Companion, etc.)

---

**Need Help?** Check the main `README.md` for detailed documentation.

