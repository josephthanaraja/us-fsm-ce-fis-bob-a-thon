#!/usr/bin/env python3
"""
OpenShift MCP Server
Provides tools for Bob to interact with Red Hat OpenShift for container orchestration and deployment
"""

import os
import json
import asyncio
import logging
from typing import Any, Optional, Sequence
from datetime import datetime
import subprocess
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openshift-mcp-server")

# OpenShift Configuration
OPENSHIFT_API_URL = os.getenv("OPENSHIFT_API_URL", "https://api.openshift.example.com:6443")
OPENSHIFT_TOKEN = os.getenv("OPENSHIFT_TOKEN", "")
OPENSHIFT_NAMESPACE = os.getenv("OPENSHIFT_NAMESPACE", "default")

class OpenShiftClient:
    """Client for interacting with OpenShift via oc CLI"""
    
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url
        self.token = token
        self.logged_in = False
    
    def _run_oc_command(self, command: list[str]) -> dict:
        """Run oc command and return JSON output"""
        try:
            # Login if not already logged in
            if not self.logged_in and self.token:
                login_cmd = [
                    "oc", "login", self.api_url,
                    "--token", self.token,
                    "--insecure-skip-tls-verify=true"
                ]
                subprocess.run(login_cmd, capture_output=True, text=True, check=True)
                self.logged_in = True
                logger.info(f"Logged into OpenShift: {self.api_url}")
            
            # Run the actual command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "error": result.stderr or "Command failed",
                    "command": " ".join(command)
                }
            
            # Try to parse as JSON
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                # Return raw output if not JSON
                return {"output": result.stdout, "raw": True}
                
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out", "command": " ".join(command)}
        except Exception as e:
            logger.error(f"OpenShift command failed: {e}")
            return {"error": str(e), "command": " ".join(command)}
    
    def get_cluster_info(self) -> dict:
        """Get OpenShift cluster information"""
        cmd = ["oc", "cluster-info"]
        result = self._run_oc_command(cmd)
        
        # Also get version info
        version_cmd = ["oc", "version", "-o", "json"]
        version_info = self._run_oc_command(version_cmd)
        
        return {
            "cluster_info": result,
            "version": version_info
        }
    
    def list_projects(self) -> dict:
        """List all OpenShift projects (namespaces)"""
        cmd = ["oc", "get", "projects", "-o", "json"]
        return self._run_oc_command(cmd)
    
    def get_project_status(self, project: str) -> dict:
        """Get status of a specific project"""
        cmd = ["oc", "status", "-n", project, "-o", "json"]
        status = self._run_oc_command(cmd)
        
        # Get resource counts
        pods_cmd = ["oc", "get", "pods", "-n", project, "-o", "json"]
        pods = self._run_oc_command(pods_cmd)
        
        services_cmd = ["oc", "get", "services", "-n", project, "-o", "json"]
        services = self._run_oc_command(services_cmd)
        
        routes_cmd = ["oc", "get", "routes", "-n", project, "-o", "json"]
        routes = self._run_oc_command(routes_cmd)
        
        return {
            "project": project,
            "status": status,
            "pods": pods,
            "services": services,
            "routes": routes
        }
    
    def list_pods(self, project: str, label_selector: Optional[str] = None) -> dict:
        """List pods in a project"""
        cmd = ["oc", "get", "pods", "-n", project, "-o", "json"]
        if label_selector:
            cmd.extend(["-l", label_selector])
        return self._run_oc_command(cmd)
    
    def get_pod_logs(self, project: str, pod_name: str, container: Optional[str] = None, 
                     tail: int = 100, previous: bool = False) -> dict:
        """Get logs from a pod"""
        cmd = ["oc", "logs", pod_name, "-n", project, f"--tail={tail}"]
        if container:
            cmd.extend(["-c", container])
        if previous:
            cmd.append("--previous")
        
        result = self._run_oc_command(cmd)
        return {
            "pod": pod_name,
            "project": project,
            "container": container,
            "logs": result
        }
    
    def create_route(self, project: str, service_name: str, hostname: Optional[str] = None,
                     path: str = "/", tls: bool = True) -> dict:
        """Create an OpenShift route for external access"""
        cmd = ["oc", "create", "route"]
        
        if tls:
            cmd.append("edge")
        else:
            cmd.append("http")
        
        cmd.extend([
            service_name,
            "-n", project,
            f"--service={service_name}",
            f"--path={path}"
        ])
        
        if hostname:
            cmd.append(f"--hostname={hostname}")
        
        cmd.extend(["-o", "json"])
        return self._run_oc_command(cmd)
    
    def get_routes(self, project: str) -> dict:
        """Get all routes in a project"""
        cmd = ["oc", "get", "routes", "-n", project, "-o", "json"]
        return self._run_oc_command(cmd)
    
    def deploy_application(self, project: str, image: str, app_name: str,
                          replicas: int = 3, port: int = 8080,
                          env_vars: Optional[dict] = None) -> dict:
        """Deploy an application to OpenShift"""
        # Create deployment
        cmd = [
            "oc", "create", "deployment", app_name,
            "-n", project,
            f"--image={image}",
            f"--replicas={replicas}",
            "-o", "json"
        ]
        
        deployment = self._run_oc_command(cmd)
        
        if "error" in deployment:
            return deployment
        
        # Expose as service
        expose_cmd = [
            "oc", "expose", "deployment", app_name,
            "-n", project,
            f"--port={port}",
            "-o", "json"
        ]
        service = self._run_oc_command(expose_cmd)
        
        # Set environment variables if provided
        if env_vars:
            for key, value in env_vars.items():
                env_cmd = [
                    "oc", "set", "env", f"deployment/{app_name}",
                    "-n", project,
                    f"{key}={value}"
                ]
                self._run_oc_command(env_cmd)
        
        return {
            "deployment": deployment,
            "service": service,
            "app_name": app_name,
            "project": project,
            "replicas": replicas
        }
    
    def scale_deployment(self, project: str, deployment_name: str, replicas: int) -> dict:
        """Scale a deployment"""
        cmd = [
            "oc", "scale", f"deployment/{deployment_name}",
            "-n", project,
            f"--replicas={replicas}",
            "-o", "json"
        ]
        return self._run_oc_command(cmd)
    
    def get_deployment_status(self, project: str, deployment_name: str) -> dict:
        """Get deployment status"""
        cmd = ["oc", "get", "deployment", deployment_name, "-n", project, "-o", "json"]
        return self._run_oc_command(cmd)
    
    def rollout_status(self, project: str, deployment_name: str) -> dict:
        """Get rollout status of a deployment"""
        cmd = ["oc", "rollout", "status", f"deployment/{deployment_name}", "-n", project]
        return self._run_oc_command(cmd)
    
    def rollback_deployment(self, project: str, deployment_name: str) -> dict:
        """Rollback a deployment to previous version"""
        cmd = [
            "oc", "rollout", "undo", f"deployment/{deployment_name}",
            "-n", project,
            "-o", "json"
        ]
        return self._run_oc_command(cmd)
    
    def get_deployment_config(self, project: str, dc_name: str) -> dict:
        """Get OpenShift DeploymentConfig (legacy)"""
        cmd = ["oc", "get", "dc", dc_name, "-n", project, "-o", "json"]
        return self._run_oc_command(cmd)
    
    def trigger_build(self, project: str, build_config: str) -> dict:
        """Trigger an OpenShift build (Source-to-Image)"""
        cmd = ["oc", "start-build", build_config, "-n", project, "-o", "json"]
        return self._run_oc_command(cmd)
    
    def get_build_logs(self, project: str, build_name: str) -> dict:
        """Get logs from a build"""
        cmd = ["oc", "logs", f"build/{build_name}", "-n", project]
        result = self._run_oc_command(cmd)
        return {
            "build": build_name,
            "project": project,
            "logs": result
        }
    
    def list_builds(self, project: str) -> dict:
        """List all builds in a project"""
        cmd = ["oc", "get", "builds", "-n", project, "-o", "json"]
        return self._run_oc_command(cmd)
    
    def get_resource_quota(self, project: str) -> dict:
        """Get resource quotas for a project"""
        cmd = ["oc", "get", "resourcequota", "-n", project, "-o", "json"]
        return self._run_oc_command(cmd)
    
    def get_limit_ranges(self, project: str) -> dict:
        """Get limit ranges for a project"""
        cmd = ["oc", "get", "limitrange", "-n", project, "-o", "json"]
        return self._run_oc_command(cmd)
    
    def get_events(self, project: str, limit: int = 50) -> dict:
        """Get recent events in a project"""
        cmd = ["oc", "get", "events", "-n", project, "-o", "json", "--sort-by=.lastTimestamp"]
        result = self._run_oc_command(cmd)
        
        # Limit events to prevent large responses
        if isinstance(result, dict) and "items" in result:
            result["items"] = result["items"][-limit:]
        
        return result
    
    def describe_pod(self, project: str, pod_name: str) -> dict:
        """Get detailed pod information"""
        cmd = ["oc", "describe", "pod", pod_name, "-n", project]
        return self._run_oc_command(cmd)
    
    def exec_in_pod(self, project: str, pod_name: str, command: str,
                    container: Optional[str] = None) -> dict:
        """Execute a command in a pod"""
        cmd = ["oc", "exec", pod_name, "-n", project]
        if container:
            cmd.extend(["-c", container])
        cmd.extend(["--", "sh", "-c", command])
        
        return self._run_oc_command(cmd)
    
    def get_node_info(self) -> dict:
        """Get information about cluster nodes"""
        cmd = ["oc", "get", "nodes", "-o", "json"]
        return self._run_oc_command(cmd)
    
    def get_node_metrics(self) -> dict:
        """Get node resource usage metrics"""
        cmd = ["oc", "adm", "top", "nodes"]
        return self._run_oc_command(cmd)
    
    def get_pod_metrics(self, project: str) -> dict:
        """Get pod resource usage metrics"""
        cmd = ["oc", "adm", "top", "pods", "-n", project]
        return self._run_oc_command(cmd)


# Initialize MCP Server
server = Server("openshift-mcp-server")

# Initialize OpenShift client (lazy loading)
openshift_client = None

def get_openshift_client() -> OpenShiftClient:
    """Get or create OpenShift client"""
    global openshift_client
    if openshift_client is None:
        # Token is optional - if not provided, will use existing oc login session
        openshift_client = OpenShiftClient(OPENSHIFT_API_URL, OPENSHIFT_TOKEN)
        if OPENSHIFT_TOKEN:
            logger.info(f"OpenShift client initialized with token for {OPENSHIFT_API_URL}")
        else:
            logger.info(f"OpenShift client initialized (using existing oc login session) for {OPENSHIFT_API_URL}")
    return openshift_client


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available OpenShift tools"""
    return [
        Tool(
            name="get_cluster_info",
            description="Get OpenShift cluster information and version",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_projects",
            description="List all OpenShift projects (namespaces)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_project_status",
            description="Get comprehensive status of a project including pods, services, and routes",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="list_pods",
            description="List pods in a project with optional label selector",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "label_selector": {
                        "type": "string",
                        "description": "Label selector (e.g., 'app=myapp')"
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="get_pod_logs",
            description="Get logs from a pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "pod_name": {
                        "type": "string",
                        "description": "Pod name"
                    },
                    "container": {
                        "type": "string",
                        "description": "Container name (optional, for multi-container pods)"
                    },
                    "tail": {
                        "type": "number",
                        "description": "Number of lines to show (default: 100)",
                        "default": 100
                    },
                    "previous": {
                        "type": "boolean",
                        "description": "Show logs from previous container instance",
                        "default": False
                    }
                },
                "required": ["project", "pod_name"]
            }
        ),
        Tool(
            name="deploy_application",
            description="Deploy an application to OpenShift",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "image": {
                        "type": "string",
                        "description": "Container image (e.g., 'nginx:latest')"
                    },
                    "app_name": {
                        "type": "string",
                        "description": "Application name"
                    },
                    "replicas": {
                        "type": "number",
                        "description": "Number of replicas (default: 3)",
                        "default": 3
                    },
                    "port": {
                        "type": "number",
                        "description": "Container port (default: 8080)",
                        "default": 8080
                    },
                    "env_vars": {
                        "type": "object",
                        "description": "Environment variables as key-value pairs"
                    }
                },
                "required": ["project", "image", "app_name"]
            }
        ),
        Tool(
            name="scale_deployment",
            description="Scale a deployment to specified number of replicas",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "deployment_name": {
                        "type": "string",
                        "description": "Deployment name"
                    },
                    "replicas": {
                        "type": "number",
                        "description": "Number of replicas"
                    }
                },
                "required": ["project", "deployment_name", "replicas"]
            }
        ),
        Tool(
            name="create_route",
            description="Create an OpenShift route for external access to a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "service_name": {
                        "type": "string",
                        "description": "Service name to expose"
                    },
                    "hostname": {
                        "type": "string",
                        "description": "Custom hostname (optional)"
                    },
                    "path": {
                        "type": "string",
                        "description": "URL path (default: /)",
                        "default": "/"
                    },
                    "tls": {
                        "type": "boolean",
                        "description": "Enable TLS (default: true)",
                        "default": True
                    }
                },
                "required": ["project", "service_name"]
            }
        ),
        Tool(
            name="get_routes",
            description="Get all routes in a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="get_deployment_status",
            description="Get status of a deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "deployment_name": {
                        "type": "string",
                        "description": "Deployment name"
                    }
                },
                "required": ["project", "deployment_name"]
            }
        ),
        Tool(
            name="rollout_status",
            description="Get rollout status of a deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "deployment_name": {
                        "type": "string",
                        "description": "Deployment name"
                    }
                },
                "required": ["project", "deployment_name"]
            }
        ),
        Tool(
            name="rollback_deployment",
            description="Rollback a deployment to previous version",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "deployment_name": {
                        "type": "string",
                        "description": "Deployment name"
                    }
                },
                "required": ["project", "deployment_name"]
            }
        ),
        Tool(
            name="trigger_build",
            description="Trigger an OpenShift build (Source-to-Image)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "build_config": {
                        "type": "string",
                        "description": "BuildConfig name"
                    }
                },
                "required": ["project", "build_config"]
            }
        ),
        Tool(
            name="get_build_logs",
            description="Get logs from a build",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "build_name": {
                        "type": "string",
                        "description": "Build name"
                    }
                },
                "required": ["project", "build_name"]
            }
        ),
        Tool(
            name="list_builds",
            description="List all builds in a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="get_events",
            description="Get recent events in a project for troubleshooting",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of events (default: 50)",
                        "default": 50
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="get_node_info",
            description="Get information about cluster nodes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_node_metrics",
            description="Get node resource usage metrics (CPU, memory)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_pod_metrics",
            description="Get pod resource usage metrics in a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="describe_pod",
            description="Get detailed information about a pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "pod_name": {
                        "type": "string",
                        "description": "Pod name"
                    }
                },
                "required": ["project", "pod_name"]
            }
        ),
        Tool(
            name="get_resource_quota",
            description="Get resource quotas for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    }
                },
                "required": ["project"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    try:
        client = get_openshift_client()
        
        if name == "get_cluster_info":
            result = client.get_cluster_info()
            
        elif name == "list_projects":
            result = client.list_projects()
            
        elif name == "get_project_status":
            project = arguments.get("project")
            if not project:
                result = {"error": "project is required"}
            else:
                result = client.get_project_status(project)
            
        elif name == "list_pods":
            project = arguments.get("project")
            label_selector = arguments.get("label_selector")
            if not project:
                result = {"error": "project is required"}
            else:
                result = client.list_pods(project, label_selector)
            
        elif name == "get_pod_logs":
            project = arguments.get("project")
            pod_name = arguments.get("pod_name")
            container = arguments.get("container")
            tail = arguments.get("tail", 100)
            previous = arguments.get("previous", False)
            
            if not project or not pod_name:
                result = {"error": "project and pod_name are required"}
            else:
                result = client.get_pod_logs(project, pod_name, container, tail, previous)
            
        elif name == "deploy_application":
            project = arguments.get("project")
            image = arguments.get("image")
            app_name = arguments.get("app_name")
            replicas = arguments.get("replicas", 3)
            port = arguments.get("port", 8080)
            env_vars = arguments.get("env_vars")
            
            if not all([project, image, app_name]):
                result = {"error": "project, image, and app_name are required"}
            else:
                result = client.deploy_application(project, image, app_name, replicas, port, env_vars)
            
        elif name == "scale_deployment":
            project = arguments.get("project")
            deployment_name = arguments.get("deployment_name")
            replicas = arguments.get("replicas")
            
            if not all([project, deployment_name, replicas is not None]):
                result = {"error": "project, deployment_name, and replicas are required"}
            else:
                result = client.scale_deployment(project, deployment_name, replicas)
            
        elif name == "create_route":
            project = arguments.get("project")
            service_name = arguments.get("service_name")
            hostname = arguments.get("hostname")
            path = arguments.get("path", "/")
            tls = arguments.get("tls", True)
            
            if not all([project, service_name]):
                result = {"error": "project and service_name are required"}
            else:
                result = client.create_route(project, service_name, hostname, path, tls)
            
        elif name == "get_routes":
            project = arguments.get("project")
            if not project:
                result = {"error": "project is required"}
            else:
                result = client.get_routes(project)
            
        elif name == "get_deployment_status":
            project = arguments.get("project")
            deployment_name = arguments.get("deployment_name")
            if not all([project, deployment_name]):
                result = {"error": "project and deployment_name are required"}
            else:
                result = client.get_deployment_status(project, deployment_name)
            
        elif name == "rollout_status":
            project = arguments.get("project")
            deployment_name = arguments.get("deployment_name")
            if not all([project, deployment_name]):
                result = {"error": "project and deployment_name are required"}
            else:
                result = client.rollout_status(project, deployment_name)
            
        elif name == "rollback_deployment":
            project = arguments.get("project")
            deployment_name = arguments.get("deployment_name")
            if not all([project, deployment_name]):
                result = {"error": "project and deployment_name are required"}
            else:
                result = client.rollback_deployment(project, deployment_name)
            
        elif name == "trigger_build":
            project = arguments.get("project")
            build_config = arguments.get("build_config")
            if not all([project, build_config]):
                result = {"error": "project and build_config are required"}
            else:
                result = client.trigger_build(project, build_config)
            
        elif name == "get_build_logs":
            project = arguments.get("project")
            build_name = arguments.get("build_name")
            if not all([project, build_name]):
                result = {"error": "project and build_name are required"}
            else:
                result = client.get_build_logs(project, build_name)
            
        elif name == "list_builds":
            project = arguments.get("project")
            if not project:
                result = {"error": "project is required"}
            else:
                result = client.list_builds(project)
            
        elif name == "get_events":
            project = arguments.get("project")
            limit = arguments.get("limit", 50)
            if not project:
                result = {"error": "project is required"}
            else:
                result = client.get_events(project, limit)
            
        elif name == "get_node_info":
            result = client.get_node_info()
            
        elif name == "get_node_metrics":
            result = client.get_node_metrics()
            
        elif name == "get_pod_metrics":
            project = arguments.get("project")
            if not project:
                result = {"error": "project is required"}
            else:
                result = client.get_pod_metrics(project)
            
        elif name == "describe_pod":
            project = arguments.get("project")
            pod_name = arguments.get("pod_name")
            if not all([project, pod_name]):
                result = {"error": "project and pod_name are required"}
            else:
                result = client.describe_pod(project, pod_name)
            
        elif name == "get_resource_quota":
            project = arguments.get("project")
            if not project:
                result = {"error": "project is required"}
            else:
                result = client.get_resource_quota(project)
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        # Format the response
        formatted_result = json.dumps(result, indent=2)
        return [TextContent(type="text", text=formatted_result)]
        
    except Exception as e:
        logger.error(f"Error executing {name}: {e}")
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="openshift-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob