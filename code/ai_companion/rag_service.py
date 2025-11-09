"""
RAG (Retrieval-Augmented Generation) Service for AI Companion
Handles document processing, embeddings, vector storage, and retrieval
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from django.conf import settings

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger('ai_companion')


class RAGService:
    """Service for RAG operations: document processing, embeddings, and retrieval"""
    
    def __init__(self):
        """Initialize RAG service with vector database and embeddings"""
        self.embedding_model_name = getattr(
            settings, 
            'RAG_EMBEDDING_MODEL', 
            'sentence-transformers/all-MiniLM-L6-v2'
        )
        self.chroma_persist_directory = getattr(
            settings,
            'RAG_CHROMA_PERSIST_DIR',
            str(Path(settings.BASE_DIR) / 'chroma_db')
        )
        self.collection_name = getattr(
            settings,
            'RAG_COLLECTION_NAME',
            'mental_health_knowledge_base'
        )
        self.chunk_size = getattr(settings, 'RAG_CHUNK_SIZE', 500)
        self.chunk_overlap = getattr(settings, 'RAG_CHUNK_OVERLAP', 50)
        self.top_k_results = getattr(settings, 'RAG_TOP_K_RESULTS', 3)
        
        # Initialize components
        self._initialize_embeddings()
        self._initialize_vector_store()
        self._initialize_text_splitter()
    
    def _initialize_embeddings(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},  # Use 'cuda' if GPU available
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def _initialize_vector_store(self):
        """Initialize ChromaDB vector store"""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.chroma_persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize or get collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"Loaded existing collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Mental health knowledge base for RAG"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
            
            # Initialize LangChain Chroma wrapper
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.chroma_persist_directory
            )
            
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def _initialize_text_splitter(self):
        """Initialize text splitter for document chunking"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        logger.info("Text splitter initialized")
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None) -> bool:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document texts to add
            metadatas: Optional list of metadata dicts for each document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not documents:
                logger.warning("No documents provided to add")
                return False
            
            # Split documents into chunks
            all_chunks = []
            all_metadatas = []
            
            for i, doc in enumerate(documents):
                chunks = self.text_splitter.split_text(doc)
                all_chunks.extend(chunks)
                
                # Add metadata for each chunk
                if metadatas and i < len(metadatas):
                    base_metadata = metadatas[i].copy()
                    for j, chunk in enumerate(chunks):
                        chunk_metadata = base_metadata.copy()
                        chunk_metadata['chunk_index'] = j
                        chunk_metadata['total_chunks'] = len(chunks)
                        all_metadatas.append(chunk_metadata)
                else:
                    # Default metadata
                    for j in range(len(chunks)):
                        all_metadatas.append({
                            'document_index': i,
                            'chunk_index': j,
                            'total_chunks': len(chunks)
                        })
            
            # Add to vector store
            if all_chunks:
                self.vector_store.add_texts(
                    texts=all_chunks,
                    metadatas=all_metadatas
                )
                logger.info(f"Added {len(all_chunks)} chunks from {len(documents)} documents")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    def add_document_from_file(self, file_path: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a document from a file to the vector store
        
        Args:
            file_path: Path to the document file
            metadata: Optional metadata for the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Read file content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata['source_file'] = str(path)
            doc_metadata['file_name'] = path.name
            
            # Add document
            return self.add_documents([content], [doc_metadata])
            
        except Exception as e:
            logger.error(f"Error adding document from file: {str(e)}")
            return False
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Search for relevant documents based on query
        
        Args:
            query: Search query text
            top_k: Number of results to return (defaults to configured value)
            
        Returns:
            List of dictionaries with 'content' and 'metadata' keys
        """
        try:
            if not query or not query.strip():
                logger.warning("Empty query provided")
                return []
            
            top_k = top_k or self.top_k_results
            
            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score)
                })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def get_relevant_context(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Get relevant context as a formatted string for RAG
        
        Args:
            query: Search query
            top_k: Number of results to include
            
        Returns:
            Formatted context string
        """
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        # Format context with citations
        context_parts = []
        for i, result in enumerate(results, 1):
            content = result['content']
            metadata = result.get('metadata', {})
            source = metadata.get('source_file', metadata.get('source', 'Unknown'))
            
            context_parts.append(f"[Source {i}: {source}]\n{content}\n")
        
        return "\n---\n".join(context_parts)
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store collection"""
        try:
            count = self.collection.count()
            return {
                'collection_name': self.collection_name,
                'document_count': count,
                'embedding_model': self.embedding_model_name,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {'error': str(e)}
    
    def reset_collection(self) -> bool:
        """Reset/clear the entire collection"""
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            self._initialize_vector_store()
            logger.info(f"Collection {self.collection_name} reset successfully")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            return False


# Singleton instance
_rag_service_instance = None

def get_rag_service() -> RAGService:
    """Get or create the singleton RAG service instance"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance

