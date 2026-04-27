#!/usr/bin/env python3
import argparse
import asyncio
import json

from mcp import ClientSession
from mcp.client.sse import sse_client


def format_input_schema(schema: dict) -> str:
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect one or all tools from a running FusionMCP server.")
    parser.add_argument("--url", default="http://127.0.0.1:8081/mcp/sse", help="FusionMCP SSE endpoint URL")
    parser.add_argument("--tool", help="Optional tool name to inspect")
    args = parser.parse_args()

    async with sse_client(args.url) as streams:
        read_stream, write_stream = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()

    selected = sorted(tools.tools, key=lambda item: item.name)
    if args.tool:
        selected = [tool for tool in selected if tool.name == args.tool]

    if not selected:
        raise SystemExit(f"No tool found for name: {args.tool}")

    for tool in selected:
        print(f"Name: {tool.name}")
        print(f"Description: {tool.description}")
        print("Input schema:")
        print(format_input_schema(tool.inputSchema))
        print()


if __name__ == "__main__":
    asyncio.run(main())
