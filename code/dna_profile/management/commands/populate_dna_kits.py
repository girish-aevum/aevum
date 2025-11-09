from django.core.management.base import BaseCommand
from dna_profile.models import DNAKitType
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with sample DNA kit types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing kit types before adding new ones'
        )

    def handle(self, *args, **options):
        if options['clear']:
            DNAKitType.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing DNA kit types'))

        # Sample DNA Kit Types
        kit_types = [
            {
                'name': 'AncestryPlus DNA Kit',
                'category': 'ANCESTRY',
                'description': 'Discover your ethnic background and find relatives with our comprehensive ancestry analysis. Includes detailed ethnicity breakdown, migration patterns, and family tree building tools.',
                'price': Decimal('9999.00'),  # ₹9,999
                'processing_time_days': 21,
                'features': [
                    'Ethnicity breakdown (500+ regions)',
                    'DNA relative matching',
                    'Migration patterns',
                    'Historical insights',
                    'Family tree builder'
                ],
                'is_active': True,
                'requires_prescription': False
            },
            {
                'name': 'Health Insights Pro',
                'category': 'HEALTH',
                'description': 'Comprehensive health risk assessment based on genetic markers. Includes predisposition analysis for common conditions and personalized health recommendations.',
                'price': Decimal('19999.00'),  # ₹19,999
                'processing_time_days': 28,
                'features': [
                    'Disease risk assessment (150+ conditions)',
                    'Genetic predispositions',
                    'Carrier status screening',
                    'Health recommendations',
                    'Genetic counselor consultation'
                ],
                'is_active': True,
                'requires_prescription': False
            },
            {
                'name': 'FitGene DNA Analysis',
                'category': 'FITNESS',
                'description': 'Optimize your fitness and nutrition based on your genetic makeup. Personalized workout plans and dietary recommendations.',
                'price': Decimal('14999.00'),  # ₹14,999
                'processing_time_days': 14,
                'features': [
                    'Exercise response analysis',
                    'Nutrition optimization',
                    'Metabolism insights',
                    'Injury risk assessment',
                    'Personalized fitness plan'
                ],
                'is_active': True,
                'requires_prescription': False
            },
            {
                'name': 'Complete Genome Analysis',
                'category': 'COMPREHENSIVE',
                'description': 'Our most comprehensive analysis covering ancestry, health, fitness, and traits. The ultimate genetic profile for complete insights.',
                'price': Decimal('29999.00'),  # ₹29,999
                'processing_time_days': 35,
                'features': [
                    'Full ancestry analysis',
                    'Complete health screening',
                    'Fitness & nutrition insights',
                    'Physical traits analysis',
                    'Pharmacogenomics report',
                    'Raw data download',
                    'Priority support'
                ],
                'is_active': True,
                'requires_prescription': False
            },
            {
                'name': 'PharmaDNA Pro',
                'category': 'PHARMACOGENOMICS',
                'description': 'Understand how your genes affect drug response and metabolism. Essential for personalized medication management.',
                'price': Decimal('17999.00'),  # ₹17,999
                'processing_time_days': 21,
                'features': [
                    'Drug response analysis (200+ medications)',
                    'Metabolism insights',
                    'Dosage recommendations',
                    'Drug interaction warnings',
                    'Pharmacist consultation'
                ],
                'is_active': True,
                'requires_prescription': True
            },
            {
                'name': 'Wellness Essentials',
                'category': 'HEALTH',
                'description': 'Basic health and wellness insights for everyday health management. Perfect for health-conscious individuals.',
                'price': Decimal('7999.00'),  # ₹7,999
                'processing_time_days': 14,
                'features': [
                    'Basic health risks',
                    'Vitamin deficiency risks',
                    'Sleep pattern insights',
                    'Stress response analysis',
                    'Wellness recommendations'
                ],
                'is_active': True,
                'requires_prescription': False
            }
        ]

        created_count = 0
        for kit_data in kit_types:
            kit_type, created = DNAKitType.objects.get_or_create(
                name=kit_data['name'],
                defaults=kit_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created: {kit_type.name} (₹{kit_type.price})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Already exists: {kit_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully created {created_count} new DNA kit types!')
        )
        
        # Display summary
        total_kits = DNAKitType.objects.count()
        active_kits = DNAKitType.objects.filter(is_active=True).count()
        
        self.stdout.write(f'\n📊 SUMMARY:')
        self.stdout.write(f'Total Kit Types: {total_kits}')
        self.stdout.write(f'Active Kit Types: {active_kits}')
        
        # Show by category
        categories = DNAKitType.objects.values_list('category', flat=True).distinct()
        for category in categories:
            count = DNAKitType.objects.filter(category=category).count()
            self.stdout.write(f'{category}: {count} kits') 