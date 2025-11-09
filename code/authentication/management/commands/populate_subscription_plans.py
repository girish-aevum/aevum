from django.core.management.base import BaseCommand
from authentication.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Populate subscription plans for Aevum Health platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating subscription plans...'))

        # Free Plan
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Free Plan',
            plan_type='FREE',
            defaults={
                'description': 'Basic health tracking at no cost. Perfect for getting started with your health journey.',
                'price': 0.00,
                'billing_cycle': 'MONTHLY',
                'dna_kits_included': 0,
                'mood_entries_limit': 30,
                'ai_insights_enabled': False,
                'priority_support': False,
                'data_export_enabled': False,
                'api_access_enabled': False,
                'is_active': True,
                'is_featured': False,
                'sort_order': 1,
            }
        )
        if created:
            self.stdout.write(f'✅ Created: {free_plan.name}')
        else:
            self.stdout.write(f'ℹ️  Already exists: {free_plan.name}')

        # Basic Plan
        basic_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Basic Health',
            plan_type='BASIC',
            defaults={
                'description': 'Essential health tracking with DNA insights. Ideal for individuals starting their health optimization journey.',
                'price': 2499.00,  # ₹2,499/month
                'billing_cycle': 'MONTHLY',
                'dna_kits_included': 1,
                'mood_entries_limit': 0,  # Unlimited
                'ai_insights_enabled': True,
                'priority_support': False,
                'data_export_enabled': True,
                'api_access_enabled': False,
                'is_active': True,
                'is_featured': True,
                'sort_order': 2,
            }
        )
        if created:
            self.stdout.write(f'✅ Created: {basic_plan.name}')
        else:
            self.stdout.write(f'ℹ️  Already exists: {basic_plan.name}')

        # Premium Plan
        premium_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Premium Wellness',
            plan_type='PREMIUM',
            defaults={
                'description': 'Complete health optimization with advanced AI insights, priority support, and unlimited features.',
                'price': 7999.00,  # ₹7,999/month
                'billing_cycle': 'MONTHLY',
                'dna_kits_included': 3,
                'mood_entries_limit': 0,  # Unlimited
                'ai_insights_enabled': True,
                'priority_support': True,
                'data_export_enabled': True,
                'api_access_enabled': True,
                'is_active': True,
                'is_featured': True,
                'sort_order': 3,
            }
        )
        if created:
            self.stdout.write(f'✅ Created: {premium_plan.name}')
        else:
            self.stdout.write(f'ℹ️  Already exists: {premium_plan.name}')

        # Enterprise Plan
        enterprise_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Enterprise Health',
            plan_type='ENTERPRISE',
            defaults={
                'description': 'Comprehensive health platform for organizations, healthcare providers, and research institutions.',
                'price': 19999.00,  # ₹19,999/month
                'billing_cycle': 'MONTHLY',
                'dna_kits_included': 0,  # Unlimited
                'mood_entries_limit': 0,  # Unlimited
                'ai_insights_enabled': True,
                'priority_support': True,
                'data_export_enabled': True,
                'api_access_enabled': True,
                'is_active': True,
                'is_featured': False,
                'sort_order': 4,
            }
        )
        if created:
            self.stdout.write(f'✅ Created: {enterprise_plan.name}')
        else:
            self.stdout.write(f'ℹ️  Already exists: {enterprise_plan.name}')

        # Annual Plans (with discounts)
        basic_annual, created = SubscriptionPlan.objects.get_or_create(
            name='Basic Health (Annual)',
            plan_type='BASIC',
            defaults={
                'description': 'Essential health tracking with DNA insights. Save 20% with annual billing!',
                'price': 23990.00,  # ₹23,990/year (~₹2,000/month - 20% discount)
                'billing_cycle': 'YEARLY',
                'dna_kits_included': 2,  # Bonus kit for annual
                'mood_entries_limit': 0,
                'ai_insights_enabled': True,
                'priority_support': False,
                'data_export_enabled': True,
                'api_access_enabled': False,
                'is_active': True,
                'is_featured': False,
                'sort_order': 5,
            }
        )
        if created:
            self.stdout.write(f'✅ Created: {basic_annual.name}')
        else:
            self.stdout.write(f'ℹ️  Already exists: {basic_annual.name}')

        premium_annual, created = SubscriptionPlan.objects.get_or_create(
            name='Premium Wellness (Annual)',
            plan_type='PREMIUM',
            defaults={
                'description': 'Complete health optimization with advanced AI insights. Save 25% with annual billing!',
                'price': 71990.00,  # ₹71,990/year (~₹6,000/month - 25% discount)
                'billing_cycle': 'YEARLY',
                'dna_kits_included': 5,  # Bonus kits for annual
                'mood_entries_limit': 0,
                'ai_insights_enabled': True,
                'priority_support': True,
                'data_export_enabled': True,
                'api_access_enabled': True,
                'is_active': True,
                'is_featured': True,
                'sort_order': 6,
            }
        )
        if created:
            self.stdout.write(f'✅ Created: {premium_annual.name}')
        else:
            self.stdout.write(f'ℹ️  Already exists: {premium_annual.name}')

        # Lifetime Plan (special offer)
        lifetime_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Lifetime Wellness',
            plan_type='PREMIUM',
            defaults={
                'description': 'One-time payment for lifetime access to all Premium features. Limited time offer!',
                'price': 199999.00,  # ₹1,99,999 lifetime
                'billing_cycle': 'LIFETIME',
                'dna_kits_included': 0,  # Unlimited
                'mood_entries_limit': 0,
                'ai_insights_enabled': True,
                'priority_support': True,
                'data_export_enabled': True,
                'api_access_enabled': True,
                'is_active': True,
                'is_featured': True,
                'sort_order': 7,
            }
        )
        if created:
            self.stdout.write(f'✅ Created: {lifetime_plan.name}')
        else:
            self.stdout.write(f'ℹ️  Already exists: {lifetime_plan.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Subscription plans setup complete!\n'
                f'Created plans: {SubscriptionPlan.objects.count()}\n'
                f'Active plans: {SubscriptionPlan.objects.filter(is_active=True).count()}\n'
                f'Featured plans: {SubscriptionPlan.objects.filter(is_featured=True).count()}'
            )
        ) 