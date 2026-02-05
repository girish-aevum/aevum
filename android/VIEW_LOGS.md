# How to View Logs in Android Studio

## Steps to View Logcat:

1. **Open Logcat Tab:**
   - At the bottom of Android Studio, click on the **"Logcat"** tab
   - If you don't see it, go to: `View` → `Tool Windows` → `Logcat`

2. **Filter Logs:**
   - In the Logcat search box, type: `RetrofitClient` or `AuthRepository`
   - Or use: `tag:RetrofitClient` or `tag:AuthRepository`
   - You can also filter by package: `package:com.aevum.health`

3. **Look for These Log Tags:**
   - `RetrofitClient` - Shows raw API response
   - `AuthRepository` - Shows API call status
   - `ProfileActivity` - Shows profile loading status

4. **Clear Logs:**
   - Click the trash icon (🗑️) to clear old logs
   - Then navigate to Profile page to see fresh logs

5. **Save Logs:**
   - Right-click in Logcat → `Save Logcat to File` to export logs

## What to Look For:

When you open the Profile page, you should see logs like:

```
D/RetrofitClient: =========================================
D/RetrofitClient: RAW API RESPONSE for http://10.0.2.2:8080/api/authentication/profile/
D/RetrofitClient: Response Code: 200
D/RetrofitClient: Response Body: {"id":1,"user":{"id":1,"username":"...","email":"..."},...}
D/RetrofitClient: =========================================
```

Copy the **Response Body** JSON and share it!

