import cv2
from fdlite import FaceDetection, FaceDetectionModel
from fdlite.render import Colors, detections_to_render_data, render_to_image
from PIL import Image
import numpy as np
import asyncio
import websockets

# Server data
PORT = 7890
print("Server listening on Port " + str(PORT))

# A set of connected ws clients
connected = set()

# Function to send face images frames to WebSocket server
async def send_face_images():
    async with websockets.connect('ws://localhost:7890') as websocket:  # Change WebSocket server address/port as needed
        # Initialize the face detection model
        detect_faces = FaceDetection(model_type=FaceDetectionModel.BACK_CAMERA)

        # Open a connection to the webcam
        cap = cv2.VideoCapture(0)

        while True:
            # Capture a frame from the webcam
            ret, frame = cap.read()

            if not ret:
                break

            # Convert the frame to a PIL image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Detect faces in the image
            faces = detect_faces(image)

            # If faces are detected, render them on the image and extract face regions
            if faces:
                render_data = detections_to_render_data(faces, bounds_color=Colors.GREEN)
                image = render_to_image(render_data, image)

                # Convert PIL image back to OpenCV format for extracting faces
                frame_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # List to store cropped face images for each detected face
                face_images = []

                for face in faces:
                    bbox = face.bbox
                    # Extract bounding box coordinates
                    x1 = int(bbox.xmin * frame.shape[1]) - 40  # Adding padding to left
                    y1 = int(bbox.ymin * frame.shape[0]) - 40  # Adding padding to top
                    x2 = int(bbox.xmax * frame.shape[1]) + 60  # Adding padding to right
                    y2 = int(bbox.ymax * frame.shape[0]) + 60  # Adding padding to bottom

                    # Ensure the coordinates are within the image boundaries
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(frame.shape[1], x2)
                    y2 = min(frame.shape[0], y2)

                    # Extract the face region with padding
                    face_img = frame[y1:y2, x1:x2]
                    face_images.append(face_img)

                # Sort faces based on their x-coordinate in descending order
                face_images.sort(key=lambda img: img.shape[1], reverse=True)

                for face_img in face_images:
                    # Convert frame to bytes
                    _, buffer = cv2.imencode('.jpg', face_img)
                    image_bytes = buffer.tobytes()
                    # Send face image frame to WebSocket server
                    await websocket.send(image_bytes)

            # Convert the PIL image back to a format suitable for OpenCV
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Display the frame with detected faces
            cv2.imshow('Webcam Face Detection', frame)

            # Exit the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the webcam and close the window
        cap.release()
        cv2.destroyAllWindows()

async def echo(websocket, path):
    print("A client just connected")
    # Store a copy of the connected client
    connected.add(websocket)
    # Handle incoming messages
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            print("Received message from client: " + message)
    # Handle disconnecting clients 
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
    finally:
        connected.remove(websocket)        
        
start_server = websockets.serve(echo, "localhost", PORT)
asyncio.get_event_loop().create_task(send_face_images())  # Start sending data
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()