from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.ingest import ingest_xml


def _render_tool_result(result) -> str:
    parts = []
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    structured = getattr(result, "structuredContent", None)
    if structured:
        parts.append(str(structured))
    return "\n".join(parts) or str(result)


async def _scenario(db_url: str):
    env = dict(os.environ)
    env["DATABASE_URL"] = db_url
    env["PYTHONPATH"] = str(Path.cwd())

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server"],
        env=env,
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            listed = await session.list_tools()
            names = {tool.name for tool in listed.tools}
            assert {
                "search_trademark",
                "compare_trademark",
                "get_trademark",
            }.issubset(names)

            search = await session.call_tool(
                "search_trademark",
                arguments={
                    "query": "MARCA EXEMPLO",
                    "nice_classes": [39],
                    "limit": 10,
                },
            )
            assert not getattr(search, "isError", False)
            assert "123456789" in _render_tool_result(search)

            get_result = await session.call_tool(
                "get_trademark",
                arguments={"process_number": "123456789"},
            )
            assert not getattr(get_result, "isError", False)
            rendered_get = _render_tool_result(get_result)
            assert "123456789" in rendered_get
            assert "MARCA EXEMPLO" in rendered_get

            compare = await session.call_tool(
                "compare_trademark",
                arguments={
                    "left_name": "MARCA EXEMPLO",
                    "right_name": "MARCA EXEMPLO",
                    "left_classes": [39],
                    "right_classes": [39],
                },
            )
            assert not getattr(compare, "isError", False)
            assert "1.0" in _render_tool_result(compare)


def test_mcp_stdio_transport_with_real_tool_calls(tmp_path):
    db_path = tmp_path / "mcp-stdio.db"
    db_url = f"sqlite+pysqlite:///{db_path.as_posix()}"

    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        ingest_xml(session, "fixtures/rpi-layout-sample.xml")

    asyncio.run(_scenario(db_url))
