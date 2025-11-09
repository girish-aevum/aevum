"""
Management command to add documents to the RAG knowledge base
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import os

from ai_companion.rag_service import get_rag_service


class Command(BaseCommand):
    help = 'Add documents to the RAG knowledge base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to a file to add to the knowledge base',
        )
        parser.add_argument(
            '--text',
            type=str,
            help='Text content to add directly',
        )
        parser.add_argument(
            '--title',
            type=str,
            help='Title/name for the document',
            default='Manual Entry'
        )
        parser.add_argument(
            '--source',
            type=str,
            help='Source identifier for the document',
            default='manual'
        )
        parser.add_argument(
            '--directory',
            type=str,
            help='Directory containing multiple files to add',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset/clear the knowledge base before adding documents',
        )

    def handle(self, *args, **options):
        rag_service = get_rag_service()
        
        # Reset collection if requested
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting knowledge base...'))
            if rag_service.reset_collection():
                self.stdout.write(self.style.SUCCESS('Knowledge base reset successfully'))
            else:
                self.stdout.write(self.style.ERROR('Failed to reset knowledge base'))
                return
        
        # Get collection stats
        stats = rag_service.get_collection_stats()
        self.stdout.write(f"Current knowledge base: {stats.get('document_count', 0)} documents")
        
        documents_added = 0
        
        # Add single file
        if options['file']:
            file_path = options['file']
            if os.path.exists(file_path):
                metadata = {
                    'title': options['title'],
                    'source': options['source'],
                    'file_path': file_path
                }
                if rag_service.add_document_from_file(file_path, metadata):
                    self.stdout.write(self.style.SUCCESS(f'✓ Added file: {file_path}'))
                    documents_added += 1
                else:
                    self.stdout.write(self.style.ERROR(f'✗ Failed to add file: {file_path}'))
            else:
                self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        
        # Add text directly
        if options['text']:
            metadata = {
                'title': options['title'],
                'source': options['source']
            }
            if rag_service.add_documents([options['text']], [metadata]):
                self.stdout.write(self.style.SUCCESS('✓ Added text content'))
                documents_added += 1
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to add text content'))
        
        # Add directory of files
        if options['directory']:
            dir_path = Path(options['directory'])
            if dir_path.exists() and dir_path.is_dir():
                files = list(dir_path.glob('*.txt')) + list(dir_path.glob('*.md'))
                
                for file_path in files:
                    metadata = {
                        'title': file_path.stem,
                        'source': 'directory_import',
                        'file_path': str(file_path)
                    }
                    if rag_service.add_document_from_file(str(file_path), metadata):
                        self.stdout.write(self.style.SUCCESS(f'✓ Added: {file_path.name}'))
                        documents_added += 1
                    else:
                        self.stdout.write(self.style.ERROR(f'✗ Failed: {file_path.name}'))
                
                self.stdout.write(f'\nProcessed {len(files)} files from directory')
            else:
                self.stdout.write(self.style.ERROR(f'Directory not found: {dir_path}'))
        
        # Show final stats
        if documents_added > 0:
            stats = rag_service.get_collection_stats()
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully added {documents_added} document(s)'
                )
            )
            self.stdout.write(f"Knowledge base now contains: {stats.get('document_count', 0)} documents")
        else:
            self.stdout.write(self.style.WARNING('No documents were added. Use --file, --text, or --directory'))

