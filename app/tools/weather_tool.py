import requests
from geopy.geocoders import Nominatim
from langchain_core.tools import tool
from pydantic import BaseModel, Field

geolocator = Nominatim(user_agent="weather-app")


# Input schema for the tool
class SearchInput(BaseModel):
    location: str = Field(description="The city and state, e.g., San Francisco")
    date: str = Field(
        description="The forecasting date for when to get the weather format (yyyy-mm-dd)"
    )


# Tool definition
@tool("get_weather_forecast", args_schema=SearchInput, return_direct=True)
def get_weather_forecast(location: str, date: str):
    """Retrieves the weather using Open-Meteo API for a given location (city) and a date (yyyy-mm-dd)."""
    location_data = geolocator.geocode(location)
    if location_data:
        try:
            response = requests.get(
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={location_data.latitude}&longitude={location_data.longitude}&"
                f"hourly=temperature_2m&start_date={date}&end_date={date}"
            )
            data = response.json()
            return {
                time: temp
                for time, temp in zip(
                    data["hourly"]["time"], data["hourly"]["temperature_2m"]
                )
            }
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "Location not found"}
