```mermaid
graph TD
    A[LINE User] -->|Sends message| B[LINE Webhook]
    B -->|POST /webhook| C[FastAPI App<br/>agent_with_mcp_adk/app.py]
    C -->|call_agent()| D[ADK Agent Server<br/>localhost:8000]
    D -->|Uses MCP Tools| E[MCP Server<br/>0.0.0.0:7000/sse<br/>src/mcp_server/tools.py]

    E -->|get_time tool| F[Time Tool]
    E -->|extract_wikipedia_article tool| G[Wikipedia Tool]

    D -->|Gemini 2.5-flash| H[Google Gemini API]

    C -->|Reply message| B
    B -->|Response| A

    subgraph "Testing Components"
        T1[submit-agent-a.sh<br/>Test script]
        T2[01_init_session.hurl<br/>Session init test]
        T3[02_submit_agent_a.hurl<br/>Submit message test]
        T4[explain.py<br/>Response parser]
    end

    T1 -->|Runs| T2
    T1 -->|Runs| T3
    T3 -->|Output| T4

    subgraph "Main Components"
        C1[main.py<br/>Runs FastAPI with uvicorn]
        C2[src/agent_with_mcp_adk/app.py<br/>Webhook handler]
        C3[src/agent_a/agent.py<br/>Agent definition with MCP tools]
        C4[src/mcp_server/tools.py<br/>MCP server with tools]
    end

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style H fill:#f1f8e9
    style T1 fill:#fff8e1
    style T2 fill:#fff8e1
    style T3 fill:#fff8e1
    style T4 fill:#fff8e1
```</content>
<parameter name="filePath">d:\2WarRoom\2025DevFest\devfest-2025-from-code-to-deployment-build-mcp-tools-for-gemini-and-adk\architecture_diagram.md