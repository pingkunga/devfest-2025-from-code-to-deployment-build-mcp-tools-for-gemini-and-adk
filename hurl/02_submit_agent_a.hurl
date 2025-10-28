POST http://localhost:8000/run
Content-Type: application/json
{
    "app_name": "{{AGENT_NAME}}",
    "user_id": "u_123",
    "session_id": "{{SESSION_ID}}",
    "new_message": {
        "role": "user",
        "parts": [{
            "text": "Hey whats the current weather and time in new york today"
        }]
    }
}
