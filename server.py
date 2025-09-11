import socket
import threading
import json
from datetime import datetime

class ConnectionServer:
    def __init__(self, host='localhost', port=9999, police_port=8888):
        self.host = host
        self.port = port
        self.police_port = police_port
        self.clients = []
        self.lock = threading.Lock()
        
    def notify_police(self, user_name, action):
        """Send notification to police monitor about user connection"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.police_port))
                message = {
                    'user': user_name,
                    'action': action,
                    'timestamp': datetime.now().isoformat()
                }
                s.send(json.dumps(message).encode())
        except Exception as e:
            print(f"Could not notify police: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle incoming client connections"""
        try:
            # Receive user name
            user_name = client_socket.recv(1024).decode()
            if not user_name:
                return
                
            print(f"User {user_name} connected from {address}")
            
            # Notify police about the connection
            self.notify_police(user_name, 'connect')
            
            # Add to clients list
            with self.lock:
                self.clients.append((user_name, client_socket))
                
            # Keep connection alive until client disconnects
            while True:
                try:
                    # Check if client is still connected
                    client_socket.send(b'ping')
                    threading.Event().wait(5)  # Wait 5 seconds
                except:
                    break
                    
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            # Clean up on disconnect
            with self.lock:
                for i, (name, sock) in enumerate(self.clients):
                    if sock == client_socket:
                        self.clients.pop(i)
                        print(f"User {name} disconnected")
                        self.notify_police(name, 'disconnect')
                        break
            client_socket.close()
    
    def start(self):
        """Start the server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"Server listening on {self.host}:{self.port}")
        
        try:
            while True:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = ConnectionServer()
    server.start()
