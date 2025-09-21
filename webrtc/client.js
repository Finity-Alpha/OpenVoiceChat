// Daily.co Audio-Only Client Implementation
class DailyAudioClient {
    constructor() {
        this.callObject = null;
        this.isConnected = false;
        this.isMuted = false;
        this.participants = {};
        this.activeSpeaker = null;
        
        // Initialize after DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        console.log('Initializing Daily Audio Client...');
        this.setupEventListeners();
        this.updateUI();
    }

    setupEventListeners() {
        // Set up periodic network stats updates
        setInterval(() => {
            if (this.callObject && this.isConnected) {
                this.updateNetworkStats();
            }
        }, 5000);
    }


    async joinCall() {
        const roomUrl = document.getElementById('room-url').value.trim();
        const username = document.getElementById('username').value.trim() || 'Anonymous';

        if (!roomUrl) {
            alert('Please enter a room URL');
            return;
        }

        try {
            console.log('Joining call...', roomUrl);

            // Create Daily call object with audio-only configuration
            this.callObject = DailyIframe.createCallObject({
                // Audio-only configuration as per Daily.co docs
                videoSource: false,  // Disable camera streams
                subscribeToTracksAutomatically: false  // Enable manual track subscriptions
            });

            // Set up event listeners
            this.setupCallEventListeners();

            // Join the call
            await this.callObject.join({
                url: roomUrl,
                userName: username,
                startAudioOff: false,  // Start with audio on
                startVideoOff: true    // Ensure video is off
            });

            console.log('Successfully joined call');

        } catch (error) {
            console.error('Error joining call:', error);
            alert('Failed to join call: ' + error.message);
        }
    }

    setupCallEventListeners() {
        // Call state events
        this.callObject
            .on('joined-meeting', this.handleJoinedMeeting.bind(this))
            .on('left-meeting', this.handleLeftMeeting.bind(this))
            .on('participant-joined', this.handleParticipantJoined.bind(this))
            .on('participant-left', this.handleParticipantLeft.bind(this))
            .on('participant-updated', this.handleParticipantUpdated.bind(this))
            .on('active-speaker-change', this.handleActiveSpeakerChange.bind(this))
            .on('track-started', this.handleTrackStarted.bind(this))
            .on('track-stopped', this.handleTrackStopped.bind(this))
            .on('error', this.handleError.bind(this));
    }

    handleJoinedMeeting(event) {
        console.log('Joined meeting:', event);
        this.isConnected = true;
        this.updateUI();
        this.updateParticipants();
        
        // Subscribe to all participants' audio tracks
        this.subscribeToAllAudio();
    }

    handleLeftMeeting(event) {
        console.log('Left meeting:', event);
        this.isConnected = false;
        
        // Clean up all audio elements
        this.cleanupAllAudioElements();
        
        this.participants = {};
        this.activeSpeaker = null;
        this.updateUI();
    }

    handleParticipantJoined(event) {
        console.log('Participant joined:', event.participant);
        this.updateParticipants();
        
        // Subscribe to new participant's audio
        this.subscribeToParticipantAudio(event.participant.session_id);
    }

    handleParticipantLeft(event) {
        console.log('Participant left:', event.participant);
        
        // Clean up audio element for the participant who left
        this.removeAudioElement(event.participant.session_id);
        
        delete this.participants[event.participant.session_id];
        this.updateParticipants();
    }

    handleParticipantUpdated(event) {
        console.log('Participant updated:', event.participant);
        this.updateParticipants();
    }

    handleActiveSpeakerChange(event) {
        console.log('Active speaker changed:', event);
        this.activeSpeaker = event.activeSpeaker;
        this.updateActiveSpeaker();
    }

    handleError(event) {
        console.error('Daily call error:', event);
        alert('Call error: ' + (event.errorMsg || 'Unknown error'));
    }

    handleTrackStarted(event) {
        console.log('Track started:', event);
        
        // Only handle audio tracks from remote participants
        if (event.track && event.track.kind === 'audio' && !event.participant.local) {
            this.createAudioElement(event.participant.session_id, event.track);
        }
    }

    handleTrackStopped(event) {
        console.log('Track stopped:', event);
        
        // Clean up audio element when track stops
        if (event.track && event.track.kind === 'audio' && !event.participant.local) {
            this.removeAudioElement(event.participant.session_id);
        }
    }

    createAudioElement(sessionId, track) {
        console.log(`Creating audio element for participant: ${sessionId}`);
        
        // Remove existing audio element if it exists
        this.removeAudioElement(sessionId);
        
        // Create new audio element
        const audioElement = document.createElement('audio');
        audioElement.id = `audio-${sessionId}`;
        audioElement.autoplay = true;
        audioElement.playsInline = true;
        audioElement.style.display = 'none'; // Hidden audio element
        
        // Set the track as the source
        if (track && track instanceof MediaStreamTrack) {
            const mediaStream = new MediaStream([track]);
            audioElement.srcObject = mediaStream;
        }
        
        // Add to DOM (hidden)
        document.body.appendChild(audioElement);
        
        // Handle audio play errors
        audioElement.addEventListener('error', (e) => {
            console.error('Audio playback error:', e);
        });
        
        // Attempt to play
        audioElement.play().catch(error => {
            console.error('Failed to play audio:', error);
            // Note: This might happen due to browser autoplay policies
        });
        
        console.log(`Audio element created and playing for participant: ${sessionId}`);
        
        // Update debug counter
        this.updateAudioElementCount();
    }

    removeAudioElement(sessionId) {
        const audioElement = document.getElementById(`audio-${sessionId}`);
        if (audioElement) {
            audioElement.pause();
            audioElement.srcObject = null;
            audioElement.remove();
            console.log(`Audio element removed for participant: ${sessionId}`);
            
            // Update debug counter
            this.updateAudioElementCount();
        }
    }

    cleanupAllAudioElements() {
        // Find and remove all audio elements created by this client
        const audioElements = document.querySelectorAll('audio[id^="audio-"]');
        audioElements.forEach(audioElement => {
            audioElement.pause();
            audioElement.srcObject = null;
            audioElement.remove();
        });
        console.log('All audio elements cleaned up');
        
        // Update debug counter
        this.updateAudioElementCount();
    }

    subscribeToAllAudio() {
        if (!this.callObject) return;

        const participants = this.callObject.participants();
        Object.values(participants).forEach(participant => {
            if (participant.session_id !== this.callObject.participants().local.session_id) {
                this.subscribeToParticipantAudio(participant.session_id);
            }
        });
    }

    subscribeToParticipantAudio(sessionId) {
        if (!this.callObject) return;

        try {
            this.callObject.updateParticipant(sessionId, {
                setSubscribedTracks: {
                    audio: true,
                    video: false  // Ensure no video subscription
                }
            });
            console.log(`Subscribed to audio for participant: ${sessionId}`);
        } catch (error) {
            console.error('Error subscribing to participant audio:', error);
        }
    }

    async toggleMute() {
        if (!this.callObject) return;

        try {
            this.isMuted = !this.isMuted;
            await this.callObject.setLocalAudio(!this.isMuted);
            
            const muteBtn = document.getElementById('mute-btn');
            muteBtn.textContent = this.isMuted ? '🔇 Unmute' : '🎤 Mute';
            muteBtn.className = this.isMuted ? 'btn-danger' : 'btn-warning';
            
            console.log('Mute toggled:', this.isMuted);
        } catch (error) {
            console.error('Error toggling mute:', error);
        }
    }

    async leaveCall() {
        if (!this.callObject) return;

        try {
            await this.callObject.leave();
            this.callObject.destroy();
            this.callObject = null;
            console.log('Left call successfully');
        } catch (error) {
            console.error('Error leaving call:', error);
        }
    }

    updateUI() {
        const setupSection = document.getElementById('setup');
        const callInterface = document.getElementById('call-interface');
        const statusElement = document.getElementById('call-status');

        if (this.isConnected) {
            setupSection.classList.add('hidden');
            callInterface.classList.remove('hidden');
            statusElement.textContent = 'Connected';
            statusElement.className = 'status connected';
        } else {
            setupSection.classList.remove('hidden');
            callInterface.classList.add('hidden');
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'status disconnected';
        }
    }

    updateParticipants() {
        if (!this.callObject) return;

        const participants = this.callObject.participants();
        const participantsList = document.getElementById('participants-list');
        
        participantsList.innerHTML = '';

        Object.values(participants).forEach(participant => {
            const participantDiv = document.createElement('div');
            participantDiv.className = 'participant';
            participantDiv.id = `participant-${participant.session_id}`;

            // Add speaking class if this is the active speaker
            if (this.activeSpeaker && this.activeSpeaker.peerId === participant.session_id) {
                participantDiv.classList.add('speaking');
            }

            // Add muted class if participant is muted
            if (!participant.audio) {
                participantDiv.classList.add('muted');
            }

            const name = participant.user_name || 'Anonymous';
            const isLocal = participant.local;
            const audioStatus = participant.audio ? '🎤' : '🔇';
            
            participantDiv.innerHTML = `
                <div class="participant-name">
                    ${name} ${isLocal ? '(You)' : ''}
                </div>
                <div class="participant-status">
                    ${audioStatus}
                </div>
                <div class="audio-level ${participant.audio ? 'active' : ''}"></div>
            `;

            participantsList.appendChild(participantDiv);
        });
    }

    updateActiveSpeaker() {
        // Remove speaking class from all participants
        document.querySelectorAll('.participant').forEach(p => {
            p.classList.remove('speaking');
        });

        // Add speaking class to active speaker
        if (this.activeSpeaker && this.activeSpeaker.peerId) {
            const speakerElement = document.getElementById(`participant-${this.activeSpeaker.peerId}`);
            if (speakerElement) {
                speakerElement.classList.add('speaking');
            }

            // Update debug info
            const participants = this.callObject.participants();
            const speaker = participants[this.activeSpeaker.peerId];
            const speakerName = speaker ? (speaker.user_name || 'Anonymous') : 'Unknown';
            document.getElementById('active-speaker').textContent = speakerName;
        } else {
            document.getElementById('active-speaker').textContent = '-';
        }
    }

    async updateNetworkStats() {
        if (!this.callObject) return;

        try {
            const stats = await this.callObject.getNetworkStats();
            const statsText = `Bitrate: ${Math.round(stats.stats.latest.recvBitsPerSecond / 1000)}kbps`;
            document.getElementById('network-stats').textContent = statsText;
        } catch (error) {
            console.error('Error getting network stats:', error);
        }
    }

    updateAudioElementCount() {
        const audioElements = document.querySelectorAll('audio[id^="audio-"]');
        const countElement = document.getElementById('audio-count');
        if (countElement) {
            countElement.textContent = audioElements.length;
        }
    }
}

// Global functions called by HTML buttons
let dailyClient;

function joinCall() {
    if (!dailyClient) {
        dailyClient = new DailyAudioClient();
    }
    dailyClient.joinCall();
}


function toggleMute() {
    if (dailyClient) {
        dailyClient.toggleMute();
    }
}

function leaveCall() {
    if (dailyClient) {
        dailyClient.leaveCall();
    }
}

// Initialize the client when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Daily.co Audio Client loaded');
    
    // Check if Daily is available
    if (typeof DailyIframe === 'undefined') {
        console.error('Daily.co SDK not loaded');
        alert('Daily.co SDK failed to load. Please check your internet connection.');
    } else {
        console.log('Daily.co SDK loaded successfully');
    }
});
