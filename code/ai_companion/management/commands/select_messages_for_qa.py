from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from ai_companion.models import Message
import random


class Command(BaseCommand):
    help = 'Randomly select AI messages for QA testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of messages to select for QA (default: 10)'
        )
        parser.add_argument(
            '--sender',
            type=str,
            default='AI',
            choices=['AI', 'USER'],
            help='Type of messages to select (default: AI)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Include messages already selected for QA'
        )
        parser.add_argument(
            '--min-length',
            type=int,
            default=20,
            help='Minimum message content length (default: 20 characters)'
        )

    def handle(self, *args, **options):
        count = options['count']
        sender = options['sender']
        force = options['force']
        min_length = options['min_length']

        self.stdout.write(
            self.style.SUCCESS(f'Selecting {count} {sender} messages for QA testing...')
        )

        # Build query filters
        filters = {
            'sender': sender,
            'content__length__gte': min_length,
        }
        
        if not force:
            filters['is_selected_for_qa'] = False

        # Get eligible messages
        eligible_messages = Message.objects.filter(**filters)
        
        if not eligible_messages.exists():
            raise CommandError(f'No eligible {sender} messages found for QA selection')

        total_eligible = eligible_messages.count()
        self.stdout.write(f'Found {total_eligible} eligible messages')

        # Randomly select messages
        if count > total_eligible:
            self.stdout.write(
                self.style.WARNING(
                    f'Requested {count} messages but only {total_eligible} available. '
                    f'Selecting all {total_eligible} messages.'
                )
            )
            count = total_eligible

        # Use random sampling
        selected_messages = random.sample(list(eligible_messages), count)

        # Mark selected messages for QA
        updated_count = 0
        for message in selected_messages:
            message.select_for_qa()
            updated_count += 1
            
            self.stdout.write(
                f'Selected: {message.message_id} - '
                f'{message.content[:50]}{"..." if len(message.content) > 50 else ""}'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully selected {updated_count} messages for QA testing!'
            )
        )

        # Show summary statistics
        self.show_qa_summary()

    def show_qa_summary(self):
        """Show current QA statistics"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('QA TESTING SUMMARY'))
        self.stdout.write('='*50)

        # Overall stats
        total_messages = Message.objects.count()
        qa_selected = Message.objects.filter(is_selected_for_qa=True).count()
        
        self.stdout.write(f'Total Messages: {total_messages}')
        self.stdout.write(f'Selected for QA: {qa_selected} ({qa_selected/total_messages*100:.1f}%)')

        # Status breakdown
        for status_code, status_name in Message.QA_STATUS_CHOICES:
            count = Message.objects.filter(qa_status=status_code).count()
            if count > 0:
                self.stdout.write(f'{status_name}: {count}')

        # Score statistics
        reviewed_messages = Message.objects.filter(qa_score__isnull=False)
        if reviewed_messages.exists():
            scores = [msg.qa_score for msg in reviewed_messages]
            avg_score = sum(scores) / len(scores)
            self.stdout.write(f'Average QA Score: {avg_score:.2f}/10.0')
            
            # Grade distribution
            grades = {}
            for msg in reviewed_messages:
                grade = msg.qa_score_grade
                grades[grade] = grades.get(grade, 0) + 1
            
            self.stdout.write('Grade Distribution:')
            for grade, count in sorted(grades.items()):
                self.stdout.write(f'  {grade}: {count}') 