"""
Shared test fixtures and configuration for the RAG system tests.
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any
from fastapi.testclient import TestClient

from backend.config import Config
from backend.models import Course, Lesson, CourseChunk
from backend.rag_system import RAGSystem
from backend.vector_store import VectorStore
from backend.ai_generator import AIGenerator
from backend.session_manager import SessionManager


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    config = Config()
    config.anthropic_api_key = "test-api-key"
    config.chroma_persist_directory = ":memory:"  # Use in-memory database for tests
    config.chunk_size = 800
    config.chunk_overlap = 100
    config.embedding_model_name = "test-embedding-model"
    config.anthropic_model = "claude-3-sonnet-20240229"
    return config


@pytest.fixture
def mock_vector_store():
    """Provide a mock vector store for testing."""
    mock_store = Mock(spec=VectorStore)
    mock_store.add_documents.return_value = None
    mock_store.similarity_search.return_value = [
        {
            "content": "Test content about machine learning",
            "metadata": {
                "course_title": "Test Course",
                "lesson_number": 1,
                "lesson_title": "Introduction",
                "chunk_index": 0
            }
        }
    ]
    mock_store.get_all_courses_metadata.return_value = [
        {
            "title": "Test Course",
            "instructor": "Test Instructor",
            "course_link": "https://example.com/course",
            "lessons": [
                {
                    "lesson_number": 1,
                    "lesson_title": "Introduction",
                    "lesson_link": "https://example.com/lesson1"
                }
            ]
        }
    ]
    mock_store.get_course_link.return_value = "https://example.com/course"
    mock_store.get_lesson_link.return_value = "https://example.com/lesson1"
    return mock_store


@pytest.fixture
def mock_ai_generator():
    """Provide a mock AI generator for testing."""
    mock_ai = Mock(spec=AIGenerator)
    mock_ai.generate_with_tools.return_value = (
        "This is a test response about machine learning basics.",
        [{"text": "Test source", "url": "https://example.com/course"}]
    )
    return mock_ai


@pytest.fixture
def mock_session_manager():
    """Provide a mock session manager for testing."""
    mock_manager = Mock(spec=SessionManager)
    mock_manager.create_session.return_value = "test-session-123"
    mock_manager.get_conversation_history.return_value = []
    mock_manager.add_to_conversation.return_value = None
    return mock_manager


@pytest.fixture
def mock_rag_system(mock_config, mock_vector_store, mock_ai_generator, mock_session_manager):
    """Provide a mock RAG system for testing."""
    with patch('backend.rag_system.VectorStore', return_value=mock_vector_store), \
         patch('backend.rag_system.AIGenerator', return_value=mock_ai_generator), \
         patch('backend.rag_system.SessionManager', return_value=mock_session_manager):
        
        rag_system = RAGSystem(mock_config)
        rag_system.vector_store = mock_vector_store
        rag_system.ai_generator = mock_ai_generator
        rag_system.session_manager = mock_session_manager
        return rag_system


@pytest.fixture
def sample_courses_data():
    """Provide sample course data for testing."""
    return [
        Course(
            title="Machine Learning Basics",
            instructor="Dr. Smith",
            course_link="https://example.com/ml-course",
            lessons=[
                Lesson(
                    lesson_number=1,
                    lesson_title="Introduction to ML",
                    lesson_link="https://example.com/ml-lesson1"
                ),
                Lesson(
                    lesson_number=2,
                    lesson_title="Supervised Learning",
                    lesson_link="https://example.com/ml-lesson2"
                )
            ]
        ),
        Course(
            title="Deep Learning Advanced",
            instructor="Dr. Johnson",
            course_link="https://example.com/dl-course",
            lessons=[
                Lesson(
                    lesson_number=1,
                    lesson_title="Neural Networks",
                    lesson_link="https://example.com/dl-lesson1"
                )
            ]
        )
    ]


@pytest.fixture
def sample_chunks_data():
    """Provide sample chunk data for testing."""
    return [
        CourseChunk(
            content="Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            course_title="Machine Learning Basics",
            lesson_number=1,
            lesson_title="Introduction to ML",
            chunk_index=0
        ),
        CourseChunk(
            content="Supervised learning uses labeled data to train models for prediction tasks.",
            course_title="Machine Learning Basics",
            lesson_number=2,
            lesson_title="Supervised Learning",
            chunk_index=0
        )
    ]


@pytest.fixture
def temp_docs_directory():
    """Create a temporary directory with sample documents for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create sample course documents
    course1_content = """
    Course Title: Machine Learning Basics
    Instructor: Dr. Smith
    Course Link: https://example.com/ml-course

    Lesson 1: Introduction to ML
    Lesson Link: https://example.com/ml-lesson1

    Machine learning is a subset of artificial intelligence that focuses on algorithms.
    It enables computers to learn and make decisions from data without explicit programming.
    
    Lesson 2: Supervised Learning  
    Lesson Link: https://example.com/ml-lesson2
    
    Supervised learning uses labeled data to train models for prediction tasks.
    """
    
    with open(os.path.join(temp_dir, "course1.txt"), "w") as f:
        f.write(course1_content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [
        Mock(text="This is a test response about the query.")
    ]
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()