import os
import sys
import logging
from getpass import getpass


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def ensure_directory_exists(path):
    """Ensure that a directory exists; if not, create it."""
    if not os.path.exists(path):
        os.makedirs(path)


def get_api_key(env_var, client_name):
    """Retrieve API key from environment or prompt user if not found."""
    api_key = os.getenv(env_var)
    if not api_key:
        logging.info(
            f"API key for {client_name} ({env_var}) not found. Please enter your API key:"
        )
        api_key = getpass(
            prompt=(
                f"\nAPI key for {client_name} ({env_var}) not found. Please enter your API key:\n"
            )
        )
    return api_key


def exit_with_message(message, code=1):
    """Print an error message and exit with a given code."""
    logging.error(message)
    sys.exit(code)
