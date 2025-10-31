start-webhook:
	uv run main.py
start-mcp-server:
	python src/mcp_server/tools.py
start-agent-a:
	uv run adk api_server src/agent_a
submit-agent-a:
	./scripts/submit-agent-a.sh
