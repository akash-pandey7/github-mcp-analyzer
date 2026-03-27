import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.runners import InMemoryRunner
from google.genai import types 

# 1. Connect to your local Python MCP server via standard I/O (stdio)
github_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=["server.py"] 
        )
    )
)

# 2. Define your Agent
agent = LlmAgent(
    model='gemini-3.1-pro-preview', 
    name='github_analyzer',
    instruction="""
    You are a Developer Profile Analyzer. 
    Use your tools to fetch a user's GitHub repositories.
    Provide a concise, 2-paragraph summary of their main programming languages 
    and the overall themes of the projects they build.
    """,
    tools=[github_toolset]
)

# Set our App Name and IDs clearly to satisfy the ADK
APP_NAME = "github_app"
USER_ID = "test_user"
SESSION_ID = "test_session"

# 3. Create a Runner 
runner = InMemoryRunner(agent=agent, app_name=APP_NAME)

# 4. A quick script to test the agent locally
async def test_agent():
    print("Asking the agent to analyze Linus Torvalds...\n")
    
    user_prompt = types.Content(
        role="user",
        parts=[types.Part.from_text(text="What kind of projects does the user 'torvalds' work on?")]
    )
    
    # THE MISSING PIECE: Force the ADK to create the session in memory first!
    await runner.session_service.create_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )
    
    # Now run_async has both the required IDs AND an existing session to use
    events = runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_prompt
    )
    
    print("--- Agent Response ---")
    
    async for event in events:
        if getattr(event, 'content', None) and getattr(event.content, 'parts', None):
            for part in event.content.parts:
                if getattr(part, 'text', None):
                    print(part.text, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    asyncio.run(test_agent())