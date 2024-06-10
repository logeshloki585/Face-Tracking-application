import websockets
import asyncio
import datetime

# Server data
PORT = 7890
print("Server listening on Port " + str(PORT))

# A set of connected ws clients
connected = set()

# Function to send data to all connected clients
async def send_data():
    while True:
        # Create new data (current timestamp)
        data = str(datetime.datetime.now())
        # Send the data to all connected clients
        for conn in connected:
            await conn.send(data)
        # Wait for one second before sending the next data
        await asyncio.sleep(1)

# The main behavior function for this server
async def echo(websocket, path):
    print("A client just connected")
    # Store a copy of the connected client
    connected.add(websocket)
    # Handle incoming messages
    try:
        async for message in websocket:
            print("Received message from client: " + message)
    # Handle disconnecting clients 
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
    finally:
        connected.remove(websocket)

# Start the server
start_server = websockets.serve(echo, "localhost", PORT)
asyncio.get_event_loop().create_task(send_data())  # Start sending data
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
