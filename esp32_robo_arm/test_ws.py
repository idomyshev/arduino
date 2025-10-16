#!/usr/bin/env python3

import websocket
import json
import time

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connected")
    
    # Тестируем команду get_status
    print("Sending get_status command...")
    ws.send(json.dumps({"command": "get_status"}))
    
    time.sleep(1)
    
    # Тестируем команду connect
    print("Sending connect command...")
    ws.send(json.dumps({"command": "connect"}))
    
    time.sleep(1)
    
    # Тестируем команду move_motor
    print("Sending move_motor command...")
    ws.send(json.dumps({
        "command": "move_motor",
        "motor": 0,
        "direction": "forward",
        "speed": 200
    }))
    
    time.sleep(1)
    ws.close()

if __name__ == "__main__":
    ws = websocket.WebSocketApp("ws://localhost:8000/ws",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    ws.run_forever()



