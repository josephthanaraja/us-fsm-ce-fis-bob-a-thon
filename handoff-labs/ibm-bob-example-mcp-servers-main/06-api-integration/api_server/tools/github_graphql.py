"""
GitHub GraphQL Tool - Demonstrates GraphQL queries.

This module shows how to make GraphQL requests, which differ from REST APIs.

Key Concepts:
- GraphQL uses POST requests with query in the body
- Single endpoint for all queries
- Request exactly the data you need (no over/under-fetching)
- Nested queries and relationships
- Variables for dynamic queries
- Introspection capabilities
"""

import logging
import httpx
from typing import Dict, Any, Optional, List

from ..config import GITHUB_TOKEN, GITHUB_GRAPHQL_URL, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


async def search_repositories(
    query: str,
    limit: int = 10,
    sort: str = "STARS"
) -> Dict[str, Any]:
    """
    Search GitHub repositories using GraphQL.
    
    This demonstrates a GraphQL query with:
    - POST request to GraphQL endpoint
    - Query string in request body
    - Variables for dynamic values
    - Nested data selection
    - Pagination parameters
    
    Args:
        query: Search query (e.g., "language:python stars:>1000")
        limit: Maximum number of results (default: 10)
        sort: Sort order (STARS, FORKS, UPDATED, default: STARS)
        
    Returns:
        Dictionary containing repository search results
        
    Raises:
        ValueError: If GitHub token is not configured
        httpx.HTTPError: If the API request fails
    """
    if not GITHUB_TOKEN:
        raise ValueError(
            "GITHUB_TOKEN not configured. "
            "Please set it in your .env file. "
            "Get a token at: https://github.com/settings/tokens"
        )
    
    logger.info(f"Searching repositories with query: {query}")
    
    # GraphQL query with variables
    # Note: GitHub's search API doesn't support explicit sorting in GraphQL
    # Results are sorted by best match/relevance by default
    # To get repos by stars, include "sort:stars" in the query string
    graphql_query = """
    query SearchRepositories($query: String!, $limit: Int!) {
      search(query: $query, type: REPOSITORY, first: $limit) {
        repositoryCount
        edges {
          node {
            ... on Repository {
              name
              nameWithOwner
              description
              url
              stargazerCount
              forkCount
              primaryLanguage {
                name
                color
              }
              createdAt
              updatedAt
              isPrivate
              owner {
                login
                avatarUrl
              }
            }
          }
        }
      }
    }
    """
    
    # Variables for the query
    variables = {
        "query": query,
        "limit": limit
    }
    
    # Request body for GraphQL
    request_body = {
        "query": graphql_query,
        "variables": variables
    }
    
    # Headers
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MCP-API-Integration-Server"
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            # GraphQL always uses POST
            response = await client.post(
                GITHUB_GRAPHQL_URL,
                json=request_body,
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return {
                    "status": "error",
                    "message": "GraphQL query failed",
                    "errors": data["errors"]
                }
            
            # Extract repository data
            search_data = data["data"]["search"]
            repositories = []
            
            for edge in search_data["edges"]:
                repo = edge["node"]
                repositories.append({
                    "name": repo["name"],
                    "full_name": repo["nameWithOwner"],
                    "description": repo.get("description", ""),
                    "url": repo["url"],
                    "stars": repo["stargazerCount"],
                    "forks": repo["forkCount"],
                    "language": repo["primaryLanguage"]["name"] if repo.get("primaryLanguage") else None,
                    "owner": repo["owner"]["login"],
                    "created_at": repo["createdAt"],
                    "updated_at": repo["updatedAt"],
                    "is_private": repo["isPrivate"]
                })
            
            result = {
                "status": "success",
                "total_count": search_data["repositoryCount"],
                "returned_count": len(repositories),
                "repositories": repositories
            }
            
            logger.info(f"Found {search_data['repositoryCount']} repositories, returned {len(repositories)}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in GraphQL query: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"GraphQL request failed: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error in GraphQL query: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }


async def get_user_profile(
    username: str,
    include_repos: bool = True
) -> Dict[str, Any]:
    """
    Get a GitHub user's profile using GraphQL.
    
    This demonstrates:
    - Conditional fields based on parameters
    - Nested queries (user -> repositories)
    - Multiple related resources in one query
    
    Args:
        username: GitHub username
        include_repos: Whether to include user's repositories
        
    Returns:
        Dictionary containing user profile data
    """
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not configured")
    
    logger.info(f"Fetching profile for user: {username}")
    
    # Build query dynamically based on parameters
    repos_fragment = """
        repositories(first: 10, orderBy: {field: STARGAZERS, direction: DESC}) {
          totalCount
          nodes {
            name
            description
            stargazerCount
            url
          }
        }
    """ if include_repos else ""
    
    graphql_query = f"""
    query GetUserProfile($username: String!) {{
      user(login: $username) {{
        login
        name
        bio
        company
        location
        email
        websiteUrl
        avatarUrl
        followers {{
          totalCount
        }}
        following {{
          totalCount
        }}
        createdAt
        {repos_fragment}
      }}
    }}
    """
    
    variables = {"username": username}
    request_body = {
        "query": graphql_query,
        "variables": variables
    }
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MCP-API-Integration-Server"
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.post(
                GITHUB_GRAPHQL_URL,
                json=request_body,
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                return {
                    "status": "error",
                    "message": "GraphQL query failed",
                    "errors": data["errors"]
                }
            
            user = data["data"]["user"]
            if not user:
                return {
                    "status": "error",
                    "message": f"User '{username}' not found"
                }
            
            result = {
                "status": "success",
                "username": user["login"],
                "name": user.get("name"),
                "bio": user.get("bio"),
                "company": user.get("company"),
                "location": user.get("location"),
                "email": user.get("email"),
                "website": user.get("websiteUrl"),
                "avatar_url": user["avatarUrl"],
                "followers": user["followers"]["totalCount"],
                "following": user["following"]["totalCount"],
                "created_at": user["createdAt"]
            }
            
            if include_repos and "repositories" in user:
                result["repository_count"] = user["repositories"]["totalCount"]
                result["top_repositories"] = [
                    {
                        "name": repo["name"],
                        "description": repo.get("description"),
                        "stars": repo["stargazerCount"],
                        "url": repo["url"]
                    }
                    for repo in user["repositories"]["nodes"]
                ]
            
            logger.info(f"Successfully fetched profile for: {username}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching user profile: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to fetch user profile: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error fetching user profile: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }


async def get_repository_issues(
    owner: str,
    repo: str,
    state: str = "OPEN",
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get issues for a repository using GraphQL.
    
    This demonstrates:
    - Deeply nested queries (repository -> issues -> comments)
    - Filtering with arguments
    - Pagination
    
    Args:
        owner: Repository owner
        repo: Repository name
        state: Issue state (OPEN, CLOSED)
        limit: Maximum number of issues
        
    Returns:
        Dictionary containing repository issues
    """
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not configured")
    
    logger.info(f"Fetching issues for {owner}/{repo}")
    
    graphql_query = """
    query GetRepositoryIssues($owner: String!, $repo: String!, $state: IssueState!, $limit: Int!) {
      repository(owner: $owner, name: $repo) {
        name
        issues(first: $limit, states: [$state], orderBy: {field: CREATED_AT, direction: DESC}) {
          totalCount
          nodes {
            number
            title
            body
            state
            createdAt
            updatedAt
            author {
              login
            }
            comments {
              totalCount
            }
            labels(first: 5) {
              nodes {
                name
                color
              }
            }
          }
        }
      }
    }
    """
    
    variables = {
        "owner": owner,
        "repo": repo,
        "state": state,
        "limit": limit
    }
    
    request_body = {
        "query": graphql_query,
        "variables": variables
    }
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MCP-API-Integration-Server"
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.post(
                GITHUB_GRAPHQL_URL,
                json=request_body,
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                return {
                    "status": "error",
                    "message": "GraphQL query failed",
                    "errors": data["errors"]
                }
            
            repository = data["data"]["repository"]
            if not repository:
                return {
                    "status": "error",
                    "message": f"Repository '{owner}/{repo}' not found"
                }
            
            issues_data = repository["issues"]
            issues = []
            
            for issue in issues_data["nodes"]:
                issues.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "body": issue["body"][:200] + "..." if issue.get("body") and len(issue["body"]) > 200 else issue.get("body", ""),
                    "state": issue["state"],
                    "author": issue["author"]["login"] if issue.get("author") else None,
                    "created_at": issue["createdAt"],
                    "updated_at": issue["updatedAt"],
                    "comment_count": issue["comments"]["totalCount"],
                    "labels": [
                        {"name": label["name"], "color": label["color"]}
                        for label in issue["labels"]["nodes"]
                    ]
                })
            
            result = {
                "status": "success",
                "repository": repository["name"],
                "total_issues": issues_data["totalCount"],
                "returned_count": len(issues),
                "issues": issues
            }
            
            logger.info(f"Found {issues_data['totalCount']} issues, returned {len(issues)}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching issues: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to fetch issues: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error fetching issues: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }

# Made with Bob
