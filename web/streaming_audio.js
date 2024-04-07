const socket = new WebSocket('ws://localhost:8000/ws');
// Start recording when the WebSocket connection is open
socket.onopen = () => {
  console.log('WebSocket connection opened');
  mediaRecorder.start();
};

// Stop recording when the WebSocket connection is closed
socket.onclose = () => {
  console.log('WebSocket connection closed');
  mediaRecorder.stop();
};

// Handle WebSocket connection error
socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
// Request access to the user's microphone
navigator.mediaDevices.getUserMedia({ audio: true })
  .then((stream) => {
    const audioContext = new AudioContext();
    const audioSource = audioContext.createMediaStreamSource(stream);
    const audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);

    // Event handler for audio processing
    audioProcessor.onaudioprocess = (event) => {
      const audioData = event.inputBuffer.getChannelData(0);
      console.log(audioData); // Log the audio data to the console
      socket.send(audioData);
    };

    // Connect the audio source to the audio processor
    audioSource.connect(audioProcessor);
    audioProcessor.connect(audioContext.destination);
  })
  .catch((error) => {
    console.error('Error accessing microphone:', error);
  });
