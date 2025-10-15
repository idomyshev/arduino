#!/usr/bin/env python3
"""
Простой тест WebSocket с командой connect
"""

import asyncio
import websockets
import json

async def test_connect():
    """Тест команды connect через WebSocket"""
    try:
        uri = "ws://localhost:8000/ws"
        print(f"Подключение к {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket подключен!")
            
            # Отправляем команду connect
            connect_msg = {"command": "connect"}
            await websocket.send(json.dumps(connect_msg))
            print(f"📤 Отправлена команда: {connect_msg}")
            
            # Ждем ответ
            print("⏳ Ожидание ответа...")
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Получен ответ: {data}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_connect())
