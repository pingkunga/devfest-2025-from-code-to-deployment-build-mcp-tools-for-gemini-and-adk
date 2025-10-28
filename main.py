# main.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agent_with_mcp_adk.app:app", host="0.0.0.0", port=8000, reload=True)
