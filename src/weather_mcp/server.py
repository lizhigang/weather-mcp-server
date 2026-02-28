"""MCP Weather Server - Provides mock weather information via MCP protocol."""

import argparse
import signal
import sys

from mcp.server.fastmcp import FastMCP

try:
    from weather_mcp.weather_service import get_cities, get_current_weather, get_forecast
    print("✅ 使用绝对导入: weather_mcp.weather_service")
except ModuleNotFoundError:
    from weather_service import get_cities, get_current_weather, get_forecast
    print("✅ 使用相对导入: weather_service")


def create_mcp_server(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    """Create and configure the MCP server with tools."""
    mcp = FastMCP("weather-server", host=host, port=port)

    @mcp.tool()
    def get_current_weather_tool(city: str) -> dict:
        """Get the current weather for a specified city.

        Returns temperature, humidity, wind speed, weather conditions and more.
        Use list_supported_cities to see which cities are available.

        Args:
            city: Name of the city, e.g. "Beijing", "London", "New York"
        """
        return get_current_weather(city)

    @mcp.tool()
    def get_weather_forecast_tool(city: str, days: int = 3) -> dict:
        """Get a multi-day weather forecast for a specified city.

        Returns daily forecasts including high/low temperatures, conditions,
        humidity, wind speed and precipitation chance.

        Args:
            city: Name of the city, e.g. "Tokyo", "Paris", "Sydney"
            days: Number of forecast days (1-7, default 3)
        """
        return get_forecast(city, days)

    @mcp.tool()
    def list_supported_cities_tool() -> list[dict]:
        """List all cities supported by this weather service.

        Returns city names with their country and coordinates.
        Use this to discover which cities you can query weather for.
        """
        return get_cities()

    return mcp


def signal_handler(sig, frame, transport: str = "stdio"):
    """Handle shutdown signals gracefully."""
    # Only print to stdout for HTTP modes; stdio mode must not pollute stdout
    if transport != "stdio":
        print("\n👋 Shutting down gracefully...", file=sys.stderr)
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Weather MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport type: stdio (default), sse, or streamable-http"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="HTTP server host (default: 0.0.0.0, only used with --transport sse/streamable-http)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="HTTP server port (default: 8080, only used with --transport sse/streamable-http)"
    )

    args = parser.parse_args()

    # Create a signal handler bound to the current transport
    def bound_signal_handler(sig, frame):
        signal_handler(sig, frame, transport=args.transport)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, bound_signal_handler)
    signal.signal(signal.SIGTERM, bound_signal_handler)

    try:
        if args.transport == "stdio":
            mcp = create_mcp_server()
            mcp.run(transport="stdio")
        elif args.transport in ("sse", "streamable-http"):
            print(f"🌐 Starting HTTP server on http://{args.host}:{args.port}", file=sys.stderr)
            print("Press Ctrl+C to stop", file=sys.stderr)
            mcp = create_mcp_server(host=args.host, port=args.port)
            mcp.run(transport=args.transport)
    except KeyboardInterrupt:
        bound_signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    main()
