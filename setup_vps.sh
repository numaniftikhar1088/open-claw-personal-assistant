#!/bin/bash
# Autonomous AI Job Scraper & Profiler Agent - VPS Setup Script

set -e

echo "🚀 Starting VPS Environment Setup for Autonomous AI Job Scraper & Profiler..."

# 1. Update System & Install Core Dependencies
sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv git curl build-essential

# 2. Install Ollama
if ! command -v ollama &> /dev/null
then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama is already installed."
fi

# 3. Start Ollama Service & Pull llama3.2 Model
echo "🧠 Starting Ollama service and pulling llama3.2..."
sudo systemctl enable ollama || true
sudo systemctl start ollama || true
ollama pull llama3.2

# 4. Set Up Python Virtual Environment
echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ VPS Setup Complete!"
echo "To launch the Streamlit Web Interface, run:"
echo "  source .venv/bin/activate"
echo "  streamlit run app.py --server.port=8501 --server.address=0.0.0.0"
