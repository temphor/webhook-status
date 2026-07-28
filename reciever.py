from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1455588118144094412/Pu5Hkyd8xgBlyVv71ehF6S83CWKWOlXjC8aOdtXr0oX0wSpgOdl7vW3ZICi3SD_ax0no"

def send_to_discord(client_id, status, player_name="", server=""):
    colors = {
        "idle": 0x00ff00,
        "left": 0xff0000,
        "executed": 0x00aaff
    }
    
    embed = {
        "title": f"{player_name or client_id}",
        "fields": [
            {"name": "sum tuff status", "value": status.upper(), "inline": True},
            {"name": "id", "value": client_id[:8] + "...", "inline": True},
            {"name": "serv", "value": server or "Unknown", "inline": True}
        ],
        "color": colors.get(status, 0x808080),
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]})
        return True
    except:
        return False

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'GET':
        return jsonify({
            "message": "Webhook receiver is running!",
            "status": "online"
        })
    
    if request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data"}), 400
            
        client_id = data.get('client_id')
        player_name = data.get('player_name', 'Unknown')
        server = data.get('server', 'Unknown')
        status = data.get('status', 'idle')
        
        if client_id:
            success = send_to_discord(client_id, status, player_name, server)
            return jsonify({"status": "success", "client": client_id})
        else:
            return jsonify({"error": "Missing client_id"}), 400

app = app
