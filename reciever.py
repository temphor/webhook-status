import requests
import json
from datetime import datetime
import os

WEBHOOK_URL = "https://discord.com/api/webhooks/1455588118144094412/Pu5Hkyd8xgBlyVv71ehF6S83CWKWOlXjC8aOdtXr0oX0wSpgOdl7vW3ZICi3SD_ax0no"

# Store client statuses (in-memory, resets on function cold start)
clients = {}

def send_to_discord(client_id, status, player_name="", server=""):
    """Send status update to Discord"""
    colors = {
        "idle": 0x00ff00,
        "left": 0xff0000,
        "executed": 0x00aaff
    }
    
    embed = {
        "title": f"{player_name or client_id}",
        "fields": [
            {"name": "status", "value": status.upper(), "inline": True},
            {"name": "id", "value": client_id[:8] + "...", "inline": True},
            {"name": "server", "value": server or "Unknown", "inline": True}
        ],
        "color": colors.get(status, 0x808080),
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]})
    except Exception as e:
        print(f"Webhook error: {e}")

def handler(request):
    """Vercel serverless function handler"""
    
    # Handle GET request (for testing)
    if request.method == "GET":
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Webhook receiver is running!",
                "clients": len(clients)
            })
        }
    
    if request.method == "POST":
        try:
            # Parse the incoming JSON
            data = request.get_json()
            
            client_id = data.get('client_id')
            player_name = data.get('player_name', 'Unknown')
            server = data.get('server', 'Unknown')
            status = data.get('status', 'idle')
            
                # Update client info
                clients[client_id] = {
                    'last_seen': datetime.now().isoformat(),
                    'status': status,
                    'player_name': player_name,
                    'server': server
                }
                
                send_to_discord(client_id, status, player_name, server)
                
                return {
                    "statusCode": 200,
                    "body": json.dumps({"status": "success"})
                }
            
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)})
            }
    
    return {
        "statusCode": 405,
        "body": json.dumps({"error": "Method not allowed"})
    }
