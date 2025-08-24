#!/usr/bin/env python3
"""
US Weather Assistant MCP Server

This MCP server provides weather information for US locations using the OpenWeatherMap API.
It offers tools to get current weather, forecasts, and weather alerts.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
import aiohttp
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-server")

# OpenWeatherMap API configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Create MCP server instance
server = Server("us-weather-assistant")

class WeatherService:
    """Service class to handle weather API calls"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_current_weather(self, city: str, state: str = None) -> Dict[str, Any]:
        """Get current weather for a US city"""
        location = f"{city},{state},US" if state else f"{city},US"
        url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "imperial"  # Fahrenheit for US
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise Exception(f"Weather API error: {error_data.get('message', 'Unknown error')}")
    
    async def get_forecast(self, city: str, state: str = None, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a US city"""
        location = f"{city},{state},US" if state else f"{city},US"
        url = f"{OPENWEATHER_BASE_URL}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "imperial",
            "cnt": min(days * 8, 40)  # API returns 3-hour intervals, max 40 entries
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise Exception(f"Forecast API error: {error_data.get('message', 'Unknown error')}")

def format_current_weather(weather_data: Dict[str, Any]) -> str:
    """Format current weather data into readable text"""
    main = weather_data["main"]
    weather = weather_data["weather"][0]
    wind = weather_data.get("wind", {})
    
    location = f"{weather_data['name']}, {weather_data['sys']['country']}"
    temp = round(main["temp"])
    feels_like = round(main["feels_like"])
    humidity = main["humidity"]
    description = weather["description"].title()
    
    result = f"Current Weather in {location}:\n"
    result += f"🌡️ Temperature: {temp}°F (feels like {feels_like}°F)\n"
    result += f"☁️ Conditions: {description}\n"
    result += f"💧 Humidity: {humidity}%\n"
    
    if "speed" in wind:
        wind_speed = round(wind["speed"])
        result += f"💨 Wind Speed: {wind_speed} mph\n"
    
    if "pressure" in main:
        pressure = main["pressure"]
        result += f"🔽 Pressure: {pressure} hPa\n"
    
    return result

def format_forecast(forecast_data: Dict[str, Any]) -> str:
    """Format forecast data into readable text"""
    city = forecast_data["city"]["name"]
    country = forecast_data["city"]["country"]
    forecasts = forecast_data["list"]
    
    result = f"Weather Forecast for {city}, {country}:\n\n"
    
    # Group forecasts by day
    daily_forecasts = {}
    for forecast in forecasts:
        date = forecast["dt_txt"].split(" ")[0]
        if date not in daily_forecasts:
            daily_forecasts[date] = []
        daily_forecasts[date].append(forecast)
    
    # Format each day
    for date, day_forecasts in list(daily_forecasts.items())[:5]:  # Limit to 5 days
        # Get midday forecast for the day summary
        midday_forecast = day_forecasts[len(day_forecasts)//2]
        main = midday_forecast["main"]
        weather = midday_forecast["weather"][0]
        
        temp_high = max(f["main"]["temp_max"] for f in day_forecasts)
        temp_low = min(f["main"]["temp_min"] for f in day_forecasts)
        
        result += f"📅 {date}:\n"
        result += f"   🌡️ High: {round(temp_high)}°F, Low: {round(temp_low)}°F\n"
        result += f"   ☁️ {weather['description'].title()}\n"
        result += f"   💧 Humidity: {main['humidity']}%\n\n"
    
    return result

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available weather tools"""
    return [
        types.Tool(
            name="get_current_weather",
            description="Get current weather conditions for a US city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'New York', 'Los Angeles')"
                    },
                    "state": {
                        "type": "string",
                        "description": "The state abbreviation (e.g., 'NY', 'CA') - optional but recommended for accuracy"
                    }
                },
                "required": ["city"]
            }
        ),
        types.Tool(
            name="get_weather_forecast",
            description="Get weather forecast for a US city (up to 5 days)",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'New York', 'Los Angeles')"
                    },
                    "state": {
                        "type": "string",
                        "description": "The state abbreviation (e.g., 'NY', 'CA') - optional but recommended for accuracy"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast (1-5, default: 5)",
                        "minimum": 1,
                        "maximum": 5
                    }
                },
                "required": ["city"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    if not OPENWEATHER_API_KEY:
        return [types.TextContent(
            type="text",
            text="Error: OpenWeatherMap API key not configured. Please set the OPENWEATHER_API_KEY environment variable."
        )]
    
    try:
        async with WeatherService(OPENWEATHER_API_KEY) as weather_service:
            if name == "get_current_weather":
                city = arguments.get("city")
                state = arguments.get("state")
                
                if not city:
                    return [types.TextContent(
                        type="text",
                        text="Error: City name is required"
                    )]
                
                weather_data = await weather_service.get_current_weather(city, state)
                formatted_weather = format_current_weather(weather_data)
                
                return [types.TextContent(
                    type="text",
                    text=formatted_weather
                )]
            
            elif name == "get_weather_forecast":
                city = arguments.get("city")
                state = arguments.get("state")
                days = arguments.get("days", 5)
                
                if not city:
                    return [types.TextContent(
                        type="text",
                        text="Error: City name is required"
                    )]
                
                forecast_data = await weather_service.get_forecast(city, state, days)
                formatted_forecast = format_forecast(forecast_data)
                
                return [types.TextContent(
                    type="text",
                    text=formatted_forecast
                )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'"
                )]
    
    except Exception as e:
        logger.error(f"Error in tool '{name}': {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Main function to run the MCP server"""
    # Server capabilities
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="us-weather-assistant",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
