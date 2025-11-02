import datetime
import json
import os
from zoneinfo import ZoneInfo

import google.generativeai as genai
import requests
from dotenv import load_dotenv
# from google.adk.tools.mcp_tool.mcp_toolset import (
#     MCPToolset,
#     SseServerParams,
# )
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
# from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# def get_weather(city: str) -> dict:
#     """Retrieves the current weather report for a specified city.

#     Args:
#         city (str): The name of the city for which to retrieve the weather report.

#     Returns:
#         dict: status and result or error msg.
#     """
#     print(f"Call <get_weather> with {city}")
#     try:
#         # Step 1: Use Gemini to get latitude and longitude from city name
#         model = genai.GenerativeModel("gemini-2.0-flash-exp")

#         prompt = f"""Given the city name '{city}', provide the latitude and longitude coordinates.
#         Return ONLY a JSON object in this exact format with no additional text:
#         {{"latitude": <number>, "longitude": <number>}}"""

#         response = model.generate_content(prompt)

#         # Parse the response to extract coordinates
#         coords_text = response.text.strip()
#         # Remove markdown code blocks if present
#         if "```json" in coords_text:
#             coords_text = coords_text.split("```json")[1].split("```")[0].strip()
#         elif "```" in coords_text:
#             coords_text = coords_text.split("```")[1].split("```")[0].strip()

#         coords = json.loads(coords_text)
#         latitude = coords["latitude"]
#         longitude = coords["longitude"]

#         # Step 2: Call OpenMeteo API with the coordinates
#         openmeteo_url = "https://api.open-meteo.com/v1/forecast"
#         params = {
#             "latitude": latitude,
#             "longitude": longitude,
#             "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
#             "temperature_unit": "celsius",
#             "wind_speed_unit": "kmh",
#         }

#         weather_response = requests.get(openmeteo_url, params=params, timeout=10)
#         weather_response.raise_for_status()
#         weather_data = weather_response.json()

#         # Step 3: Format the weather report
#         current = weather_data["current"]
#         temp = current["temperature_2m"]
#         feels_like = current["apparent_temperature"]
#         humidity = current["relative_humidity_2m"]
#         wind_speed = current["wind_speed_10m"]
#         precipitation = current["precipitation"]

#         # Weather code interpretation (simplified)
#         weather_code = current["weather_code"]
#         weather_descriptions = {
#             0: "Clear sky",
#             1: "Mainly clear",
#             2: "Partly cloudy",
#             3: "Overcast",
#             45: "Foggy",
#             48: "Depositing rime fog",
#             51: "Light drizzle",
#             53: "Moderate drizzle",
#             55: "Dense drizzle",
#             61: "Slight rain",
#             63: "Moderate rain",
#             65: "Heavy rain",
#             71: "Slight snow",
#             73: "Moderate snow",
#             75: "Heavy snow",
#             80: "Slight rain showers",
#             81: "Moderate rain showers",
#             82: "Violent rain showers",
#             95: "Thunderstorm",
#         }
#         weather_desc = weather_descriptions.get(weather_code, "Unknown conditions")

#         report = (
#             f"The weather in {city} is {weather_desc.lower()} with a temperature of {temp}°C "
#             f"(feels like {feels_like}°C). Humidity is {humidity}%, wind speed is {wind_speed} km/h"
#         )

#         if precipitation > 0:
#             report += f", and there is {precipitation}mm of precipitation"

#         report += "."

#         print(f"Result <get_current_time> with {report}")
#         return {
#             "status": "success",
#             "report": report,
#         }

#     except json.JSONDecodeError as e:
#         # print(f"Error <get_current_time> with Failed to parse coordinates for '{city}': {str(e)}")
#         return {
#             "status": "error",
#             "error_message": f"Failed to parse coordinates for '{city}': {str(e)}",
#         }
#     except requests.RequestException as e:
#         # print(f"Error <get_current_time> with Failed to fetch weather data for '{city}': {str(e)}")
#         return {
#             "status": "error",
#             "error_message": f"Failed to fetch weather data for '{city}': {str(e)}",
#         }
#     except KeyError as e:
#         # print(f"Error <get_current_time> with Unexpected response format: missing key {str(e)}")
#         return {
#             "status": "error",
#             "error_message": f"Unexpected response format: missing key {str(e)}",
#         }
#     except Exception as e:
#         # print(f"Error <get_current_time> with An error occurred while fetching weather for '{city}': {str(e)}")
#         return {
#             "status": "error",
#             "error_message": f"An error occurred while fetching weather for '{city}': {str(e)}",
#         }


# def get_current_time(city: str) -> dict:
#     """Returns the current time in a specified city.

#     Args:
#         city (str): The name of the city for which to retrieve the current time.

#     Returns:
#         dict: status and result or error msg.
#     """
#     print(f"Call <get_current_time> with {city}")

#     if city.lower() == "new york":
#         tz_identifier = "America/New_York"
#     else:
#         return {
#             "status": "error",
#             "error_message": (f"Sorry, I don't have timezone information for {city}."),
#         }

#     tz = ZoneInfo(tz_identifier)
#     now = datetime.datetime.now(tz)
#     report = f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
#     print(f"Result <get_current_time> with {report}")
#     return {"status": "success", "report": report}

mcp_port = os.getenv("MCP_PORT", "7000")
mcp_server_url = f"http://localhost:{mcp_port}/sse"

tools = MCPToolset(
        connection_params=SseServerParams(url=mcp_server_url)
)
# tools = get_tools_async()

root_agent = Agent(
        name="weather_time_agent",
        model="gemini-2.5-flash",
        description="Agent to answer questions about the time and weather in a city.",
        instruction=(
            "You are a helpful agent who can answer user questions about the time and weather in a city."
        ),
        tools=[tools]
    )

a2a_app = to_a2a(root_agent)