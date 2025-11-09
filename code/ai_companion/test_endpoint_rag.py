"""
Test script to verify the API endpoint is using RAG correctly
This simulates a real API call to test the RAG integration
"""

import os
import sys
import django
import json

# Add the code directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from ai_companion.views import ai_companion_raw
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request


def test_endpoint_with_rag():
    """Test the endpoint with RAG integration"""
    print("=" * 70)
    print("Testing AI Companion Endpoint with RAG Integration")
    print("=" * 70)
    
    # Create a test request
    factory = APIRequestFactory()
    
    test_queries = [
        {
            "text": "Tell me about managing anxiety",
            "description": "Anxiety management query"
        },
        {
            "text": "What are the symptoms of depression?",
            "description": "Depression symptoms query"
        },
        {
            "text": "How can I manage stress effectively?",
            "description": "Stress management query"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test_case['description']}")
        print(f"{'='*70}")
        print(f"Query: \"{test_case['text']}\"")
        print()
        
        try:
            # Create POST request
            request = factory.post(
                '/api/ai-companion/ai-companion-raw/',
                data={'text': test_case['text']},
                format='json'
            )
            
            # Make request anonymous (no auth required for this endpoint)
            request.user = AnonymousUser()
            
            # Call the view
            response = ai_companion_raw(request)
            
            # Parse response
            if hasattr(response, 'data'):
                response_data = response.data
            else:
                response_data = json.loads(response.content.decode()) if response.content else {}
            
            # Display results
            status = response_data.get('status', 'unknown')
            rag_enabled = response_data.get('rag_enabled', False)
            rag_sources = response_data.get('rag_sources', [])
            response_text = response_data.get('text', '')
            
            print(f"Status: {status}")
            print(f"RAG Enabled: {rag_enabled}")
            
            if rag_sources:
                print(f"RAG Sources Used: {len(rag_sources)}")
                for source in rag_sources:
                    print(f"  - {source}")
            else:
                print("RAG Sources: None (knowledge base may be empty or no matches)")
            
            print(f"\nResponse Preview:")
            preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
            print(f"  {preview}")
            
            # Check if RAG was used
            if rag_enabled and rag_sources:
                print(f"\n✅ RAG Integration: SUCCESS - Context retrieved from knowledge base")
            elif rag_enabled and not rag_sources:
                print(f"\n⚠️  RAG Enabled but no sources found - Knowledge base may need more documents")
            else:
                print(f"\n⚠️  RAG is disabled in settings")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("✅ Endpoint Testing Complete")
    print(f"{'='*70}")


def test_rag_service_directly():
    """Test RAG service directly to verify it's working"""
    print("\n" + "=" * 70)
    print("Verifying RAG Service Directly")
    print("=" * 70)
    
    try:
        from ai_companion.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        
        # Test search
        test_query = "anxiety management techniques"
        print(f"\nTesting search with query: '{test_query}'")
        
        results = rag_service.search(test_query, top_k=3)
        
        if results:
            print(f"✅ Found {len(results)} relevant documents")
            for i, result in enumerate(results, 1):
                score = result.get('similarity_score', 0)
                content_preview = result.get('content', '')[:100]
                print(f"  [{i}] Score: {score:.4f} | {content_preview}...")
        else:
            print("⚠️  No results found - Knowledge base may be empty")
        
        # Get stats
        stats = rag_service.get_collection_stats()
        print(f"\n📊 Knowledge Base Stats:")
        print(f"  Documents: {stats.get('document_count', 0)}")
        print(f"  Collection: {stats.get('collection_name')}")
        
    except Exception as e:
        print(f"❌ Error testing RAG service: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("\n🧪 Starting RAG Endpoint Tests\n")
    
    # First verify RAG service is working
    test_rag_service_directly()
    
    # Then test the endpoint
    test_endpoint_with_rag()
    
    print("\n" + "=" * 70)
    print("💡 Next Steps:")
    print("  1. Start Django server: python manage.py runserver")
    print("  2. Test with curl or Postman")
    print("  3. Add more documents to knowledge base")
    print("  4. Monitor response quality and adjust parameters")
    print("=" * 70)

