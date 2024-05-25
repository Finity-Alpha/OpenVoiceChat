//TODO: client side buffering of incoming audio

const socket = new WebSocket(window.location.href+ 'ws');
//I have changed this 

let audioCtx;
let audioQueue = [];
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
//socket.onmessage = async (event) => {
//    const float32Array = new Float32Array(await event.data.arrayBuffer());
//    const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 44100);
//    audioBuffer.getChannelData(0).set(float32Array);
//    playAudio(audioBuffer);
//};

// Handle received messages that contain audio data
socket.onmessage = async (event) => {
    const float32Array = new Float32Array(await event.data.arrayBuffer());
    const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 44100);
    audioBuffer.getChannelData(0).set(float32Array);
    audioQueue.push(audioBuffer);  // Add the audio buffer to the queue
    if (audioQueue.length === 1) {  // If this is the first audio buffer, start playing
        playAudioFromQueue();
    }
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
//        console.log(buffer);
        socket.send(buffer);  // Send audio data to the server
    };

    audioSource.connect(audioProcessor);
    audioProcessor.connect(audioCtx.destination);  // Connect processor to output (necessary for Chrome)
}
let currentSourceNode = null;
socket.onmessage = async (event) => {
    const receivedData = new TextDecoder().decode(await event.data.arrayBuffer());
    if (receivedData === 'stop') {
        // Handle the 'stop' command
        console.log('Received stop command');
        if (currentSourceNode) {
            currentSourceNode.stop();  // Stop the currently playing audio
            currentSourceNode = null;
        }
        isPlaying = false;  // Stop playing audio
        audioQueue = [];  // Clear the audio queue
    } else {
        const float32Array = new Float32Array(await event.data.arrayBuffer());
        const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 44100);
        audioBuffer.getChannelData(0).set(float32Array);
        audioQueue.push(audioBuffer);  // Add the audio buffer to the queue
        if (audioQueue.length === 1 && !isPlaying) {  // If this is the first audio buffer and no audio is currently playing, start playing
            playAudioFromQueue();
        }
    }
};
// Handle received messages that contain audio data
//socket.onmessage = async (event) => {
//
//    const float32Array = new Float32Array(await event.data.arrayBuffer());
//    const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 44100);
//    audioBuffer.getChannelData(0).set(float32Array);
//    audioQueue.push(audioBuffer);  // Add the audio buffer to the queue
//    if (audioQueue.length === 1) {  // If this is the first audio buffer, start playing
//        playAudioFromQueue();
//    }
//};
let isPlaying = false;  // Flag to indicate whether an audio is currently playing
function playAudioFromQueue() {
    if (audioQueue.length > 0 && !isPlaying) {
        isPlaying = true;  // Set the flag to true when an audio starts playing
        const audioBuffer = audioQueue.shift();  // Remove the first audio buffer from the queue
        currentSourceNode = audioCtx.createBufferSource();
        currentSourceNode.buffer = audioBuffer;
        currentSourceNode.connect(audioCtx.destination);
        currentSourceNode.start();
        currentSourceNode.onended = () => {
            isPlaying = false;  // Set the flag to false when the audio finishes playing
            playAudioFromQueue();  // When the audio buffer finishes playing, start the next one
        };
    }
}
//function playAudioFromQueue() {
//    if (audioQueue.length > 0 && !isPlaying) {
//        isPlaying = true;  // Set the flag to true when an audio starts playing
//        const audioBuffer = audioQueue.shift();  // Remove the first audio buffer from the queue
//        const sourceNode = audioCtx.createBufferSource();
//        sourceNode.buffer = audioBuffer;
//        sourceNode.connect(audioCtx.destination);
//        sourceNode.start();
//        sourceNode.onended = () => {
//            isPlaying = false;  // Set the flag to false when the audio finishes playing
//            playAudioFromQueue();  // When the audio buffer finishes playing, start the next one
//        };
//    }
//}
//
function playAudio(audioBuffer) {
    const sourceNode = audioCtx.createBufferSource();
    sourceNode.buffer = audioBuffer;
    sourceNode.connect(audioCtx.destination);
    sourceNode.start();
}

