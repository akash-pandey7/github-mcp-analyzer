from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.runners import InMemoryRunner
from google.genai import types
import uuid

# 1. Initialize FastAPI
app = FastAPI()

# 2. Set up the Tool, Agent, and Runner (same as before)
github_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command="python", args=["server.py"])
    )
)

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

APP_NAME = "github_app"
runner = InMemoryRunner(agent=agent, app_name=APP_NAME)

# 3. Define the Web Request Format
class AnalyzeRequest(BaseModel):
    username: str

# 4. Create the Web Endpoint
@app.post("/analyze")
async def analyze_profile(request: AnalyzeRequest):
    # Generate a unique session for every web request
    session_id = str(uuid.uuid4())
    user_id = "web_user"
    
    await runner.session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    
    user_prompt = types.Content(
        role="user",
        parts=[types.Part.from_text(text=f"What kind of projects does the user '{request.username}' work on?")]
    )
    
    events = runner.run_async(
        user_id=user_id, session_id=session_id, new_message=user_prompt
    )
    
    # Gather the streamed text into one final string for the web response
    final_response = ""
    async for event in events:
        if getattr(event, 'content', None) and getattr(event.content, 'parts', None):
            for part in event.content.parts:
                if getattr(part, 'text', None):
                    final_response += part.text
                    
    return {"username": request.username, "summary": final_response}