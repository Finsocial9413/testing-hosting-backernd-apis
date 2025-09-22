import asyncio
import websockets
import json
import requests
import time
from typing import Optional

class HindAIWebSocketClient:
    def __init__(self, base_url: str = "http://157.157.221.29:31535", ws_base_url: str = "ws://157.157.221.29:31535"):
        self.base_url = base_url
        self.ws_base_url = ws_base_url
        self.api_key = "your-api-key-here"  # Replace with your actual API key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def start_agent_task(self, request_data: dict) -> str:
        """Start an agent task and return the task ID."""
        try:
            response = requests.post(
                f"{self.base_url}/chats/run-agent",
                headers=self.headers,
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Task started successfully! Task ID: {result['task_id']}")
                return result['task_id']
            else:
                print(f"❌ Failed to start task: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting task: {e}")
            return None
    
    async def check_task_status(self, task_id: str) -> dict:
        """Check the status of a task."""
        try:
            response = requests.get(f"{self.base_url}/chats/task/{task_id}/status")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to check status: {response.status_code}")
                return {"status": "error"}
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            return {"status": "error"}
    
    async def stream_task_results(self, task_id: str, timeout: int = 300):
        """Stream task results via WebSocket."""
        ws_url = f"{self.ws_base_url}/chats/task/{task_id}/stream"
        
        print(f"🔌 Connecting to WebSocket: {ws_url}")
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print(f"✅ WebSocket connected for task: {task_id}")
                
                start_time = time.time()
                
                while True:
                    # Check for timeout
                    if time.time() - start_time > timeout:
                        print(f"⏰ Timeout reached ({timeout}s)")
                        break
                    
                    try:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        
                        # Print the raw message
                        print("\n" + "="*80)
                        print("📨 RAW WEBSOCKET MESSAGE:")
                        print("="*80)
                        print(message)
                        print("="*80)
                        
                        try:
                            data = json.loads(message)
                            
                            # Print the parsed JSON data
                            print("\n📊 PARSED JSON DATA:")
                            print("-"*40)
                            print(json.dumps(data, indent=2, ensure_ascii=False))
                            print("-"*40)
                            
                            message_type = data.get("type", "unknown")
                            
                            if message_type == "reasoning":
                                print(f"\n🧠 REASONING CONTENT:")
                                print("-"*40)
                                reasoning_content = data.get('content', '')
                                print(reasoning_content)
                                print("-"*40)
                                
                            elif message_type == "final":
                                status = data.get("status")
                                print(f"\n🏁 FINAL RESULT - Status: {status}")
                                
                                if status == "completed":
                                    print(f"\n💬 FULL AI RESPONSE:")
                                    print("-"*40)
                                    full_response = data.get('response', '')
                                    print(full_response)
                                    print("-"*40)
                                    
                                    print(f"\n📁 Chat ID: {data.get('chat_id')}")
                                    
                                    if data.get('Reasoning File'):
                                        print(f"📄 Reasoning File: {data.get('Reasoning File')}")
                                    if data.get('Main content file'):
                                        print(f"📄 Main Content File: {data.get('Main content file')}")
                                        
                                elif status == "error":
                                    print(f"\n❌ ERROR DETAILS:")
                                    print("-"*40)
                                    print(f"Error: {data.get('error')}")
                                    print("-"*40)
                                    
                                elif status == "cancelled":
                                    print(f"\n🚫 TASK CANCELLED:")
                                    print("-"*40)
                                    print(f"Message: {data.get('message')}")
                                    print("-"*40)
                                
                                # WebSocket gives us everything we need, so we can return here
                                return data
                                
                            elif "error" in data:
                                print(f"\n❌ WEBSOCKET ERROR:")
                                print("-"*40)
                                print(f"Error: {data['error']}")
                                print("-"*40)
                                return data
                                
                            else:
                                print(f"\n📨 UNKNOWN MESSAGE TYPE:")
                                print("-"*40)
                                print(f"Type: {message_type}")
                                print(f"Full data: {data}")
                                print("-"*40)
                                
                        except json.JSONDecodeError as e:
                            print(f"\n❌ JSON DECODE ERROR:")
                            print("-"*40)
                            print(f"Error: {e}")
                            print(f"Raw message: {message}")
                            print("-"*40)
                            continue
                    
                    except asyncio.TimeoutError:
                        # No message received in timeout period, continue waiting
                        print("⏳ Waiting for message...")
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("🔌 WebSocket connection closed")
                        break
                
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return None
    
    async def test_complete_flow(self, request_data: dict):
        """Test the complete flow: start task -> stream results via WebSocket only."""
        print("🚀 Starting complete flow test...")
        
        # Start the task
        task_id = await self.start_agent_task(request_data)
        if not task_id:
            return
        
        print(f"📋 Task ID: {task_id}")
        
        # Wait a moment for the task to initialize
        await asyncio.sleep(1)
        
        # Check initial status (optional - just to see the task started)
        status = await self.check_task_status(task_id)
        print(f"📊 Initial status: {status}")
        
        # Stream the results - this gives us everything we need!
        final_result = await self.stream_task_results(task_id)
        
        if final_result:
            print(f"\n✅ Task completed via WebSocket! Status: {final_result.get('status', 'unknown')}")
        else:
            print(f"\n❌ Task completed but no final result received")

# Test configurations
def get_test_request_data():
    """Get sample request data for testing."""
    return {
        "username": "1234",
        "chat_id": "new",
        "api": "no",
        "api_reasoning_platform": "no",
        "api_final_model_platform": "no",
        "model_name": "google/gemini-2.5-pro",
        "reasoning_model_name": "google/gemini-2.5-pro",
        "reasoning": False,
        "message": "Hello! Can you explain what artificial intelligence is?",
        "language": "English",
        "language_code": "eng_Latn",
        "google_search": "n",
        "deep_google_search": "n",
        "current_time": "2025-08-22T10:00:00Z"
    }

async def main():
    """Main test function."""
    # Initialize the client
    client = HindAIWebSocketClient(
        base_url="http://157.157.221.29:31535",
        ws_base_url="ws://157.157.221.29:31535"
    )
    
    # Get test data
    test_data = get_test_request_data()
    
    print("🧪 HindAI WebSocket Client Test")
    print("=" * 50)
    print(f"📝 Test message: {test_data['message']}")
    print(f"👤 Username: {test_data['username']}")
    print(f"🤖 Model: {test_data['model_name']}")
    print(f"🧠 Reasoning enabled: {test_data['reasoning']}")
    print("=" * 50)
    
    # Run the complete test
    await client.test_complete_flow(test_data)
    
    print("\n✅ Test completed!")

# Alternative: Test only WebSocket with existing task ID
async def test_existing_task():
    """Test WebSocket connection with an existing task ID."""
    client = HindAIWebSocketClient()
    
    # Replace with an actual task ID from your system
    existing_task_id = input("Enter existing task ID: ")
    
    print(f"🧪 Testing WebSocket with existing task: {existing_task_id}")
    result = await client.stream_task_results(existing_task_id)
    
    if result:
        print(f"✅ Got result: {result.get('status', 'unknown')}")

# Run the tests
if __name__ == "__main__":
    print("Select test mode:")
    print("1. Complete flow test (start new task + WebSocket)")
    print("2. WebSocket only (with existing task ID)")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(test_existing_task())
    else:
        print("Invalid choice!")