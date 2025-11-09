from django.apps import apps

def get_model(model_name):
    """
    Safely get a model from the ai_companion app
    
    Args:
        model_name (str): Name of the model to retrieve
    
    Returns:
        Model class
    """
    return apps.get_model('ai_companion', model_name)

from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone

# Now import or define models using get_model
Thread = get_model('Thread')
Message = get_model('Message')
ThreadSuggestion = get_model('ThreadSuggestion')


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    sender_display = serializers.CharField(source='get_sender_display', read_only=True)
    time_ago = serializers.SerializerMethodField()
    can_react = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_display',
            'content',
            'is_helpful',
            'user_feedback',
            'confidence_score',
            'processing_time_ms',
            'token_count',
            'can_react',
            'time_ago',
            'created_at'
        ]
        read_only_fields = ['message_id', 'created_at', 'confidence_score', 'processing_time_ms', 'token_count']
    
    def get_time_ago(self, obj):
        """Calculate time since message was created"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def get_can_react(self, obj):
        """Check if user can react to this message (only AI messages)"""
        return obj.sender == 'AI'


class ThreadListSerializer(serializers.ModelSerializer):
    """Serializer for thread list view"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    message_count = serializers.ReadOnlyField()
    total_messages = serializers.ReadOnlyField()
    last_message = MessageSerializer(read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Thread
        fields = [
            'thread_id',
            'title',
            'category',
            'category_display',
            'is_favorite',
            'is_archived',
            'message_count',
            'total_messages',
            'last_message',
            'time_ago',
            'last_activity_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['thread_id', 'created_at', 'updated_at', 'last_activity_at']
    
    def get_time_ago(self, obj):
        """Calculate time since thread was last updated"""
        now = timezone.now()
        diff = now - obj.last_activity_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"


class ThreadDetailSerializer(serializers.ModelSerializer):
    """Serializer for thread detail view with messages"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.ReadOnlyField()
    total_messages = serializers.ReadOnlyField()
    
    class Meta:
        model = Thread
        fields = [
            'thread_id',
            'title',
            'category',
            'category_display',
            'is_favorite',
            'is_archived',
            'message_count',
            'total_messages',
            'total_ai_tokens_used',
            'average_response_time_ms',
            'messages',
            'last_activity_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'thread_id', 'created_at', 'updated_at', 'last_activity_at',
            'total_ai_tokens_used', 'average_response_time_ms'
        ]


class ThreadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new threads"""
    
    thread_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Thread
        fields = ['thread_id', 'title', 'category']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat message requests"""
    
    thread_id = serializers.UUIDField()
    message = serializers.CharField(max_length=2000)
    
    def validate_message(self, value):
        """Validate message content"""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    
    thread_id = serializers.UUIDField()
    user_message = MessageSerializer()
    ai_response = MessageSerializer()
    thread_title = serializers.CharField()
    
    class Meta:
        fields = [
            'thread_id', 'user_message', 'ai_response', 'thread_title'
        ]


class MessageReactionSerializer(serializers.Serializer):
    """Serializer for message reactions"""
    
    message_id = serializers.UUIDField()
    is_helpful = serializers.BooleanField()
    feedback_comment = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_message_id(self, value):
        """Validate that message exists and belongs to user's thread"""
        try:
            message = Message.objects.get(message_id=value)
            # Check if message belongs to user's thread
            if message.thread.user != self.context['request'].user:
                raise serializers.ValidationError("Message not found")
            # Check if it's an AI message (only AI messages can be rated)
            if message.sender != 'AI':
                raise serializers.ValidationError("Can only react to AI messages")
            return value
        except Message.DoesNotExist:
            raise serializers.ValidationError("Message not found")


class ThreadSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for thread suggestions"""
    
    suggestion_type_display = serializers.CharField(source='get_suggestion_type_display', read_only=True)
    category_display = serializers.CharField(source='get_suggested_category_display', read_only=True)
    based_on_thread_title = serializers.CharField(source='based_on_thread.title', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = ThreadSuggestion
        fields = [
            'id',
            'suggestion_type',
            'suggestion_type_display',
            'title',
            'description',
            'suggested_category',
            'category_display',
            'suggested_first_message',
            'relevance_score',
            'based_on_thread_title',
            'is_dismissed',
            'is_used',
            'time_ago',
            'created_at'
        ]
        read_only_fields = [
            'id', 'relevance_score', 'is_dismissed', 'is_used', 'created_at'
        ]
    
    def get_time_ago(self, obj):
        """Calculate time since suggestion was created"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            return "Recently"


class SuggestionActionSerializer(serializers.Serializer):
    """Serializer for suggestion actions (dismiss/use)"""
    
    suggestion_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['dismiss', 'use'])
    thread_title = serializers.CharField(max_length=200, required=False)  # For 'use' action
    
    def validate_suggestion_id(self, value):
        """Validate that suggestion exists and belongs to user"""
        try:
            suggestion = ThreadSuggestion.objects.get(id=value)
            if suggestion.user != self.context['request'].user:
                raise serializers.ValidationError("Suggestion not found")
            if suggestion.is_dismissed or suggestion.is_used:
                raise serializers.ValidationError("Suggestion already processed")
            return value
        except ThreadSuggestion.DoesNotExist:
            raise serializers.ValidationError("Suggestion not found")
    
    def validate(self, data):
        """Validate that thread_title is provided for 'use' action"""
        if data['action'] == 'use' and not data.get('thread_title'):
            raise serializers.ValidationError("thread_title is required for 'use' action")
        return data


class UserFeedbackSerializer(serializers.Serializer):
    """Enhanced serializer for user feedback on AI messages"""
    
    message_id = serializers.UUIDField()
    is_helpful = serializers.BooleanField()
    feedback_comment = serializers.CharField(
        max_length=1000, 
        required=False, 
        allow_blank=True,
        help_text="Optional detailed feedback about the AI response"
    )
    
    def validate_message_id(self, value):
        """Validate that message exists and belongs to user's thread"""
        try:
            message = Message.objects.get(message_id=value)
            # Check if message belongs to user's thread
            if message.thread.user != self.context['request'].user:
                raise serializers.ValidationError("Message not found or access denied")
            # Check if it's an AI message (only AI messages can be rated)
            if message.sender != 'AI':
                raise serializers.ValidationError("Can only provide feedback on AI messages")
            return value
        except Message.DoesNotExist:
            raise serializers.ValidationError("Message not found")


class QAFeedbackSerializer(serializers.Serializer):
    """Serializer for QA team feedback on messages"""
    
    message_id = serializers.UUIDField()
    qa_score = serializers.FloatField(
        min_value=0.0, 
        max_value=10.0,
        help_text="QA score from 0.0 to 10.0"
    )
    qa_status = serializers.ChoiceField(
        choices=Message.QA_STATUS_CHOICES,
        help_text="QA review status"
    )
    qa_feedback = serializers.CharField(
        max_length=2000, 
        required=False, 
        allow_blank=True,
        help_text="Detailed QA feedback and notes"
    )
    qa_tags = serializers.CharField(
        max_length=500, 
        required=False, 
        allow_blank=True,
        help_text="Comma-separated tags (e.g., 'accuracy,tone,helpfulness')"
    )
    
    def validate_message_id(self, value):
        """Validate that message exists and is selected for QA"""
        try:
            message = Message.objects.get(message_id=value)
            # Check if message is selected for QA
            if not message.is_selected_for_qa:
                raise serializers.ValidationError("Message is not selected for QA testing")
            return value
        except Message.DoesNotExist:
            raise serializers.ValidationError("Message not found")
    
    def validate(self, data):
        """Additional validation for QA feedback"""
        # Ensure QA feedback is provided for certain statuses
        if data['qa_status'] in ['NEEDS_IMPROVEMENT', 'REJECTED'] and not data.get('qa_feedback'):
            raise serializers.ValidationError(
                "QA feedback is required when status is 'NEEDS_IMPROVEMENT' or 'REJECTED'"
            )
        return data


class MessageWithQASerializer(serializers.ModelSerializer):
    """Serializer for messages with QA information (for QA team)"""
    
    sender_display = serializers.CharField(source='get_sender_display', read_only=True)
    qa_status_display = serializers.CharField(source='get_qa_status_display', read_only=True)
    qa_score_grade = serializers.CharField(read_only=True)
    qa_reviewer_username = serializers.CharField(source='qa_reviewer.username', read_only=True)
    thread_title = serializers.CharField(source='thread.title', read_only=True)
    thread_user = serializers.CharField(source='thread.user.username', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'thread_title',
            'thread_user',
            'sender',
            'sender_display',
            'content',
            'created_at',
            # User feedback
            'is_helpful',
            'user_feedback',
            # QA fields
            'is_selected_for_qa',
            'qa_score',
            'qa_score_grade',
            'qa_status',
            'qa_status_display',
            'qa_feedback',
            'qa_reviewer_username',
            'qa_reviewed_at',
            'qa_tags',
            # AI quality metrics
            'confidence_score',
            'processing_time_ms',
            'token_count'
        ]
        read_only_fields = [
            'message_id', 'created_at', 'confidence_score', 
            'processing_time_ms', 'token_count', 'qa_reviewed_at'
        ]


class QAStatsSerializer(serializers.Serializer):
    """Serializer for QA statistics response"""
    
    class OverviewSerializer(serializers.Serializer):
        total_messages = serializers.IntegerField()
        ai_messages = serializers.IntegerField()
        selected_for_qa = serializers.IntegerField()
        qa_reviewed = serializers.IntegerField()
        qa_coverage_percentage = serializers.FloatField()
        review_completion_rate = serializers.FloatField()
    
    class StatusBreakdownSerializer(serializers.Serializer):
        name = serializers.CharField()
        count = serializers.IntegerField()
    
    class ScoreStatsSerializer(serializers.Serializer):
        average = serializers.FloatField()
        min = serializers.FloatField()
        max = serializers.FloatField()
        count = serializers.IntegerField()
        grade_distribution = serializers.DictField()
    
    class ReviewerStatsSerializer(serializers.Serializer):
        reviews_completed = serializers.IntegerField()
        average_score_given = serializers.FloatField()
    
    class RecentActivitySerializer(serializers.Serializer):
        message_id = serializers.UUIDField()
        score = serializers.FloatField()
        grade = serializers.CharField()
        status = serializers.CharField()
        reviewer = serializers.CharField(allow_null=True)
        reviewed_at = serializers.DateTimeField()
        content_preview = serializers.CharField()
    
    overview = OverviewSerializer()
    status_breakdown = serializers.DictField(child=StatusBreakdownSerializer())
    score_statistics = ScoreStatsSerializer()
    reviewer_statistics = serializers.DictField(child=ReviewerStatsSerializer())
    recent_activity = RecentActivitySerializer(many=True)
    pending_reviews = serializers.IntegerField() 