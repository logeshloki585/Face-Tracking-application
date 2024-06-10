import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [faceImage, setFaceImage] = useState(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8765'); // Change WebSocket server address/port as needed

    socket.onopen = () => {
      console.log('Connected to WebSocket server');
    };

    socket.onmessage = (event) => {
      // Received image data
      const imageBytes = event.data;
      
      // Convert image bytes to Blob
      const blob = new Blob([imageBytes], { type: 'image/jpeg' });

      // Create Object URL from Blob
      const imageUrl = URL.createObjectURL(blob);
      
      // Set the received image URL
      setFaceImage(imageUrl);
    };

    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="App">
      <h1>Face Detection</h1>
      {faceImage && <img src={faceImage} alt="Face" />}
    </div>
  );
}

export default App;
