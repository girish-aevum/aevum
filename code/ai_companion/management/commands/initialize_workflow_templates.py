from django.core.management.base import BaseCommand
from ai_companion.workflow_service import initialize_workflow_templates

class Command(BaseCommand):
    help = 'Initialize workflow templates for AI Companion'

    def handle(self, *args, **options):
        """
        Run workflow template initialization
        """
        self.stdout.write('Initializing workflow templates...')
        
        try:
            initialize_workflow_templates()
            self.stdout.write(self.style.SUCCESS('Successfully initialized workflow templates'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing templates: {str(e)}')) 