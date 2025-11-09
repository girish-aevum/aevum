import os
import webbrowser
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime


class Command(BaseCommand):
    help = 'Preview email templates in browser'

    def add_arguments(self, parser):
        parser.add_argument(
            'template',
            choices=['password_reset', 'welcome'],
            help='Email template to preview'
        )
        parser.add_argument(
            '--user-name',
            default='John Doe',
            help='User name for template context'
        )
        parser.add_argument(
            '--no-open',
            action='store_true',
            help="Don't automatically open browser"
        )

    def handle(self, *args, **options):
        template_name = options['template']
        user_name = options['user_name']
        no_open = options['no_open']
        
        # Create previews directory inside templates
        previews_dir = os.path.join(settings.BASE_DIR, 'templates', 'previews')
        os.makedirs(previews_dir, exist_ok=True)
        
        # Prepare context based on template
        if template_name == 'password_reset':
            context = {
                'user_name': user_name,
                'reset_url': 'http://localhost:3000/reset-password?token=PREVIEW_TOKEN_123',
                'current_year': datetime.now().year
            }
            template_path = 'emails/password_reset.html'
            output_file = 'password_reset_preview.html'
            
        elif template_name == 'welcome':
            context = {
                'user_name': user_name,
                'dashboard_url': 'http://localhost:3000/dashboard',
                'current_year': datetime.now().year
            }
            template_path = 'emails/welcome.html'
            output_file = 'welcome_email_preview.html'
        
        try:
            # Render template
            html_content = render_to_string(template_path, context)
            
            # Write to previews directory inside templates
            preview_path = os.path.join(previews_dir, output_file)
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Relative path for display
            relative_path = os.path.join('templates', 'previews', output_file)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email preview generated: {relative_path}')
            )
            
            # Open in browser
            if not no_open:
                file_url = f'file://{preview_path}'
                webbrowser.open(file_url)
                self.stdout.write(
                    self.style.SUCCESS(f'🌐 Opening preview in browser...')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'📁 Preview saved to: {preview_path}')
                )
                
            self.stdout.write('')
            self.stdout.write('Template Context:')
            for key, value in context.items():
                self.stdout.write(f'  {key}: {value}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error generating preview: {e}')
            ) 