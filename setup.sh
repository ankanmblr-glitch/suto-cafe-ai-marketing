#!/bin/bash
echo "============================================================"
echo " Suto Cafe AI Marketing Platform -- PoC Setup (Mac/Linux)"
echo "============================================================"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 not found. Install Python 3.11+"
    exit 1
fi
echo "[OK] $(python3 --version)"

# Create venv
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
fi
echo "[OK] Virtual environment ready"

# Install
echo "[INFO] Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet
echo "[OK] Dependencies installed"

# Copy .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "[INFO] Created .env -- add your API keys"
else
    echo "[OK] .env already exists"
fi

echo ""
echo "============================================================"
echo " Setup complete!"
echo ""
echo " NEXT STEPS:"
echo " 1. Edit .env and add free API keys:"
echo "    GROQ_API_KEY  -> free at console.groq.com"
echo "    OPENWEATHER_API_KEY -> free at openweathermap.org"
echo "    OR: set DEMO_MODE=true to skip all API keys"
echo ""
echo " 2. Run: source venv/bin/activate && streamlit run app.py"
echo " 3. Open: http://localhost:8501"
echo "============================================================"
