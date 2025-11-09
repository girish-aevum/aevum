from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from django.urls import reverse
import uuid
import os


def journal_attachment_path(instance, filename):
    """Generate upload path for journal attachments"""
    ext = filename.split('.')[-1].lower()
    filename = f"journal_{instance.entry.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('journal_attachments', str(instance.entry.user.id), filename)


class JournalCategory(models.Model):
    """Categories for organizing journal entries"""
    
    CATEGORY_TYPES = [
        ('PERSONAL', 'Personal Life'),
        ('WORK', 'Work & Career'),
        ('HEALTH', 'Health & Wellness'),
        ('RELATIONSHIPS', 'Relationships'),
        ('GOALS', 'Goals & Achievements'),
        ('TRAVEL', 'Travel & Adventures'),
        ('LEARNING', 'Learning & Education'),
        ('CREATIVITY', 'Creative Projects'),
        ('FINANCE', 'Finance & Money'),
        ('GRATITUDE', 'Gratitude & Reflection'),
        ('DREAMS', 'Dreams & Aspirations'),
        ('DAILY', 'Daily Life'),
        ('CUSTOM', 'Custom Category'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True, null=True)
    color_hex = models.CharField(
        max_length=7, 
        default='#6366f1',
        help_text="Hex color code for UI display (e.g., #FF5733)"
    )
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Icon name or emoji for category"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='journal_categories',
        help_text="User who created this category (null for system categories)"
    )
    is_system_category = models.BooleanField(
        default=False,
        help_text="Whether this is a system-wide category or user-specific"
    )
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category_type', 'name']
        verbose_name = "Journal Category"
        verbose_name_plural = "Journal Categories"
        unique_together = ['name', 'user']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['category_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class JournalTemplate(models.Model):
    """Predefined templates for journal entries"""
    
    TEMPLATE_TYPES = [
        ('DAILY_REFLECTION', 'Daily Reflection'),
        ('GRATITUDE', 'Gratitude Journal'),
        ('GOAL_TRACKING', 'Goal Tracking'),
        ('MOOD_CHECK', 'Mood Check-in'),
        ('WORK_LOG', 'Work Log'),
        ('TRAVEL_LOG', 'Travel Log'),
        ('LEARNING_LOG', 'Learning Log'),
        ('HEALTH_LOG', 'Health Log'),
        ('RELATIONSHIP_LOG', 'Relationship Log'),
        ('CREATIVE_LOG', 'Creative Log'),
        ('CUSTOM', 'Custom Template'),
    ]
    
    name = models.CharField(max_length=150)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Template structure
    prompt_questions = models.JSONField(
        default=list,
        help_text="List of prompt questions for this template"
    )
    default_structure = models.JSONField(
        default=dict,
        help_text="Default structure/sections for entries using this template"
    )
    
    # Ownership and visibility
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='journal_templates',
        null=True,
        blank=True,
        help_text="User who created this template (null for system templates)"
    )
    is_system_template = models.BooleanField(
        default=False,
        help_text="Whether this is a system-wide template"
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether other users can use this template"
    )
    is_active = models.BooleanField(default=True)
    
    # Usage statistics
    usage_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template_type', 'name']
        verbose_name = "Journal Template"
        verbose_name_plural = "Journal Templates"
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['template_type']),
            models.Index(fields=['is_system_template']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class JournalEntry(models.Model):
    """Main journal entry model"""
    
    MOOD_CHOICES = [
        (1, '😞 Very Sad'),
        (2, '😕 Sad'),
        (3, '😐 Neutral'),
        (4, '😊 Happy'),
        (5, '😄 Very Happy'),
    ]
    
    ENERGY_CHOICES = [
        (1, '🔋 Very Low'),
        (2, '🔋 Low'),
        (3, '🔋 Moderate'),
        (4, '🔋 High'),
        (5, '🔋 Very High'),
    ]
    
    PRIVACY_CHOICES = [
        ('PRIVATE', 'Private (Only Me)'),
        ('SHARED', 'Shared (Selected People)'),
        ('PUBLIC', 'Public (Anyone)'),
    ]
    
    # Basic information
    entry_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    title = models.CharField(max_length=200, help_text="Title of the journal entry")
    content = models.TextField(help_text="Main content of the journal entry")
    
    # Categorization
    category = models.ForeignKey(
        JournalCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries'
    )
    template = models.ForeignKey(
        JournalTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries',
        help_text="Template used for this entry"
    )
    
    # Entry metadata
    entry_date = models.DateField(
        default=timezone.now,
        help_text="Date this entry represents (can be different from created_at)"
    )
    mood_rating = models.PositiveIntegerField(
        choices=MOOD_CHOICES,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    energy_level = models.PositiveIntegerField(
        choices=ENERGY_CHOICES,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Structured data
    structured_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured data based on template or custom fields"
    )
    
    # Location and context
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Location where this entry was written"
    )
    weather = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Weather conditions"
    )
    
    # Privacy and sharing
    privacy_level = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default='PRIVATE'
    )
    
    # Entry status
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    
    # AI and insights
    ai_insights = models.JSONField(
        default=dict,
        blank=True,
        help_text="AI-generated insights and analysis"
    )
    sentiment_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="AI-calculated sentiment score (-1 to 1)"
    )
    
    # Word count and reading time
    word_count = models.PositiveIntegerField(default=0)
    estimated_reading_time = models.PositiveIntegerField(
        default=0,
        help_text="Estimated reading time in minutes"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-entry_date', '-created_at']
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        indexes = [
            models.Index(fields=['user', 'entry_date']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'is_favorite']),
            models.Index(fields=['user', 'is_archived']),
            models.Index(fields=['mood_rating']),
            models.Index(fields=['energy_level']),
            models.Index(fields=['privacy_level']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.entry_date} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        """Override save to calculate word count and reading time"""
        if self.content:
            # Calculate word count
            self.word_count = len(self.content.split())
            
            # Calculate estimated reading time (average 200 words per minute)
            self.estimated_reading_time = max(1, self.word_count // 200)
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get URL for this journal entry"""
        return reverse('smart_journal:entry-detail', kwargs={'entry_id': self.entry_id})
    
    @property
    def mood_emoji(self):
        """Get emoji representation of mood"""
        mood_emojis = {1: '😞', 2: '😕', 3: '😐', 4: '😊', 5: '😄'}
        return mood_emojis.get(self.mood_rating, '😐')
    
    @property
    def energy_emoji(self):
        """Get emoji representation of energy level"""
        energy_emojis = {1: '🔋', 2: '🔋🔋', 3: '🔋🔋🔋', 4: '🔋🔋🔋🔋', 5: '🔋🔋🔋🔋🔋'}
        return energy_emojis.get(self.energy_level, '🔋🔋🔋')
    
    def mark_as_favorite(self):
        """Mark entry as favorite"""
        self.is_favorite = True
        self.save(update_fields=['is_favorite'])
    
    def archive(self):
        """Archive this entry"""
        self.is_archived = True
        self.save(update_fields=['is_archived'])


class JournalTag(models.Model):
    """Tags for journal entries"""
    
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_tags')
    color_hex = models.CharField(
        max_length=7,
        default='#6b7280',
        help_text="Hex color code for tag display"
    )
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'user']
        indexes = [
            models.Index(fields=['user', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class JournalEntryTag(models.Model):
    """Many-to-many relationship between entries and tags"""
    
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    tag = models.ForeignKey(JournalTag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['entry', 'tag']
        indexes = [
            models.Index(fields=['entry']),
            models.Index(fields=['tag']),
        ]


class JournalAttachment(models.Model):
    """File attachments for journal entries"""
    
    ATTACHMENT_TYPES = [
        ('IMAGE', 'Image'),
        ('DOCUMENT', 'Document'),
        ('AUDIO', 'Audio'),
        ('VIDEO', 'Video'),
        ('OTHER', 'Other'),
    ]
    
    entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(
        upload_to=journal_attachment_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'mp3', 'wav', 'mp4', 'mov']
            )
        ]
    )
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPES)
    description = models.CharField(max_length=500, blank=True, null=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Journal Attachment"
        verbose_name_plural = "Journal Attachments"
    
    def save(self, *args, **kwargs):
        """Override save to set file metadata"""
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
            
            # Determine file type based on extension
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                self.file_type = 'IMAGE'
            elif ext in ['pdf', 'doc', 'docx', 'txt']:
                self.file_type = 'DOCUMENT'
            elif ext in ['mp3', 'wav', 'ogg']:
                self.file_type = 'AUDIO'
            elif ext in ['mp4', 'mov', 'avi']:
                self.file_type = 'VIDEO'
            else:
                self.file_type = 'OTHER'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()})"


class JournalStreak(models.Model):
    """Track user's journaling streaks"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='journal_streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_entries = models.PositiveIntegerField(default=0)
    last_entry_date = models.DateField(null=True, blank=True)
    
    # Milestone tracking
    milestones_achieved = models.JSONField(
        default=list,
        help_text="List of achieved milestones"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Journal Streak"
        verbose_name_plural = "Journal Streaks"
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} day streak"
    
    def update_streak(self, entry_date):
        """Update streak based on new entry"""
        from datetime import timedelta
        
        if not self.last_entry_date:
            # First entry
            self.current_streak = 1
            self.longest_streak = 1
        else:
            # Check if entry is consecutive
            expected_date = self.last_entry_date + timedelta(days=1)
            
            if entry_date == expected_date:
                # Consecutive day
                self.current_streak += 1
                self.longest_streak = max(self.longest_streak, self.current_streak)
            elif entry_date == self.last_entry_date:
                # Same day, don't update streak
                pass
            else:
                # Streak broken
                self.current_streak = 1
        
        self.last_entry_date = entry_date
        self.total_entries += 1
        
        # Check for milestones
        self.check_milestones()
        
        self.save()
    
    def check_milestones(self):
        """Check and add new milestones"""
        milestones = [
            (1, "First Entry"),
            (7, "One Week Streak"),
            (30, "One Month Streak"),
            (100, "100 Entries"),
            (365, "One Year Streak"),
        ]
        
        for threshold, milestone in milestones:
            if (self.current_streak >= threshold or self.total_entries >= threshold) and milestone not in self.milestones_achieved:
                self.milestones_achieved.append({
                    'milestone': milestone,
                    'achieved_at': timezone.now().isoformat(),
                    'value': max(self.current_streak, self.total_entries)
                })


class JournalInsight(models.Model):
    """AI-generated insights about user's journaling patterns"""
    
    INSIGHT_TYPES = [
        ('MOOD_PATTERN', 'Mood Pattern'),
        ('WORD_FREQUENCY', 'Word Frequency'),
        ('TOPIC_ANALYSIS', 'Topic Analysis'),
        ('SENTIMENT_TREND', 'Sentiment Trend'),
        ('WRITING_STYLE', 'Writing Style'),
        ('TIME_PATTERN', 'Time Pattern'),
        ('CATEGORY_ANALYSIS', 'Category Analysis'),
        ('GOAL_PROGRESS', 'Goal Progress'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Insight data
    insight_data = models.JSONField(
        default=dict,
        help_text="Structured data for the insight"
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI confidence score for this insight"
    )
    
    # Date range for analysis
    analysis_start_date = models.DateField()
    analysis_end_date = models.DateField()
    entries_analyzed = models.PositiveIntegerField(default=0)
    
    # User interaction
    is_acknowledged = models.BooleanField(default=False)
    is_helpful = models.BooleanField(null=True, blank=True)
    user_feedback = models.TextField(blank=True, null=True)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = "Journal Insight"
        verbose_name_plural = "Journal Insights"
        indexes = [
            models.Index(fields=['user', 'insight_type']),
            models.Index(fields=['user', 'generated_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    def mark_as_acknowledged(self):
        """Mark insight as acknowledged"""
        self.is_acknowledged = True
        self.save(update_fields=['is_acknowledged'])


class JournalReminder(models.Model):
    """Reminders for journaling"""
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('CUSTOM', 'Custom'),
    ]
    
    REMINDER_TYPES = [
        ('GENERAL', 'General Journaling'),
        ('GRATITUDE', 'Gratitude Practice'),
        ('REFLECTION', 'Daily Reflection'),
        ('GOAL_CHECK', 'Goal Check-in'),
        ('MOOD_CHECK', 'Mood Check'),
        ('CUSTOM', 'Custom Reminder'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_reminders')
    title = models.CharField(max_length=150)
    message = models.TextField(help_text="Reminder message to show user")
    reminder_type = models.CharField(max_length=15, choices=REMINDER_TYPES)
    
    # Timing
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    reminder_time = models.TimeField(help_text="Time of day to send reminder")
    days_of_week = models.JSONField(
        default=list,
        help_text="Days of week for weekly reminders (0=Monday, 6=Sunday)"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    next_reminder = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['reminder_time']
        verbose_name = "Journal Reminder"
        verbose_name_plural = "Journal Reminders"
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['next_reminder']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"


# Add the many-to-many relationship to JournalEntry
JournalEntry.add_to_class(
    'tags',
    models.ManyToManyField(
        JournalTag,
        through=JournalEntryTag,
        related_name='entries',
        blank=True
    )
)
