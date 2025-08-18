import warnings
warnings.filterwarnings("ignore", message="resource_tracker: There appear to be.*")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
import os

from config import config
from rag_system import RAGSystem

# Initialize FastAPI app
app = FastAPI(title="Course Materials RAG System", root_path="")

# Add trusted host middleware for proxy
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Enable CORS with proper settings for proxy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize RAG system
rag_system = RAGSystem(config)

# Pydantic models for request/response
class QueryRequest(BaseModel):
    """Request model for course queries"""
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    """Response model for course queries"""
    answer: str
    sources: List[Union[str, Dict[str, Any]]]  # Support both strings and objects with text/url
    session_id: str

class CourseStats(BaseModel):
    """Response model for course statistics"""
    total_courses: int
    course_titles: List[str]

class SessionResponse(BaseModel):
    """Response model for new session creation"""
    session_id: str

# API Endpoints

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Process a query and return response with sources"""
    try:
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session_id = rag_system.session_manager.create_session()
        
        # Process query using RAG system
        answer, sources = rag_system.query(request.query, session_id)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses", response_model=CourseStats)
async def get_course_stats():
    """Get course analytics and statistics"""
    try:
        analytics = rag_system.get_course_analytics()
        return CourseStats(
            total_courses=analytics["total_courses"],
            course_titles=analytics["course_titles"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/new-session", response_model=SessionResponse)
async def create_new_session():
    """Create a new chat session"""
    try:
        session_id = rag_system.session_manager.create_session()
        return SessionResponse(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debug-links")
async def debug_links():
    """Debug endpoint to check if lesson links are accessible"""
    try:
        # Get all course metadata to see what's stored
        all_courses = rag_system.vector_store.get_all_courses_metadata()
        
        debug_info = {
            "total_courses": len(all_courses),
            "courses": []
        }
        
        for course in all_courses:
            title = course.get('title', 'Unknown')
            course_link = course.get('course_link', None)
            lessons = course.get('lessons', [])
            
            # Test course link retrieval
            retrieved_course_link = rag_system.vector_store.get_course_link(title)
            
            course_info = {
                "title": title,
                "stored_course_link": course_link,
                "retrieved_course_link": retrieved_course_link,
                "lesson_count": len(lessons),
                "lessons": []
            }
            
            # Test first 3 lesson links
            for lesson in lessons[:3]:
                lesson_num = lesson.get('lesson_number')
                lesson_title = lesson.get('lesson_title', 'Unknown')
                stored_lesson_link = lesson.get('lesson_link', None)
                
                # Test lesson link retrieval
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

@app.get("/api/visualization-data")
async def get_visualization_data():
    """Get course data for visualization"""
    try:
        # Get detailed course metadata for visualization
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
            
            # Course node
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
            
            # Link course to instructor
            if instructor in node_id_map:
                links.append({
                    'source': node_id_map[instructor],
                    'target': course_id,
                    'type': 'teaches'
                })
            
            # Create lesson nodes and links to course
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
                
                # Link lesson to course
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

@app.on_event("startup")
async def startup_event():
    """Load initial documents on startup"""
    docs_path = "../docs"
    if os.path.exists(docs_path):
        print("Loading initial documents...")
        try:
            courses, chunks = rag_system.add_course_folder(docs_path, clear_existing=False)
            print(f"Loaded {courses} courses with {chunks} chunks")
        except Exception as e:
            print(f"Error loading documents: {e}")

# Custom static file handler with no-cache headers for development
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path


class DevStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if isinstance(response, FileResponse):
            # Add no-cache headers for development
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
    
    
# Serve static files for the frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")