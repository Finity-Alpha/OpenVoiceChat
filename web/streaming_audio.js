const socket = new WebSocket('ws://localhost:8000/ws');
// Start recording when the WebSocket connection is open
socket.onopen = () => {
  console.log('WebSocket connection opened');
//  mediaRecorder.start();
};

// Stop recording when the WebSocket connection is closed
socket.onclose = () => {
  console.log('WebSocket connection closed');
//  mediaRecorder.stop();
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
      socket.send(audioData);
    };

    // Connect the audio source to the audio processor
    audioSource.connect(audioProcessor);
    audioProcessor.connect(audioContext.destination);
  })
  .catch((error) => {
    console.error('Error accessing microphone:', error);
  });


  const ws = new WebSocket('ws://localhost:8000/ws/audio');
    let audioCtx;
    let sourceNode;

    ws.addEventListener('open', (event) => {
      console.log('WebSocket connection opened:', event);
    });

    ws.addEventListener('message', async (event) => {
      const float32Array = new Float32Array(await event.data.arrayBuffer());
      console.log('Received audio data:', float32Array);
      audioCtx = new AudioContext();
      const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 44100);
      audioBuffer.getChannelData(0).set(float32Array);
      if (!sourceNode){
          sourceNode = audioCtx.createBufferSource();
          sourceNode.connect(audioCtx.destination);

      }
      sourceNode.buffer = audioBuffer;
      sourceNode.start();

    });
