# RAG (Retrieval-Augmented Generation) System

## Overview
The RAG system enhances the AI Companion by providing evidence-based responses grounded in a curated knowledge base. Instead of relying solely on the LLM's training data, the system retrieves relevant context from a vector database before generating responses.

## Architecture

### Components
1. **Vector Database (ChromaDB)**: Stores document embeddings for fast similarity search
2. **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` - Converts text to vectors
3. **Text Splitter**: Chunks documents into optimal sizes (500 chars with 50 char overlap)
4. **RAG Service**: Handles document ingestion, search, and retrieval

### How It Works
1. User sends a query to the AI Companion endpoint
2. RAG service searches the knowledge base for relevant documents
3. Top K most relevant chunks are retrieved (default: 3)
4. Retrieved context is added to the system prompt
5. LLM generates response using both the context and its training data
6. Response includes source citations when available

## Configuration

### Settings (in `settings.py`)
```python
RAG_ENABLED = True  # Enable/disable RAG
RAG_EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
RAG_CHROMA_PERSIST_DIR = 'chroma_db'  # Storage location
RAG_COLLECTION_NAME = 'mental_health_knowledge_base'
RAG_CHUNK_SIZE = 500  # Characters per chunk
RAG_CHUNK_OVERLAP = 50  # Overlap between chunks
RAG_TOP_K_RESULTS = 3  # Number of results to retrieve
```

## Usage

### Adding Documents to Knowledge Base

#### Using Management Command
```bash
# Add a single file
python manage.py add_rag_documents --file path/to/document.txt --title "Document Title" --source "source_name"

# Add text directly
python manage.py add_rag_documents --text "Your document content here" --title "Title" --source "manual"

# Add all files from a directory
python manage.py add_rag_documents --directory path/to/documents/

# Reset knowledge base (clears all documents)
python manage.py add_rag_documents --reset
```

#### Using Python Code
```python
from ai_companion.rag_service import get_rag_service

rag_service = get_rag_service()

# Add a document from file
rag_service.add_document_from_file(
    'path/to/document.txt',
    metadata={'title': 'Document Title', 'source': 'source_name'}
)

# Add text directly
rag_service.add_documents(
    ['Document content here'],
    [{'title': 'Title', 'source': 'manual'}]
)

# Search for relevant documents
results = rag_service.search('anxiety management', top_k=3)

# Get formatted context
context = rag_service.get_relevant_context('depression support')
```

### API Endpoint
The `ai_companion_raw` endpoint automatically uses RAG when enabled:

```bash
curl -X POST http://localhost:8000/api/ai-companion/ai-companion-raw/ \
  -H 'Content-Type: application/json' \
  -d '{"text": "Tell me about managing anxiety"}'
```

**Response includes:**
- `text`: AI-generated response (enhanced with RAG context)
- `status`: Response status
- `rag_enabled`: Whether RAG was used
- `rag_sources`: List of source documents used (if any)

## Knowledge Base Structure

### Sample Documents
Sample mental health documents are included in `knowledge_base/`:
- `anxiety_management.txt` - Anxiety coping strategies
- `depression_support.txt` - Depression information and support
- `stress_management.txt` - Stress management techniques

### Adding Your Own Documents
1. Create text files with your content
2. Use the management command to add them:
   ```bash
   python manage.py add_rag_documents --directory ai_companion/knowledge_base/
   ```

## Best Practices

### Document Format
- Use clear, structured content
- Include headings and sections
- Keep paragraphs focused and concise
- Add metadata (title, source) when possible

### Content Quality
- Use evidence-based information
- Keep content accurate and up-to-date
- Focus on actionable advice
- Include disclaimers when appropriate

### Maintenance
- Regularly update documents with new information
- Review and remove outdated content
- Monitor search results for relevance
- Check collection stats periodically

## Troubleshooting

### No Results Returned
- Knowledge base may be empty - add documents first
- Query may not match any content - try rephrasing
- Check if RAG is enabled in settings

### Poor Quality Results
- Increase `RAG_TOP_K_RESULTS` to retrieve more context
- Adjust `RAG_CHUNK_SIZE` for better chunking
- Review document quality and structure

### Performance Issues
- Embedding model loads on first use (may take time)
- Consider using GPU for faster embeddings
- Monitor vector database size

## Technical Details

### Embedding Model
- Model: `all-MiniLM-L6-v2`
- Dimensions: 384
- Speed: Fast (optimized for speed vs. accuracy)
- Alternative models can be configured in settings

### Vector Database
- Storage: Persistent on disk
- Location: `chroma_db/` directory
- Collection: `mental_health_knowledge_base`
- Reset: Use `--reset` flag or `reset_collection()` method

### Text Chunking
- Strategy: Recursive character text splitter
- Chunk size: 500 characters
- Overlap: 50 characters
- Separators: Paragraphs, sentences, words

## Future Enhancements
- Support for PDF, DOCX, and other file formats
- Automatic document updates and versioning
- Multi-language support
- Advanced filtering and metadata search
- Hybrid search (semantic + keyword)

