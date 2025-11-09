import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import JSONField  # Use Django's built-in JSONField

class WorkflowType(models.TextChoices):
    """Predefined workflow types"""
    MENTAL_HEALTH = 'MENTAL_HEALTH', 'Mental Health Coaching'
    NUTRITION = 'NUTRITION', 'Nutrition Guidance'
    FITNESS = 'FITNESS', 'Fitness Tracking'
    THERAPY = 'THERAPY', 'Personal Therapy'
    GENERAL = 'GENERAL', 'General Conversation'

class WorkflowState(models.TextChoices):
    """Standard workflow states"""
    INITIALIZED = 'INITIALIZED', 'Workflow Started'
    IN_PROGRESS = 'IN_PROGRESS', 'Ongoing Interaction'
    NEEDS_REVIEW = 'NEEDS_REVIEW', 'Requires Human Review'
    COMPLETED = 'COMPLETED', 'Workflow Finished'
    PAUSED = 'PAUSED', 'Temporarily Suspended'

class Workflow(models.Model):
    """
    Represents a complex, multi-step interaction workflow
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User and Thread Association
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    thread = models.ForeignKey('Thread', on_delete=models.SET_NULL, null=True, related_name='workflows')
    
    # Workflow Metadata
    type = models.CharField(
        max_length=20, 
        choices=WorkflowType.choices, 
        default=WorkflowType.GENERAL
    )
    
    state = models.CharField(
        max_length=20, 
        choices=WorkflowState.choices, 
        default=WorkflowState.INITIALIZED
    )
    
    # Contextual Information
    context = JSONField(default=dict)
    
    # Tracking and Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Workflow Progress
    current_step = models.IntegerField(default=0)
    total_steps = models.IntegerField(default=0)
    
    # Metadata and Insights
    insights = JSONField(default=dict)
    
    def update_context(self, new_context):
        """Merge new context with existing"""
        current_context = self.context or {}
        current_context.update(new_context)
        self.context = current_context
        self.save(update_fields=['context'])
    
    def advance_step(self):
        """Progress to next workflow step"""
        self.current_step += 1
        if self.current_step >= self.total_steps:
            self.state = WorkflowState.COMPLETED
        self.save()
    
    def add_insight(self, key, value):
        """Add an insight to the workflow"""
        current_insights = self.insights or {}
        current_insights[key] = value
        self.insights = current_insights
        self.save(update_fields=['insights'])
    
    def __str__(self):
        return f"{self.type} Workflow for {self.user.username}"

class WorkflowStep(models.Model):
    """
    Detailed record of each step in a workflow
    """
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='steps')
    
    # Step Identification
    step_number = models.IntegerField()
    
    # Interaction Details
    user_input = models.TextField()
    ai_response = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional Scoring/Feedback
    relevance_score = models.FloatField(null=True, blank=True)
    feedback = JSONField(default=dict)
    
    def record_feedback(self, feedback_data):
        """Record step-specific feedback"""
        current_feedback = self.feedback or {}
        current_feedback.update(feedback_data)
        self.feedback = current_feedback
        self.save(update_fields=['feedback'])
    
    def __str__(self):
        return f"Step {self.step_number} of {self.workflow}"

class WorkflowTemplate(models.Model):
    """
    Predefined workflow templates for different interaction types
    """
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20, 
        choices=WorkflowType.choices
    )
    
    # Template Configuration
    steps_config = JSONField()
    
    # Metadata
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name 