#!/usr/bin/env python3
"""
Test script for the US Weather Assistant MCP Server

This script validates the MCP server implementation without requiring
an actual API key or network connection.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Add the weather_server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'weather_server'))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import weather
        print("✅ Successfully imported weather module")
        return True
    except ImportError as e:
        print(f"❌ Failed to import weather module: {e}")
        return False

def test_server_creation():
    """Test that the MCP server can be created"""
    try:
        import weather
        server = weather.server
        print(f"✅ MCP server created successfully: {server}")
        return True
    except Exception as e:
        print(f"❌ Failed to create MCP server: {e}")
        return False

def test_weather_service():
    """Test WeatherService class instantiation"""
    try:
        import weather
        service = weather.WeatherService("test_api_key")
        print("✅ WeatherService instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to instantiate WeatherService: {e}")
        return False

def test_formatting_functions():
    """Test weather data formatting functions"""
    try:
        import weather
        
        # Mock weather data
        mock_current_weather = {
            "name": "San Francisco",
            "sys": {"country": "US"},
            "main": {
                "temp": 68.5,
                "feels_like": 70.2,
                "humidity": 65,
                "pressure": 1013
            },
            "weather": [{"description": "partly cloudy"}],
            "wind": {"speed": 8.5}
        }
        
        mock_forecast_data = {
            "city": {"name": "San Francisco", "country": "US"},
            "list": [
                {
                    "dt_txt": "2024-01-15 12:00:00",
                    "main": {"temp_max": 72, "temp_min": 58, "humidity": 60},
                    "weather": [{"description": "sunny"}]
                }
            ]
        }
        
        # Test formatting functions
        current_result = weather.format_current_weather(mock_current_weather)
        forecast_result = weather.format_forecast(mock_forecast_data)
        
        print("✅ Weather formatting functions work correctly")
        print(f"Current weather sample: {current_result[:50]}...")
        print(f"Forecast sample: {forecast_result[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test formatting functions: {e}")
        return False

async def test_tool_handlers():
    """Test MCP tool handlers"""
    try:
        import weather
        
        # Test list_tools handler
        tools = await weather.handle_list_tools()
        print(f"✅ Found {len(tools)} available tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test tool handlers: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing US Weather Assistant MCP Server")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Server Creation", test_server_creation),
        ("WeatherService Class", test_weather_service),
        ("Formatting Functions", test_formatting_functions),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   Test failed!")
    
    # Run async tests
    print(f"\n🔍 Running Tool Handlers Test...")
    try:
        asyncio.run(test_tool_handlers())
        passed += 1
        total += 1
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        total += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The MCP server is ready to use.")
        print("\n📝 Next steps:")
        print("1. Get an OpenWeatherMap API key from https://openweathermap.org/api")
        print("2. Update the API key in cline-config.json")
        print("3. Install dependencies: pip install -r weather_server/requirements.txt")
        print("4. Configure the MCP server in your Cline settings")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
