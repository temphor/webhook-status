import requests
import json
from datetime import datetime, timedelta
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class StatusReceiver:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.clients = {}
        self.running = True
        
    def send_to_discord(self, client_id, status, player_name="", server=""):
        """Send status update to Discord"""
        colors = {
            "idle": 0x00ff00,    # Green
            "left": 0xff0000,    # Red
            "executed": 0x00aaff # Blue
        }
        
        embed = {
            "title": f"{player_name or client_id}",
            "fields": [
                {"name": "uh value ig", "value": status.upper(), "inline": True},
                {"name": "last updated yes", "value": datetime.now().strftime("%H:%M:%S")}
            ],
            "color": colors.get(status, 0x808080),
            "timestamp": datetime.now().isoformat()
        }
        
        payload = {
            "embeds": [embed],
            "username": "Roblox Monitor"
        }
        
        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f"Webhook error: {e}")
    
    def process_payload(self, payload):
        """Process incoming payload from Roblox"""
        try:
            data = json.loads(payload)
            client_id = data.get('client_id')
            player_name = data.get('player_name', 'Unknown')
            server = data.get('server', 'Unknown')
            status = data.get('status', 'idle')
            game_data = data.get('game_data', {})
            
            if client_id:
                # Update client info
                self.clients[client_id] = {
                    'last_seen': datetime.now(),
                    'status': status,
                    'player_name': player_name,
                    'server': server,
                    'game_data': game_data
                }
                
                # Send initial execution notification
                if status == 'executed':
                    self.send_to_discord(client_id, 'executed', player_name, server)
                    self.send_to_discord(client_id, 'idle', player_name, server)
                else:
                    self.send_to_discord(client_id, status, player_name, server)
                
                return True
        except Exception as e:
            print(f"Process error: {e}")
            return False
    
    def check_timeouts(self, timeout_seconds=15):
        """Check for clients that haven't reported"""
        while self.running:
            time.sleep(5)
            now = datetime.now()
            
            for client_id, info in list(self.clients.items()):
                if (now - info['last_seen']).total_seconds() > timeout_seconds:
                    if info['status'] != 'left':
                        self.send_to_discord(client_id, 'left', info.get('player_name', 'Unknown'), info.get('server', 'Unknown'))
                        self.clients[client_id]['status'] = 'left'
    
    def start(self):
        """Start the monitoring system"""
        checker = threading.Thread(target=self.check_timeouts)
        checker.daemon = True
        checker.start()
        
        print("")
        print("")
        
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                try:
                    payload = post_data.decode('utf-8')
                    success = receiver.process_payload(payload)
                    
                    self.send_response(200 if success else 400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    
                    response = json.dumps({"status": "success" if success else "error"})
                    self.wfile.write(response.encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    print(f"Handler error: {e}")
            
            def log_message(self, format, *args):
                pass
        
        server = HTTPServer(('localhost', 8080), Handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.running = False
            server.shutdown()

receiver = StatusReceiver("https://discord.com/api/webhooks/1455588118144094412/Pu5Hkyd8xgBlyVv71ehF6S83CWKWOlXjC8aOdtXr0oX0wSpgOdl7vW3ZICi3SD_ax0no")
receiver.start()
