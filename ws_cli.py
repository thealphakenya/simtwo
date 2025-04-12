import asyncio
import websockets
import json

WS_URL = "ws://localhost:8765"  # Replace with your server's WebSocket URL if different

async def listen_and_send():
    async with websockets.connect(WS_URL) as websocket:
        print(f"Connected to {WS_URL}")

        async def send_messages():
            while True:
                raw = input("Enter JSON message to send (or 'exit'): ")
                if raw.lower() == "exit":
                    break
                try:
                    data = json.loads(raw)
                    await websocket.send(json.dumps(data))
                except json.JSONDecodeError:
                    print("Invalid JSON. Try again.")

        async def receive_messages():
            try:
                async for message in websocket:
                    try:
                        print("Received:", json.dumps(json.loads(message), indent=2))
                    except json.JSONDecodeError:
                        print("Received non-JSON message:", message)
            except websockets.ConnectionClosed:
                print("Connection closed by server.")

        await asyncio.gather(send_messages(), receive_messages())

if __name__ == "__main__":
    try:
        asyncio.run(listen_and_send())
    except KeyboardInterrupt:
        print("\nDisconnected.")