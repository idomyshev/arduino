#!/usr/bin/env python3
"""
Тест WebSocket соединения
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Тест WebSocket соединения"""
    try:
        uri = "ws://localhost:8000/ws"
        print(f"Подключение к {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket подключен успешно!")
            
            # Отправляем команду получения статуса
            await websocket.send(json.dumps({"command": "get_status"}))
            print("📤 Отправлена команда get_status")
            
            # Получаем ответ
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Получен ответ: {data}")
            
            # Отправляем команду подключения к роботу
            await websocket.send(json.dumps({"command": "connect"}))
            print("📤 Отправлена команда connect")
            
            # Получаем ответ
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Получен ответ: {data}")
            
    except Exception as e:
        print(f"❌ Ошибка WebSocket: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
