"""
Code execution tools for running code in isolated sandbox environment.

This module provides tools for safely executing code in multiple languages
with resource limits and timeout controls.
"""

import subprocess
import json
import logging
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CodeExecutor:
    """Manages safe code execution in sandbox environment."""
    
    def __init__(self, timeout: int = 30, max_output_size: int = 1048576):
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.sandbox_dir = Path("/sandbox")
        self.sandbox_dir.mkdir(exist_ok=True)
    
    def _execute_command(self, cmd: list, stdin_data: str | None = None) -> Dict[str, Any]:
        """Execute a command with timeout and capture output."""
        try:
            result = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(self.sandbox_dir)
            )
            
            # Truncate output if too large
            stdout = result.stdout[:self.max_output_size]
            stderr = result.stderr[:self.max_output_size]
            
            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "timed_out": False
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout} seconds",
                "exit_code": -1,
                "timed_out": True
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": -1,
                "timed_out": False
            }


def create_executor_tools(mcp, timeout: int, max_output_size: int):
    """Register all code execution tools with the MCP server."""
    
    executor = CodeExecutor(timeout, max_output_size)
    
    @mcp.tool()
    def execute_python(code: str, stdin: str = "") -> str:
        """
        Execute Python code in a sandboxed environment.
        
        Args:
            code: Python code to execute
            stdin: Optional input to provide to the program
        
        Returns:
            JSON string with execution results (stdout, stderr, exit_code)
        
        Example:
            execute_python("print('Hello, World!')")
            execute_python("x = input(); print(x.upper())", "hello")
        """
        try:
            # Write code to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                dir=str(executor.sandbox_dir),
                delete=False
            ) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute Python code
                result = executor._execute_command(
                    ["python3", temp_file],
                    stdin_data=stdin
                )
                
                logger.info(f"Executed Python code, exit code: {result['exit_code']}")
                return json.dumps(result, indent=2)
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            error_msg = f"Error executing Python code: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def execute_javascript(code: str, stdin: str = "") -> str:
        """
        Execute JavaScript code in a sandboxed environment.
        
        Args:
            code: JavaScript code to execute
            stdin: Optional input to provide to the program
        
        Returns:
            JSON string with execution results (stdout, stderr, exit_code)
        
        Example:
            execute_javascript("console.log('Hello, World!');")
        """
        try:
            # Write code to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.js',
                dir=str(executor.sandbox_dir),
                delete=False
            ) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute JavaScript code
                result = executor._execute_command(
                    ["node", temp_file],
                    stdin_data=stdin
                )
                
                logger.info(f"Executed JavaScript code, exit code: {result['exit_code']}")
                return json.dumps(result, indent=2)
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            error_msg = f"Error executing JavaScript code: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def execute_bash(script: str, stdin: str = "") -> str:
        """
        Execute Bash script in a sandboxed environment.
        
        Args:
            script: Bash script to execute
            stdin: Optional input to provide to the script
        
        Returns:
            JSON string with execution results (stdout, stderr, exit_code)
        
        Example:
            execute_bash("echo 'Hello, World!'")
            execute_bash("ls -la")
        """
        try:
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.sh',
                dir=str(executor.sandbox_dir),
                delete=False
            ) as f:
                f.write(script)
                temp_file = f.name
            
            # Make script executable
            os.chmod(temp_file, 0o755)
            
            try:
                # Execute Bash script
                result = executor._execute_command(
                    ["bash", temp_file],
                    stdin_data=stdin
                )
                
                logger.info(f"Executed Bash script, exit code: {result['exit_code']}")
                return json.dumps(result, indent=2)
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            error_msg = f"Error executing Bash script: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def execute_command(command: str, args: str = "") -> str:
        """
        Execute a shell command with arguments.
        
        Args:
            command: Command to execute (e.g., "ls", "cat", "grep")
            args: Command arguments as a single string
        
        Returns:
            JSON string with execution results (stdout, stderr, exit_code)
        
        Example:
            execute_command("echo", "Hello World")
            execute_command("ls", "-la /sandbox")
        """
        try:
            # Build command list
            cmd_list = [command]
            if args:
                # Simple split - in production, use proper shell parsing
                cmd_list.extend(args.split())
            
            result = executor._execute_command(cmd_list)
            
            logger.info(f"Executed command '{command}', exit code: {result['exit_code']}")
            return json.dumps(result, indent=2)
                    
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    logger.info("Code execution tools registered successfully")

# Made with Bob