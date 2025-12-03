"""
Example Database Module
Demonstrates database connection and operations.
"""
import sqlite3
from typing import Optional, List, Dict


class DatabaseConnection:
    """Manages database connections and operations."""
    
    def __init__(self, connection_string: str):
        """Initialize database connection."""
        self.connection_string = connection_string
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.connection_string)
        self.conn.row_factory = sqlite3.Row
    
    def insert(self, table: str, data: Dict) -> int:
        """Insert a record into the database."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.conn.cursor()
        cursor.execute(query, list(data.values()))
        self.conn.commit()
        return cursor.lastrowid
    
    def query(self, table: str, conditions: Dict) -> Optional[Dict]:
        """Query a single record from the database."""
        where_clause = ' AND '.join([f"{k} = ?" for k in conditions.keys()])
        query = f"SELECT * FROM {table} WHERE {where_clause}"
        
        cursor = self.conn.cursor()
        cursor.execute(query, list(conditions.values()))
        row = cursor.fetchone()
        
        return dict(row) if row else None
    
    def query_all(self, table: str) -> List[Dict]:
        """Query all records from a table."""
        query = f"SELECT * FROM {table}"
        
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def update(self, table: str, record_id: int, updates: Dict) -> bool:
        """Update a record in the database."""
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        
        cursor = self.conn.cursor()
        cursor.execute(query, list(updates.values()) + [record_id])
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete(self, table: str, record_id: int) -> bool:
        """Delete a record from the database."""
        query = f"DELETE FROM {table} WHERE id = ?"
        
        cursor = self.conn.cursor()
        cursor.execute(query, [record_id])
        self.conn.commit()
        return cursor.rowcount > 0
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


