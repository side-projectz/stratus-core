import os
import signal
import subprocess
from pathlib import Path

import typer
from dotenv import find_dotenv, load_dotenv

import app.config as config

load_dotenv(find_dotenv())
app_cli = typer.Typer()
PID_FILE = Path("server.pid")


@app_cli.command()
def start():
	"""
	Start the FastAPI app using Uvicorn.
	"""
	if PID_FILE.exists():
		typer.secho(
			"Server seems to be already running (pidfile exists).", fg=typer.colors.RED
		)
		raise typer.Exit(code=1)

	# Start the server in a subprocess
	process = subprocess.Popen(
		[
			"python",
			"main.py",
		]
	)

	# Store the PID so we can shut it down later
	PID_FILE.write_text(str(process.pid))
	typer.secho(
		f"Server started on http://{config.HOST}:{config.PORT} (PID: {process.pid})",
		fg=typer.colors.GREEN,
	)


@app_cli.command()
def stop():
	"""
	Stop the FastAPI app if it's running (based on the PID file).
	"""
	if not PID_FILE.exists():
		typer.secho(
			"No server PID file found. Is the server running?", fg=typer.colors.RED
		)
		raise typer.Exit(code=1)

	pid_str = PID_FILE.read_text().strip()
	try:
		pid = int(pid_str)
	except ValueError:
		typer.secho("PID file is corrupted.", fg=typer.colors.RED)
		raise typer.Exit(code=1)

	# Send SIGTERM (polite request to terminate)
	try:
		os.kill(pid, signal.SIGTERM)
		typer.secho(
			f"Sent SIGTERM to server process (PID {pid}).", fg=typer.colors.GREEN
		)
	except ProcessLookupError:
		typer.secho("No process found with that PID.", fg=typer.colors.RED)

	# Remove the PID file regardless
	PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
	app_cli()
