#!/usr/bin/env python
"""Run Django management commands for the CloudOps chatbot."""
import os
import sys


def main() -> None:
    """Initialize Django settings and dispatch the requested command."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartchat.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
