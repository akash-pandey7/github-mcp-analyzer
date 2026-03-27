import requests
from mcp.server.fastmcp import FastMCP

# 1. Initialize the FastMCP server
mcp = FastMCP("GitHubProfileAnalyzer")

# 2. Register the tool. 
# The docstring and type hints automatically generate the schema the LLM reads.
@mcp.tool()
def fetch_github_repos(username: str) -> str:
    """
    Fetches the public repositories for a given GitHub username.
    Returns a formatted string containing repository names, descriptions, and primary languages.
    """
    url = f"https://api.github.com/users/{username}/repos"
    
    # Standard header requested by GitHub's REST API
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MCP-GenAIAcademy-Agent"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
        
        if not repos:
            return f"No public repositories found for user: {username}"
            
        repo_summaries = []
        
        # Limit to the first 10 repositories to keep the LLM context window clean
        for repo in repos[:10]:
            name = repo.get("name")
            desc = repo.get("description") or "No description"
            lang = repo.get("language") or "Unknown"
            
            # Format the output clearly for the LLM to digest
            repo_summaries.append(f"Project: {name} | Language: {lang} | Desc: {desc}")
            
        return "\n".join(repo_summaries)
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from GitHub API: {str(e)}"

# 3. Run the server
if __name__ == "__main__":
    # ADK typically connects to local MCP servers via Standard I/O (stdio)
    mcp.run()