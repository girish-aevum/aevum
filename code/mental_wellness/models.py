from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, timedelta
import uuid


class MoodCategory(models.Model):
    """Categories for different types of moods"""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    color_hex = models.CharField(max_length=7, help_text="Hex color code for UI display (e.g., #FF5733)")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon name or emoji")
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Mood Categories"
    
    def __str__(self):
        return self.name


class Emotion(models.Model):
    """Specific emotions that can be associated with mood entries"""
    
    EMOTION_TYPES = [
        ('POSITIVE', 'Positive'),
        ('NEGATIVE', 'Negative'),
        ('NEUTRAL', 'Neutral'),
        ('MIXED', 'Mixed'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    emotion_type = models.CharField(max_length=10, choices=EMOTION_TYPES)
    description = models.TextField(blank=True, null=True)
    intensity_scale = models.CharField(
        max_length=20, 
        default='1-10',
        help_text="Scale used to measure intensity (e.g., '1-10', '1-5')"
    )
    color_hex = models.CharField(max_length=7, help_text="Hex color code for UI display")
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['emotion_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_emotion_type_display()})"


class ActivityType(models.Model):
    """Types of activities that can influence mood"""
    
    ACTIVITY_CATEGORIES = [
        ('EXERCISE', 'Exercise & Fitness'),
        ('SOCIAL', 'Social Activities'),
        ('WORK', 'Work & Career'),
        ('RELAXATION', 'Relaxation & Rest'),
        ('HOBBIES', 'Hobbies & Interests'),
        ('HEALTH', 'Health & Medical'),
        ('FAMILY', 'Family Time'),
        ('EDUCATION', 'Learning & Education'),
        ('SPIRITUAL', 'Spiritual & Meditation'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=ACTIVITY_CATEGORIES)
    description = models.TextField(blank=True, null=True)
    typical_mood_impact = models.CharField(
        max_length=10,
        choices=[('POSITIVE', 'Positive'), ('NEGATIVE', 'Negative'), ('NEUTRAL', 'Neutral')],
        default='NEUTRAL'
    )
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class MoodTrigger(models.Model):
    """Common triggers that can affect mood"""
    
    TRIGGER_CATEGORIES = [
        ('STRESS', 'Stress & Pressure'),
        ('RELATIONSHIPS', 'Relationships'),
        ('WORK', 'Work & Career'),
        ('HEALTH', 'Health Issues'),
        ('FINANCIAL', 'Financial Concerns'),
        ('ENVIRONMENT', 'Environmental Factors'),
        ('SLEEP', 'Sleep Related'),
        ('HORMONAL', 'Hormonal Changes'),
        ('SEASONAL', 'Seasonal Changes'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TRIGGER_CATEGORIES)
    description = models.TextField(blank=True, null=True)
    typical_impact = models.CharField(
        max_length=10,
        choices=[('NEGATIVE', 'Negative'), ('POSITIVE', 'Positive'), ('NEUTRAL', 'Neutral')],
        default='NEGATIVE'
    )
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class MoodEntry(models.Model):
    """Main model for logging mood entries"""
    
    MOOD_LEVELS = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Below Average'),
        (4, 'Average'),
        (5, 'Above Average'),
        (6, 'Good'),
        (7, 'Very Good'),
        (8, 'Great'),
        (9, 'Excellent'),
        (10, 'Outstanding'),
    ]
    
    ENERGY_LEVELS = [
        (1, 'Exhausted'),
        (2, 'Very Low'),
        (3, 'Low'),
        (4, 'Below Average'),
        (5, 'Average'),
        (6, 'Above Average'),
        (7, 'Good'),
        (8, 'High'),
        (9, 'Very High'),
        (10, 'Energetic'),
    ]
    
    ANXIETY_LEVELS = [
        (1, 'No Anxiety'),
        (2, 'Very Low'),
        (3, 'Low'),
        (4, 'Mild'),
        (5, 'Moderate'),
        (6, 'Above Average'),
        (7, 'High'),
        (8, 'Very High'),
        (9, 'Severe'),
        (10, 'Extreme'),
    ]
    
    # Entry identification
    entry_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_entries')
    
    # Date and time
    entry_date = models.DateField(default=date.today)
    entry_time = models.TimeField(default=timezone.now)
    
    # Core mood metrics
    mood_level = models.IntegerField(
        choices=MOOD_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Overall mood level (1-10 scale)"
    )
    energy_level = models.IntegerField(
        choices=ENERGY_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Energy level (1-10 scale)"
    )
    anxiety_level = models.IntegerField(
        choices=ANXIETY_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Anxiety level (1-10 scale)"
    )
    
    # Optional detailed tracking
    stress_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Stress level (1-10 scale)"
    )
    sleep_quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Sleep quality from previous night (1-10 scale)"
    )
    sleep_hours = models.DecimalField(
        max_digits=4, decimal_places=1,
        null=True, blank=True,
        help_text="Hours of sleep from previous night"
    )
    
    # Relationships
    mood_category = models.ForeignKey(
        MoodCategory, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        help_text="Primary mood category for this entry"
    )
    emotions = models.ManyToManyField(
        Emotion, 
        blank=True,
        help_text="Specific emotions experienced"
    )
    activities = models.ManyToManyField(
        ActivityType,
        blank=True,
        help_text="Activities done today that might affect mood"
    )
    triggers = models.ManyToManyField(
        MoodTrigger,
        blank=True,
        help_text="Triggers that affected mood today"
    )
    
    # Free text fields
    notes = models.TextField(
        blank=True, null=True,
        help_text="Additional notes about mood, feelings, or events"
    )
    gratitude_note = models.TextField(
        blank=True, null=True,
        help_text="Something you're grateful for today"
    )
    goals_tomorrow = models.TextField(
        blank=True, null=True,
        help_text="Goals or intentions for tomorrow"
    )
    
    # Weather and environment (optional)
    weather_condition = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="Weather condition (e.g., sunny, rainy, cloudy)"
    )
    location = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Location where mood was logged"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-entry_date', '-entry_time']
        unique_together = ['user', 'entry_date', 'entry_time']
        verbose_name_plural = "Mood Entries"
    
    def __str__(self):
        return f"{self.user.username} - {self.entry_date} - Mood: {self.mood_level}/10"
    
    @property
    def overall_wellbeing_score(self):
        """Calculate an overall wellbeing score based on multiple metrics"""
        # Handle None values gracefully
        if not all([self.mood_level, self.energy_level, self.anxiety_level]):
            return 0.0
        
        # Weight the different metrics
        mood_weight = 0.4
        energy_weight = 0.3
        anxiety_weight = 0.2  # Inverted (lower anxiety is better)
        stress_weight = 0.1   # Inverted (lower stress is better)
        
        score = (self.mood_level * mood_weight + 
                self.energy_level * energy_weight + 
                (11 - self.anxiety_level) * anxiety_weight)
        
        if self.stress_level is not None:
            score += (11 - self.stress_level) * stress_weight
        else:
            # If no stress level, redistribute the weight to other metrics
            adjusted_mood_weight = 0.45
            adjusted_energy_weight = 0.35
            adjusted_anxiety_weight = 0.2
            
            score = (self.mood_level * adjusted_mood_weight + 
                    self.energy_level * adjusted_energy_weight + 
                    (11 - self.anxiety_level) * adjusted_anxiety_weight)
        
        return round(score, 2)
    
    @property
    def mood_trend_indicator(self):
        """Get mood trend compared to recent entries"""
        # Handle case where mood_level is None
        if self.mood_level is None:
            return 'NEUTRAL'
            
        recent_entries = MoodEntry.objects.filter(
            user=self.user,
            entry_date__lt=self.entry_date
        ).order_by('-entry_date')[:7]  # Last 7 days
        
        if not recent_entries:
            return 'NEUTRAL'
        
        # Filter out entries with None mood_level
        valid_entries = [entry for entry in recent_entries if entry.mood_level is not None]
        
        if not valid_entries:
            return 'NEUTRAL'
        
        recent_avg = sum(entry.mood_level for entry in valid_entries) / len(valid_entries)
        
        if self.mood_level > recent_avg + 1:
            return 'IMPROVING'
        elif self.mood_level < recent_avg - 1:
            return 'DECLINING'
        else:
            return 'STABLE'
    
    def save(self, *args, **kwargs):
        # Ensure entry_time is set
        if not self.entry_time:
            self.entry_time = timezone.now().time()
        super().save(*args, **kwargs)


class MoodInsight(models.Model):
    """AI-generated insights and patterns from mood data"""
    
    INSIGHT_TYPES = [
        ('PATTERN', 'Pattern Recognition'),
        ('CORRELATION', 'Correlation Analysis'),
        ('TREND', 'Trend Analysis'),
        ('RECOMMENDATION', 'Recommendation'),
        ('MILESTONE', 'Milestone Achievement'),
        ('WARNING', 'Warning/Alert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    
    # Insight content
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Confidence in this insight (0-100%)"
    )
    
    # Related data
    related_entries = models.ManyToManyField(MoodEntry, blank=True)
    date_range_start = models.DateField()
    date_range_end = models.DateField()
    
    # Action items
    actionable = models.BooleanField(default=False)
    action_items = models.JSONField(default=list, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    user_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
