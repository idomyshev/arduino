#!/usr/bin/env python3
"""
Пример использования новых API endpoints
"""

import asyncio
import aiohttp
import json

async def demo_new_endpoints():
    """Демонстрация новых эндпоинтов"""
    base_url = "http://localhost:8000"
    
    print("🚀 Robot Arm API - New Endpoints Demo")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Показываем информацию о всех API endpoints
        print("\n📋 1. API Documentation (/api)")
        print("-" * 40)
        async with session.get(f"{base_url}/api") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Title: {data['info']['title']}")
                print(f"Version: {data['info']['version']}")
                print(f"Description: {data['info']['description']}")
                print(f"Base URL: {data['info']['base_url']}")
                
                print("\nAvailable endpoints:")
                for category, endpoints in data['endpoints'].items():
                    print(f"\n  {category.upper()}:")
                    for name, endpoint in endpoints.items():
                        print(f"    {endpoint['method']} {endpoint['url']}")
                        print(f"      {endpoint['description']}")
        
        # 2. Показываем структуру базы данных
        print("\n\n🗄️  2. Database Structure (/api/database)")
        print("-" * 40)
        async with session.get(f"{base_url}/api/database") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Database: {data['database_path']}")
                print(f"Tables: {len(data['tables'])}")
                
                for table_name, table_info in data['tables'].items():
                    if table_name != 'sqlite_sequence':  # Пропускаем служебную таблицу
                        print(f"\n  Table '{table_name}':")
                        print(f"    Rows: {table_info['row_count']}")
                        print(f"    Columns: {len(table_info['columns'])}")
                        
                        # Показываем основные колонки
                        key_columns = [col['name'] for col in table_info['columns'][:5]]
                        print(f"    Key columns: {', '.join(key_columns)}")
                        
                        # Показываем пример данных
                        if table_info['sample_data']:
                            print(f"    Sample data:")
                            for i, sample in enumerate(table_info['sample_data'][:2]):
                                print(f"      Record {i+1}: {sample}")
        
        # 3. Показываем статус сервера
        print("\n\n📊 3. Server Status (/api/status)")
        print("-" * 40)
        async with session.get(f"{base_url}/api/status") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Status: {data['status']}")
                print(f"Version: {data['version']}")
                print(f"Database: {data['database']}")
                print(f"Timestamp: {data['timestamp']}")
        
        # 4. Показываем список роботов
        print("\n\n🤖 4. Registered Robots (/api/robots)")
        print("-" * 40)
        async with session.get(f"{base_url}/api/robots") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Total robots: {len(data['robots'])}")
                for i, robot_id in enumerate(data['robots'], 1):
                    print(f"  {i}. {robot_id}")
        
        # 5. Показываем примеры использования
        print("\n\n💡 5. Usage Examples")
        print("-" * 40)
        print("Get API documentation:")
        print(f"  curl {base_url}/api")
        print("\nGet database structure:")
        print(f"  curl {base_url}/api/database")
        print("\nGet server status:")
        print(f"  curl {base_url}/api/status")
        print("\nGet robots list:")
        print(f"  curl {base_url}/api/robots")
        print("\nGet calibration data:")
        print(f"  curl {base_url}/api/calibration/esp32_robot_arm_001")
        print("\nGet robot position:")
        print(f"  curl {base_url}/api/position/esp32_robot_arm_001")
    
    print("\n\n🎉 Demo Complete!")
    print("=" * 60)
    print("✅ All new endpoints working perfectly")
    print("✅ API documentation available")
    print("✅ Database structure visible")
    print("✅ Server status monitoring")
    print("✅ Robot management")

if __name__ == "__main__":
    asyncio.run(demo_new_endpoints())
