import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = "sites.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id TEXT PRIMARY KEY,
            product_type TEXT,
            design_style TEXT,
            reference_url TEXT,
            html_content TEXT,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TIMESTAMP,
            meta_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_pending_site(site_id: str, data: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO sites (id, product_type, design_style, reference_url, status, created_at, meta_data)
        VALUES (?, ?, ?, ?, 'pending', ?, ?)
    ''', (
        site_id,
        data.get("product_type"),
        data.get("design_style"),
        data.get("reference_url"),
        datetime.now(),
        json.dumps(data)
    ))
    conn.commit()
    conn.close()

def update_site_success_with_meta(site_id: str, html_content: str, meta_data: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE sites 
        SET html_content = ?, status = 'completed', meta_data = ?
        WHERE id = ?
    ''', (html_content, json.dumps(meta_data), site_id))
    conn.commit()
    conn.close()

def update_site_success(site_id: str, html_content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE sites 
        SET html_content = ?, status = 'completed'
        WHERE id = ?
    ''', (html_content, site_id))
    conn.commit()
    conn.close()

def update_site_error(site_id: str, error_message: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE sites 
        SET error_message = ?, status = 'error'
        WHERE id = ?
    ''', (error_message, site_id))
    conn.commit()
    conn.close()

def get_site(site_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM sites WHERE id = ?', (site_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_all_sites() -> List[Dict[str, Any]]:
    """Get all completed sites for gallery"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT id, product_type, design_style, reference_url, created_at, html_content 
        FROM sites 
        WHERE status = 'completed'
        ORDER BY created_at DESC
    ''')
    result = [dict(row) for row in c.fetchall()]
    conn.close()
    return result

def delete_site(site_id: str) -> bool:
    """Delete a site by ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM sites WHERE id = ?', (site_id,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# Initialize on module load
init_db()
