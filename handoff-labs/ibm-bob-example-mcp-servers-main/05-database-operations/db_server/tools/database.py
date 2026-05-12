"""
Database operation tools for SQLite database management.

This module provides tools for common database operations including:
- Creating and managing tables
- CRUD operations (Create, Read, Update, Delete)
- Query execution
- Schema inspection
"""

import sqlite3
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database file exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount


def create_database_tools(mcp, db_path: str):
    """Register all database tools with the MCP server."""
    
    db_manager = DatabaseManager(db_path)
    
    @mcp.tool()
    def create_table(table_name: str, columns: str) -> str:
        """
        Create a new table in the database.
        
        Args:
            table_name: Name of the table to create
            columns: Column definitions (e.g., "id INTEGER PRIMARY KEY, name TEXT, age INTEGER")
        
        Returns:
            Success message or error details
        
        Example:
            create_table("users", "id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE")
        """
        try:
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            db_manager.execute_update(query)
            logger.info(f"Table '{table_name}' created successfully")
            return f"Table '{table_name}' created successfully"
        except Exception as e:
            error_msg = f"Error creating table: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @mcp.tool()
    def insert_record(table_name: str, data: str) -> str:
        """
        Insert a new record into a table.
        
        Args:
            table_name: Name of the table
            data: JSON string with column-value pairs (e.g., '{"name": "John", "age": 30}')
        
        Returns:
            Success message with row count or error details
        
        Example:
            insert_record("users", '{"name": "Alice", "email": "alice@example.com"}')
        """
        try:
            data_dict = json.loads(data)
            columns = ", ".join(data_dict.keys())
            placeholders = ", ".join(["?" for _ in data_dict])
            values = tuple(data_dict.values())
            
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            rows_affected = db_manager.execute_update(query, values)
            
            logger.info(f"Inserted {rows_affected} record(s) into '{table_name}'")
            return f"Successfully inserted {rows_affected} record(s) into '{table_name}'"
        except Exception as e:
            error_msg = f"Error inserting record: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @mcp.tool()
    def select_records(table_name: str, where_clause: str = "", limit: int = 100) -> str:
        """
        Select records from a table.
        
        Args:
            table_name: Name of the table
            where_clause: Optional WHERE clause (e.g., "age > 25")
            limit: Maximum number of records to return (default: 100)
        
        Returns:
            JSON string with query results or error details
        
        Example:
            select_records("users", "age > 25", 10)
        """
        try:
            query = f"SELECT * FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            query += f" LIMIT {limit}"
            
            results = db_manager.execute_query(query)
            logger.info(f"Retrieved {len(results)} record(s) from '{table_name}'")
            return json.dumps(results, indent=2)
        except Exception as e:
            error_msg = f"Error selecting records: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def update_records(table_name: str, set_clause: str, where_clause: str) -> str:
        """
        Update records in a table.
        
        Args:
            table_name: Name of the table
            set_clause: SET clause with updates (e.g., "age = 31, name = 'John Doe'")
            where_clause: WHERE clause to identify records (e.g., "id = 1")
        
        Returns:
            Success message with row count or error details
        
        Example:
            update_records("users", "age = 31", "id = 1")
        """
        try:
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            rows_affected = db_manager.execute_update(query)
            
            logger.info(f"Updated {rows_affected} record(s) in '{table_name}'")
            return f"Successfully updated {rows_affected} record(s) in '{table_name}'"
        except Exception as e:
            error_msg = f"Error updating records: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @mcp.tool()
    def delete_records(table_name: str, where_clause: str) -> str:
        """
        Delete records from a table.
        
        Args:
            table_name: Name of the table
            where_clause: WHERE clause to identify records (e.g., "age < 18")
        
        Returns:
            Success message with row count or error details
        
        Example:
            delete_records("users", "age < 18")
        """
        try:
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            rows_affected = db_manager.execute_update(query)
            
            logger.info(f"Deleted {rows_affected} record(s) from '{table_name}'")
            return f"Successfully deleted {rows_affected} record(s) from '{table_name}'"
        except Exception as e:
            error_msg = f"Error deleting records: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    @mcp.tool()
    def execute_custom_query(query: str) -> str:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query to execute
        
        Returns:
            JSON string with results for SELECT queries, or success message for other queries
        
        Example:
            execute_custom_query("SELECT COUNT(*) as total FROM users")
        """
        try:
            query_upper = query.strip().upper()
            
            if query_upper.startswith("SELECT"):
                results = db_manager.execute_query(query)
                logger.info(f"Query returned {len(results)} record(s)")
                return json.dumps(results, indent=2)
            else:
                rows_affected = db_manager.execute_update(query)
                logger.info(f"Query affected {rows_affected} record(s)")
                return f"Query executed successfully. Rows affected: {rows_affected}"
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def list_tables() -> str:
        """
        List all tables in the database.
        
        Returns:
            JSON string with list of table names
        
        Example:
            list_tables()
        """
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            results = db_manager.execute_query(query)
            tables = [row["name"] for row in results]
            
            logger.info(f"Found {len(tables)} table(s)")
            return json.dumps({"tables": tables}, indent=2)
        except Exception as e:
            error_msg = f"Error listing tables: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def get_table_schema(table_name: str) -> str:
        """
        Get the schema (column definitions) for a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            JSON string with column information
        
        Example:
            get_table_schema("users")
        """
        try:
            query = f"PRAGMA table_info({table_name})"
            results = db_manager.execute_query(query)
            
            logger.info(f"Retrieved schema for table '{table_name}'")
            return json.dumps(results, indent=2)
        except Exception as e:
            error_msg = f"Error getting table schema: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    logger.info("Database tools registered successfully")

# Made with Bob