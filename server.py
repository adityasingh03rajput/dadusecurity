from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
import uuid
from datetime import datetime
import requests

app = FastAPI(title="User Connection Tracking Server")

# In-memory storage (in production, use a database)
active_connections: Dict[str, dict] = {}
connection_history: List[dict] = []

class UserConnection(BaseModel):
    user_id: str
    user_name: str
    action: str  # "connect" or "disconnect"

# Webhook URL for police notifications (would be set in your environment)
POLICE_WEBHOOK_URL = "https://dadusecurity-2.onrender.com/notify"

def notify_police(user_data: dict):
    """Send notification to police monitor about user connection"""
    try:
        # In a real implementation, this would send to your webhook URL
        # For now, we'll just print and store the notification
        print(f"POLICE NOTIFICATION: {user_data['user_name']} {user_data['action']}ed")
        
        # This is where you would send the actual HTTP request:
        # response = requests.post(
        #     POLICE_WEBHOOK_URL,
        #     json=user_data,
        #     headers={"Content-Type": "application/json"}
        # )
    except Exception as e:
        print(f"Failed to notify police: {e}")

@app.post("/connect")
async def user_connect(user_data: UserConnection, background_tasks: BackgroundTasks):
    """Endpoint for users to connect"""
    try:
        connection_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        connection_record = {
            "connection_id": connection_id,
            "user_id": user_data.user_id,
            "user_name": user_data.user_name,
            "action": "connect",
            "timestamp": timestamp
        }
        
        # Store the connection
        active_connections[user_data.user_id] = connection_record
        connection_history.append(connection_record)
        
        # Notify police in the background
        background_tasks.add_task(notify_police, connection_record)
        
        return {"status": "success", "message": f"User {user_data.user_name} connected", "connection_id": connection_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/disconnect")
async def user_disconnect(user_data: UserConnection, background_tasks: BackgroundTasks):
    """Endpoint for users to disconnect"""
    try:
        if user_data.user_id not in active_connections:
            raise HTTPException(status_code=404, detail="User not found in active connections")
        
        timestamp = datetime.now().isoformat()
        
        connection_record = {
            "connection_id": active_connections[user_data.user_id]["connection_id"],
            "user_id": user_data.user_id,
            "user_name": user_data.user_name,
            "action": "disconnect",
            "timestamp": timestamp
        }
        
        # Remove from active connections and add to history
        del active_connections[user_data.user_id]
        connection_history.append(connection_record)
        
        # Notify police in the background
        background_tasks.add_task(notify_police, connection_record)
        
        return {"status": "success", "message": f"User {user_data.user_name} disconnected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/active-connections")
async def get_active_connections():
    """Get all currently active connections"""
    return {"active_connections": list(active_connections.values())}

@app.get("/connection-history")
async def get_connection_history(limit: int = 100):
    """Get connection history"""
    return {"connection_history": connection_history[-limit:]}

@app.post("/notify")
async def police_notification(user_data: UserConnection):
    """Endpoint for police to receive notifications (webhook)"""
    # In a real implementation, this would process notifications from your server
    # For this demo, we'll just acknowledge receipt
    print(f"Received police notification: {user_data.user_name} {user_data.action}")
    return {"status": "notification received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
