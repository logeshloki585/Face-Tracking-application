import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [faceImages, setFaceImages] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:7890');

    ws.onopen = () => {
      console.log('Connected to server');
    };

    ws.onmessage = (event) => {
      setFaceImages(JSON.parse(event.data));
    };

    ws.onclose = () => {
      console.log('Connection closed');
    };

    return () => {
      ws.close();
    };
  }, []);

  const calculateGridSize = () => {
    const numParticipants = faceImages.length;
    if (numParticipants === 1) {
      return '70%'; // Take whole container space
    } else if (numParticipants === 2) {
      return '50% 50%'; // Split equally for each participant
    } else if (numParticipants === 3) {
      return '33.33% 33.33% 33.33%'; // Share equally
    } else if (numParticipants >= 4) {
      return '50% 50%'; // Place 2 participants on 1st row, and remaining 2 on second row
    }
  };

  return (
    <div className="main">
      <div className='gallery'>
        <h1 className='gallery_heading'>Received Face Images</h1>
        <hr />
        <div className='gallery_container' style={{ gridTemplateColumns: calculateGridSize() }}>
          {faceImages.map((imageData, index) => (
            <div className='gallery_image_container'>
              <img key={index} src={`data:image/jpeg;base64,${imageData}`} alt={`Face ${index}`} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
