from flask import Flask
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
    return {"status": "healthy", "host": socket.gethostname()}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
