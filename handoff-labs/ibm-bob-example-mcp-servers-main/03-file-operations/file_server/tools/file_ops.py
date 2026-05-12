"""
File operation tools for reading, writing, searching, and manipulating files.

This module provides tools for common file system operations including:
- Reading and writing files
- Searching file contents
- Directory operations
- File metadata and statistics
"""

import os
import json
import logging
import shutil
import glob
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class FileOperations:
    """Manages file system operations."""
    
    def __init__(self, base_path: str, encoding: str = "utf-8", max_file_size: int = 10485760):
        self.base_path = Path(base_path).resolve()
        self.encoding = encoding
        self.max_file_size = max_file_size
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to base_path and ensure it's within base_path."""
        resolved = (self.base_path / path).resolve()
        
        # Security check: ensure path is within base_path
        try:
            resolved.relative_to(self.base_path)
        except ValueError:
            raise ValueError(f"Path {path} is outside the allowed base directory")
        
        return resolved
    
    def _check_file_size(self, path: Path) -> None:
        """Check if file size is within limits."""
        if path.exists() and path.stat().st_size > self.max_file_size:
            raise ValueError(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")


def create_file_tools(mcp, base_path: str, encoding: str, max_file_size: int):
    """Register all file operation tools with the MCP server."""
    
    file_ops = FileOperations(base_path, encoding, max_file_size)
    
    @mcp.tool()
    def read_file(path: str, start_line: int = 0, end_line: int = -1) -> str:
        """
        Read contents of a file.
        
        Args:
            path: Path to the file (relative to base directory)
            start_line: Starting line number (0-indexed, default: 0)
            end_line: Ending line number (-1 for end of file, default: -1)
        
        Returns:
            JSON string with file contents and metadata
        
        Example:
            read_file("config.json")
            read_file("large_file.txt", 100, 200)
        """
        try:
            file_path = file_ops._resolve_path(path)
            
            if not file_path.exists():
                return json.dumps({"error": f"File not found: {path}"})
            
            if not file_path.is_file():
                return json.dumps({"error": f"Path is not a file: {path}"})
            
            file_ops._check_file_size(file_path)
            
            with open(file_path, 'r', encoding=file_ops.encoding) as f:
                lines = f.readlines()
            
            # Handle line range
            if end_line == -1:
                end_line = len(lines)
            
            selected_lines = lines[start_line:end_line]
            content = ''.join(selected_lines)
            
            result = {
                "path": path,
                "total_lines": len(lines),
                "start_line": start_line,
                "end_line": end_line,
                "lines_returned": len(selected_lines),
                "content": content
            }
            
            logger.info(f"Read file: {path} (lines {start_line}-{end_line})")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def write_file(path: str, content: str, mode: str = "w") -> str:
        """
        Write content to a file.
        
        Args:
            path: Path to the file (relative to base directory)
            content: Content to write
            mode: Write mode - "w" (overwrite) or "a" (append)
        
        Returns:
            Success message or error details
        
        Example:
            write_file("output.txt", "Hello, World!")
            write_file("log.txt", "New entry\\n", "a")
        """
        try:
            if mode not in ["w", "a"]:
                return json.dumps({"error": "Mode must be 'w' (write) or 'a' (append)"})
            
            file_path = file_ops._resolve_path(path)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, mode, encoding=file_ops.encoding) as f:
                f.write(content)
            
            result = {
                "path": path,
                "mode": mode,
                "bytes_written": len(content.encode(file_ops.encoding)),
                "message": f"Successfully {'wrote to' if mode == 'w' else 'appended to'} file"
            }
            
            logger.info(f"Wrote to file: {path} (mode: {mode})")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error writing file: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def delete_file(path: str) -> str:
        """
        Delete a file.
        
        Args:
            path: Path to the file (relative to base directory)
        
        Returns:
            Success message or error details
        
        Example:
            delete_file("temp.txt")
        """
        try:
            file_path = file_ops._resolve_path(path)
            
            if not file_path.exists():
                return json.dumps({"error": f"File not found: {path}"})
            
            if not file_path.is_file():
                return json.dumps({"error": f"Path is not a file: {path}"})
            
            file_path.unlink()
            
            logger.info(f"Deleted file: {path}")
            return json.dumps({"message": f"Successfully deleted file: {path}"})
        except Exception as e:
            error_msg = f"Error deleting file: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def list_directory(path: str = ".", recursive: bool = False, pattern: str = "*") -> str:
        """
        List files and directories.
        
        Args:
            path: Directory path (relative to base directory, default: ".")
            recursive: List recursively (default: False)
            pattern: Glob pattern to filter results (default: "*")
        
        Returns:
            JSON string with list of files and directories
        
        Example:
            list_directory()
            list_directory("src", True, "*.py")
        """
        try:
            dir_path = file_ops._resolve_path(path)
            
            if not dir_path.exists():
                return json.dumps({"error": f"Directory not found: {path}"})
            
            if not dir_path.is_dir():
                return json.dumps({"error": f"Path is not a directory: {path}"})
            
            items = []
            
            if recursive:
                glob_pattern = f"**/{pattern}"
                paths = dir_path.glob(glob_pattern)
            else:
                paths = dir_path.glob(pattern)
            
            for item_path in sorted(paths):
                try:
                    relative_path = item_path.relative_to(file_ops.base_path)
                    stat = item_path.stat()
                    
                    items.append({
                        "path": str(relative_path),
                        "name": item_path.name,
                        "type": "directory" if item_path.is_dir() else "file",
                        "size": stat.st_size if item_path.is_file() else 0,
                        "modified": stat.st_mtime
                    })
                except Exception as e:
                    logger.warning(f"Error processing {item_path}: {str(e)}")
                    continue
            
            result = {
                "path": path,
                "recursive": recursive,
                "pattern": pattern,
                "total_items": len(items),
                "items": items
            }
            
            logger.info(f"Listed directory: {path} ({len(items)} items)")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error listing directory: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def search_files(path: str, pattern: str, file_pattern: str = "*", case_sensitive: bool = False) -> str:
        """
        Search for text pattern in files.
        
        Args:
            path: Directory to search (relative to base directory)
            pattern: Text pattern to search for (regex supported)
            file_pattern: Glob pattern for files to search (default: "*")
            case_sensitive: Case-sensitive search (default: False)
        
        Returns:
            JSON string with search results
        
        Example:
            search_files("src", "TODO", "*.py")
            search_files(".", "function.*\\(", "*.js", True)
        """
        try:
            dir_path = file_ops._resolve_path(path)
            
            if not dir_path.exists():
                return json.dumps({"error": f"Directory not found: {path}"})
            
            if not dir_path.is_dir():
                return json.dumps({"error": f"Path is not a directory: {path}"})
            
            # Compile regex pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            results = []
            files_searched = 0
            
            # Search files
            for file_path in dir_path.rglob(file_pattern):
                if not file_path.is_file():
                    continue
                
                try:
                    # Skip files that are too large
                    if file_path.stat().st_size > file_ops.max_file_size:
                        continue
                    
                    files_searched += 1
                    relative_path = file_path.relative_to(file_ops.base_path)
                    
                    with open(file_path, 'r', encoding=file_ops.encoding, errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": str(relative_path),
                                    "line": line_num,
                                    "content": line.rstrip()
                                })
                                
                                # Limit results
                                if len(results) >= 1000:
                                    break
                    
                    if len(results) >= 1000:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error searching {file_path}: {str(e)}")
                    continue
            
            result = {
                "path": path,
                "pattern": pattern,
                "file_pattern": file_pattern,
                "case_sensitive": case_sensitive,
                "files_searched": files_searched,
                "matches_found": len(results),
                "results": results[:1000]  # Limit to 1000 results
            }
            
            logger.info(f"Searched files in {path}: {len(results)} matches in {files_searched} files")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error searching files: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def copy_file(source: str, destination: str) -> str:
        """
        Copy a file to a new location.
        
        Args:
            source: Source file path (relative to base directory)
            destination: Destination file path (relative to base directory)
        
        Returns:
            Success message or error details
        
        Example:
            copy_file("config.json", "config.backup.json")
        """
        try:
            source_path = file_ops._resolve_path(source)
            dest_path = file_ops._resolve_path(destination)
            
            if not source_path.exists():
                return json.dumps({"error": f"Source file not found: {source}"})
            
            if not source_path.is_file():
                return json.dumps({"error": f"Source is not a file: {source}"})
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_path, dest_path)
            
            result = {
                "source": source,
                "destination": destination,
                "message": "File copied successfully"
            }
            
            logger.info(f"Copied file: {source} -> {destination}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error copying file: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def move_file(source: str, destination: str) -> str:
        """
        Move or rename a file.
        
        Args:
            source: Source file path (relative to base directory)
            destination: Destination file path (relative to base directory)
        
        Returns:
            Success message or error details
        
        Example:
            move_file("old_name.txt", "new_name.txt")
            move_file("temp/file.txt", "archive/file.txt")
        """
        try:
            source_path = file_ops._resolve_path(source)
            dest_path = file_ops._resolve_path(destination)
            
            if not source_path.exists():
                return json.dumps({"error": f"Source file not found: {source}"})
            
            if not source_path.is_file():
                return json.dumps({"error": f"Source is not a file: {source}"})
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(dest_path))
            
            result = {
                "source": source,
                "destination": destination,
                "message": "File moved successfully"
            }
            
            logger.info(f"Moved file: {source} -> {destination}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error moving file: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def get_file_info(path: str) -> str:
        """
        Get detailed information about a file or directory.
        
        Args:
            path: Path to the file or directory (relative to base directory)
        
        Returns:
            JSON string with file/directory information
        
        Example:
            get_file_info("config.json")
        """
        try:
            file_path = file_ops._resolve_path(path)
            
            if not file_path.exists():
                return json.dumps({"error": f"Path not found: {path}"})
            
            stat = file_path.stat()
            
            info = {
                "path": path,
                "name": file_path.name,
                "type": "directory" if file_path.is_dir() else "file",
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
                "permissions": oct(stat.st_mode)[-3:],
                "is_symlink": file_path.is_symlink()
            }
            
            if file_path.is_file():
                info["extension"] = file_path.suffix
                
                # Try to count lines for text files
                try:
                    with open(file_path, 'r', encoding=file_ops.encoding) as f:
                        info["lines"] = sum(1 for _ in f)
                except:
                    info["lines"] = None
            
            logger.info(f"Got file info: {path}")
            return json.dumps(info, indent=2)
        except Exception as e:
            error_msg = f"Error getting file info: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def create_directory(path: str) -> str:
        """
        Create a new directory (including parent directories if needed).
        
        Args:
            path: Directory path to create (relative to base directory)
        
        Returns:
            Success message or error details
        
        Example:
            create_directory("new_folder")
            create_directory("parent/child/grandchild")
        """
        try:
            dir_path = file_ops._resolve_path(path)
            
            if dir_path.exists():
                return json.dumps({"error": f"Path already exists: {path}"})
            
            dir_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Created directory: {path}")
            return json.dumps({"message": f"Successfully created directory: {path}"})
        except Exception as e:
            error_msg = f"Error creating directory: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    logger.info("File operation tools registered successfully")

# Made with Bob