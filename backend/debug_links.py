#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from vector_store import VectorStore

def test_links():
    # Initialize vector store
    vector_store = VectorStore(
        chroma_path=config.CHROMA_PATH,
        embedding_model=config.EMBEDDING_MODEL,
        max_results=config.MAX_RESULTS
    )
    
    print("=== Testing Link Retrieval ===")
    
    # Get all courses metadata to see what's stored
    courses_metadata = vector_store.get_all_courses_metadata()
    print(f"\nFound {len(courses_metadata)} courses:")
    
    for course in courses_metadata:
        title = course.get('title', 'Unknown')
        course_link = course.get('course_link', 'None')
        lessons = course.get('lessons', [])
        
        print(f"\nCourse: {title}")
        print(f"Course Link: {course_link}")
        print(f"Lessons: {len(lessons)}")
        
        # Test course link retrieval
        retrieved_course_link = vector_store.get_course_link(title)
        print(f"Retrieved course link: {retrieved_course_link}")
        
        # Test first few lesson links
        for i, lesson in enumerate(lessons[:3]):
            lesson_num = lesson.get('lesson_number')
            lesson_title = lesson.get('lesson_title', 'Unknown')
            lesson_link = lesson.get('lesson_link', 'None')
            
            print(f"  Lesson {lesson_num}: {lesson_title}")
            print(f"  Stored link: {lesson_link}")
            
            # Test lesson link retrieval
            retrieved_lesson_link = vector_store.get_lesson_link(title, lesson_num)
            print(f"  Retrieved link: {retrieved_lesson_link}")
            print()

if __name__ == "__main__":
    test_links()