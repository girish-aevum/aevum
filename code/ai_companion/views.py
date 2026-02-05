from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
import logging
import time
from django.db import models as django_models
from django.apps import apps
from django.conf import settings
from transformers import pipeline
import requests
from django.urls import reverse
import json

# Create a logger specifically for ai_companion
logger = logging.getLogger('ai_companion')

def get_model(model_name):
    """
    Safely get a model from the ai_companion app
    
    Args:
        model_name (str): Name of the model to retrieve
    
    Returns:
        Model class
    """
    return apps.get_model('ai_companion', model_name)

# Instead, use the get_model function to dynamically import models
Thread = get_model('Thread')
Message = get_model('Message')
ThreadSuggestion = get_model('ThreadSuggestion')

from .serializers import (
    ThreadListSerializer,
    ThreadDetailSerializer,
    ThreadCreateSerializer,
    MessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
    MessageReactionSerializer,
    ThreadSuggestionSerializer,
    SuggestionActionSerializer,
    UserFeedbackSerializer,
    QAFeedbackSerializer,
    MessageWithQASerializer
)
from .groq_client import GroqClient
from .workflow_service import WorkflowService, WorkflowType
from .rag_service import get_rag_service

# Initialize logger and Groq client
groq_client = GroqClient()


# Replace direct model imports with this method in the file
# For example, instead of:
# from .models import Thread, Message, ThreadSuggestion
# You would use:
# Thread = get_model('Thread')
# Message = get_model('Message')
# ThreadSuggestion = get_model('ThreadSuggestion')


@extend_schema(tags=['AI Companion'])
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Health check endpoint for AI Companion service"""
    return Response({
        "status": "ok", 
        "app": "ai_companion",
        "groq_configured": bool(groq_client.api_key)
    })


@extend_schema_view(
    get=extend_schema(
        tags=['AI Companion'],
        summary="List User's Chat Threads",
        description="Get all chat threads for the authenticated user with filtering options"
    ),
    post=extend_schema(
        tags=['AI Companion'],
        summary="Create New Chat Thread",
        description="Create a new chat thread with optional category"
    )
)
class ThreadListView(generics.ListCreateAPIView):
    """List and create chat threads with filtering"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_favorite', 'is_archived']
    search_fields = ['title']
    ordering_fields = ['created_at', 'last_activity_at', 'message_count']
    ordering = ['-is_favorite', '-last_activity_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ThreadCreateSerializer
        return ThreadListSerializer
    
    def get_queryset(self):
        return Thread.objects.filter(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        tags=['AI Companion'],
        summary="Get Chat Thread Details",
        description="Get detailed information about a chat thread including all messages"
    ),
    put=extend_schema(
        tags=['AI Companion'],
        summary="Update Chat Thread",
        description="Update thread title, category, or other properties"
    ),
    patch=extend_schema(
        tags=['AI Companion'],
        summary="Update Chat Thread",
        description="Partially update thread title, category, or other properties"
    ),
    delete=extend_schema(
        tags=['AI Companion'],
        summary="Delete Chat Thread",
        description="Delete a chat thread and all its messages"
    )
)
class ThreadDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific thread"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadDetailSerializer
    lookup_field = 'thread_id'
    
    def get_queryset(self):
        return Thread.objects.filter(user=self.request.user)

    
@extend_schema(
    tags=['AI Companion'],
    description="Enhanced chat endpoint supporting workflow-based interactions",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'thread_id': {
                    'type': 'string', 
                    'format': 'uuid',
                    'description': 'Unique identifier of the thread',
                    'example': '550e8400-e29b-41d4-a716-446655440000'
                },
                'message': {
                    'type': 'string', 
                    'description': 'User\'s message content',
                    'example': 'Tell me about managing stress effectively'
                },
                'workflow_type': {
                    'type': 'string', 
                    'description': 'Type of workflow for the conversation',
                    'enum': ['GENERAL', 'MENTAL_HEALTH', 'NUTRITION', 'FITNESS', 'THERAPY'],
                    'default': 'GENERAL',
                    'example': 'MENTAL_HEALTH'
                },
                'workflow_id': {
                    'type': 'string', 
                    'format': 'uuid',
                    'description': 'Optional existing workflow identifier',
                    'example': '550e8400-e29b-41d4-a716-446655440001'
                }
            },
            'required': ['thread_id', 'message']
        }
    },
    responses={
        status.HTTP_200_OK: {
            'type': 'object',
            'properties': {
                'thread_id': {'type': 'string', 'format': 'uuid', 'description': 'Thread identifier'},
                'workflow_id': {'type': 'string', 'format': 'uuid', 'description': 'Workflow identifier'},
                'workflow_type': {'type': 'string', 'description': 'Type of workflow used'},
                'workflow_stage': {'type': 'string', 'description': 'Current stage of the workflow'},
                'user_message': {
                    'type': 'object', 
                    'description': 'Details of the user\'s message',
                    'properties': {
                        'content': {'type': 'string'},
                        'sender': {'type': 'string', 'enum': ['USER']},
                        'created_at': {'type': 'string', 'format': 'date-time'}
                    }
                },
                'ai_response': {
                    'type': 'object', 
                    'description': 'Details of the AI\'s response',
                    'properties': {
                        'content': {'type': 'string'},
                        'sender': {'type': 'string', 'enum': ['AI']},
                        'created_at': {'type': 'string', 'format': 'date-time'}
                    }
                },
                'ai_summary': {
                    'type': 'string', 
                    'description': 'Optional summary of the AI response',
                    'nullable': True
                },
                'thread_title': {'type': 'string', 'description': 'Title of the thread'}
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Bad request, e.g., missing required fields',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'},
                            'details': {'type': 'object'}
                        }
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'description': 'Internal server error',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            'Mental Health Workflow Chat',
            value={
                'thread_id': '550e8400-e29b-41d4-a716-446655440000',
                'message': 'I\'m feeling stressed lately. Can you help me?',
                'workflow_type': 'MENTAL_HEALTH'
            },
            status_codes=[status.HTTP_200_OK]
        ),
        OpenApiExample(
            'General Conversation',
            value={
                'thread_id': '550e8400-e29b-41d4-a716-446655440001',
                'message': 'What are some interesting facts about space?',
                'workflow_type': 'GENERAL'
            },
            status_codes=[status.HTTP_200_OK]
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Enhanced chat endpoint supporting workflow-based interactions
    
    Request can include:
    - thread_id (required)
    - message (required)
    - workflow_type (optional)
    - workflow_id (optional)
    """
    
    # Validate request
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract data
    thread_id = serializer.validated_data['thread_id']
    user_message_content = serializer.validated_data['message']
    workflow_type = request.data.get('workflow_type', WorkflowType.GENERAL)
    workflow_id = request.data.get('workflow_id')
    
    # Get the thread
    thread = get_object_or_404(Thread, thread_id=thread_id, user=request.user)
        
    try:
        with transaction.atomic():
            # Create user message
            user_message = Message.objects.create(
            thread=thread,
                sender='USER',
            content=user_message_content
        )
        
            # Workflow Management
            if workflow_id:
                # Retrieve existing workflow
                workflow = Workflow.objects.get(
                    id=workflow_id, 
                    user=request.user
                )
            else:
                # Create new workflow if not exists
                workflow = WorkflowService.create_workflow(
                    user=request.user, 
                    thread=thread, 
                    workflow_type=workflow_type
                )
            
            # Start timing for workflow response
        start_time = time.time()
            
        # Process workflow step
        workflow_result = WorkflowService.process_workflow_step(
            workflow, 
            user_message_content
        )
            
            # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Get AI response (either from workflow or standard method)
        ai_response_content = workflow_result.get('response')
        
        # Fallback to standard AI response if workflow fails
        if not ai_response_content:
            ai_response_content, standard_response_metadata = get_ai_response(thread, user_message_content)
            processing_time_ms = int((time.time() - start_time) * 1000)
            response_metadata = standard_response_metadata
        else:
            # Create a minimal response metadata for workflow responses
            response_metadata = {
                'token_count': len(ai_response_content.split()),
                'confidence_score': 0.7  # Default confidence for workflow responses
            }
            
        # Create AI message
        ai_message = Message.objects.create(
            thread=thread,
                sender='AI',
            content=ai_response_content,
            processing_time_ms=processing_time_ms,
                token_count=response_metadata.get('token_count', 0),
                confidence_score=response_metadata.get('confidence_score', 0.0)
        )
        
        # Update thread analytics
        thread.update_analytics(
            tokens_used=response_metadata.get('token_count', 0),
            response_time_ms=processing_time_ms
        )
        
        # Prepare response
        response_data = {
            'thread_id': thread.thread_id,
                'workflow_id': str(workflow.id),
                'workflow_type': workflow.type,
                'workflow_stage': workflow_result.get('stage', 'default'),
        'user_message': MessageSerializer(user_message).data,
        'ai_response': MessageSerializer(ai_message).data,
                'ai_summary': workflow_result.get('summary', ''),  # Add summary to response
        'thread_title': thread.title or "New Chat"
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in enhanced chat endpoint: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

def get_ai_response(thread, user_message):
    """Get AI response using Groq client with metadata"""
    
    try:
        # Get recent messages for context (last 10 messages)
        recent_messages = thread.messages.order_by('-created_at')[:10]
        
        # Build conversation history for context
        conversation_history = []
        for msg in reversed(recent_messages):
            role = "user" if msg.sender == 'USER' else "assistant"
            conversation_history.append({
                "role": role,
                "content": msg.content
            })
        
        # Add current user message
        conversation_history.append({
            "role": "user", 
            "content": user_message
        })
        
        # Get response from Groq
        original_response = groq_client.get_chat_response(conversation_history)
        
        # Return response with basic metadata
        return original_response, {
            'token_count': len(original_response.split()) * 1.3,
            'confidence_score': 0.85,
            'original_word_count': len(original_response.split()),
            'summarized_word_count': len(original_response.split()),
                'was_summarized': False
            }
        
    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return "I'm sorry, I'm having trouble responding right now. Please try again in a moment.", {
            'token_count': 0,
            'confidence_score': 0.0,
            'original_word_count': 0,
            'summarized_word_count': 0,
            'was_summarized': False
        }


@extend_schema(
    tags=['AI Companion'],
    summary="React to AI Message",
    description="Give feedback on an AI message (👍/👎) with optional comment",
    request=MessageReactionSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def react_to_message(request):
    """React to an AI message with thumbs up/down and optional feedback"""
    
    serializer = MessageReactionSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message_id = serializer.validated_data['message_id']
    is_helpful = serializer.validated_data['is_helpful']
    feedback_comment = serializer.validated_data.get('feedback_comment', '')
    
    try:
        message = Message.objects.get(message_id=message_id)
        
        if is_helpful:
            message.mark_as_helpful(feedback_comment)
        else:
            message.mark_as_unhelpful(feedback_comment)
            
            return Response({
            'message': 'Feedback recorded successfully',
            'message_id': message_id,
            'is_helpful': is_helpful,
            'has_feedback': bool(feedback_comment)
        })
        
    except Message.DoesNotExist:
        return Response(
            {'error': 'Message not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    tags=['AI Companion'],
    summary="Toggle Thread Favorite",
    description="Mark or unmark a thread as favorite"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, thread_id):
    """Toggle thread favorite status"""
    
    thread = get_object_or_404(Thread, thread_id=thread_id, user=request.user)
    
    if thread.is_favorite:
        thread.unmark_as_favorite()
        message = "Thread removed from favorites"
    else:
        thread.mark_as_favorite()
        message = "Thread marked as favorite"
    
    return Response({
        'message': message,
        'is_favorite': thread.is_favorite
    })

    
@extend_schema(
    tags=['AI Companion'],
summary="Toggle Thread Archive",
description="Archive or unarchive a thread"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_archive(request, thread_id):
    """Toggle thread archive status"""
    
    thread = get_object_or_404(Thread, thread_id=thread_id, user=request.user)
    
    if thread.is_archived:
        thread.unarchive()
        message = "Thread unarchived"
    else:
        thread.archive()
        message = "Thread archived"
    
    return Response({
        'message': message,
        'is_archived': thread.is_archived
    })


@extend_schema_view(
    get=extend_schema(
        tags=['AI Companion'],
        summary="Get Thread Suggestions",
        description="Get AI-generated suggestions for new threads based on user patterns"
    )
)
class ThreadSuggestionListView(generics.ListAPIView):
    """List thread suggestions for the user"""
    
    serializer_class = ThreadSuggestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['suggestion_type', 'suggested_category']
    
    def get_queryset(self):
        return ThreadSuggestion.objects.filter(
            user=self.request.user,
            is_dismissed=False,
            is_used=False
        ).order_by('-relevance_score', '-created_at')


@extend_schema(
    tags=['AI Companion'],
    summary="Handle Suggestion Action",
    description="Dismiss a suggestion or use it to create a new thread",
    request=SuggestionActionSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_suggestion(request):
    """Handle suggestion actions (dismiss or use)"""
    
    serializer = SuggestionActionSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    suggestion_id = serializer.validated_data['suggestion_id']
    action = serializer.validated_data['action']
    
    try:
        suggestion = ThreadSuggestion.objects.get(id=suggestion_id)
        
        if action == 'dismiss':
            suggestion.dismiss()
            return Response({
                'message': 'Suggestion dismissed',
                'suggestion_id': suggestion_id
            })
        
        elif action == 'use':
            # Create new thread based on suggestion
            thread_title = serializer.validated_data.get('thread_title', suggestion.title)
            
            thread = Thread.objects.create(
                user=request.user,
                title=thread_title,
                category=suggestion.suggested_category
            )
            
            # Optionally create first message if suggested
            if suggestion.suggested_first_message:
                Message.objects.create(
                    thread=thread,
                    sender='USER',
                    content=suggestion.suggested_first_message
                )
            
            # Mark suggestion as used
            suggestion.mark_as_used(thread)
            
            return Response({
                'message': 'Thread created from suggestion',
                'suggestion_id': suggestion_id,
                'thread_id': thread.thread_id,
                'thread': ThreadDetailSerializer(thread).data
            })
        
    except ThreadSuggestion.DoesNotExist:
        return Response(
            {'error': 'Suggestion not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    
@extend_schema(
    tags=['AI Companion'],
summary="Get AI Companion Statistics",
description="Get comprehensive usage statistics for the AI companion"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats(request):
    """Get user's AI companion usage statistics"""
    
    user_threads = Thread.objects.filter(user=request.user)
    total_messages = Message.objects.filter(thread__user=request.user)
    ai_messages = total_messages.filter(sender='AI')
    
    # Calculate helpfulness stats
    helpful_reactions = ai_messages.filter(is_helpful=True).count()
    unhelpful_reactions = ai_messages.filter(is_helpful=False).count()
    total_reactions = helpful_reactions + unhelpful_reactions
    
    stats_data = {
        'threads': {
            'total': user_threads.count(),
            'favorites': user_threads.filter(is_favorite=True).count(),
            'archived': user_threads.filter(is_archived=True).count(),
            'mental_health': user_threads.filter(category='MENTAL_HEALTH').count(),
            'nutrition': user_threads.filter(category='NUTRITION').count(),
        },
        'messages': {
            'total': total_messages.count(),
            'user_messages': total_messages.filter(sender='USER').count(),
            'ai_messages': ai_messages.count(),
        },
        'ai_quality': {
            'helpful_reactions': helpful_reactions,
            'unhelpful_reactions': unhelpful_reactions,
            'total_reactions': total_reactions,
            'helpfulness_rate': (helpful_reactions / total_reactions * 100) if total_reactions > 0 else 0,
            'average_response_time': user_threads.filter(
                average_response_time_ms__isnull=False
            ).aggregate(avg=django_models.Avg('average_response_time_ms'))['avg'],
        },
        'suggestions': {
            'active': ThreadSuggestion.objects.filter(
                user=request.user, 
                is_dismissed=False, 
                is_used=False
            ).count(),
            'used': ThreadSuggestion.objects.filter(
                user=request.user, 
                is_used=True
            ).count(),
        },
        'recent_threads': ThreadListSerializer(
            user_threads[:5], many=True
        ).data
    }
    
    return Response(stats_data)


@extend_schema(tags=['AI Companion'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def qa_stats(request):
    """Get QA testing statistics (for admin/QA team use)"""
    
    # Check if user has permission to view QA stats (staff only)
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied. Staff access required.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get all messages for QA analysis
    all_messages = Message.objects.all()
    ai_messages = all_messages.filter(sender='AI')
    qa_selected = all_messages.filter(is_selected_for_qa=True)
    qa_reviewed = qa_selected.filter(qa_score__isnull=False)
    
    # Status breakdown
    status_breakdown = {}
    for status_code, status_name in Message.QA_STATUS_CHOICES:
        count = qa_selected.filter(qa_status=status_code).count()
        status_breakdown[status_code.lower()] = {
            'name': status_name,
            'count': count
        }
    
    # Score statistics
    score_stats = {}
    if qa_reviewed.exists():
        scores = [msg.qa_score for msg in qa_reviewed]
        score_stats = {
            'average': sum(scores) / len(scores),
            'min': min(scores),
            'max': max(scores),
            'count': len(scores)
        }
        
        # Grade distribution
        grade_distribution = {}
        for msg in qa_reviewed:
            grade = msg.qa_score_grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        score_stats['grade_distribution'] = grade_distribution
    
    # Reviewer statistics
    reviewer_stats = {}
    if qa_reviewed.exists():
        reviewers = qa_reviewed.values('qa_reviewer__username').annotate(
            count=django_models.Count('id'),
            avg_score=django_models.Avg('qa_score')
        ).filter(qa_reviewer__isnull=False)
        
        for reviewer in reviewers:
            reviewer_stats[reviewer['qa_reviewer__username']] = {
                'reviews_completed': reviewer['count'],
                'average_score_given': reviewer['avg_score']
            }
    
    # Recent QA activity
    recent_reviews = qa_reviewed.filter(
        qa_reviewed_at__isnull=False
    ).order_by('-qa_reviewed_at')[:10]
    
    recent_activity = []
    for review in recent_reviews:
        recent_activity.append({
            'message_id': str(review.message_id),
            'score': review.qa_score,
            'grade': review.qa_score_grade,
            'status': review.qa_status,
            'reviewer': review.qa_reviewer.username if review.qa_reviewer else None,
            'reviewed_at': review.qa_reviewed_at,
            'content_preview': review.content[:50] + "..." if len(review.content) > 50 else review.content
        })
    
    qa_stats_data = {
        'overview': {
            'total_messages': all_messages.count(),
            'ai_messages': ai_messages.count(),
            'selected_for_qa': qa_selected.count(),
            'qa_reviewed': qa_reviewed.count(),
            'qa_coverage_percentage': (qa_selected.count() / ai_messages.count() * 100) if ai_messages.count() > 0 else 0,
            'review_completion_rate': (qa_reviewed.count() / qa_selected.count() * 100) if qa_selected.count() > 0 else 0
        },
        'status_breakdown': status_breakdown,
        'score_statistics': score_stats,
        'reviewer_statistics': reviewer_stats,
        'recent_activity': recent_activity,
        'pending_reviews': qa_selected.filter(qa_status='PENDING').count()
    }
    
    return Response(qa_stats_data)


@extend_schema(tags=['AI Companion'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_user_feedback(request):
    """Submit user feedback on an AI message"""
    
    serializer = UserFeedbackSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message_id = serializer.validated_data['message_id']
    is_helpful = serializer.validated_data['is_helpful']
    feedback_comment = serializer.validated_data.get('feedback_comment', '')
    
    try:
        message = Message.objects.get(message_id=message_id)
        
        # Update message with user feedback
        if is_helpful:
            message.mark_as_helpful(feedback_comment)
        else:
            message.mark_as_unhelpful(feedback_comment)
        
        return Response({
            'message': 'User feedback submitted successfully',
            'data': {
                'message_id': str(message.message_id),
                'is_helpful': message.is_helpful,
                'has_feedback': bool(message.user_feedback),
                'feedback_comment': message.user_feedback
            }
        })
        
    except Message.DoesNotExist:
        return Response(
            {'error': 'Message not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(tags=['AI Companion'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_qa_feedback(request):
    """Submit QA team feedback on a message (staff only)"""
    
    # Check if user has permission to submit QA feedback (staff only)
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied. Staff access required.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = QAFeedbackSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message_id = serializer.validated_data['message_id']
    qa_score = serializer.validated_data['qa_score']
    qa_status = serializer.validated_data['qa_status']
    qa_feedback = serializer.validated_data.get('qa_feedback', '')
    qa_tags = serializer.validated_data.get('qa_tags', '')
    
    try:
        message = Message.objects.get(message_id=message_id)
        
        # Complete QA review
        message.complete_qa_review(
            score=qa_score,
            status=qa_status,
            feedback=qa_feedback,
            reviewer=request.user,
            tags=qa_tags
        )
        
        return Response({
            'message': 'QA feedback submitted successfully',
            'data': {
                'message_id': str(message.message_id),
                'qa_score': message.qa_score,
                'qa_score_grade': message.qa_score_grade,
                'qa_status': message.qa_status,
                'qa_status_display': message.get_qa_status_display(),
                'qa_feedback': message.qa_feedback,
                'qa_tags': message.qa_tags,
                'qa_reviewer': message.qa_reviewer.username if message.qa_reviewer else None,
                'qa_reviewed_at': message.qa_reviewed_at
            }
        })
        
    except Message.DoesNotExist:
        return Response(
            {'error': 'Message not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(tags=['AI Companion'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_qa_messages(request):
    """Get messages selected for QA testing (staff only)"""
    
    # Check if user has permission to view QA messages (staff only)
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied. Staff access required.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get query parameters
    qa_status = request.query_params.get('status', None)
    reviewed = request.query_params.get('reviewed', None)
    reviewer = request.query_params.get('reviewer', None)
    limit = int(request.query_params.get('limit', 20))
    
    # Build query
    queryset = Message.objects.filter(is_selected_for_qa=True)
    
    if qa_status:
        queryset = queryset.filter(qa_status=qa_status)
    
    if reviewed == 'true':
        queryset = queryset.filter(qa_score__isnull=False)
    elif reviewed == 'false':
        queryset = queryset.filter(qa_score__isnull=True)
    
    if reviewer:
        queryset = queryset.filter(qa_reviewer__username=reviewer)
    
    # Order by creation date (newest first)
    queryset = queryset.order_by('-created_at')[:limit]
    
    # Serialize the data
    serializer = MessageWithQASerializer(queryset, many=True)
    
    return Response({
        'count': queryset.count(),
        'messages': serializer.data
    })


@extend_schema(tags=['AI Companion'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_feedback_history(request):
    """Get user's feedback history on AI messages"""
    
    # Get user's messages with feedback
    user_messages = Message.objects.filter(
        thread__user=request.user,
        sender='AI',
        is_helpful__isnull=False
    ).order_by('-created_at')
    
    # Get query parameters
    limit = int(request.query_params.get('limit', 50))
    helpful_only = request.query_params.get('helpful_only', None)
    
    if helpful_only == 'true':
        user_messages = user_messages.filter(is_helpful=True)
    elif helpful_only == 'false':
        user_messages = user_messages.filter(is_helpful=False)
    
    user_messages = user_messages[:limit]
    
    # Serialize the data
    feedback_data = []
    for message in user_messages:
        feedback_data.append({
            'message_id': str(message.message_id),
            'thread_title': message.thread.title or f"Thread {str(message.thread.thread_id)[:8]}...",
            'content': message.content[:100] + "..." if len(message.content) > 100 else message.content,
            'is_helpful': message.is_helpful,
            'user_feedback': message.user_feedback,
            'created_at': message.created_at,
            'feedback_given_at': message.created_at  # Approximation since we don't track exact feedback time
        })
    
    # Get summary statistics
    total_feedback = Message.objects.filter(
        thread__user=request.user,
        sender='AI',
        is_helpful__isnull=False
    ).count()
    
    helpful_count = Message.objects.filter(
        thread__user=request.user,
        sender='AI',
        is_helpful=True
    ).count()
    
    unhelpful_count = Message.objects.filter(
        thread__user=request.user,
        sender='AI',
        is_helpful=False
    ).count()
    
    return Response({
        'summary': {
            'total_feedback': total_feedback,
            'helpful_count': helpful_count,
            'unhelpful_count': unhelpful_count,
            'helpfulness_rate': (helpful_count / total_feedback * 100) if total_feedback > 0 else 0
        },
        'feedback_history': feedback_data
    })


# Initialize summarization model
try:
    # Explicitly set to None to prevent model loading
    summarizer = None
except Exception as e:
    logger.error(f"Summarization model initialization skipped: {e}")
    summarizer = None

def call_summarization_service(text, max_length=80, min_length=20, request=None):
    """
    Disabled summarization service
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum summary length
        min_length (int): Minimum summary length
        request (HttpRequest, optional): Current request object
    
    Returns:
        dict: Error response indicating summarization is disabled
    """
    logger.warning("Summarization service is currently disabled")
    return {
        'error': 'Summarization service is currently disabled',
        'status': 'disabled'
    }

def summarize_text(request):
    """
    Endpoint for text summarization (currently disabled)
    """
    logger.warning("Summarization endpoint is currently disabled")
    return Response({
        "error": "Summarization service is currently disabled",
        "status": "disabled"
    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@extend_schema(
    tags=['AI Companion'],
    description="Raw AI companion response without summarization",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'text': {
                    'type': 'string', 
                    'description': 'User input text',
                    'example': 'Tell me about the latest advancements in AI.'
                }
            },
            'required': ['text']
        }
    },
    responses={
        status.HTTP_200_OK: {
            'type': 'object',
            'properties': {
                'text': {'type': 'string', 'description': 'Full AI response without summarization'},
                'status': {'type': 'string', 'description': 'Status of the response generation'}
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Bad request, e.g., no text provided',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'},
                            'status': {'type': 'string'}
                        }
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'description': 'Internal server error',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'},
                            'status': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
)
@api_view(['POST'])
def ai_companion_raw(request):
    """
    Endpoint for raw AI companion response without summarization
    
    Expected payload:
    {
        "text": "User input text"
    }
    """
    # Print and log the incoming request details
    print(f"📨 Raw AI Companion Request Headers: {dict(request.headers)}")
    logger.debug(f"Raw AI Companion Request Headers: {dict(request.headers)}")
    print(f"📋 Raw AI Companion Request Data: {request.data}")
    logger.debug(f"Raw AI Companion Request Data: {request.data}")

    # Validate input
    text = request.data.get('text')
    if not text:
        print("⚠️ No text provided for AI companion")
        logger.warning("No text provided for AI companion")
        return Response({
            "error": "No text provided",
            "status": "error"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Prepare context-aware prompt focused on mental health
        system_prompt = """
        You are a dedicated mental health support AI assistant. 
        Your primary focus is on providing compassionate, professional, 
        and evidence-based mental health support.
        
        Guidelines:
        - Only discuss topics directly related to mental health and well-being
        - Provide empathetic, supportive, and non-judgmental responses
        - Offer coping strategies, emotional support, and guidance
        - Encourage professional help when needed
        - Maintain strict confidentiality and ethical boundaries
        - IMPORTANT: Keep your responses SHORT and CONCISE (Maximum 3-5 sentences).
        """
        
        # Check if the input is related to mental health
        def is_mental_health_topic(text):
            mental_health_keywords = [
                'anxiety', 'depression', 'stress', 'mental health', 
                'therapy', 'counseling', 'emotional', 'mood', 
                'psychological', 'trauma', 'ptsd', 'burnout', 
                'mental wellness', 'self-care', 'mental well-being'
            ]
            
            # Convert text to lowercase for case-insensitive matching
            text_lower = text.lower()
            
            # Check if any mental health keyword is in the text
            return any(keyword in text_lower for keyword in mental_health_keywords)
        
        # Validate input is mental health related
        if not is_mental_health_topic(text):
            non_mental_health_response = """
            I am a specialized mental health support AI assistant. 
            My expertise is focused exclusively on mental health and emotional well-being. 
            
            If you would like to discuss mental health topics such as:
            - Anxiety and stress management
            - Depression support
            - Emotional wellness
            - Coping strategies
            - Self-care techniques

            I'm here to help. Could you rephrase your query to relate to mental health?
            """
            
            print(f"⚠️ Non-mental health topic detected: {text}")
            logger.warning(f"Non-mental health topic attempted: {text}")
            
            response_data = {
                "text": non_mental_health_response,
                "status": "restricted"
            }
            
            return Response(response_data)
        
        # RAG Integration: Retrieve relevant context from knowledge base
        rag_context = ""
        rag_sources = []
        use_rag = getattr(settings, 'RAG_ENABLED', True)
        
        if use_rag:
            try:
                rag_service = get_rag_service()
                rag_results = rag_service.search(text, top_k=getattr(settings, 'RAG_TOP_K_RESULTS', 3))
                
                if rag_results:
                    # Build context from retrieved documents
                    context_parts = []
                    for i, result in enumerate(rag_results, 1):
                        content = result.get('content', '')
                        metadata = result.get('metadata', {})
                        source = metadata.get('source_file', metadata.get('source', f'Document {i}'))
                        
                        context_parts.append(f"[Reference {i}]\n{content}")
                        rag_sources.append(source)
                    
                    rag_context = "\n\n---\n\n".join(context_parts)
                    
                    print(f"📚 RAG Context Retrieved: {len(rag_results)} documents found")
                    logger.info(f"RAG: Retrieved {len(rag_results)} relevant documents")
                else:
                    print("ℹ️ No RAG context found - knowledge base may be empty")
                    logger.info("RAG: No relevant documents found in knowledge base")
                    
            except Exception as e:
                print(f"⚠️ RAG Error (continuing without RAG): {str(e)}")
                logger.warning(f"RAG retrieval error: {str(e)}")
                # Continue without RAG if there's an error
        
        # Enhance system prompt with RAG context if available
        enhanced_system_prompt = system_prompt
        
        if rag_context:
            enhanced_system_prompt += f"""

RELEVANT KNOWLEDGE BASE CONTEXT:
{rag_context}

IMPORTANT: Use the above context to provide accurate, evidence-based information. 
When referencing information from the knowledge base, be specific and cite sources when possible.
If the context doesn't fully answer the user's question, acknowledge this and provide 
general guidance based on your training while encouraging professional consultation.
"""
        
        # Generate response using Groq with RAG-enhanced context
        conversation_history = [
            {"role": "system", "content": enhanced_system_prompt},
            {"role": "user", "content": text}
        ]
        
        # Generate full response
        full_response = groq_client.get_chat_response(conversation_history)
        
        # Print and log the response
        print(f"📝 Raw AI Companion Response: {full_response}")
        logger.debug(f"Raw AI Companion Response: {full_response}")
        
        # Return the full response with RAG metadata
        response_data = {
            "text": full_response,
            "status": "success",
            "rag_enabled": use_rag,
            "rag_sources": rag_sources if rag_sources else None
        }
        
        print(f"✅ Raw AI Companion Response Data: {json.dumps(response_data, indent=2)}")
        logger.debug(f"Raw AI Companion Response Data: {response_data}")
        
        return Response(response_data)
    
    except Exception as e:
        print(f"❌ Raw AI Companion error: {str(e)}")
        logger.error(f"Raw AI Companion error: {str(e)}")
        return Response({
            "error": str(e),
            "status": "error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
