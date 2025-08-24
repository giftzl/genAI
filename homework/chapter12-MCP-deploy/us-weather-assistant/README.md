# US Weather Assistant MCP Server

A Model Context Protocol (MCP) server that provides weather information for US locations using the OpenWeatherMap API.

## Features

- **Current Weather**: Get real-time weather conditions for any US city
- **Weather Forecast**: Get up to 5-day weather forecasts
- **US-Focused**: Optimized for US locations with imperial units (Fahrenheit, mph)
- **Rich Formatting**: Weather data presented with emojis and clear formatting

## Setup Instructions

### 1. Get OpenWeatherMap API Key

1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key from your dashboard

### 2. Install Dependencies

```bash
cd us-weather-assistant/weather_server
pip install -r requirements.txt
```

### 3. Configure API Key

Update the `cline-config.json` file with your OpenWeatherMap API key:

```json
{
  "mcpServers": {
    "us-weather-assistant": {
      "command": "python",
      "args": [
        "weather_server/weather.py"
      ],
      "cwd": "us-weather-assistant",
      "env": {
        "OPENWEATHER_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

### 4. Test the Server

You can test the server directly:

```bash
cd us-weather-assistant
python weather_server/weather.py
```

## Available Tools

### get_current_weather

Get current weather conditions for a US city.

**Parameters:**
- `city` (required): The city name (e.g., "New York", "Los Angeles")
- `state` (optional): The state abbreviation (e.g., "NY", "CA") - recommended for accuracy

**Example:**
```json
{
  "city": "San Francisco",
  "state": "CA"
}
```

### get_weather_forecast

Get weather forecast for a US city (up to 5 days).

**Parameters:**
- `city` (required): The city name (e.g., "New York", "Los Angeles")
- `state` (optional): The state abbreviation (e.g., "NY", "CA") - recommended for accuracy
- `days` (optional): Number of days to forecast (1-5, default: 5)

**Example:**
```json
{
  "city": "Miami",
  "state": "FL",
  "days": 3
}
```

## Usage with Cline

1. Copy the `cline-config.json` to your Cline configuration directory
2. Update the API key in the configuration
3. Restart Cline to load the MCP server
4. Use the weather tools in your conversations:
   - "What's the current weather in New York?"
   - "Give me a 3-day forecast for Los Angeles, CA"

## Project Structure

```
us-weather-assistant/
├── weather_server/
│   ├── weather.py          # Main MCP server implementation
│   ├── requirements.txt    # Python dependencies
│   └── sdk/               # Optional: Manual MCP SDK installation
├── cline-config.json      # Cline MCP server configuration
└── README.md             # This file
```

## Error Handling

The server includes comprehensive error handling for:
- Missing API key configuration
- Invalid city names
- API rate limits
- Network connectivity issues
- Malformed requests

## Development

To contribute or modify the server:

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black weather_server/weather.py
   ```

4. Lint code:
   ```bash
   flake8 weather_server/weather.py
   ```

## License

This project is open source and available under the MIT License.
