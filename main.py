from mcp.server.fastmcp import Context, FastMCP
import asyncio

mcp = FastMCP(name="Context Example")


@mcp.tool()
async def add(x: int, y: int, ctx: Context) -> int:
    out = x+y
    await ctx.info(f"adding {x} and {y}")
    return out

@mcp.tool()
async def multiply(x:int, y: int, ctx: Context) -> int:
    out = x*y
    await ctx.info(f"multipling {x} and {y}")
    return out

@mcp.tool()
async def subtract(x:int, y: int, ctx: Context) -> int:
    out = x-y
    await ctx.info(f"subtracting {x} and {y}")
    return out

@mcp.tool()
async def divide(x:int, y: int, ctx: Context) -> int:
    out = x/y
    await ctx.info(f"dividing {x} and {y}")
    return out

if __name__ == "__main__":
    mcp.run(transport="sse")
