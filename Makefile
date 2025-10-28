test:
	uv run pytest
start:
	uv run main.py

start-agent-a:
	uv run adk api_server src/agent_a
submit-agent-a:
	./scripts/submit-agent-a.sh
