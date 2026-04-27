#!/usr/bin/env python3
import argparse
import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client


async def main() -> None:
    parser = argparse.ArgumentParser(description="List all tools from a running FusionMCP server.")
    parser.add_argument("--url", default="http://127.0.0.1:8081/mcp/sse", help="FusionMCP SSE endpoint URL")
    args = parser.parse_args()

    async with sse_client(args.url) as streams:
        read_stream, write_stream = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()

    print("Registered FusionMCP tools:")
    for tool in sorted(tools.tools, key=lambda item: item.name):
        print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
