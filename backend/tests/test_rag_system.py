"""
Unit tests for the RAG system core functionality.
"""

import pytest
from unittest.mock import Mock, patch
from backend.rag_system import RAGSystem
from backend.models import Course, Lesson, CourseChunk


class TestRAGSystem:
    """Test suite for RAG system functionality."""

    @pytest.mark.unit
    def test_rag_system_initialization(self, mock_config):
        """Test RAG system initializes correctly with mocked dependencies."""
        with patch('backend.rag_system.VectorStore') as mock_vector_store, \
             patch('backend.rag_system.AIGenerator') as mock_ai_generator, \
             patch('backend.rag_system.SessionManager') as mock_session_manager:
            
            rag_system = RAGSystem(mock_config)
            
            assert rag_system.config == mock_config
            mock_vector_store.assert_called_once()
            mock_ai_generator.assert_called_once()
            mock_session_manager.assert_called_once()

    @pytest.mark.unit
    def test_query_with_session(self, mock_rag_system):
        """Test query processing with existing session."""
        # Setup mocks
        mock_rag_system.session_manager.get_conversation_history.return_value = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]
        mock_rag_system.ai_generator.generate_with_tools.return_value = (
            "This is a comprehensive answer about machine learning.",
            [{"text": "ML Course", "url": "https://example.com/ml"}]
        )
        
        # Execute query
        answer, sources = mock_rag_system.query("What is machine learning?", "session-123")
        
        # Verify results
        assert isinstance(answer, str)
        assert isinstance(sources, list)
        assert answer == "This is a comprehensive answer about machine learning."
        
        # Verify session manager was called
        mock_rag_system.session_manager.get_conversation_history.assert_called_once_with("session-123")
        mock_rag_system.session_manager.add_to_conversation.assert_called()

    @pytest.mark.unit
    def test_query_without_session(self, mock_rag_system):
        """Test query processing without session creates new one."""
        mock_rag_system.session_manager.create_session.return_value = "new-session-456"
        mock_rag_system.ai_generator.generate_with_tools.return_value = (
            "Answer without session",
            []
        )
        
        # Execute query without session
        answer, sources = mock_rag_system.query("Test query")
        
        # Verify new session was created
        mock_rag_system.session_manager.create_session.assert_called_once()

    @pytest.mark.unit
    def test_add_course_folder(self, mock_rag_system, temp_docs_directory):
        """Test adding courses from folder."""
        # Mock document processor behavior
        mock_courses = [
            Course(
                title="Test Course",
                instructor="Dr. Test",
                course_link="https://example.com/course",
                lessons=[
                    Lesson(
                        lesson_number=1,
                        lesson_title="Introduction",
                        lesson_link="https://example.com/lesson1"
                    )
                ]
            )
        ]
        mock_chunks = [
            CourseChunk(
                content="Test content",
                course_title="Test Course",
                lesson_number=1,
                lesson_title="Introduction",
                chunk_index=0
            )
        ]
        
        with patch('backend.rag_system.DocumentProcessor') as mock_processor_class:
            mock_processor = mock_processor_class.return_value
            mock_processor.process_folder.return_value = (mock_courses, mock_chunks)
            
            # Execute method
            courses_count, chunks_count = mock_rag_system.add_course_folder(temp_docs_directory)
            
            # Verify results
            assert courses_count == 1
            assert chunks_count == 1
            
            # Verify vector store was updated
            mock_rag_system.vector_store.add_documents.assert_called()

    @pytest.mark.unit
    def test_get_course_analytics(self, mock_rag_system):
        """Test course analytics retrieval."""
        # Setup mock data
        mock_courses = [
            {
                "title": "Course 1",
                "instructor": "Dr. A",
                "lessons": [{"lesson_number": 1}]
            },
            {
                "title": "Course 2", 
                "instructor": "Dr. B",
                "lessons": [{"lesson_number": 1}, {"lesson_number": 2}]
            }
        ]
        mock_rag_system.vector_store.get_all_courses_metadata.return_value = mock_courses
        
        # Execute method
        analytics = mock_rag_system.get_course_analytics()
        
        # Verify analytics structure
        assert "total_courses" in analytics
        assert "course_titles" in analytics
        assert "instructors" in analytics
        assert "total_lessons" in analytics
        
        # Verify values
        assert analytics["total_courses"] == 2
        assert len(analytics["course_titles"]) == 2
        assert "Course 1" in analytics["course_titles"]
        assert "Course 2" in analytics["course_titles"]

    @pytest.mark.unit
    def test_error_handling_in_query(self, mock_rag_system):
        """Test error handling during query processing."""
        # Setup mock to raise exception
        mock_rag_system.ai_generator.generate_with_tools.side_effect = Exception("AI generation failed")
        
        # Test that exception is propagated
        with pytest.raises(Exception) as exc_info:
            mock_rag_system.query("Test query", "session-123")
        
        assert "AI generation failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_clear_existing_data(self, mock_rag_system, temp_docs_directory):
        """Test clearing existing data when adding new courses."""
        with patch('backend.rag_system.DocumentProcessor') as mock_processor_class:
            mock_processor = mock_processor_class.return_value
            mock_processor.process_folder.return_value = ([], [])
            
            # Execute with clear_existing=True
            mock_rag_system.add_course_folder(temp_docs_directory, clear_existing=True)
            
            # Verify clear_collection was called
            mock_rag_system.vector_store.clear_collection.assert_called()

    @pytest.mark.unit
    def test_session_history_integration(self, mock_rag_system):
        """Test that conversation history is properly integrated."""
        # Setup conversation history
        conversation_history = [
            {"role": "user", "content": "What is AI?"},
            {"role": "assistant", "content": "AI is artificial intelligence."}
        ]
        mock_rag_system.session_manager.get_conversation_history.return_value = conversation_history
        
        # Execute query
        mock_rag_system.query("Tell me more about machine learning", "session-123")
        
        # Verify AI generator was called with conversation history
        call_args = mock_rag_system.ai_generator.generate_with_tools.call_args
        assert call_args is not None
        
        # Check that conversation history was included in the call
        mock_rag_system.session_manager.get_conversation_history.assert_called_with("session-123")
        mock_rag_system.session_manager.add_to_conversation.assert_called()

    @pytest.mark.integration
    def test_full_workflow(self, mock_config, temp_docs_directory):
        """Integration test for complete RAG workflow."""
        with patch('backend.rag_system.VectorStore') as mock_vector_store_class, \
             patch('backend.rag_system.AIGenerator') as mock_ai_generator_class, \
             patch('backend.rag_system.SessionManager') as mock_session_manager_class, \
             patch('backend.rag_system.DocumentProcessor') as mock_processor_class:
            
            # Setup mocks
            mock_vector_store = Mock()
            mock_ai_generator = Mock()
            mock_session_manager = Mock()
            mock_processor = Mock()
            
            mock_vector_store_class.return_value = mock_vector_store
            mock_ai_generator_class.return_value = mock_ai_generator
            mock_session_manager_class.return_value = mock_session_manager
            mock_processor_class.return_value = mock_processor
            
            # Setup mock responses
            mock_processor.process_folder.return_value = ([], [])
            mock_session_manager.create_session.return_value = "test-session"
            mock_session_manager.get_conversation_history.return_value = []
            mock_ai_generator.generate_with_tools.return_value = ("Test answer", [])
            mock_vector_store.get_all_courses_metadata.return_value = []
            
            # Initialize RAG system
            rag_system = RAGSystem(mock_config)
            
            # Test adding documents
            rag_system.add_course_folder(temp_docs_directory)
            mock_processor.process_folder.assert_called_once()
            
            # Test querying
            answer, sources = rag_system.query("Test query")
            assert answer == "Test answer"
            
            # Test analytics
            analytics = rag_system.get_course_analytics()
            assert "total_courses" in analytics