#!/bin/bash
set -e

echo "=== Strategem Core VPS Deployment ==="

# Configuration
APP_DIR="/opt/strategem"
REPO_URL="https://github.com/0xmaritime/strategem.git"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "[1/6] Installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git nginx

echo "[2/6] Setting up application directory..."
if [ -d "$APP_DIR" ]; then
    echo "Directory exists, pulling latest code..."
    cd "$APP_DIR"
    git pull
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

echo "[3/6] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/6] Creating systemd service..."
cp strategem.service /etc/systemd/system/
systemctl daemon-reload

echo "[5/6] Setting permissions..."
mkdir -p strategem/storage strategem/reports
chown -R www-data:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"

echo "[6/6] Starting service..."
systemctl enable strategem
systemctl start strategem

echo ""
echo "=== Deployment Complete ==="
echo "Status: $(systemctl is-active strategem)"
echo "Logs: sudo journalctl -u strategem -f"
echo "URL: http://YOUR_VPS_IP:8000"
echo ""
echo "Next steps:"
echo "1. Edit /etc/systemd/system/strategem.service to add your API key"
echo "2. Run: sudo systemctl restart strategem"
echo "3. Set up Nginx reverse proxy (optional, see nginx.conf)"
