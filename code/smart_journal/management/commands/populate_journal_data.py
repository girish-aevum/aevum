from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from smart_journal.models import JournalCategory, JournalTemplate


class Command(BaseCommand):
    help = 'Populate sample data for Smart Journal system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating smart journal sample data...'))

        # Create system categories
        system_categories = [
            {
                'name': 'Personal Life',
                'category_type': 'PERSONAL',
                'description': 'Personal thoughts, experiences, and daily life',
                'color_hex': '#3b82f6',
                'icon': '👤',
                'is_system_category': True
            },
            {
                'name': 'Work & Career',
                'category_type': 'WORK',
                'description': 'Professional development, work experiences, and career goals',
                'color_hex': '#f59e0b',
                'icon': '💼',
                'is_system_category': True
            },
            {
                'name': 'Health & Wellness',
                'category_type': 'HEALTH',
                'description': 'Physical health, mental wellness, and fitness journey',
                'color_hex': '#10b981',
                'icon': '🏥',
                'is_system_category': True
            },
            {
                'name': 'Relationships',
                'category_type': 'RELATIONSHIPS',
                'description': 'Family, friends, and personal relationships',
                'color_hex': '#ef4444',
                'icon': '❤️',
                'is_system_category': True
            },
            {
                'name': 'Goals & Dreams',
                'category_type': 'GOALS',
                'description': 'Personal goals, aspirations, and achievements',
                'color_hex': '#8b5cf6',
                'icon': '🎯',
                'is_system_category': True
            },
            {
                'name': 'Travel & Adventures',
                'category_type': 'TRAVEL',
                'description': 'Travel experiences, adventures, and explorations',
                'color_hex': '#06b6d4',
                'icon': '✈️',
                'is_system_category': True
            },
            {
                'name': 'Learning & Growth',
                'category_type': 'LEARNING',
                'description': 'Education, skill development, and personal growth',
                'color_hex': '#84cc16',
                'icon': '📚',
                'is_system_category': True
            },
            {
                'name': 'Creative Projects',
                'category_type': 'CREATIVITY',
                'description': 'Art, writing, music, and creative endeavors',
                'color_hex': '#f97316',
                'icon': '🎨',
                'is_system_category': True
            },
            {
                'name': 'Gratitude & Reflection',
                'category_type': 'GRATITUDE',
                'description': 'Daily gratitude practice and mindful reflection',
                'color_hex': '#ec4899',
                'icon': '🙏',
                'is_system_category': True
            },
            {
                'name': 'Daily Life',
                'category_type': 'DAILY',
                'description': 'Everyday experiences, routines, and observations',
                'color_hex': '#64748b',
                'icon': '📅',
                'is_system_category': True
            }
        ]

        created_categories = 0
        for cat_data in system_categories:
            category, created = JournalCategory.objects.get_or_create(
                name=cat_data['name'],
                user_id=1,  # Assign to admin user or create a system user
                defaults=cat_data
            )
            if created:
                created_categories += 1
                self.stdout.write(f'✅ Created category: {category.name}')
            else:
                self.stdout.write(f'ℹ️  Category already exists: {category.name}')

        # Create system templates
        system_templates = [
            {
                'name': 'Daily Reflection',
                'template_type': 'DAILY_REFLECTION',
                'description': 'End-of-day reflection on experiences and feelings',
                'prompt_questions': [
                    'What was the highlight of your day?',
                    'What challenged you today?',
                    'What are you grateful for?',
                    'How did you feel throughout the day?',
                    'What would you do differently?'
                ],
                'default_structure': {
                    'sections': ['highlights', 'challenges', 'gratitude', 'mood', 'lessons'],
                    'mood_tracking': True,
                    'energy_tracking': True
                },
                'is_system_template': True,
                'is_public': True
            },
            {
                'name': 'Gratitude Journal',
                'template_type': 'GRATITUDE',
                'description': 'Daily gratitude practice to cultivate positivity',
                'prompt_questions': [
                    'What are three things you\'re grateful for today?',
                    'Who made a positive impact on your day?',
                    'What small moment brought you joy?',
                    'What opportunity are you thankful for?'
                ],
                'default_structure': {
                    'sections': ['three_gratitudes', 'people', 'moments', 'opportunities'],
                    'mood_tracking': True
                },
                'is_system_template': True,
                'is_public': True
            },
            {
                'name': 'Goal Progress Tracker',
                'template_type': 'GOAL_TRACKING',
                'description': 'Track progress toward your personal and professional goals',
                'prompt_questions': [
                    'What progress did you make toward your goals today?',
                    'What obstacles did you encounter?',
                    'What actions will you take tomorrow?',
                    'How do you feel about your progress?'
                ],
                'default_structure': {
                    'sections': ['progress', 'obstacles', 'next_actions', 'reflection'],
                    'goal_tracking': True,
                    'progress_rating': True
                },
                'is_system_template': True,
                'is_public': True
            },
            {
                'name': 'Work Log',
                'template_type': 'WORK_LOG',
                'description': 'Professional development and work experience tracking',
                'prompt_questions': [
                    'What did you accomplish at work today?',
                    'What challenges did you face?',
                    'What did you learn?',
                    'What are your priorities for tomorrow?'
                ],
                'default_structure': {
                    'sections': ['accomplishments', 'challenges', 'learnings', 'priorities'],
                    'productivity_rating': True
                },
                'is_system_template': True,
                'is_public': True
            },
            {
                'name': 'Health & Wellness Log',
                'template_type': 'HEALTH_LOG',
                'description': 'Track your physical and mental health journey',
                'prompt_questions': [
                    'How did you take care of your health today?',
                    'What physical activities did you do?',
                    'How are you feeling mentally and emotionally?',
                    'What healthy choices did you make?'
                ],
                'default_structure': {
                    'sections': ['health_activities', 'physical_activity', 'mental_state', 'healthy_choices'],
                    'mood_tracking': True,
                    'energy_tracking': True
                },
                'is_system_template': True,
                'is_public': True
            },
            {
                'name': 'Travel Journal',
                'template_type': 'TRAVEL_LOG',
                'description': 'Document your travel experiences and adventures',
                'prompt_questions': [
                    'Where did you go today?',
                    'What did you see and experience?',
                    'Who did you meet?',
                    'What was your favorite moment?',
                    'What would you recommend to others?'
                ],
                'default_structure': {
                    'sections': ['location', 'experiences', 'people', 'highlights', 'recommendations'],
                    'location_tracking': True
                },
                'is_system_template': True,
                'is_public': True
            }
        ]

        created_templates = 0
        for template_data in system_templates:
            template, created = JournalTemplate.objects.get_or_create(
                name=template_data['name'],
                user_id=1,  # Assign to admin user
                defaults=template_data
            )
            if created:
                created_templates += 1
                self.stdout.write(f'✅ Created template: {template.name}')
            else:
                self.stdout.write(f'ℹ️  Template already exists: {template.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Smart Journal setup complete!\n'
                f'Created categories: {created_categories}\n'
                f'Created templates: {created_templates}\n'
                f'Total categories: {JournalCategory.objects.count()}\n'
                f'Total templates: {JournalTemplate.objects.count()}'
            )
        ) 