import cv2
from fdlite import FaceDetection, FaceDetectionModel
from fdlite.render import Colors, detections_to_render_data, render_to_image
from PIL import Image
import numpy as np
import asyncio
import websockets
import base64
import json

# Server data
PORT = 7890
print("Server listening on Port " + str(PORT))

async def send_face_images(websocket):
    detect_faces = FaceDetection(model_type=FaceDetectionModel.BACK_CAMERA)
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        faces = detect_faces(image)
        if faces:
            render_data = detections_to_render_data(faces, bounds_color=Colors.GREEN)
            image = render_to_image(render_data, image)
            frame_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            face_images = []
            for face in faces:
                bbox = face.bbox
                x1 = int(bbox.xmin * frame.shape[1]) - 40  # Adding padding to left
                y1 = int(bbox.ymin * frame.shape[0]) - 40  # Adding padding to top
                x2 = int(bbox.xmax * frame.shape[1]) + 60  # Adding padding to right
                y2 = int(bbox.ymax * frame.shape[0]) + 60  # Adding padding to bottom
                
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x2)
                y2 = min(frame.shape[0], y2)

                face_img = frame[y1:y2, x1:x2]
                face_images.append(face_img)

            face_images.sort(key=lambda img: img.shape[1], reverse=True)
            face_images_bytes = []
            for face_img in face_images:
                _, buffer = cv2.imencode('.jpg', face_img)
                face_images_bytes.append(base64.b64encode(buffer).decode('utf-8'))
                
            await websocket.send(json.dumps(face_images_bytes))

async def echo(websocket, path):
    print("A client just connected")
    try:
        await send_face_images(websocket)
    except websockets.exceptions.ConnectionClosed as e:
        print("Client disconnected")
        
start_server = websockets.serve(echo, "localhost", PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
