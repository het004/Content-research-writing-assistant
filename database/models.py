from datetime import datetime
from typing import Optional, Dict, List
import json
import sqlite3
from pathlib import Path

class ContentModel:
    """Model for storing generated content in database"""
    
    def __init__(self):
        self.db_path = Path("data/content.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content_type TEXT NOT NULL,
                target_audience TEXT,
                final_content TEXT,
                word_count INTEGER,
                sources_count INTEGER,
                confidence_score INTEGER,
                revision_made BOOLEAN,
                metadata TEXT,
                citations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                stage TEXT,
                status TEXT,
                message TEXT,
                duration_seconds FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(content_id) REFERENCES generated_content(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_content(self, state: Dict) -> int:
        """Save generated content to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO generated_content 
            (topic, content_type, target_audience, final_content, 
             word_count, sources_count, confidence_score, revision_made, 
             metadata, citations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            state.get('topic'),
            state.get('content_type'),
            state.get('target_audience'),
            state.get('final_content'),
            state.get('metadata', {}).get('word_count'),
            state.get('metadata', {}).get('sources_used'),
            state.get('metadata', {}).get('confidence_score'),
            state.get('metadata', {}).get('revision_made'),
            json.dumps(state.get('metadata', {})),
            json.dumps(state.get('citations', []))
        ))
        
        conn.commit()
        content_id = cursor.lastrowid
        conn.close()
        
        return content_id
    
    def get_content(self, content_id: int) -> Optional[Dict]:
        """Retrieve content from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM generated_content WHERE id = ?",
            (content_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'topic': result[1],
                'content_type': result[2],
                'target_audience': result[3],
                'final_content': result[4],
                'word_count': result[5],
                'sources_count': result[6],
                'confidence_score': result[7],
                'revision_made': result[8],
                'metadata': json.loads(result[9]) if result[9] else {},
                'citations': json.loads(result[10]) if result[10] else [],
                'created_at': result[11]
            }
        
        return None
    
    def get_all_content(self, limit: int = 50) -> List[Dict]:
        """Retrieve all generated content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM generated_content ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'topic': r[1],
                'content_type': r[2],
                'word_count': r[5],
                'confidence_score': r[7],
                'created_at': r[11]
            }
            for r in results
        ]
    
    def delete_content(self, content_id: int) -> bool:
        """Delete content from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM generated_content WHERE id = ?", (content_id,))
        cursor.execute("DELETE FROM execution_logs WHERE content_id = ?", (content_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
