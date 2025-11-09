"""
Test script to verify RAG integration with the AI Companion endpoint
Run this script to test the RAG system end-to-end
"""

import os
import sys
import django

# Add the code directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
django.setup()

from ai_companion.rag_service import get_rag_service
from django.conf import settings


def test_rag_service():
    """Test the RAG service functionality"""
    print("=" * 60)
    print("RAG Service Test")
    print("=" * 60)
    
    rag_service = get_rag_service()
    
    # Get collection stats
    stats = rag_service.get_collection_stats()
    print(f"\n📊 Knowledge Base Statistics:")
    print(f"   Collection: {stats.get('collection_name')}")
    print(f"   Documents: {stats.get('document_count', 0)}")
    print(f"   Embedding Model: {stats.get('embedding_model')}")
    print(f"   Chunk Size: {stats.get('chunk_size')}")
    
    # Test searches
    print(f"\n🔍 Testing Search Functionality:")
    test_queries = [
        "anxiety management techniques",
        "depression symptoms",
        "stress relief methods"
    ]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        results = rag_service.search(query, top_k=2)
        
        if results:
            print(f"   ✓ Found {len(results)} relevant documents")
            for i, result in enumerate(results, 1):
                score = result.get('similarity_score', 0)
                content = result.get('content', '')[:80]
                print(f"      [{i}] Similarity: {score:.4f} | {content}...")
        else:
            print(f"   ✗ No results found")
    
    print("\n" + "=" * 60)
    print("✅ RAG Service Test Complete")
    print("=" * 60)


def test_rag_configuration():
    """Test RAG configuration"""
    print("\n" + "=" * 60)
    print("RAG Configuration Check")
    print("=" * 60)
    
    config = {
        'RAG_ENABLED': getattr(settings, 'RAG_ENABLED', True),
        'RAG_EMBEDDING_MODEL': getattr(settings, 'RAG_EMBEDDING_MODEL', ''),
        'RAG_TOP_K_RESULTS': getattr(settings, 'RAG_TOP_K_RESULTS', 3),
        'RAG_CHUNK_SIZE': getattr(settings, 'RAG_CHUNK_SIZE', 500),
    }
    
    print("\n📋 Current Configuration:")
    for key, value in config.items():
        status = "✓" if value else "✗"
        print(f"   {status} {key}: {value}")
    
    if config['RAG_ENABLED']:
        print("\n✅ RAG is ENABLED - Endpoint will use RAG")
    else:
        print("\n⚠️  RAG is DISABLED - Endpoint will not use RAG")
    
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_rag_configuration()
        test_rag_service()
        print("\n🎉 All tests passed! RAG system is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Start your Django server: python manage.py runserver")
        print("   2. Test the endpoint: POST /api/ai-companion/ai-companion-raw/")
        print("   3. Add more documents: python manage.py add_rag_documents --directory <path>")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

