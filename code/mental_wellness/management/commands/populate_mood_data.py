from django.core.management.base import BaseCommand
from django.db import transaction
from mental_wellness.models import MoodCategory, Emotion, ActivityType, MoodTrigger


class Command(BaseCommand):
    help = 'Populate sample mood tracking data (categories, emotions, activities, triggers)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing mood data...')
            MoodTrigger.objects.all().delete()
            ActivityType.objects.all().delete()
            Emotion.objects.all().delete()
            MoodCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))
        
        with transaction.atomic():
            self._create_mood_categories()
            self._create_emotions()
            self._create_activity_types()
            self._create_mood_triggers()
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Successfully populated mood tracking data!')
        )
    
    def _create_mood_categories(self):
        """Create mood categories"""
        categories = [
            {
                'name': 'Joyful',
                'description': 'Happy, elated, cheerful moods',
                'color_hex': '#4CAF50',
                'icon': '😊'
            },
            {
                'name': 'Calm',
                'description': 'Peaceful, relaxed, serene moods',
                'color_hex': '#2196F3',
                'icon': '😌'
            },
            {
                'name': 'Energetic',
                'description': 'Active, motivated, dynamic moods',
                'color_hex': '#FF9800',
                'icon': '⚡'
            },
            {
                'name': 'Anxious',
                'description': 'Worried, nervous, stressed moods',
                'color_hex': '#FF5722',
                'icon': '😰'
            },
            {
                'name': 'Sad',
                'description': 'Down, melancholic, blue moods',
                'color_hex': '#607D8B',
                'icon': '😢'
            },
            {
                'name': 'Neutral',
                'description': 'Balanced, neither positive nor negative',
                'color_hex': '#9E9E9E',
                'icon': '😐'
            },
            {
                'name': 'Irritated',
                'description': 'Annoyed, frustrated, agitated moods',
                'color_hex': '#F44336',
                'icon': '😤'
            },
            {
                'name': 'Focused',
                'description': 'Concentrated, clear-minded, productive',
                'color_hex': '#673AB7',
                'icon': '🎯'
            }
        ]
        
        created_count = 0
        for category_data in categories:
            category, created = MoodCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✓ Created {created_count} mood categories')
    
    def _create_emotions(self):
        """Create emotions"""
        emotions = [
            # Positive emotions
            {'name': 'Happy', 'emotion_type': 'POSITIVE', 'color_hex': '#4CAF50'},
            {'name': 'Excited', 'emotion_type': 'POSITIVE', 'color_hex': '#FF9800'},
            {'name': 'Grateful', 'emotion_type': 'POSITIVE', 'color_hex': '#8BC34A'},
            {'name': 'Proud', 'emotion_type': 'POSITIVE', 'color_hex': '#9C27B0'},
            {'name': 'Content', 'emotion_type': 'POSITIVE', 'color_hex': '#00BCD4'},
            {'name': 'Optimistic', 'emotion_type': 'POSITIVE', 'color_hex': '#CDDC39'},
            {'name': 'Loved', 'emotion_type': 'POSITIVE', 'color_hex': '#E91E63'},
            {'name': 'Accomplished', 'emotion_type': 'POSITIVE', 'color_hex': '#3F51B5'},
            {'name': 'Peaceful', 'emotion_type': 'POSITIVE', 'color_hex': '#009688'},
            {'name': 'Energetic', 'emotion_type': 'POSITIVE', 'color_hex': '#FF5722'},
            
            # Negative emotions
            {'name': 'Sad', 'emotion_type': 'NEGATIVE', 'color_hex': '#607D8B'},
            {'name': 'Anxious', 'emotion_type': 'NEGATIVE', 'color_hex': '#FF5722'},
            {'name': 'Angry', 'emotion_type': 'NEGATIVE', 'color_hex': '#F44336'},
            {'name': 'Frustrated', 'emotion_type': 'NEGATIVE', 'color_hex': '#FF9800'},
            {'name': 'Lonely', 'emotion_type': 'NEGATIVE', 'color_hex': '#9E9E9E'},
            {'name': 'Overwhelmed', 'emotion_type': 'NEGATIVE', 'color_hex': '#795548'},
            {'name': 'Disappointed', 'emotion_type': 'NEGATIVE', 'color_hex': '#673AB7'},
            {'name': 'Stressed', 'emotion_type': 'NEGATIVE', 'color_hex': '#E91E63'},
            {'name': 'Worried', 'emotion_type': 'NEGATIVE', 'color_hex': '#FF7043'},
            {'name': 'Jealous', 'emotion_type': 'NEGATIVE', 'color_hex': '#8BC34A'},
            
            # Neutral emotions
            {'name': 'Calm', 'emotion_type': 'NEUTRAL', 'color_hex': '#2196F3'},
            {'name': 'Focused', 'emotion_type': 'NEUTRAL', 'color_hex': '#673AB7'},
            {'name': 'Tired', 'emotion_type': 'NEUTRAL', 'color_hex': '#795548'},
            {'name': 'Bored', 'emotion_type': 'NEUTRAL', 'color_hex': '#9E9E9E'},
            {'name': 'Curious', 'emotion_type': 'NEUTRAL', 'color_hex': '#00BCD4'},
            
            # Mixed emotions
            {'name': 'Confused', 'emotion_type': 'MIXED', 'color_hex': '#FF9800'},
            {'name': 'Nostalgic', 'emotion_type': 'MIXED', 'color_hex': '#9C27B0'},
            {'name': 'Hopeful', 'emotion_type': 'MIXED', 'color_hex': '#4CAF50'},
            {'name': 'Uncertain', 'emotion_type': 'MIXED', 'color_hex': '#607D8B'},
            {'name': 'Relieved', 'emotion_type': 'MIXED', 'color_hex': '#009688'},
        ]
        
        created_count = 0
        for emotion_data in emotions:
            emotion, created = Emotion.objects.get_or_create(
                name=emotion_data['name'],
                defaults=emotion_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✓ Created {created_count} emotions')
    
    def _create_activity_types(self):
        """Create activity types"""
        activities = [
            # Exercise & Fitness
            {'name': 'Running', 'category': 'EXERCISE', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Yoga', 'category': 'EXERCISE', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Gym Workout', 'category': 'EXERCISE', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Walking', 'category': 'EXERCISE', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Swimming', 'category': 'EXERCISE', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Cycling', 'category': 'EXERCISE', 'typical_mood_impact': 'POSITIVE'},
            
            # Social Activities
            {'name': 'Hanging out with friends', 'category': 'SOCIAL', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Date night', 'category': 'SOCIAL', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Party/Event', 'category': 'SOCIAL', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Video call with family', 'category': 'SOCIAL', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Team meeting', 'category': 'SOCIAL', 'typical_mood_impact': 'NEUTRAL'},
            
            # Work & Career
            {'name': 'Productive work day', 'category': 'WORK', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Stressful deadline', 'category': 'WORK', 'typical_mood_impact': 'NEGATIVE'},
            {'name': 'Presentation', 'category': 'WORK', 'typical_mood_impact': 'NEUTRAL'},
            {'name': 'Team collaboration', 'category': 'WORK', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Problem solving', 'category': 'WORK', 'typical_mood_impact': 'NEUTRAL'},
            
            # Relaxation & Rest
            {'name': 'Meditation', 'category': 'RELAXATION', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Nap', 'category': 'RELAXATION', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Bath/Shower', 'category': 'RELAXATION', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Deep breathing', 'category': 'RELAXATION', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Massage', 'category': 'RELAXATION', 'typical_mood_impact': 'POSITIVE'},
            
            # Hobbies & Interests
            {'name': 'Reading', 'category': 'HOBBIES', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Watching movies', 'category': 'HOBBIES', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Playing music', 'category': 'HOBBIES', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Cooking', 'category': 'HOBBIES', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Gaming', 'category': 'HOBBIES', 'typical_mood_impact': 'NEUTRAL'},
            {'name': 'Gardening', 'category': 'HOBBIES', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Photography', 'category': 'HOBBIES', 'typical_mood_impact': 'POSITIVE'},
            
            # Health & Medical
            {'name': 'Doctor appointment', 'category': 'HEALTH', 'typical_mood_impact': 'NEUTRAL'},
            {'name': 'Therapy session', 'category': 'HEALTH', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Taking medication', 'category': 'HEALTH', 'typical_mood_impact': 'NEUTRAL'},
            {'name': 'Health checkup', 'category': 'HEALTH', 'typical_mood_impact': 'NEUTRAL'},
            
            # Family Time
            {'name': 'Playing with kids', 'category': 'FAMILY', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Family dinner', 'category': 'FAMILY', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Family outing', 'category': 'FAMILY', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Helping with homework', 'category': 'FAMILY', 'typical_mood_impact': 'NEUTRAL'},
            
            # Spiritual & Meditation
            {'name': 'Prayer', 'category': 'SPIRITUAL', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Church/Temple visit', 'category': 'SPIRITUAL', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Mindfulness practice', 'category': 'SPIRITUAL', 'typical_mood_impact': 'POSITIVE'},
            {'name': 'Journaling', 'category': 'SPIRITUAL', 'typical_mood_impact': 'POSITIVE'},
        ]
        
        created_count = 0
        for activity_data in activities:
            activity, created = ActivityType.objects.get_or_create(
                name=activity_data['name'],
                category=activity_data['category'],
                defaults=activity_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✓ Created {created_count} activity types')
    
    def _create_mood_triggers(self):
        """Create mood triggers"""
        triggers = [
            # Stress & Pressure
            {'name': 'Work deadline', 'category': 'STRESS', 'typical_impact': 'NEGATIVE'},
            {'name': 'Public speaking', 'category': 'STRESS', 'typical_impact': 'NEGATIVE'},
            {'name': 'Financial pressure', 'category': 'STRESS', 'typical_impact': 'NEGATIVE'},
            {'name': 'Heavy workload', 'category': 'STRESS', 'typical_impact': 'NEGATIVE'},
            {'name': 'Time pressure', 'category': 'STRESS', 'typical_impact': 'NEGATIVE'},
            
            # Relationships
            {'name': 'Argument with partner', 'category': 'RELATIONSHIPS', 'typical_impact': 'NEGATIVE'},
            {'name': 'Family conflict', 'category': 'RELATIONSHIPS', 'typical_impact': 'NEGATIVE'},
            {'name': 'Friend cancellation', 'category': 'RELATIONSHIPS', 'typical_impact': 'NEGATIVE'},
            {'name': 'Social rejection', 'category': 'RELATIONSHIPS', 'typical_impact': 'NEGATIVE'},
            {'name': 'Loneliness', 'category': 'RELATIONSHIPS', 'typical_impact': 'NEGATIVE'},
            
            # Work & Career
            {'name': 'Job interview', 'category': 'WORK', 'typical_impact': 'NEGATIVE'},
            {'name': 'Performance review', 'category': 'WORK', 'typical_impact': 'NEGATIVE'},
            {'name': 'Workplace conflict', 'category': 'WORK', 'typical_impact': 'NEGATIVE'},
            {'name': 'Job uncertainty', 'category': 'WORK', 'typical_impact': 'NEGATIVE'},
            {'name': 'Promotion opportunity', 'category': 'WORK', 'typical_impact': 'POSITIVE'},
            
            # Health Issues
            {'name': 'Physical pain', 'category': 'HEALTH', 'typical_impact': 'NEGATIVE'},
            {'name': 'Illness', 'category': 'HEALTH', 'typical_impact': 'NEGATIVE'},
            {'name': 'Medical test results', 'category': 'HEALTH', 'typical_impact': 'NEGATIVE'},
            {'name': 'Chronic condition flare', 'category': 'HEALTH', 'typical_impact': 'NEGATIVE'},
            
            # Financial Concerns
            {'name': 'Unexpected expense', 'category': 'FINANCIAL', 'typical_impact': 'NEGATIVE'},
            {'name': 'Bill due date', 'category': 'FINANCIAL', 'typical_impact': 'NEGATIVE'},
            {'name': 'Investment loss', 'category': 'FINANCIAL', 'typical_impact': 'NEGATIVE'},
            {'name': 'Budget concerns', 'category': 'FINANCIAL', 'typical_impact': 'NEGATIVE'},
            
            # Environmental Factors
            {'name': 'Bad weather', 'category': 'ENVIRONMENT', 'typical_impact': 'NEGATIVE'},
            {'name': 'Noise pollution', 'category': 'ENVIRONMENT', 'typical_impact': 'NEGATIVE'},
            {'name': 'Traffic jam', 'category': 'ENVIRONMENT', 'typical_impact': 'NEGATIVE'},
            {'name': 'Crowded spaces', 'category': 'ENVIRONMENT', 'typical_impact': 'NEGATIVE'},
            {'name': 'Beautiful sunset', 'category': 'ENVIRONMENT', 'typical_impact': 'POSITIVE'},
            
            # Sleep Related
            {'name': 'Poor sleep quality', 'category': 'SLEEP', 'typical_impact': 'NEGATIVE'},
            {'name': 'Insomnia', 'category': 'SLEEP', 'typical_impact': 'NEGATIVE'},
            {'name': 'Early morning', 'category': 'SLEEP', 'typical_impact': 'NEGATIVE'},
            {'name': 'Sleep deprivation', 'category': 'SLEEP', 'typical_impact': 'NEGATIVE'},
            
            # Hormonal Changes
            {'name': 'PMS symptoms', 'category': 'HORMONAL', 'typical_impact': 'NEGATIVE'},
            {'name': 'Menstruation', 'category': 'HORMONAL', 'typical_impact': 'NEGATIVE'},
            {'name': 'Hormonal medication', 'category': 'HORMONAL', 'typical_impact': 'NEUTRAL'},
            
            # Seasonal Changes
            {'name': 'Winter blues', 'category': 'SEASONAL', 'typical_impact': 'NEGATIVE'},
            {'name': 'Spring energy', 'category': 'SEASONAL', 'typical_impact': 'POSITIVE'},
            {'name': 'Holiday stress', 'category': 'SEASONAL', 'typical_impact': 'NEGATIVE'},
            {'name': 'Summer vacation', 'category': 'SEASONAL', 'typical_impact': 'POSITIVE'},
        ]
        
        created_count = 0
        for trigger_data in triggers:
            trigger, created = MoodTrigger.objects.get_or_create(
                name=trigger_data['name'],
                category=trigger_data['category'],
                defaults=trigger_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✓ Created {created_count} mood triggers') 