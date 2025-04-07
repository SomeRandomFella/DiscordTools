#!/bin/bash
# Discord Tools Suite Boot Script
# This script provides a unified way to start different components
# of the Discord Tools Suite.

# Help function to display usage info
show_help() {
  echo "Discord Tools Suite Boot Script"
  echo "Usage: ./boot.sh [command]"
  echo ""
  echo "Commands:"
  echo "  server        Start the web application server"
  echo "  check         Check if bot modules are installed properly"
  echo "  help          Show this help message"
}

# Function to start the web server
start_server() {
  echo "Starting Discord Tools Suite web server..."
  if command -v gunicorn &> /dev/null; then
    gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
  else
    echo "Gunicorn not found, falling back to Flask development server"
    python main.py
  fi
}

# Function to check if bot modules are properly installed
check_bot() {
  echo "Checking Discord bot modules..."
  python bot_check.py
}

# Main logic
case "$1" in
  server)
    start_server
    ;;
  check)
    check_bot
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    if [ -z "$1" ]; then
      # Default action if no argument provided
      start_server
    else
      echo "Unknown command: $1"
      show_help
      exit 1
    fi
    ;;
esac
