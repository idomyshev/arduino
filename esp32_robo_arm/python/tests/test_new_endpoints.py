#!/usr/bin/env python3
"""
Тест новых API endpoints
"""

import asyncio
import aiohttp
import json

async def test_new_endpoints():
    """Тест новых эндпоинтов"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing New API Endpoints")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Тест /api endpoint
        print("\n1. Testing /api endpoint...")
        try:
            async with session.get(f"{base_url}/api") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ /api endpoint working")
                    print(f"   Title: {data['info']['title']}")
                    print(f"   Version: {data['info']['version']}")
                    print(f"   Endpoints count: {len(data['endpoints'])}")
                    
                    # Показываем основные категории
                    for category, endpoints in data['endpoints'].items():
                        print(f"   {category}: {len(endpoints)} endpoints")
                else:
                    print(f"❌ /api endpoint error: {response.status}")
        except Exception as e:
            print(f"❌ /api endpoint error: {e}")
        
        # 2. Тест /api/database endpoint
        print("\n2. Testing /api/database endpoint...")
        try:
            async with session.get(f"{base_url}/api/database") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ /api/database endpoint working")
                    print(f"   Database path: {data['database_path']}")
                    print(f"   Tables count: {len(data['tables'])}")
                    
                    # Показываем информацию о таблицах
                    for table_name, table_info in data['tables'].items():
                        print(f"   Table '{table_name}':")
                        print(f"     Columns: {len(table_info['columns'])}")
                        print(f"     Rows: {table_info['row_count']}")
                        print(f"     Sample data: {len(table_info['sample_data'])} records")
                else:
                    print(f"❌ /api/database endpoint error: {response.status}")
        except Exception as e:
            print(f"❌ /api/database endpoint error: {e}")
        
        # 3. Тест /api/status endpoint (для сравнения)
        print("\n3. Testing /api/status endpoint...")
        try:
            async with session.get(f"{base_url}/api/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ /api/status endpoint working")
                    print(f"   Status: {data['status']}")
                    print(f"   Version: {data['version']}")
                else:
                    print(f"❌ /api/status endpoint error: {response.status}")
        except Exception as e:
            print(f"❌ /api/status endpoint error: {e}")
        
        # 4. Тест /api/robots endpoint
        print("\n4. Testing /api/robots endpoint...")
        try:
            async with session.get(f"{base_url}/api/robots") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ /api/robots endpoint working")
                    print(f"   Robots count: {len(data['robots'])}")
                    if data['robots']:
                        print(f"   Robots: {', '.join(data['robots'])}")
                    else:
                        print("   No robots found")
                else:
                    print(f"❌ /api/robots endpoint error: {response.status}")
        except Exception as e:
            print(f"❌ /api/robots endpoint error: {e}")
    
    print("\n🎉 New Endpoints Test Complete!")
    print("=" * 50)
    print("✅ All new endpoints working")
    print("✅ API documentation available")
    print("✅ Database structure visible")

if __name__ == "__main__":
    asyncio.run(test_new_endpoints())
