# review_mcp/server.py

from mcp.server.fastmcp import FastMCP

from review_mcp.tools.review_project import review_project

mcp = FastMCP(
    "Review MCP",
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


if __name__ == "__main__":
    mcp.run()