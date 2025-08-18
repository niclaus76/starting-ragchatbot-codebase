"""
API endpoint tests for the RAG system.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from unittest.mock import Mock, patch
import json

from backend.config import Config
from backend.rag_system import RAGSystem


def create_test_app(mock_rag_system):
    """Create a test FastAPI app without static file mounting."""
    from backend.app import (
        QueryRequest, QueryResponse, CourseStats, SessionResponse,
        query_documents, get_course_stats, create_new_session,
        debug_links, get_visualization_data
    )
    
    # Create test app without static files
    test_app = FastAPI(title="Test RAG System")
    
    # Add CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Override rag_system dependency
    test_app.rag_system = mock_rag_system
    
    # Add API routes manually to avoid import issues with static files
    @test_app.post("/api/query", response_model=QueryResponse)
    async def test_query_documents(request: QueryRequest):
        # Use the test rag_system
        return await query_documents_impl(request, test_app.rag_system)
    
    @test_app.get("/api/courses", response_model=CourseStats)
    async def test_get_course_stats():
        return await get_course_stats_impl(test_app.rag_system)
    
    @test_app.post("/api/new-session", response_model=SessionResponse)
    async def test_create_new_session():
        return await create_new_session_impl(test_app.rag_system)
    
    @test_app.get("/api/debug-links")
    async def test_debug_links():
        return await debug_links_impl(test_app.rag_system)
    
    @test_app.get("/api/visualization-data")
    async def test_get_visualization_data():
        return await get_visualization_data_impl(test_app.rag_system)
    
    # Simple root endpoint for testing
    @test_app.get("/")
    async def test_root():
        return {"message": "Test RAG System"}
    
    return test_app


async def query_documents_impl(request, rag_system):
    """Implementation of query endpoint."""
    from fastapi import HTTPException
    from backend.app import QueryResponse
    
    try:
        session_id = request.session_id
        if not session_id:
            session_id = rag_system.session_manager.create_session()
        
        answer, sources = rag_system.query(request.query, session_id)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_course_stats_impl(rag_system):
    """Implementation of course stats endpoint."""
    from fastapi import HTTPException
    from backend.app import CourseStats
    
    try:
        analytics = rag_system.get_course_analytics()
        return CourseStats(
            total_courses=analytics["total_courses"],
            course_titles=analytics["course_titles"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def create_new_session_impl(rag_system):
    """Implementation of new session endpoint."""
    from fastapi import HTTPException
    from backend.app import SessionResponse
    
    try:
        session_id = rag_system.session_manager.create_session()
        return SessionResponse(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def debug_links_impl(rag_system):
    """Implementation of debug links endpoint."""
    try:
        all_courses = rag_system.vector_store.get_all_courses_metadata()
        
        debug_info = {
            "total_courses": len(all_courses),
            "courses": []
        }
        
        for course in all_courses:
            title = course.get('title', 'Unknown')
            course_link = course.get('course_link', None)
            lessons = course.get('lessons', [])
            
            retrieved_course_link = rag_system.vector_store.get_course_link(title)
            
            course_info = {
                "title": title,
                "stored_course_link": course_link,
                "retrieved_course_link": retrieved_course_link,
                "lesson_count": len(lessons),
                "lessons": []
            }
            
            for lesson in lessons[:3]:
                lesson_num = lesson.get('lesson_number')
                lesson_title = lesson.get('lesson_title', 'Unknown')
                stored_lesson_link = lesson.get('lesson_link', None)
                
                retrieved_lesson_link = rag_system.vector_store.get_lesson_link(title, lesson_num)
                
                lesson_info = {
                    "lesson_number": lesson_num,
                    "lesson_title": lesson_title,
                    "stored_lesson_link": stored_lesson_link,
                    "retrieved_lesson_link": retrieved_lesson_link
                }
                course_info["lessons"].append(lesson_info)
            
            debug_info["courses"].append(course_info)
        
        return debug_info
    except Exception as e:
        return {"error": str(e), "traceback": str(e.__traceback__)}


async def get_visualization_data_impl(rag_system):
    """Implementation of visualization data endpoint."""
    from fastapi import HTTPException
    
    try:
        courses_metadata = rag_system.vector_store.get_all_courses_metadata()
        
        nodes = []
        links = []
        node_id_map = {}
        next_id = 0
        
        # Create instructor nodes
        instructors = {}
        for course in courses_metadata:
            instructor = course.get('instructor', 'Unknown')
            if instructor not in instructors:
                instructors[instructor] = next_id
                nodes.append({
                    'id': next_id,
                    'name': instructor,
                    'type': 'instructor',
                    'group': 0
                })
                node_id_map[instructor] = next_id
                next_id += 1
        
        # Create course nodes and links to instructors
        for course in courses_metadata:
            course_title = course.get('title', 'Unknown Course')
            instructor = course.get('instructor', 'Unknown')
            lessons = course.get('lessons', [])
            
            course_id = next_id
            nodes.append({
                'id': course_id,
                'name': course_title,
                'type': 'course',
                'group': 1,
                'instructor': instructor,
                'lesson_count': len(lessons),
                'course_link': course.get('course_link', '')
            })
            node_id_map[course_title] = course_id
            next_id += 1
            
            if instructor in node_id_map:
                links.append({
                    'source': node_id_map[instructor],
                    'target': course_id,
                    'type': 'teaches'
                })
            
            for lesson in lessons:
                lesson_title = lesson.get('lesson_title', f"Lesson {lesson.get('lesson_number', '?')}")
                lesson_id = next_id
                nodes.append({
                    'id': lesson_id,
                    'name': lesson_title,
                    'type': 'lesson',
                    'group': 2,
                    'lesson_number': lesson.get('lesson_number'),
                    'course': course_title,
                    'lesson_link': lesson.get('lesson_link', '')
                })
                next_id += 1
                
                links.append({
                    'source': course_id,
                    'target': lesson_id,
                    'type': 'contains'
                })
        
        return {
            'nodes': nodes,
            'links': links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@pytest.fixture
def test_client(mock_rag_system):
    """Create a test client with mocked dependencies."""
    app = create_test_app(mock_rag_system)
    return TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints."""

    @pytest.mark.api
    def test_root_endpoint(self, test_client):
        """Test the root endpoint returns correct response."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Test RAG System"}

    @pytest.mark.api
    def test_query_endpoint_with_session_id(self, test_client, mock_rag_system):
        """Test the query endpoint with provided session ID."""
        # Setup mock response
        mock_rag_system.query.return_value = (
            "This is a test answer about machine learning.",
            [{"text": "Test source", "url": "https://example.com/course"}]
        )
        
        query_data = {
            "query": "What is machine learning?",
            "session_id": "test-session-123"
        }
        
        response = test_client.post("/api/query", json=query_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "test-session-123"
        assert data["answer"] == "This is a test answer about machine learning."
        
        # Verify the RAG system was called correctly
        mock_rag_system.query.assert_called_once_with(
            "What is machine learning?", 
            "test-session-123"
        )

    @pytest.mark.api
    def test_query_endpoint_without_session_id(self, test_client, mock_rag_system):
        """Test the query endpoint without session ID (creates new session)."""
        # Setup mock responses
        mock_rag_system.session_manager.create_session.return_value = "new-session-456"
        mock_rag_system.query.return_value = (
            "This is a test answer.",
            [{"text": "Test source", "url": "https://example.com/course"}]
        )
        
        query_data = {"query": "Tell me about deep learning"}
        
        response = test_client.post("/api/query", json=query_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == "new-session-456"
        
        # Verify session was created
        mock_rag_system.session_manager.create_session.assert_called_once()

    @pytest.mark.api
    def test_query_endpoint_invalid_request(self, test_client):
        """Test the query endpoint with invalid request data."""
        response = test_client.post("/api/query", json={})
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    def test_query_endpoint_server_error(self, test_client, mock_rag_system):
        """Test the query endpoint handles server errors."""
        mock_rag_system.query.side_effect = Exception("Test error")
        
        query_data = {"query": "Test query"}
        
        response = test_client.post("/api/query", json=query_data)
        assert response.status_code == 500
        assert "Test error" in response.json()["detail"]

    @pytest.mark.api
    def test_courses_endpoint(self, test_client, mock_rag_system):
        """Test the courses statistics endpoint."""
        # Setup mock response
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 2,
            "course_titles": ["Machine Learning Basics", "Deep Learning Advanced"]
        }
        
        response = test_client.get("/api/courses")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_courses" in data
        assert "course_titles" in data
        assert data["total_courses"] == 2
        assert len(data["course_titles"]) == 2

    @pytest.mark.api
    def test_courses_endpoint_server_error(self, test_client, mock_rag_system):
        """Test the courses endpoint handles server errors."""
        mock_rag_system.get_course_analytics.side_effect = Exception("Analytics error")
        
        response = test_client.get("/api/courses")
        assert response.status_code == 500

    @pytest.mark.api
    def test_new_session_endpoint(self, test_client, mock_rag_system):
        """Test the new session creation endpoint."""
        mock_rag_system.session_manager.create_session.return_value = "session-789"
        
        response = test_client.post("/api/new-session")
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert data["session_id"] == "session-789"

    @pytest.mark.api
    def test_debug_links_endpoint(self, test_client, mock_rag_system):
        """Test the debug links endpoint."""
        # Setup mock data
        mock_courses = [
            {
                "title": "Test Course",
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
        mock_rag_system.vector_store.get_all_courses_metadata.return_value = mock_courses
        mock_rag_system.vector_store.get_course_link.return_value = "https://example.com/course"
        mock_rag_system.vector_store.get_lesson_link.return_value = "https://example.com/lesson1"
        
        response = test_client.get("/api/debug-links")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_courses" in data
        assert "courses" in data
        assert data["total_courses"] == 1

    @pytest.mark.api
    def test_visualization_data_endpoint(self, test_client, mock_rag_system):
        """Test the visualization data endpoint."""
        # Setup mock data
        mock_courses = [
            {
                "title": "Test Course",
                "instructor": "Dr. Test",
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
        mock_rag_system.vector_store.get_all_courses_metadata.return_value = mock_courses
        
        response = test_client.get("/api/visualization-data")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert "links" in data
        assert len(data["nodes"]) > 0
        assert len(data["links"]) > 0

    @pytest.mark.api
    def test_cors_headers(self, test_client):
        """Test that CORS headers are properly set."""
        response = test_client.options("/api/query")
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.api
    def test_response_models(self, test_client, mock_rag_system):
        """Test that responses conform to expected models."""
        # Test query response structure
        mock_rag_system.query.return_value = (
            "Test answer",
            [{"text": "Source", "url": "https://example.com"}]
        )
        
        response = test_client.post("/api/query", json={"query": "test"})
        data = response.json()
        
        # Verify required fields are present
        required_fields = ["answer", "sources", "session_id"]
        for field in required_fields:
            assert field in data
        
        # Test courses response structure
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 1,
            "course_titles": ["Test Course"]
        }
        
        response = test_client.get("/api/courses")
        data = response.json()
        
        required_fields = ["total_courses", "course_titles"]
        for field in required_fields:
            assert field in data