import os
import subprocess

import click


@click.group()
def cli():
	"""CLI for RAG Backend Service."""
	pass


@cli.command()
def start():
	"""Start the backend service."""
	subprocess.Popen(
		["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
		stdout=subprocess.PIPE,
	)


@cli.command()
def stop():
	"""Stop the backend service."""
	os.system("pkill -f 'uvicorn main:app'")


@cli.command()
def restart():
	"""Restart the backend service."""
	os.system("pkill -f 'uvicorn main:app'")
	subprocess.Popen(
		["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
		stdout=subprocess.PIPE,
	)


if __name__ == "__main__":
	cli()
