# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development
- **Start development server**: `./run.sh` or `cd backend && uv run uvicorn app:app --reload --port 8000`
- **Install dependencies**: `uv sync`
- **Create .env file**: Add `ANTHROPIC_API_KEY=your_key_here` to root directory

### Application Access
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## High-Level Architecture

### Core Components
This is a RAG (Retrieval-Augmented Generation) system built with FastAPI backend and vanilla HTML/JS frontend.

**Main System Flow (rag_system.py)**:
- `RAGSystem` orchestrates all components
- Uses tool-based search architecture via `ToolManager` and `CourseSearchTool`
- Processes queries through AI with function calling, not direct vector similarity

**Backend Structure**:
- `app.py`: FastAPI application with CORS, serves frontend static files, handles API endpoints
- `rag_system.py`: Main orchestrator coordinating all components
- `vector_store.py`: ChromaDB wrapper for embeddings and semantic search
- `ai_generator.py`: Anthropic Claude API client with system prompts and tool support
- `document_processor.py`: Processes course documents into chunks and metadata
- `search_tools.py`: Function calling tools for Claude to search course content
- `session_manager.py`: Manages conversation history per session
- `models.py`: Pydantic models for Course, Lesson, and CourseChunk

**Key Architecture Patterns**:
- Tool-based search: Claude uses function calls to search, not direct RAG retrieval
- Session-based conversations: Each chat session maintains context
- Dual storage: Course metadata + content chunks in separate ChromaDB collections
- Document chunking: 800 char chunks with 100 char overlap for semantic search
- Static file serving: Frontend served from `/frontend` directory

**Data Flow**:
1. Documents in `/docs` loaded on startup into ChromaDB
2. User queries processed by `RAGSystem.query()`
3. Claude AI uses `CourseSearchTool` for content lookup
4. Response generated with conversation history context
5. Session state maintained for follow-up questions

**Configuration**:
- All settings centralized in `config.py`
- Environment variables loaded from `.env`
- ChromaDB persisted in `./chroma_db`
- Uses Claude Sonnet 4 and all-MiniLM-L6-v2 embeddings
- always use uv and not use pip