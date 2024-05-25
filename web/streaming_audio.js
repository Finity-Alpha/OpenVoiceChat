const socket = new WebSocket('ws://192.168.18.16:8000/ws');
//I have changed this 

let audioCtx;

// Start recording when the WebSocket connection is open
socket.onopen = () => {
    console.log('WebSocket connection opened');
    // Initialize the AudioContext
    audioCtx = new AudioContext();
    // Request access to the user's microphone
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => setupAudioProcessors(stream))
        .catch(error => console.error('Error accessing microphone:', error));
};

// Handle received messages that contain audio data
socket.onmessage = async (event) => {
    const float32Array = new Float32Array(await event.data.arrayBuffer());
    const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 44100);
    audioBuffer.getChannelData(0).set(float32Array);
    playAudio(audioBuffer);
};

// Handle WebSocket connection error
socket.onerror = (error) => {
    console.error('WebSocket error:', error);
};

// Stop recording when the WebSocket connection is closed
socket.onclose = () => {
    console.log('WebSocket connection closed');
};

function setupAudioProcessors(stream) {
    const audioSource = audioCtx.createMediaStreamSource(stream);
    const audioProcessor = audioCtx.createScriptProcessor(16384, 1, 1);
    console.log(audioCtx.sampleRate);

    audioProcessor.onaudioprocess = (event) => {
        const audioData = event.inputBuffer.getChannelData(0);
        const buffer = new Float32Array(audioData);  // Convert audio to Float32Array
        // log the bytes
        console.log(buffer);
        socket.send(buffer);  // Send audio data to the server
    };

    audioSource.connect(audioProcessor);
    audioProcessor.connect(audioCtx.destination);  // Connect processor to output (necessary for Chrome)
}

function playAudio(audioBuffer) {
    const sourceNode = audioCtx.createBufferSource();
    sourceNode.buffer = audioBuffer;
    sourceNode.connect(audioCtx.destination);
    sourceNode.start();
}

