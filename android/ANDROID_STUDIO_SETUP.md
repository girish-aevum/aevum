# How to Open in Android Studio - Step by Step Guide

## 📱 Opening the Project in Android Studio

### Step 1: Install Android Studio (if not already installed)

1. Download Android Studio from: https://developer.android.com/studio
2. Install it with default settings
3. Launch Android Studio

### Step 2: Open the Project

#### Method 1: From Android Studio Welcome Screen

1. **Open Android Studio**
   - If you see the welcome screen, click **"Open"**
   - If a project is already open, go to `File > Open`

2. **Navigate to the project folder**
   - Browse to: `/home/girish/project/aevum/aevum/android`
   - **Important**: Select the `android` folder (not the parent folder)
   - Click **"OK"**

3. **Trust the Project** (if prompted)
   - Android Studio may ask "Trust Project?"
   - Click **"Trust Project"**

#### Method 2: From File Menu

1. In Android Studio, go to: **File > Open**
2. Navigate to: `/home/girish/project/aevum/aevum/android`
3. Select the `android` folder
4. Click **"OK"**

### Step 3: Wait for Gradle Sync

1. **Gradle Sync will start automatically**
   - You'll see "Gradle sync in progress..." at the bottom
   - First time may take 5-10 minutes (downloading dependencies)
   - Progress bar will show in the bottom status bar

2. **If sync fails:**
   - Check internet connection
   - Click **"Sync Now"** in the notification bar
   - Or go to: **File > Sync Project with Gradle Files**

### Step 4: Configure API URL

1. **Open `gradle.properties`**
   - In the Project panel (left side), navigate to: `android > gradle.properties`
   - Double-click to open

2. **Update the API URL:**
   ```properties
   # For Android Emulator (use this if testing on emulator)
   AEVUM_API_BASE_URL=http://10.0.2.2:8080
   
   # For Physical Device (replace XXX with your computer's IP)
   # Find your IP: 
   #   Linux/Mac: ifconfig | grep inet
   #   Windows: ipconfig
   AEVUM_API_BASE_URL=http://192.168.1.XXX:8080
   ```

3. **Save the file** (Ctrl+S or Cmd+S)

4. **Sync Gradle again:**
   - Click **"Sync Now"** in the notification
   - Or: **File > Sync Project with Gradle Files**

### Step 5: Set Up Android Emulator (or use physical device)

#### Option A: Android Emulator

1. **Open Device Manager:**
   - Click **Tools > Device Manager** (or the device icon in toolbar)

2. **Create Virtual Device:**
   - Click **"Create Device"**
   - Select a device (e.g., **Pixel 5**)
   - Click **"Next"**

3. **Select System Image:**
   - Choose **API 34** (Android 14) or **API 33** (Android 13)
   - Click **"Download"** if needed (may take a few minutes)
   - Click **"Next"**

4. **Finish Setup:**
   - Review settings
   - Click **"Finish"**

5. **Start Emulator:**
   - Click the **▶️ Play** button next to your device
   - Wait for emulator to boot (first time may take 2-3 minutes)

#### Option B: Physical Android Device

1. **Enable Developer Options on your phone:**
   - Go to **Settings > About Phone**
   - Tap **"Build Number"** 7 times
   - You'll see "You are now a developer!"

2. **Enable USB Debugging:**
   - Go to **Settings > Developer Options**
   - Enable **"USB Debugging"**

3. **Connect Device:**
   - Connect phone to computer via USB
   - On phone, allow USB debugging when prompted
   - In Android Studio, your device should appear

### Step 6: Start Backend Server

**Open a terminal and run:**
```bash
cd /home/girish/project/aevum/aevum/code
source ../env/bin/activate  # Activate virtual environment
python manage.py runserver 0.0.0.0:8080
```

**Keep this terminal open** - the server must be running for the app to work.

### Step 7: Run the App

1. **Select Device:**
   - At the top toolbar, click the device dropdown
   - Select your emulator or connected device

2. **Run the App:**
   - Click the green **▶️ Run** button (or press `Shift + F10`)
   - Or go to: **Run > Run 'app'**

3. **Wait for Build:**
   - Android Studio will build the app (first time may take 2-3 minutes)
   - You'll see build progress in the bottom status bar

4. **App Installation:**
   - The app will install on your device/emulator
   - It will launch automatically

### Step 8: Verify It Works

1. **App should show Login screen**
2. **Try registering a new account:**
   - Click "Register"
   - Fill in the form
   - Submit

3. **Try logging in:**
   - Use your credentials
   - You should see the Dashboard

## 🎯 Quick Reference

### Project Location
```
/home/girish/project/aevum/aevum/android
```

### Important Files
- `gradle.properties` - API URL configuration
- `app/build.gradle.kts` - App dependencies
- `app/src/main/AndroidManifest.xml` - App manifest

### Keyboard Shortcuts
- **Run App**: `Shift + F10`
- **Sync Gradle**: `Ctrl + Shift + O` (or File menu)
- **Build Project**: `Ctrl + F9`
- **Clean Project**: `Build > Clean Project`

## 🐛 Troubleshooting

### "Gradle sync failed"
1. Check internet connection
2. Go to: **File > Invalidate Caches / Restart**
3. Select **"Invalidate and Restart"**
4. Wait for sync to complete

### "Cannot resolve symbol"
1. **File > Sync Project with Gradle Files**
2. If still fails: **Build > Clean Project**
3. Then: **Build > Rebuild Project**

### "App won't install"
1. Check device/emulator is running
2. Check device has enough storage
3. Try: **Build > Clean Project** then rebuild

### "Cannot connect to API"
1. Verify backend is running: Open browser to `http://localhost:8080/api/authentication/health/`
2. Check API URL in `gradle.properties`
3. For emulator: Use `http://10.0.2.2:8080`
4. For device: Use your computer's IP address

### "Build failed"
1. Check Android Studio logs (bottom panel)
2. Try: **Build > Clean Project**
3. Then: **Build > Rebuild Project**
4. Check if all dependencies downloaded (Gradle sync)

## ✅ Checklist

Before running:
- [ ] Android Studio installed
- [ ] Project opened in Android Studio
- [ ] Gradle sync completed successfully
- [ ] API URL configured in `gradle.properties`
- [ ] Emulator running OR device connected
- [ ] Backend server running on port 8080
- [ ] No build errors in Android Studio

## 📚 Next Steps

Once the app is running:
1. Explore the code structure
2. Check `README.md` for detailed documentation
3. Start adding features (Mental Wellness, AI Companion, etc.)

---

**Need Help?** Check the main `README.md` or `SETUP_GUIDE.md` for more details!

