#!/bin/bash

exec > /var/log/userdata.log 2>&1
set -x

# Update packages
apt-get update -y

# Install Python and venv
apt-get install -y python3 python3-pip python3-venv

# Create app directory
mkdir -p /home/ubuntu/app
chown -R ubuntu:ubuntu /home/ubuntu/app

# Create virtual environment
python3 -m venv /home/ubuntu/app/venv

# Install Flask inside venv
/home/ubuntu/app/venv/bin/pip install flask

# Write Flask app directly
cat > /home/ubuntu/app/app.py << 'APPEOF'
from flask import Flask, jsonify
import socket
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    hostname  = socket.gethostname()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <html>
    <body style="font-family:monospace;background:#0d1117;color:#58a6ff;
                 display:flex;align-items:center;justify-content:center;
                 height:100vh;margin:0;">
      <div style="text-align:center">
        <h1 style="color:#f0883e">IaC Demo</h1>
        <p>Served by: <strong>{hostname}</strong></p>
        <p>Time: {timestamp}</p>
        <p style="color:#8b949e;font-size:12px">
          Terraform · Ansible · AWS
        </p>
      </div>
    </body>
    </html>
    """

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "host": socket.gethostname()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
APPEOF

# Create systemd service
cat > /etc/systemd/system/flaskapp.service << 'SVCEOF'
[Unit]
Description=Flask IaC Demo App
After=network.target

[Service]
User=root
WorkingDirectory=/home/ubuntu/app
ExecStart=/home/ubuntu/app/venv/bin/python /home/ubuntu/app/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

# Enable and start Flask
systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp

echo "Bootstrap complete — Flask running on port 80"
