# 🚀 Quick Start - Open Android Project in Android Studio

## Step-by-Step Visual Guide

### Step 1: Launch Android Studio

1. **Open Android Studio** from your applications
2. You'll see the **Welcome Screen** with options:
   - "New Project"
   - "Open"
   - "Get from VCS"

### Step 2: Open the Project

**Click "Open"** (or if a project is already open, go to **File > Open**)

### Step 3: Navigate to Project Folder

1. In the file browser, navigate to:
   ```
   /home/girish/project/aevum/aevum/android
   ```

2. **Important**: Select the **`android`** folder (not the parent `aevum` folder)

3. Click **"OK"** or **"Open"**

### Step 4: Trust the Project

If Android Studio asks:
```
"Trust Project?"
```
Click **"Trust Project"** button

### Step 5: Wait for Gradle Sync

1. Android Studio will automatically start **Gradle Sync**
   - Look at the bottom status bar
   - You'll see: "Gradle sync in progress..."
   - Progress bar will show download progress

2. **First time setup** (5-10 minutes):
   - Downloads Gradle wrapper
   - Downloads Android SDK components
   - Downloads project dependencies
   - This is normal and only happens once

3. **Wait for completion:**
   - Status will change to: "Gradle sync finished"
   - You may see some warnings (these are usually fine)

### Step 6: Configure API URL

1. **Open `gradle.properties` file:**
   - In the left **Project** panel
   - Navigate to: `android` > `gradle.properties`
   - Double-click to open

2. **Find this line:**
   ```properties
   AEVUM_API_BASE_URL=http://10.0.2.2:8080
   ```

3. **Update if needed:**
   - **For Android Emulator**: Keep `http://10.0.2.2:8080` (this is correct)
   - **For Physical Device**: Change to your computer's IP
     ```properties
     AEVUM_API_BASE_URL=http://192.168.1.XXX:8080
     ```
     (Replace XXX with your computer's IP address)

4. **Save the file**: Press `Ctrl+S` (or `Cmd+S` on Mac)

5. **Sync again**: Click "Sync Now" in the notification, or go to **File > Sync Project with Gradle Files**

### Step 7: Set Up Android Emulator (Recommended for First Time)

1. **Open Device Manager:**
   - Click **Tools** menu → **Device Manager**
   - Or click the device icon in the toolbar

2. **Create Virtual Device:**
   - Click **"Create Device"** button
   - Select a device (e.g., **Pixel 5** or **Pixel 6**)
   - Click **"Next"**

3. **Select System Image:**
   - Choose **API 34** (Android 14) or **API 33** (Android 13)
   - If not downloaded, click **"Download"** (may take a few minutes)
   - Click **"Next"**

4. **Finish Setup:**
   - Review the settings
   - Click **"Finish"**

5. **Start Emulator:**
   - In Device Manager, click the **▶️ Play** button next to your device
   - Wait for emulator to boot (2-3 minutes first time)

### Step 8: Start Backend Server

**Open a terminal** and run:

```bash
cd /home/girish/project/aevum/aevum/code
source ../env/bin/activate
python manage.py runserver 0.0.0.0:8080
```

**Keep this terminal open** - the server must be running!

### Step 9: Run the App

1. **Select Device:**
   - At the top toolbar, click the device dropdown
   - Select your emulator or connected device

2. **Run the App:**
   - Click the green **▶️ Run** button (or press `Shift + F10`)
   - Or go to: **Run > Run 'app'**

3. **Wait for Build:**
   - Android Studio will build the app
   - First build may take 2-3 minutes
   - Progress shown in bottom status bar

4. **App Installation:**
   - App will install on device/emulator
   - App will launch automatically

### Step 10: Verify It Works

1. **App should show Login screen**
2. **Try registering:**
   - Click "Register"
   - Fill in the form
   - Submit

3. **Try logging in:**
   - Use your credentials
   - You should see the Dashboard

## ✅ Success Checklist

- [ ] Android Studio opened successfully
- [ ] Project opened without errors
- [ ] Gradle sync completed
- [ ] API URL configured in `gradle.properties`
- [ ] Emulator running OR device connected
- [ ] Backend server running on port 8080
- [ ] App builds successfully
- [ ] App launches on device/emulator
- [ ] Login screen appears

## 🐛 Common Issues & Solutions

### Issue: "Gradle sync failed"

**Solution:**
1. Check internet connection
2. Go to: **File > Invalidate Caches / Restart**
3. Select **"Invalidate and Restart"**
4. Wait for sync to complete

### Issue: "Cannot resolve symbol"

**Solution:**
1. **File > Sync Project with Gradle Files**
2. If still fails: **Build > Clean Project**
3. Then: **Build > Rebuild Project**

### Issue: "App won't install"

**Solution:**
1. Check device/emulator is running
2. Check device has enough storage
3. Try: **Build > Clean Project** then rebuild

### Issue: "Cannot connect to API"

**Solution:**
1. Verify backend is running: Open browser to `http://localhost:8080/api/authentication/health/`
2. Check API URL in `gradle.properties`
3. For emulator: Use `http://10.0.2.2:8080`
4. For device: Use your computer's IP address

### Issue: "Build failed"

**Solution:**
1. Check Android Studio logs (bottom panel)
2. Try: **Build > Clean Project**
3. Then: **Build > Rebuild Project**
4. Check if all dependencies downloaded (Gradle sync)

## 📱 Alternative: Using Physical Device

If you prefer to use a physical Android device:

1. **Enable Developer Options:**
   - Go to **Settings > About Phone**
   - Tap **"Build Number"** 7 times
   - You'll see "You are now a developer!"

2. **Enable USB Debugging:**
   - Go to **Settings > Developer Options**
   - Enable **"USB Debugging"**

3. **Connect Device:**
   - Connect phone to computer via USB
   - On phone, allow USB debugging when prompted
   - In Android Studio, your device should appear in device dropdown

4. **Update API URL:**
   - In `gradle.properties`, change to your computer's IP:
     ```properties
     AEVUM_API_BASE_URL=http://192.168.1.XXX:8080
     ```
   - Find your IP: `ifconfig` (Linux/Mac) or `ipconfig` (Windows)

5. **Run the app** as described in Step 9

## 🎯 Next Steps

Once the app is running:

1. **Explore the code:**
   - Check `app/src/main/java/com/aevum/health/`
   - Review activities and layouts

2. **Read documentation:**
   - See `README.md` for detailed documentation
   - See `PROJECT_SUMMARY.md` for project overview

3. **Start developing:**
   - Add new features
   - Customize UI
   - Integrate with backend APIs

## 💡 Tips

- **Keyboard Shortcuts:**
  - Run: `Shift + F10`
  - Build: `Ctrl + F9`
  - Sync: `Ctrl + Shift + O`

- **Useful Views:**
  - **Logcat**: View app logs (bottom panel)
  - **Build**: See build output (bottom panel)
  - **Project**: File structure (left panel)

- **Debugging:**
  - Set breakpoints by clicking left of line numbers
  - Use **Run > Debug 'app'** to debug

---

**Need more help?** Check the detailed guide: `ANDROID_STUDIO_SETUP.md`


