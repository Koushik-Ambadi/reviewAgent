# review_mcp/server.py

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from review_mcp.tools.review_project import review_project

mcp = FastMCP(
    "Review MCP",
    instructions=(
        Path(__file__).parent
        .joinpath("skills", "agent_context.md")
        .read_text(encoding="utf-8")
    ),
)


@mcp.tool(name="review_project")
def review_project_tool(
    repository_path: str,
) -> dict:
    """
    Run the Review Platform on a local repository.
    """

    return review_project(
        repository_path,
    )

@mcp.prompt(title="Reviewer")
def reviewer_persona() -> str:
    return (
        Path(__file__).parent
        .joinpath("skills", "reviewer.md")
        .read_text(encoding="utf-8")
    )


@mcp.prompt(title="Optimizer")
def optimizer_persona() -> str:
    return (
        Path(__file__).parent
        .joinpath("skills", "optimizer.md")
        .read_text(encoding="utf-8")
    )


@mcp.prompt(title="Builder")
def builder_persona() -> str:
    return (
        Path(__file__).parent
        .joinpath("skills", "builder.md")
        .read_text(encoding="utf-8")
    )




if __name__ == "__main__":
    mcp.run()