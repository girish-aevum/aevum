from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from .workflow_models import Workflow, WorkflowType, WorkflowState
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)


class Thread(models.Model):
    """Chat thread - like ChatGPT conversations"""
    
    CATEGORY_CHOICES = [
        ('MENTAL_HEALTH', 'Mental Health & Wellness'),
        ('NUTRITION', 'Nutrition & Diet'),
    ]
    
    # Thread identification
    thread_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_threads')
    
    # Thread metadata
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Auto-generated thread title from first message"
    )
    
    # Thread organization
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='MENTAL_HEALTH',
        help_text="Thread category for better organization"
    )
    is_favorite = models.BooleanField(
        default=False,
        help_text="User marked this thread as favorite"
    )
    is_archived = models.BooleanField(
        default=False,
        help_text="Thread is archived (hidden from main list)"
    )
    
    # Thread analytics
    last_activity_at = models.DateTimeField(
        auto_now=True,
        help_text="Last time a message was sent in this thread"
    )
    total_ai_tokens_used = models.PositiveIntegerField(
        default=0,
        help_text="Total tokens used by AI in this thread"
    )
    average_response_time_ms = models.FloatField(
        null=True, 
        blank=True,
        help_text="Average AI response time in milliseconds"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_favorite', '-last_activity_at']
        verbose_name = "Chat Thread"
        verbose_name_plural = "Chat Threads"
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'is_favorite']),
            models.Index(fields=['user', 'is_archived']),
            models.Index(fields=['last_activity_at']),
        ]
    
    def __str__(self):
        return self.title or f"Thread {str(self.thread_id)[:8]}..."
    
    @property
    def message_count(self):
        """Get number of user messages in this thread (excludes AI responses)"""
        return self.messages.filter(sender='USER').count()
    
    @property
    def last_message(self):
        """Get the last message in this thread"""
        return self.messages.last()
    
    @property
    def total_messages(self):
        """Get total number of messages (user + AI)"""
        return self.messages.count()
    
    def generate_title_from_first_message(self):
        """Generate thread title from first user message"""
        first_user_message = self.messages.filter(sender='USER').first()
        if first_user_message and not self.title:
            # Take first 50 characters of the message as title
            content = first_user_message.content.strip()
            self.title = content[:50] + "..." if len(content) > 50 else content
            self.save(update_fields=['title'])
    
    def update_analytics(self, tokens_used=0, response_time_ms=None):
        """Update thread analytics"""
        if tokens_used > 0:
            self.total_ai_tokens_used += tokens_used
        
        if response_time_ms is not None:
            # Calculate running average of response time
            ai_messages = self.messages.filter(
                sender='AI', 
                processing_time_ms__isnull=False
            )
            if ai_messages.exists():
                total_time = sum(msg.processing_time_ms for msg in ai_messages)
                self.average_response_time_ms = total_time / ai_messages.count()
        
        self.save(update_fields=['total_ai_tokens_used', 'average_response_time_ms'])
    
    def mark_as_favorite(self):
        """Mark thread as favorite"""
        self.is_favorite = True
        self.save(update_fields=['is_favorite'])
    
    def unmark_as_favorite(self):
        """Remove favorite status"""
        self.is_favorite = False
        self.save(update_fields=['is_favorite'])
    
    def archive(self):
        """Archive this thread"""
        self.is_archived = True
        self.save(update_fields=['is_archived'])
    
    def unarchive(self):
        """Unarchive this thread"""
        self.is_archived = False
        self.save(update_fields=['is_archived'])


def fallback_summarize(text, max_length=100, min_length=20):
    """
    Fallback summarization method using local transformers pipeline
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum summary length
        min_length (int): Minimum summary length
    
    Returns:
        dict: Summarization result
    """
    try:
        # Use the same summarizer as in views
        local_summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        
        # Perform summarization
        result = local_summarizer(
            text, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False
        )
        
        return {
            "text": result[0]["summary_text"],
            "original_length": len(text.split()),
            "summary_length": len(result[0]["summary_text"].split()),
            "compression_ratio": len(result[0]["summary_text"].split()) / len(text.split()),
            "status": "success"
        }
    except Exception as e:
        logger.warning(f"Fallback summarization failed: {str(e)}")
        return {
            "error": str(e),
            "status": "error"
        }

class Message(models.Model):
    """Individual messages within a thread"""
    
    SENDER_CHOICES = [
        ('USER', 'User'),
        ('AI', 'Aevum AI'),
    ]
    
    QA_STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
        ('REJECTED', 'Rejected'),
        ('SKIPPED', 'Skipped'),
    ]
    
    # Message identification
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    
    # Message content
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField(help_text="The message content")
    
    # Add summary field
    summary = models.TextField(
        blank=True, 
        null=True, 
        help_text="Concise summary of the AI response"
    )
    
    # Message reactions and feedback (for AI messages)
    is_helpful = models.BooleanField(
        null=True, 
        blank=True,
        help_text="User feedback: was this AI response helpful? (👍/👎)"
    )
    user_feedback = models.TextField(
        blank=True, 
        null=True,
        help_text="Optional user comment about this message"
    )
    
    # QA Testing Fields (Optional - for random message testing)
    is_selected_for_qa = models.BooleanField(
        default=False,
        help_text="Message randomly selected for QA testing"
    )
    qa_score = models.FloatField(
        null=True,
        blank=True,
        help_text="QA score (0.0 to 10.0) - quality assessment by QA team"
    )
    qa_status = models.CharField(
        max_length=20,
        choices=QA_STATUS_CHOICES,
        null=True,
        blank=True,
        help_text="QA review status"
    )
    qa_feedback = models.TextField(
        blank=True,
        null=True,
        help_text="QA team feedback and notes"
    )
    qa_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qa_reviewed_messages',
        help_text="QA team member who reviewed this message"
    )
    qa_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the QA review was completed"
    )
    qa_tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Comma-separated tags for QA categorization (e.g., 'accuracy,tone,helpfulness')"
    )
    
    # AI response quality tracking (for AI messages only)
    confidence_score = models.FloatField(
        null=True, 
        blank=True,
        help_text="AI confidence score (0.0 to 1.0)"
    )
    processing_time_ms = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Time taken to generate AI response in milliseconds"
    )
    token_count = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Number of tokens used for AI response"
    )
    
    # Response summarization tracking (for AI messages only)
    original_word_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Word count of original AI response before summarization"
    )
    was_summarized = models.BooleanField(
        default=False,
        help_text="Whether this response was summarized before being sent to user"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        indexes = [
            models.Index(fields=['thread', 'sender']),
            models.Index(fields=['thread', 'created_at']),
            models.Index(fields=['is_helpful']),
            models.Index(fields=['is_selected_for_qa']),
            models.Index(fields=['qa_status']),
            models.Index(fields=['qa_score']),
        ]
    
    def __str__(self):
        return f"{self.get_sender_display()}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate summary if not provided
        """
        # If no summary is provided, generate one automatically
        if not self.summary and self.content:
            try:
                # Try to use the dynamic service first
                try:
                    # Lazy import to avoid circular dependency
                    from .views import call_summarization_service
                    from django.urls import reverse
                    from django.test import RequestFactory
                    
                    request = RequestFactory().get(reverse('ai_companion:chat'))
                    summary_result = call_summarization_service(
                        self.content, 
                        max_length=100, 
                        min_length=20,
                        request=request
                    )
                except Exception:
                    # Fallback to local summarization if no request context
                    summary_result = fallback_summarize(
                        self.content, 
                        max_length=100, 
                        min_length=20
                    )
                
                # Check if summary was successfully generated
                if summary_result.get('status') == 'success':
                    self.summary = summary_result.get('text', '')
            except Exception as e:
                # Log the error but don't prevent saving
                logger.warning(f"Could not generate summary: {str(e)}")
        
        super().save(*args, **kwargs)
        # Update thread's updated_at timestamp
        self.thread.save(update_fields=['updated_at'])
        # Generate thread title if it's the first user message
        if self.sender == 'USER':
            self.thread.generate_title_from_first_message()
    
    def mark_as_helpful(self, feedback_comment=None):
        """Mark AI message as helpful"""
        self.is_helpful = True
        if feedback_comment:
            self.user_feedback = feedback_comment
        self.save(update_fields=['is_helpful', 'user_feedback'])
    
    def mark_as_unhelpful(self, feedback_comment=None):
        """Mark AI message as unhelpful"""
        self.is_helpful = False
        if feedback_comment:
            self.user_feedback = feedback_comment
        self.save(update_fields=['is_helpful', 'user_feedback'])
    
    # QA Testing Methods
    def select_for_qa(self):
        """Mark message for QA testing"""
        self.is_selected_for_qa = True
        self.qa_status = 'PENDING'
        self.save(update_fields=['is_selected_for_qa', 'qa_status'])
    
    def complete_qa_review(self, score, status, feedback=None, reviewer=None, tags=None):
        """Complete QA review for this message"""
        self.qa_score = score
        self.qa_status = status
        self.qa_reviewed_at = timezone.now()
        
        if feedback:
            self.qa_feedback = feedback
        if reviewer:
            self.qa_reviewer = reviewer
        if tags:
            self.qa_tags = tags
            
        self.save(update_fields=[
            'qa_score', 'qa_status', 'qa_reviewed_at', 
            'qa_feedback', 'qa_reviewer', 'qa_tags'
        ])
    
    @property
    def qa_score_grade(self):
        """Get letter grade based on QA score"""
        if self.qa_score is None:
            return None
        
        if self.qa_score >= 9.0:
            return 'A+'
        elif self.qa_score >= 8.0:
            return 'A'
        elif self.qa_score >= 7.0:
            return 'B'
        elif self.qa_score >= 6.0:
            return 'C'
        elif self.qa_score >= 5.0:
            return 'D'
        else:
            return 'F'
    
    @classmethod
    def get_random_messages_for_qa(cls, count=10, sender='AI'):
        """Get random messages for QA testing"""
        return cls.objects.filter(
            sender=sender,
            is_selected_for_qa=False
        ).order_by('?')[:count]


class ThreadSuggestion(models.Model):
    """Smart suggestions for new threads based on user patterns"""
    
    SUGGESTION_TYPES = [
        ('TOPIC', 'Topic Suggestion'),
        ('FOLLOW_UP', 'Follow-up Question'),
        ('RELATED', 'Related Discussion'),
        ('WELLNESS_CHECK', 'Wellness Check-in'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_suggestions')
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES)
    
    # Suggestion content
    title = models.CharField(max_length=200, help_text="Suggested thread title")
    description = models.TextField(help_text="Why this suggestion is relevant")
    suggested_category = models.CharField(
        max_length=20, 
        choices=Thread.CATEGORY_CHOICES,
        help_text="Suggested category for the new thread"
    )
    suggested_first_message = models.TextField(
        blank=True,
        null=True,
        help_text="Optional suggested first message to start the conversation"
    )
    
    # Suggestion metadata
    relevance_score = models.FloatField(
        default=0.5,
        help_text="AI-calculated relevance score (0.0 to 1.0)"
    )
    based_on_thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='generated_suggestions',
        help_text="Thread that inspired this suggestion"
    )
    
    # User interaction
    is_dismissed = models.BooleanField(
        default=False,
        help_text="User dismissed this suggestion"
    )
    is_used = models.BooleanField(
        default=False,
        help_text="User created a thread based on this suggestion"
    )
    created_thread = models.ForeignKey(
        Thread,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_from_suggestion',
        help_text="Thread created from this suggestion"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-relevance_score', '-created_at']
        verbose_name = "Thread Suggestion"
        verbose_name_plural = "Thread Suggestions"
        indexes = [
            models.Index(fields=['user', 'is_dismissed', 'is_used']),
            models.Index(fields=['relevance_score']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    def dismiss(self):
        """Mark suggestion as dismissed"""
        self.is_dismissed = True
        self.dismissed_at = timezone.now()
        self.save(update_fields=['is_dismissed', 'dismissed_at'])
    
    def mark_as_used(self, created_thread):
        """Mark suggestion as used and link to created thread"""
        self.is_used = True
        self.used_at = timezone.now()
        self.created_thread = created_thread
        self.save(update_fields=['is_used', 'used_at', 'created_thread'])
