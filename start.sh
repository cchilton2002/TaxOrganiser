#!/bin/zsh

sudo systemctl start mysql

echo "Starting backend.."
source venv/bin/activate
PYTHONPATH=. python3 backend/server.py &
BACKEND_PID=$!

echo "Starting frontend"
cd frontend
gnome-terminal -- zsh -c "npm start; exec zsh"

echo "Backend running with PID $BACKEND_PID"


