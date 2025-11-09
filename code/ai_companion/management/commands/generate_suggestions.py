from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ai_companion.models import Thread, ThreadSuggestion
import random


class Command(BaseCommand):
    help = 'Generate sample thread suggestions for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to generate suggestions for (optional)'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of suggestions to generate (default: 5)'
        )
    
    def handle(self, *args, **options):
        user_id = options.get('user_id')
        count = options['count']
        
        # Get users to generate suggestions for
        if user_id:
            try:
                users = [User.objects.get(id=user_id)]
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found'))
                return
        else:
            users = User.objects.all()[:5]  # Generate for first 5 users
        
        if not users:
            self.stdout.write(self.style.WARNING('No users found to generate suggestions for'))
            return
        
        # Sample suggestions data
        suggestions_data = [
            # Mental Health suggestions
            {
                'suggestion_type': 'WELLNESS_CHECK',
                'title': 'Weekly Mental Health Check-in',
                'description': 'It\'s been a week since your last mental wellness discussion. How are you feeling today?',
                'suggested_category': 'MENTAL_HEALTH',
                'suggested_first_message': 'Hi! I wanted to check in on how you\'ve been feeling this week. Any particular emotions or situations you\'d like to talk about?',
                'relevance_score': 0.9
            },
            {
                'suggestion_type': 'TOPIC',
                'title': 'Managing Stress at Work',
                'description': 'Based on your previous conversations, you might benefit from discussing workplace stress management techniques.',
                'suggested_category': 'MENTAL_HEALTH',
                'suggested_first_message': 'I\'ve been feeling stressed at work lately. Can you help me with some strategies to manage work-related stress?',
                'relevance_score': 0.8
            },
            {
                'suggestion_type': 'FOLLOW_UP',
                'title': 'Sleep Quality Follow-up',
                'description': 'Continue the conversation about improving your sleep habits and tracking progress.',
                'suggested_category': 'MENTAL_HEALTH',
                'suggested_first_message': 'I wanted to follow up on the sleep improvement tips we discussed. How have they been working for me?',
                'relevance_score': 0.7
            },
            {
                'suggestion_type': 'RELATED',
                'title': 'Mindfulness and Meditation',
                'description': 'Explore mindfulness practices that can complement your mental wellness journey.',
                'suggested_category': 'MENTAL_HEALTH',
                'suggested_first_message': 'I\'m interested in learning about mindfulness and meditation. How can these practices help with my mental health?',
                'relevance_score': 0.75
            },
            
            # Nutrition suggestions
            {
                'suggestion_type': 'TOPIC',
                'title': 'Meal Planning for Busy Days',
                'description': 'Learn how to maintain healthy eating habits even with a busy schedule.',
                'suggested_category': 'NUTRITION',
                'suggested_first_message': 'I have a really busy schedule and often skip meals or eat unhealthy food. Can you help me with meal planning strategies?',
                'relevance_score': 0.85
            },
            {
                'suggestion_type': 'WELLNESS_CHECK',
                'title': 'Nutrition Goals Check-in',
                'description': 'Review your nutrition goals and discuss any challenges you\'re facing.',
                'suggested_category': 'NUTRITION',
                'suggested_first_message': 'I want to check in on my nutrition goals. Can we review what I\'ve been eating and how I can improve?',
                'relevance_score': 0.8
            },
            {
                'suggestion_type': 'RELATED',
                'title': 'Hydration and Energy Levels',
                'description': 'Explore the connection between proper hydration and maintaining energy throughout the day.',
                'suggested_category': 'NUTRITION',
                'suggested_first_message': 'I\'ve been feeling tired lately. Could my hydration levels be affecting my energy? How much water should I be drinking?',
                'relevance_score': 0.7
            },
            {
                'suggestion_type': 'FOLLOW_UP',
                'title': 'Healthy Snacking Options',
                'description': 'Continue exploring nutritious snack options that fit your lifestyle.',
                'suggested_category': 'NUTRITION',
                'suggested_first_message': 'Can we talk more about healthy snacking? I need some ideas for nutritious snacks I can have between meals.',
                'relevance_score': 0.65
            }
        ]
        
        total_generated = 0
        
        for user in users:
            self.stdout.write(f'\nGenerating suggestions for user: {user.username}')
            
            # Get user's existing threads for context
            user_threads = Thread.objects.filter(user=user)
            
            # Generate suggestions for this user
            user_suggestions = random.sample(suggestions_data, min(count, len(suggestions_data)))
            
            for suggestion_data in user_suggestions:
                # Optionally link to an existing thread
                based_on_thread = None
                if user_threads.exists() and random.random() > 0.5:  # 50% chance
                    based_on_thread = random.choice(user_threads)
                
                # Create the suggestion
                suggestion = ThreadSuggestion.objects.create(
                    user=user,
                    based_on_thread=based_on_thread,
                    **suggestion_data
                )
                
                self.stdout.write(
                    f'  ✓ Created: {suggestion.title} '
                    f'({suggestion.get_suggestion_type_display()}, '
                    f'{suggestion.get_suggested_category_display()}, '
                    f'{suggestion.relevance_score:.1%})'
                )
                total_generated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Generated {total_generated} thread suggestions!')
        )
        
        # Show summary
        self.stdout.write('\n📊 Summary:')
        for suggestion_type, display in ThreadSuggestion.SUGGESTION_TYPES:
            count = ThreadSuggestion.objects.filter(suggestion_type=suggestion_type).count()
            self.stdout.write(f'  {display}: {count}')
        
        self.stdout.write('\n📋 Next steps:')
        self.stdout.write('  • Users can view suggestions at: /api/ai-companion/suggestions/')
        self.stdout.write('  • Test suggestion actions at: /api/ai-companion/suggestions/handle/')
        self.stdout.write('  • Check admin interface for management') 