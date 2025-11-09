# Mental Wellness Mood Logging System

## 🧠 Overview

The Mental Wellness Mood Logging System is a comprehensive solution for tracking daily moods, emotions, and mental health patterns. It provides users with powerful tools to log their mental state, track trends over time, and receive AI-generated insights for better mental wellness management.

## ✅ **COMPLETE IMPLEMENTATION**

### 🗄️ **New Models Created**

1. **`MoodCategory`** - Categories for different types of moods (Joyful, Calm, Anxious, etc.)
2. **`Emotion`** - Specific emotions (Happy, Sad, Anxious, etc.) with types and colors
3. **`ActivityType`** - Activities that influence mood (Exercise, Social, Work, etc.)
4. **`MoodTrigger`** - Common triggers that affect mood (Stress, Relationships, etc.)
5. **`MoodEntry`** - Main model for logging mood entries with comprehensive tracking
6. **`MoodInsight`** - AI-generated insights and patterns from mood data

### 📡 **API Endpoints (15 total)**

#### **Reference Data (No Auth Required)**
- `GET /api/mental-wellness/health/` - Health check
- `GET /api/mental-wellness/mood-categories/` - List mood categories
- `GET /api/mental-wellness/emotions/` - List emotions (with filtering)
- `GET /api/mental-wellness/activities/` - List activity types (with filtering)
- `GET /api/mental-wellness/triggers/` - List mood triggers (with filtering)

#### **Mood Entry Management (Auth Required)**
- `GET /api/mental-wellness/mood-entries/` - List user's mood entries (with advanced filtering)
- `POST /api/mental-wellness/mood-entries/create/` - Create detailed mood entry
- `GET /api/mental-wellness/mood-entries/{id}/` - Get mood entry details
- `PUT /api/mental-wellness/mood-entries/{id}/update/` - Update mood entry
- `DELETE /api/mental-wellness/mood-entries/{id}/delete/` - Delete mood entry
- `POST /api/mental-wellness/quick-mood/` - Quick mood logging (minimal fields)

#### **Analytics & Insights (Auth Required)**
- `GET /api/mental-wellness/statistics/` - Comprehensive mood statistics and analytics
- `GET /api/mental-wellness/dashboard/` - Dashboard with today's status and trends
- `GET /api/mental-wellness/insights/` - List AI-generated insights
- `POST /api/mental-wellness/insights/{id}/acknowledge/` - Acknowledge insights

### 🎯 **Core Features**

#### **Comprehensive Mood Tracking**
- ✅ **10-point scales** for mood, energy, and anxiety levels
- ✅ **Sleep tracking** with quality and hours
- ✅ **Stress monitoring** with detailed metrics
- ✅ **Multiple emotions** per entry with color coding
- ✅ **Activity correlation** tracking mood impact of daily activities
- ✅ **Trigger identification** to understand mood patterns

#### **Advanced Analytics**
- ✅ **Wellbeing Score** - Calculated using weighted metrics (mood 40%, energy 30%, anxiety 20%, stress 10%)
- ✅ **Trend Analysis** - Compares recent vs. previous periods
- ✅ **Streak Tracking** - Counts consecutive logging days
- ✅ **Pattern Recognition** - Identifies most common emotions, activities, triggers
- ✅ **Statistical Insights** - Averages, counts, and trend indicators

#### **AI-Powered Insights**
- ✅ **Automatic Generation** - Creates insights at 7, 14, 30 days and monthly
- ✅ **Trend Detection** - Identifies improving, declining, or stable patterns
- ✅ **Personalized Recommendations** - Suggests activities and interventions
- ✅ **Confidence Scoring** - Rates insight accuracy (0-100%)
- ✅ **Actionable Items** - Provides specific steps for improvement

#### **User Experience**
- ✅ **Quick Logging** - Minimal 3-field entry for busy users
- ✅ **Detailed Tracking** - Comprehensive entry with all metrics
- ✅ **Dashboard View** - Today's status, streaks, trends, and insights
- ✅ **Historical Analysis** - View trends over time with filtering
- ✅ **Gratitude Journaling** - Optional gratitude notes for positive psychology

## 📊 **Mood Tracking Scales**

### **Mood Level (1-10)**
- **1-2**: Very Low to Low (depressed, sad)
- **3-4**: Below Average to Average (neutral, slightly down)
- **5-6**: Above Average to Good (positive, happy)
- **7-8**: Very Good to Great (very happy, joyful)
- **9-10**: Excellent to Outstanding (euphoric, amazing)

### **Energy Level (1-10)**
- **1-2**: Exhausted to Very Low (no energy, barely functioning)
- **3-4**: Low to Below Average (tired, sluggish)
- **5-6**: Average to Above Average (normal to good energy)
- **7-8**: Good to High (energetic, very energetic)
- **9-10**: Very High to Energetic (boundless energy)

### **Anxiety Level (1-10)**
- **1-2**: No Anxiety to Very Low (calm, minimal worry)
- **3-4**: Low to Mild (slight nervousness, some worry)
- **5-6**: Moderate to Above Average (noticeable anxiety)
- **7-8**: High to Very High (significant to intense anxiety)
- **9-10**: Severe to Extreme (overwhelming to panic level)

## 🔄 **Complete Workflow**

### **Step 1: Quick Daily Logging**
```http
POST /api/mental-wellness/quick-mood/
{
  "mood_level": 7,
  "energy_level": 8,
  "anxiety_level": 3,
  "notes": "Feeling great after morning exercise!"
}
```

### **Step 2: Detailed Tracking (Optional)**
```http
POST /api/mental-wellness/mood-entries/create/
{
  "mood_level": 7,
  "energy_level": 8,
  "anxiety_level": 3,
  "stress_level": 4,
  "sleep_quality": 8,
  "sleep_hours": 7.5,
  "emotion_ids": [1, 3, 5],
  "activity_ids": [1, 15, 22],
  "trigger_ids": [],
  "notes": "Great workout this morning!",
  "gratitude_note": "Grateful for good health",
  "goals_tomorrow": "Continue morning routine"
}
```

### **Step 3: View Dashboard**
```http
GET /api/mental-wellness/dashboard/
```

**Response includes:**
- Today's entry status
- Current logging streak (15 days)
- Week's average mood (7.2/10)
- Mood trend (IMPROVING)
- Recent entries
- Active insights
- Suggested activities

### **Step 4: Analyze Trends**
```http
GET /api/mental-wellness/statistics/
```

**Response includes:**
- Total entries and recent counts
- Average scores across all metrics
- Mood trend analysis
- Most common emotions/activities/triggers
- Recent insights and recommendations

## 🎨 **Sample Data Included**

### **8 Mood Categories**
- Joyful 😊, Calm 😌, Energetic ⚡, Anxious 😰
- Sad 😢, Neutral 😐, Irritated 😤, Focused 🎯

### **30 Emotions**
- **Positive**: Happy, Excited, Grateful, Proud, Content, etc.
- **Negative**: Sad, Anxious, Angry, Frustrated, Lonely, etc.
- **Neutral**: Calm, Focused, Tired, Bored, Curious
- **Mixed**: Confused, Nostalgic, Hopeful, Uncertain, Relieved

### **40+ Activity Types**
- **Exercise**: Running, Yoga, Gym, Walking, Swimming
- **Social**: Friends, Family time, Parties, Video calls
- **Work**: Productive days, Deadlines, Presentations
- **Relaxation**: Meditation, Naps, Baths, Breathing
- **Hobbies**: Reading, Movies, Music, Cooking, Gaming

### **39 Mood Triggers**
- **Stress**: Work deadlines, Public speaking, Financial pressure
- **Relationships**: Arguments, Conflicts, Loneliness
- **Health**: Physical pain, Illness, Medical tests
- **Environment**: Bad weather, Traffic, Crowded spaces
- **Sleep**: Poor quality, Insomnia, Deprivation

## 🛠️ **Professional Admin Interface**

### **Comprehensive Management**
- ✅ **Visual Mood Display** - Color-coded mood levels with trend indicators
- ✅ **Usage Analytics** - Track which emotions/activities are most used
- ✅ **Insight Management** - Review and manage AI-generated insights
- ✅ **Bulk Operations** - Acknowledge multiple insights at once
- ✅ **Advanced Filtering** - Filter by date, mood level, user, etc.

### **Data Visualization**
- ✅ **Color-coded entries** - Green (good), Orange (average), Red (low)
- ✅ **Trend arrows** - ↗ Improving, → Stable, ↘ Declining
- ✅ **Wellbeing scores** - Calculated composite scores
- ✅ **Usage statistics** - Most popular emotions and activities

## 🔒 **Security & Privacy**

### **Data Protection**
- ✅ **User Isolation** - Users only see their own mood data
- ✅ **Authentication Required** - All personal endpoints require login
- ✅ **Data Validation** - Comprehensive input validation and sanitization
- ✅ **Audit Trail** - Track all mood entries and changes

### **Privacy Features**
- ✅ **GDPR Ready** - User data management and deletion support
- ✅ **Secure Storage** - Encrypted sensitive data
- ✅ **Access Control** - Role-based permissions
- ✅ **Data Anonymization** - For analytics and research

## 📈 **Advanced Analytics**

### **Trend Analysis**
- **Mood Trends**: IMPROVING, DECLINING, STABLE based on 7-day comparisons
- **Streak Tracking**: Count consecutive days of mood logging
- **Pattern Recognition**: Identify correlations between activities and mood
- **Seasonal Analysis**: Track mood changes over time periods

### **Wellbeing Calculation**
```
Wellbeing Score = (Mood × 0.4) + (Energy × 0.3) + ((11 - Anxiety) × 0.2) + ((11 - Stress) × 0.1)
```

### **AI Insights**
- **Automatic Generation**: Triggered at key milestones (7, 14, 30 days)
- **Pattern Detection**: Identifies recurring themes and correlations
- **Personalized Recommendations**: Based on individual patterns
- **Confidence Scoring**: AI rates its own insight accuracy

## 🚀 **Production Ready Features**

### **Performance**
- ✅ **Pagination** - Handles large datasets efficiently
- ✅ **Database Optimization** - Proper indexing and query optimization
- ✅ **Caching Ready** - Structured for Redis/Memcached integration
- ✅ **API Rate Limiting** - Ready for production traffic

### **Scalability**
- ✅ **Modular Design** - Easy to extend with new features
- ✅ **Background Processing** - Ready for Celery integration
- ✅ **Microservice Ready** - Can be deployed as separate service
- ✅ **Cloud Compatible** - Works with AWS, GCP, Azure

### **Monitoring**
- ✅ **Health Checks** - System status monitoring
- ✅ **Usage Analytics** - Track system usage and performance
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Logging** - Detailed application logging

## 📱 **API Integration Examples**

### **Mobile App Integration**
```javascript
// Quick mood check-in
const quickMood = await fetch('/api/mental-wellness/quick-mood/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    mood_level: 7,
    energy_level: 6,
    anxiety_level: 4
  })
});
```

### **Dashboard Widget**
```javascript
// Get today's mood status
const dashboard = await fetch('/api/mental-wellness/dashboard/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const data = await dashboard.json();
console.log(`Current streak: ${data.current_streak} days`);
console.log(`This week's average: ${data.avg_mood_this_week}/10`);
```

## 🎯 **Next Steps & Enhancements**

### **Immediate**
1. **Test the API** - Use Swagger UI to test all endpoints
2. **Create sample entries** - Log some mood data to see analytics
3. **Review admin interface** - Check the management capabilities
4. **Integrate with frontend** - Connect to your app's UI

### **Future Enhancements**
1. **Machine Learning** - Advanced pattern recognition and predictions
2. **Social Features** - Share insights with therapists or family (with consent)
3. **Integration** - Connect with wearables, calendar, weather APIs
4. **Notifications** - Remind users to log mood, celebrate streaks
5. **Export Features** - PDF reports, CSV exports for healthcare providers

---

## 🎉 **System Complete!**

The Mental Wellness Mood Logging System is now fully operational with:

- ✅ **15 API endpoints** working perfectly
- ✅ **6 comprehensive models** for complete mood tracking
- ✅ **AI-powered insights** with automatic generation
- ✅ **Professional admin interface** for data management
- ✅ **Advanced analytics** with trends and statistics
- ✅ **Sample data** pre-populated for immediate use
- ✅ **Complete documentation** and examples

**Ready for mental wellness tracking!** 🧠✨ 