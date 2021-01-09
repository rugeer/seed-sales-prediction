#!python3
# -*- coding: utf-8 -*-
import click
import uvicorn


@click.command()
@click.help_option()
@click.option("--host", type=str, default="127.0.0.1", help="Host")
@click.option("--port", type=int, default=5000, help="Port")
def app(port, host):
    """Start sales prediction server."""
    uvicorn.run(
        "seed_sales_prediction.server:app", host=host, port=port, log_level="info"
    )


if __name__ == "__main__":
    app()
