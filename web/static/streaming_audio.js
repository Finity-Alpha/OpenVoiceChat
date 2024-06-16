// the canvas size
const WIDTH = 1000;
const HEIGHT = 400;
const logElement = document.getElementById('logs');
const ctx = canvas.getContext("2d");

let context;
let analyser;
let freqs;
let audioQueue = [];
let isPlaying = false;
let currentSourceNode = null;

document.getElementById('startButton').addEventListener('click', function() {
  logElement.innerText = 'starting... could take a minute';
  start();
  // Hide the start button
  this.style.display = 'none';  
});

function start() {
  const socket = new WebSocket(window.location.href + 'ws');
  let audioCtx;

  socket.onopen = () => {
    logElement.innerText = 'Connection opened';
    audioCtx = new AudioContext();
    context = audioCtx;
    analyser = context.createAnalyser();
    freqs = new Uint8Array(analyser.frequencyBinCount);

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => setupAudioProcessors(stream))
      .catch(error => console.error('Error accessing microphone:', error));
    logElement.innerText = 'Mic detected. Listening...';
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  socket.onclose = () => {
    console.log('WebSocket connection closed');
  };

  function setupAudioProcessors(stream) {
    const audioSource = audioCtx.createMediaStreamSource(stream);
    const audioProcessor = audioCtx.createScriptProcessor(16384, 1, 1);

    audioProcessor.onaudioprocess = (event) => {
      const audioData = event.inputBuffer.getChannelData(0);
      const buffer = new Float32Array(audioData);
      socket.send(buffer);
    };

    audioSource.connect(audioProcessor);
    audioProcessor.connect(audioCtx.destination);

    visualize();
  }

  socket.onmessage = async (event) => {
    const receivedData = new TextDecoder().decode(await event.data.arrayBuffer());
    if (receivedData === 'stop') {
      logElement.innerText = 'Interruption';
      if (currentSourceNode) {
        currentSourceNode.stop();
        currentSourceNode = null;
      }
      isPlaying = false;
      audioQueue = [];
    } else if (receivedData === 'none') {
//        pass
    } else {
      const float32Array = new Float32Array(await event.data.arrayBuffer());
      const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 44100);
      audioBuffer.getChannelData(0).set(float32Array);
      audioQueue.push(audioBuffer);
      if (audioQueue.length === 1 && !isPlaying) {
        playAudioFromQueue();
      }
    }
  };

  function playAudioFromQueue() {
    if (audioQueue.length > 0 && !isPlaying) {
      isPlaying = true;
      logElement.innerText = 'Speaking...';
      const audioBuffer = audioQueue.shift();
      currentSourceNode = audioCtx.createBufferSource();
      currentSourceNode.buffer = audioBuffer;
      currentSourceNode.connect(analyser);
      currentSourceNode.connect(audioCtx.destination);
      currentSourceNode.start();
      currentSourceNode.onended = () => {
        isPlaying = false;
        logElement.innerText = 'Listening...';
        playAudioFromQueue();
      };
    }
  }
}


// VISUALIZATION


// options to tweak the look
const opts = {
  smoothing: 0.6,
  fft: 8,
  minDecibels: -70,
  scale: 0.2,
  glow: 10,
  color1: [203, 36, 128],
  color2: [41, 200, 192],
  color3: [24, 137, 218],
  fillOpacity: 0.6,
  lineWidth: 1,
  blend: "screen",
  shift: 50,
  width: 60,
  amp: 1
};

// Interactive dat.GUI controls
//const gui = new dat.GUI();
//
// hide them by default
//gui.close();
//
// connect gui to opts
//gui.addColor(opts, "color1");
//gui.addColor(opts, "color2");
//gui.addColor(opts, "color3");
//gui.add(opts, "fillOpacity", 0, 1);
//gui.add(opts, "lineWidth", 0, 10).step(1);
//gui.add(opts, "glow", 0, 100);
//gui.add(opts, "blend", [
//  "normal",
//  "multiply",
//  "screen",
//  "overlay",
//  "lighten",
//  "difference"
//]);
//gui.add(opts, "smoothing", 0, 1);
//gui.add(opts, "minDecibels", -100, 0);
//gui.add(opts, "amp", 0, 5);
//gui.add(opts, "width", 0, 60);
//gui.add(opts, "shift", 0, 200);



function visualize() {
  // set analyser props in the loop react on dat.gui changes
  analyser.smoothingTimeConstant = opts.smoothing;
  analyser.fftSize = Math.pow(2, opts.fft);
  analyser.minDecibels = opts.minDecibels;
  analyser.maxDecibels = 0;
  analyser.getByteFrequencyData(freqs);

  // set size to clear the canvas on each frame
  canvas.width = WIDTH;
  canvas.height = HEIGHT;

  // draw three curves (R/G/B)
  path(0);
  path(1);
  path(2);

  // schedule next paint
  requestAnimationFrame(visualize);
}

function range(i) {
  return Array.from(Array(i).keys());
}

// shuffle frequencies so that neighbors are not too similar
const shuffle = [1, 3, 0, 4, 2];

function freq(channel, i) {
  const band = 2 * channel + shuffle[i] * 6;
  return freqs[band];
}

function scale(i) {
  const x = Math.abs(2 - i); // 2,1,0,1,2
  const s = 3 - x;           // 1,2,3,2,1
  return s / 3 * opts.amp; 
}

function path(channel) {
  const color = opts[`color${channel + 1}`].map(Math.floor);
  ctx.fillStyle = `rgba(${color}, ${opts.fillOpacity})`;
  ctx.strokeStyle = ctx.shadowColor = `rgb(${color})`;
  ctx.lineWidth = opts.lineWidth;
  ctx.shadowBlur = opts.glow;
  ctx.globalCompositeOperation = opts.blend;
  
  const m = HEIGHT / 2;
  const offset = (WIDTH - 15 * opts.width) / 2;
  const x = range(15).map(
    i => offset + channel * opts.shift + i * opts.width
  );

  const y = range(5).map(i =>
    Math.max(0, m - scale(i) * freq(channel, i))
  );

  const h = 2 * m;

  ctx.beginPath();
  ctx.moveTo(0, m);
  ctx.lineTo(x[0], m + 1);
  ctx.bezierCurveTo(x[1], m + 1, x[2], y[0], x[3], y[0]);
  ctx.bezierCurveTo(x[4], y[0], x[4], y[1], x[5], y[1]);
  ctx.bezierCurveTo(x[6], y[1], x[6], y[2], x[7], y[2]);
  ctx.bezierCurveTo(x[8], y[2], x[8], y[3], x[9], y[3]);
  ctx.bezierCurveTo(x[10], y[3], x[10], y[4], x[11], y[4]);
  ctx.bezierCurveTo(x[12], y[4], x[12], m, x[13], m);
  ctx.lineTo(1000, m + 1);
  ctx.lineTo(x[13], m - 1);
  ctx.bezierCurveTo(x[12], m, x[12], h - y[4], x[11], h - y[4]);
  ctx.bezierCurveTo(x[10], h - y[4], x[10], h - y[3], x[9], h - y[3]);
  ctx.bezierCurveTo(x[8], h - y[3], x[8], h - y[2], x[7], h - y[2]);
  ctx.bezierCurveTo(x[6], h - y[2], x[6], h - y[1], x[5], h - y[1]);
  ctx.bezierCurveTo(x[4], h - y[1], x[4], h - y[0], x[3], h - y[0]);
  ctx.bezierCurveTo(x[2], h - y[0], x[1], m, x[0], m);
  ctx.lineTo(0, m);
  ctx.fill();
  ctx.stroke();
}
