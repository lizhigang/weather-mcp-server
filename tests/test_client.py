"""Simple CLI client to test the MCP weather server via stdio.

Usage:
    python test_client.py

Make sure to activate your virtual environment first.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration - adjust these paths to match your environment
# Or use: python -m weather_mcp.server
SERVER_CMD = "python"
SERVER_CWD = str(project_root)


async def run():
    server_params = StdioServerParameters(
        command=SERVER_CMD,
        args=["-m", "weather_mcp.server"],
        cwd=SERVER_CWD,
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            while True:
                print("\n--- MCP Weather Client ---")
                print("1. Get current weather")
                print("2. Get weather forecast")
                print("3. List supported cities")
                print("q. Quit")
                choice = input("\nChoose: ").strip()

                if choice == "q":
                    break
                elif choice == "1":
                    city = input("City name: ").strip()
                    result = await session.call_tool("get_current_weather_tool", {"city": city})
                elif choice == "2":
                    city = input("City name: ").strip()
                    days = input("Days (1-7, default 3): ").strip()
                    args = {"city": city}
                    if days:
                        args["days"] = int(days)
                    result = await session.call_tool("get_weather_forecast_tool", args)
                elif choice == "3":
                    result = await session.call_tool("list_supported_cities_tool", {})
                else:
                    print("Invalid choice")
                    continue

                for c in result.content:
                    try:
                        data = json.loads(c.text)
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError:
                        print(c.text)


if __name__ == "__main__":
    asyncio.run(run())
