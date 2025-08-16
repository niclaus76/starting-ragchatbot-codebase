import warnings
warnings.filterwarnings("ignore", message="resource_tracker: There appear to be.*")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from typing import List, Optional
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
    sources: List[str]
    session_id: str

class CourseStats(BaseModel):
    """Response model for course statistics"""
    total_courses: int
    course_titles: List[str]

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