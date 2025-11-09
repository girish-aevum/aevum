from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from ai_companion.models import Message
import sys


class Command(BaseCommand):
    help = 'Interactive QA review tool for messages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reviewer',
            type=str,
            help='Username of the QA reviewer'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5,
            help='Number of messages to review in this session (default: 5)'
        )
        parser.add_argument(
            '--status',
            type=str,
            default='PENDING',
            choices=[choice[0] for choice in Message.QA_STATUS_CHOICES],
            help='Review messages with this status (default: PENDING)'
        )

    def handle(self, *args, **options):
        reviewer_username = options.get('reviewer')
        batch_size = options['batch_size']
        status = options['status']

        # Get or validate reviewer
        reviewer = None
        if reviewer_username:
            try:
                reviewer = User.objects.get(username=reviewer_username)
                self.stdout.write(f'QA Reviewer: {reviewer.get_full_name() or reviewer.username}')
            except User.DoesNotExist:
                raise CommandError(f'User "{reviewer_username}" not found')

        # Get messages to review
        messages_to_review = Message.objects.filter(
            is_selected_for_qa=True,
            qa_status=status
        )[:batch_size]

        if not messages_to_review.exists():
            self.stdout.write(
                self.style.WARNING(f'No messages with status "{status}" found for review')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting QA review session - {messages_to_review.count()} messages'
            )
        )
        self.stdout.write('='*60)

        reviewed_count = 0
        for i, message in enumerate(messages_to_review, 1):
            self.stdout.write(f'\nMessage {i}/{messages_to_review.count()}')
            self.stdout.write('-' * 40)
            
            # Display message details
            self.display_message_info(message)
            
            # Get review input
            try:
                review_data = self.get_review_input()
                if review_data is None:  # Skip
                    continue
                
                # Apply review
                message.complete_qa_review(
                    score=review_data['score'],
                    status=review_data['status'],
                    feedback=review_data['feedback'],
                    reviewer=reviewer,
                    tags=review_data['tags']
                )
                
                reviewed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Review saved for message {message.message_id}')
                )
                
            except KeyboardInterrupt:
                self.stdout.write('\n\nReview session interrupted by user.')
                break
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error saving review: {e}')
                )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(f'QA Review Session Complete: {reviewed_count} messages reviewed')
        )

    def display_message_info(self, message):
        """Display message information for review"""
        self.stdout.write(f'Message ID: {message.message_id}')
        self.stdout.write(f'Thread: {message.thread.title or "Untitled"}')
        self.stdout.write(f'Sender: {message.get_sender_display()}')
        self.stdout.write(f'Created: {message.created_at.strftime("%Y-%m-%d %H:%M")}')
        
        if message.sender == 'AI':
            if message.confidence_score:
                self.stdout.write(f'AI Confidence: {message.confidence_score:.2f}')
            if message.processing_time_ms:
                self.stdout.write(f'Processing Time: {message.processing_time_ms}ms')
        
        self.stdout.write('\nContent:')
        self.stdout.write('"' + message.content + '"')
        
        # Show user feedback if available
        if message.is_helpful is not None:
            helpful_text = "👍 Helpful" if message.is_helpful else "👎 Not Helpful"
            self.stdout.write(f'\nUser Feedback: {helpful_text}')
            if message.user_feedback:
                self.stdout.write(f'User Comment: "{message.user_feedback}"')

    def get_review_input(self):
        """Get review input from the reviewer"""
        self.stdout.write('\n' + '-' * 20 + ' REVIEW ' + '-' * 20)
        
        # Ask if they want to skip
        skip = input('Skip this message? (y/N): ').lower().strip()
        if skip in ['y', 'yes']:
            return None

        # Get score
        while True:
            try:
                score_input = input('QA Score (0.0 - 10.0): ').strip()
                score = float(score_input)
                if 0.0 <= score <= 10.0:
                    break
                else:
                    self.stdout.write('Score must be between 0.0 and 10.0')
            except ValueError:
                self.stdout.write('Please enter a valid number')

        # Get status
        self.stdout.write('\nStatus options:')
        for i, (code, name) in enumerate(Message.QA_STATUS_CHOICES, 1):
            self.stdout.write(f'{i}. {name} ({code})')
        
        while True:
            try:
                status_input = input('Select status (1-5): ').strip()
                status_index = int(status_input) - 1
                if 0 <= status_index < len(Message.QA_STATUS_CHOICES):
                    status = Message.QA_STATUS_CHOICES[status_index][0]
                    break
                else:
                    self.stdout.write('Please select a valid option (1-5)')
            except ValueError:
                self.stdout.write('Please enter a number')

        # Get feedback
        feedback = input('QA Feedback (optional): ').strip() or None

        # Get tags
        tags = input('Tags (comma-separated, optional): ').strip() or None

        return {
            'score': score,
            'status': status,
            'feedback': feedback,
            'tags': tags
        } 