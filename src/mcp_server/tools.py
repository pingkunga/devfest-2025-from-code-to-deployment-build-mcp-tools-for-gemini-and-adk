from fastmcp import FastMCP
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from dotenv import load_dotenv

import os 
import requests
from bs4 import BeautifulSoup
from html2text import html2text

load_dotenv()
mcp = FastMCP(name="FastMCP-Time_Tool")

# Input schema
class TimeQueryInput(BaseModel):
    query: str = Field(
        description='Specify the time keyword: "today", "now", "yesterday", "tomorrow"'
    )
    
# Tool definition
@mcp.tool
def get_time(query: str):
    """Returns the date or datetime for 'today', 'now', 'yesterday', or 'tomorrow'."""
    now = datetime.now()
    print(f"now : {now}")
    query_lower = query.lower()

    if query_lower == "today":
        return now.strftime("%Y-%m-%d")
    elif query_lower == "now":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif query_lower == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    elif query_lower == "tomorrow":
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        return {"error": f"Unknown time query '{query}'. Use 'today', 'now', 'yesterday', or 'tomorrow'."}

@mcp.tool()
def extract_wikipedia_article(url: str) -> str:
    """
    Retrieves and processes a Wikipedia article from the given URL, extracting
    the main content and converting it to Markdown format.

    Usage:
        extract_wikipedia_article("https://en.wikipedia.org/wiki/Gemini_(chatbot)")
    """
    print(url)
    try:
        if not url.startswith("http"):
            raise ValueError("URL must begin with http or https protocol.")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                        " AppleWebKit/537.36 (KHTML, like Gecko)"
                        " Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(
            url, 
            headers=headers, 
            # timeout=8
        )
        print(response)
        if response.status_code != 200:
            raise ValueError(f"Unable to access the article. Server returned status: {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", {"id": "mw-content-text"})
        if not content_div:
            raise ValueError("The main article content section was not found at the specified Wikipedia URL.")
        markdown_text = html2text(str(content_div))
        return markdown_text

    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {str(e)}")
    
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=int(os.getenv("MCP_PORT")))