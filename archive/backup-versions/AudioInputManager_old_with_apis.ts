/**
 * Audio Input Manager
 *
 * Handles multiple audio input sources including microphone, YouTube,
 * external audio files, and DAW integration (Ableton Live)
 */

import * as Tone from 'tone';

export type AudioInputSource =
    | 'microphone'
    | 'youtube'
    | 'spotify'
    | 'itunes'
    | 'file'
    | 'ableton'
    | 'midi'
    | 'line-in'
    | 'internal';

export interface AudioInputConfig {
    source: AudioInputSource;
    gain: number;
    enabled: boolean;
    analyzerEnabled: boolean;
    effects?: {
        highpass?: number;
        lowpass?: number;
        reverb?: number;
        delay?: number;
    };
}

export interface AudioAnalysis {
    frequency: Float32Array;
    waveform: Float32Array;
    rms: number;
    peak: number;
    pitch: number;
    tempo?: number;
}

export class AudioInputManager {
    private audioContext: AudioContext;
    private masterGain: GainNode;
    private analyzer: AnalyserNode;
    private currentSource: AudioInputSource = 'internal';
    private inputConfigs: Map<AudioInputSource, AudioInputConfig> = new Map();

    // Input sources
    private microphoneStream: MediaStream | null = null;
    private microphoneSource: MediaStreamAudioSourceNode | null = null;
    private youtubeAudio: HTMLAudioElement | null = null;
    private youtubeSource: MediaElementAudioSourceNode | null = null;
    private youtubePlayer: any = null; // YouTube iframe player
    private spotifyPlayer: any = null; // Spotify Web Playback SDK
    private itunesAudio: HTMLAudioElement | null = null;
    private itunesSource: MediaElementAudioSourceNode | null = null;
    private fileAudio: HTMLAudioElement | null = null;
    private fileSource: MediaElementAudioSourceNode | null = null;

    // Analysis
    private frequencyData: Float32Array;
    private waveformData: Float32Array;
    private isAnalyzing: boolean = false;
    private analyzeCallbacks: ((analysis: AudioAnalysis) => void)[] = [];

    // Ableton Live WebSocket connection
    private abletonWebSocket: WebSocket | null = null;
    private abletonConnected: boolean = false;

    constructor() {
        this.audioContext = Tone.getContext().rawContext as AudioContext;
        this.masterGain = this.audioContext.createGain();
        this.analyzer = this.audioContext.createAnalyser();

        // Configure analyzer
        this.analyzer.fftSize = 2048;
        this.analyzer.smoothingTimeConstant = 0.8;
        this.frequencyData = new Float32Array(this.analyzer.frequencyBinCount);
        this.waveformData = new Float32Array(this.analyzer.fftSize);

        // Connect audio graph
        this.masterGain.connect(this.analyzer);
        this.masterGain.connect(this.audioContext.destination);

        this.initializeInputConfigs();

        // Ensure AudioContext is started
        this.ensureAudioContextStarted();
    }

    private async ensureAudioContextStarted() {
        console.log('🎛️ AudioContext state:', this.audioContext.state);

        if (this.audioContext.state === 'suspended') {
            console.log('⏸️ AudioContext suspended, waiting for user gesture...');

            // Add click listener to document to resume audio context
            const resumeAudioContext = async () => {
                try {
                    await Tone.start();
                    console.log('✅ Tone.js and AudioContext started!');
                    console.log('🎛️ New AudioContext state:', this.audioContext.state);
                    document.removeEventListener('click', resumeAudioContext);
                } catch (error) {
                    console.error('❌ Failed to start audio context:', error);
                }
            };

            document.addEventListener('click', resumeAudioContext);
        } else {
            console.log('✅ AudioContext already running!');
        }
    }

    private initializeInputConfigs() {
        const defaultConfig: AudioInputConfig = {
            source: 'internal',
            gain: 0.8,
            enabled: false,
            analyzerEnabled: true,
            effects: {
                highpass: 20,
                lowpass: 20000,
                reverb: 0,
                delay: 0
            }
        };

        this.inputConfigs.set('microphone', { ...defaultConfig, source: 'microphone' });
        this.inputConfigs.set('youtube', { ...defaultConfig, source: 'youtube' });
        this.inputConfigs.set('spotify', { ...defaultConfig, source: 'spotify' });
        this.inputConfigs.set('itunes', { ...defaultConfig, source: 'itunes' });
        this.inputConfigs.set('file', { ...defaultConfig, source: 'file' });
        this.inputConfigs.set('ableton', { ...defaultConfig, source: 'ableton' });
        this.inputConfigs.set('midi', { ...defaultConfig, source: 'midi' });
        this.inputConfigs.set('line-in', { ...defaultConfig, source: 'line-in' });
        this.inputConfigs.set('internal', { ...defaultConfig, source: 'internal', enabled: true });
    }

    public async selectAudioSource(source: AudioInputSource): Promise<boolean> {
        try {
            console.log(`🔌 Connecting to audio source: ${source}`);

            // Ensure Tone.js is started (handles user gesture requirement)
            await Tone.start();
            console.log('✅ Tone.js started for audio source connection');

            // Disconnect current source
            await this.disconnectCurrentSource();

            switch (source) {
                case 'microphone':
                    await this.connectMicrophone();
                    break;
                case 'youtube':
                    // YouTube connection handled separately via connectYouTube()
                    break;
                case 'spotify':
                    await this.connectSpotify();
                    break;
                case 'itunes':
                    await this.connectItunes();
                    break;
                case 'file':
                    // File selection handled separately via connectAudioFile()
                    break;
                case 'ableton':
                    await this.connectAbleton();
                    break;
                case 'line-in':
                    await this.connectLineIn();
                    break;
                case 'internal':
                default:
                    // Internal synthesis (current AudioEngine)
                    break;
            }

            this.currentSource = source;
            this.updateInputConfig(source, { enabled: true });
            this.startAnalysis();

            return true;
        } catch (error) {
            console.error(`Failed to connect to ${source}:`, error);
            return false;
        }
    }

    private async connectMicrophone(): Promise<void> {
        try {
            this.microphoneStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: false
                }
            });

            this.microphoneSource = this.audioContext.createMediaStreamSource(this.microphoneStream);
            this.microphoneSource.connect(this.masterGain);

            console.log('🎤 Microphone connected');
        } catch (error) {
            throw new Error(`Microphone access denied: ${error}`);
        }
    }

    public async connectYouTube(videoUrl: string): Promise<boolean> {
        try {
            console.log('🔄 Attempting YouTube connection...', videoUrl);

            // Extract YouTube video ID
            const videoId = this.extractYouTubeVideoId(videoUrl);
            if (!videoId) {
                console.error('❌ Invalid YouTube URL format');
                throw new Error('Invalid YouTube URL format. Please use a valid YouTube URL.');
            }

            console.log('✅ Video ID extracted:', videoId);

            // Create YouTube iframe player (works around CORS restrictions)
            await this.createYouTubePlayer(videoId);

            console.log('📺 YouTube player created successfully');
            this.currentSource = 'youtube';
            return true;
        } catch (error) {
            console.error('❌ YouTube connection failed:', error);
            return false;
        }
    }

    private async createYouTubePlayer(videoId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            // Add timeout to prevent hanging
            const timeout = setTimeout(() => {
                console.error('⏰ YouTube player initialization timeout');
                reject(new Error('YouTube player initialization timeout after 10 seconds'));
            }, 10000);
            // Load YouTube iframe API if not already loaded
            if (!window.YT) {
                console.log('📡 Loading YouTube iframe API...');
                console.log('🌍 Current origin:', window.location.origin);

                const script = document.createElement('script');
                script.src = 'https://www.youtube.com/iframe_api';
                script.onload = () => console.log('📡 YouTube API script loaded');
                script.onerror = () => {
                    console.error('❌ Failed to load YouTube API script');
                    reject(new Error('Failed to load YouTube API'));
                };
                document.head.appendChild(script);

                window.onYouTubeIframeAPIReady = () => {
                    console.log('🎯 YouTube iframe API ready');
                    clearTimeout(timeout);
                    try {
                        this.initializeYouTubePlayer(videoId, resolve, reject);
                    } catch (error) {
                        console.error('❌ Error in onYouTubeIframeAPIReady:', error);
                        reject(error);
                    }
                };
            } else {
                console.log('✅ YouTube API already loaded');
                clearTimeout(timeout);
                this.initializeYouTubePlayer(videoId, resolve, reject);
            }
        });
    }

    private initializeYouTubePlayer(videoId: string, resolve: Function, reject: Function) {
        try {
            console.log('🔧 Initializing YouTube player with video ID:', videoId);

            // Check if YT is actually available
            if (!window.YT || !window.YT.Player) {
                throw new Error('YouTube API not properly loaded');
            }

            // Create div for YouTube player (making it visible for debugging)
            let playerDiv = document.getElementById('youtube-player');
            if (!playerDiv) {
                playerDiv = document.createElement('div');
                playerDiv.id = 'youtube-player';
                // Make player visible in bottom-right corner for debugging
                playerDiv.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 320px;
                    height: 180px;
                    z-index: 1000;
                    border: 2px solid #00ffff;
                    border-radius: 8px;
                    background: rgba(0, 0, 0, 0.8);
                `;
                document.body.appendChild(playerDiv);
                console.log('📺 YouTube player div created and made visible');
            }

            this.youtubePlayer = new window.YT.Player('youtube-player', {
                height: '180',
                width: '320',
                videoId: videoId,
                playerVars: {
                    autoplay: 0,
                    controls: 1,  // Enable controls to help with CORS issues
                    disablekb: 0,  // Allow keyboard controls
                    fs: 1,  // Allow fullscreen
                    iv_load_policy: 3,
                    modestbranding: 1,
                    rel: 0,
                    showinfo: 0,
                    origin: window.location.origin  // Specify our origin for CORS
                },
                host: 'https://www.youtube-nocookie.com', // Use privacy-enhanced mode
                events: {
                    onReady: (event: any) => {
                        console.log('🎉 YouTube player ready!');
                        // Get audio context from YouTube player
                        try {
                            const iframe = document.getElementById('youtube-player') as HTMLIFrameElement;
                            if (iframe) {
                                console.log('📺 YouTube iframe found, connecting audio...');
                                // Create audio context connection
                                this.connectYouTubeAudio(event.target);
                                resolve();
                            } else {
                                console.warn('⚠️ YouTube iframe not found');
                                resolve(); // Still resolve, player is ready
                            }
                        } catch (error) {
                            console.warn('⚠️ YouTube audio context setup failed, but player ready:', error);
                            resolve(); // Still allow YouTube to work without audio analysis
                        }
                    },
                    onStateChange: (event: any) => {
                        const states = {
                            '-1': 'unstarted',
                            '0': 'ended',
                            '1': 'playing',
                            '2': 'paused',
                            '3': 'buffering',
                            '5': 'video cued'
                        };
                        console.log(`📺 YouTube player state: ${states[event.data] || event.data}`);
                    },
                    onError: (error: any) => {
                        const errorCodes = {
                            '2': 'Invalid video ID',
                            '5': 'HTML5 player error',
                            '100': 'Video not found or private',
                            '101': 'Video not allowed in embedded players',
                            '150': 'Video not allowed in embedded players'
                        };
                        console.error('❌ YouTube player error:', errorCodes[error.data] || `Unknown error (${error.data})`);
                        reject(new Error(`YouTube player error: ${errorCodes[error.data] || error.data}`));
                    }
                }
            });
        } catch (error) {
            reject(error);
        }
    }

    private connectYouTubeAudio(player: any) {
        // Note: Due to CORS restrictions, we can't directly access YouTube's audio
        // This creates a working YouTube player that can be controlled, but audio analysis
        // will be limited. For full audio analysis, users should use file upload or other sources.
        console.log('📺 YouTube player ready (audio analysis limited due to CORS)');

        // Test if BlackHole is blocking audio context
        this.testAudioContext();
    }

    private testAudioContext() {
        try {
            console.log('🔊 Testing audio context with BlackHole...');
            const testContext = new AudioContext();
            console.log('✅ Audio context created successfully');
            console.log('🎛️ Audio context state:', testContext.state);
            console.log('🔌 Audio destination:', testContext.destination);
            testContext.close();
        } catch (error) {
            console.error('❌ BlackHole blocking audio context:', error);
        }
    }

    public async connectSpotify(): Promise<void> {
        try {
            // Initialize Spotify Web Playback SDK
            if (!window.Spotify) {
                await this.loadSpotifySDK();
            }

            // Check if user is logged into Spotify
            const token = this.getSpotifyAccessToken();
            if (!token) {
                throw new Error('Please log into Spotify first. Visit: https://accounts.spotify.com/authorize?client_id=YOUR_CLIENT_ID&response_type=token&redirect_uri=YOUR_REDIRECT_URI&scope=streaming%20user-read-email%20user-read-private');
            }

            this.spotifyPlayer = new window.Spotify.Player({
                name: 'Universal Signal Engine',
                getOAuthToken: (cb: Function) => { cb(token); },
                volume: 0.8
            });

            // Connect the player
            await this.spotifyPlayer.connect();

            console.log('🎵 Spotify connected');
        } catch (error) {
            throw new Error(`Spotify connection failed: ${error}`);
        }
    }

    public async connectItunes(): Promise<void> {
        try {
            // iTunes/Apple Music integration using MusicKit JS
            if (!window.MusicKit) {
                await this.loadMusicKitJS();
            }

            await window.MusicKit.configure({
                developerToken: 'YOUR_APPLE_MUSIC_DEVELOPER_TOKEN', // Requires Apple Developer account
                app: {
                    name: 'Universal Signal Engine',
                    build: '1.0.0'
                }
            });

            const musicInstance = window.MusicKit.getInstance();

            if (!musicInstance.isAuthorized) {
                await musicInstance.authorize();
            }

            console.log('🍎 iTunes/Apple Music connected');
        } catch (error) {
            throw new Error(`iTunes connection failed: ${error}`);
        }
    }

    private async loadSpotifySDK(): Promise<void> {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://sdk.scdn.co/spotify-player.js';
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load Spotify SDK'));
            document.head.appendChild(script);
        });
    }

    private async loadMusicKitJS(): Promise<void> {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://js-cdn.music.apple.com/musickit/v1/musickit.js';
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load MusicKit JS'));
            document.head.appendChild(script);
        });
    }

    private getSpotifyAccessToken(): string | null {
        // In a real implementation, this would handle OAuth flow
        // For now, return null to indicate no token available
        return localStorage.getItem('spotify_access_token');
    }

    public async connectAudioFile(file: File): Promise<boolean> {
        try {
            const url = URL.createObjectURL(file);

            this.fileAudio = new Audio(url);
            this.fileAudio.crossOrigin = 'anonymous';

            await new Promise((resolve, reject) => {
                this.fileAudio!.onloadeddata = resolve;
                this.fileAudio!.onerror = reject;
                this.fileAudio!.load();
            });

            this.fileSource = this.audioContext.createMediaElementSource(this.fileAudio);
            this.fileSource.connect(this.masterGain);

            console.log('📁 Audio file connected:', file.name);
            return true;
        } catch (error) {
            console.error('File connection failed:', error);
            return false;
        }
    }

    private async connectAbleton(): Promise<void> {
        try {
            // Connect to Ableton Live via WebSocket (requires Max for Live device)
            this.abletonWebSocket = new WebSocket('ws://localhost:8081');

            this.abletonWebSocket.onopen = () => {
                this.abletonConnected = true;
                console.log('🎛️ Ableton Live connected');

                // Request audio stream setup
                this.abletonWebSocket?.send(JSON.stringify({
                    type: 'setup_audio_stream',
                    sampleRate: this.audioContext.sampleRate
                }));
            };

            this.abletonWebSocket.onmessage = (event) => {
                this.handleAbletonMessage(JSON.parse(event.data));
            };

            this.abletonWebSocket.onerror = () => {
                throw new Error('Ableton Live connection failed - ensure Max for Live device is running');
            };

        } catch (error) {
            throw new Error(`Ableton connection failed: ${error}`);
        }
    }

    private async connectLineIn(): Promise<void> {
        // Similar to microphone but with different constraints
        try {
            this.microphoneStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: false,
                    noiseSuppression: false,
                    autoGainControl: false,
                    latency: 0.01 // Low latency for line input
                }
            });

            this.microphoneSource = this.audioContext.createMediaStreamSource(this.microphoneStream);
            this.microphoneSource.connect(this.masterGain);

            console.log('🔌 Line input connected');
        } catch (error) {
            throw new Error(`Line input access denied: ${error}`);
        }
    }

    private async disconnectCurrentSource(): Promise<void> {
        // Disconnect microphone
        if (this.microphoneSource) {
            this.microphoneSource.disconnect();
            this.microphoneSource = null;
        }
        if (this.microphoneStream) {
            this.microphoneStream.getTracks().forEach(track => track.stop());
            this.microphoneStream = null;
        }

        // Disconnect YouTube
        if (this.youtubeSource) {
            this.youtubeSource.disconnect();
            this.youtubeSource = null;
        }
        if (this.youtubeAudio) {
            this.youtubeAudio.pause();
            this.youtubeAudio = null;
        }
        if (this.youtubePlayer) {
            this.youtubePlayer.destroy();
            this.youtubePlayer = null;
        }

        // Disconnect Spotify
        if (this.spotifyPlayer) {
            this.spotifyPlayer.disconnect();
            this.spotifyPlayer = null;
        }

        // Disconnect iTunes
        if (this.itunesSource) {
            this.itunesSource.disconnect();
            this.itunesSource = null;
        }
        if (this.itunesAudio) {
            this.itunesAudio.pause();
            this.itunesAudio = null;
        }

        // Disconnect file
        if (this.fileSource) {
            this.fileSource.disconnect();
            this.fileSource = null;
        }
        if (this.fileAudio) {
            this.fileAudio.pause();
            this.fileAudio = null;
        }

        // Disconnect Ableton
        if (this.abletonWebSocket) {
            this.abletonWebSocket.close();
            this.abletonWebSocket = null;
            this.abletonConnected = false;
        }

        // Update configs
        for (const [source, config] of this.inputConfigs) {
            config.enabled = false;
        }
    }

    private handleAbletonMessage(message: any) {
        switch (message.type) {
            case 'audio_data':
                // Handle real-time audio data from Ableton
                this.processAbletonAudioData(message.data);
                break;
            case 'tempo':
                // Handle tempo changes
                this.handleTempoChange(message.tempo);
                break;
            case 'transport':
                // Handle play/stop/position
                this.handleTransportChange(message.state);
                break;
        }
    }

    private processAbletonAudioData(audioData: Float32Array) {
        // Process audio data from Ableton Live
        // This would be implemented with a more sophisticated audio buffer system
        console.log('Processing Ableton audio data', audioData.length);
    }

    private handleTempoChange(tempo: number) {
        console.log('Ableton tempo changed:', tempo);
    }

    private handleTransportChange(state: string) {
        console.log('Ableton transport:', state);
    }

    private extractYouTubeVideoId(url: string): string | null {
        console.log('🔍 Extracting video ID from URL:', url);

        // Multiple patterns to handle different YouTube URL formats
        const patterns = [
            /(?:youtube\.com\/watch\?v=)([^&\n?#]+)/,           // Standard: youtube.com/watch?v=ID
            /(?:youtu\.be\/)([^&\n?#]+)/,                       // Short: youtu.be/ID
            /(?:youtube\.com\/embed\/)([^&\n?#]+)/,             // Embed: youtube.com/embed/ID
            /(?:youtube\.com\/v\/)([^&\n?#]+)/,                 // Old: youtube.com/v/ID
            /(?:youtube\.com.*[?&]v=)([^&\n?#]+)/               // Any youtube.com with v= parameter
        ];

        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match && match[1]) {
                console.log('✅ Video ID found:', match[1]);
                return match[1];
            }
        }

        console.error('❌ No video ID found in URL');
        return null;
    }

    public startAnalysis() {
        if (this.isAnalyzing) return;

        this.isAnalyzing = true;
        this.analyzeLoop();
    }

    public stopAnalysis() {
        this.isAnalyzing = false;
    }

    private analyzeLoop() {
        if (!this.isAnalyzing) return;

        this.analyzer.getFloatFrequencyData(this.frequencyData);
        this.analyzer.getFloatTimeDomainData(this.waveformData);

        const analysis: AudioAnalysis = {
            frequency: this.frequencyData,
            waveform: this.waveformData,
            rms: this.calculateRMS(this.waveformData),
            peak: this.calculatePeak(this.waveformData),
            pitch: this.estimatePitch(this.frequencyData)
        };

        // Notify callbacks
        this.analyzeCallbacks.forEach(callback => callback(analysis));

        requestAnimationFrame(() => this.analyzeLoop());
    }

    private calculateRMS(waveform: Float32Array): number {
        let sum = 0;
        for (let i = 0; i < waveform.length; i++) {
            sum += waveform[i] * waveform[i];
        }
        return Math.sqrt(sum / waveform.length);
    }

    private calculatePeak(waveform: Float32Array): number {
        let peak = 0;
        for (let i = 0; i < waveform.length; i++) {
            peak = Math.max(peak, Math.abs(waveform[i]));
        }
        return peak;
    }

    private estimatePitch(frequency: Float32Array): number {
        // Simple pitch estimation - find the frequency bin with highest magnitude
        let maxIndex = 0;
        let maxValue = -Infinity;

        for (let i = 1; i < frequency.length; i++) {
            if (frequency[i] > maxValue) {
                maxValue = frequency[i];
                maxIndex = i;
            }
        }

        return (maxIndex * this.audioContext.sampleRate) / (2 * frequency.length);
    }

    public updateInputConfig(source: AudioInputSource, updates: Partial<AudioInputConfig>) {
        const config = this.inputConfigs.get(source);
        if (config) {
            Object.assign(config, updates);
        }
    }

    public getInputConfig(source: AudioInputSource): AudioInputConfig | undefined {
        return this.inputConfigs.get(source);
    }

    public getCurrentSource(): AudioInputSource {
        return this.currentSource;
    }

    public getAvailableSources(): AudioInputSource[] {
        return Array.from(this.inputConfigs.keys());
    }

    public onAnalysis(callback: (analysis: AudioAnalysis) => void) {
        this.analyzeCallbacks.push(callback);
    }

    public removeAnalysisCallback(callback: (analysis: AudioAnalysis) => void) {
        const index = this.analyzeCallbacks.indexOf(callback);
        if (index > -1) {
            this.analyzeCallbacks.splice(index, 1);
        }
    }

    public setMasterGain(gain: number) {
        this.masterGain.gain.setValueAtTime(gain, this.audioContext.currentTime);
    }

    public getMasterGain(): number {
        return this.masterGain.gain.value;
    }

    public playAudioFile() {
        if (this.fileAudio) {
            this.fileAudio.play();
        }
    }

    public pauseAudioFile() {
        if (this.fileAudio) {
            this.fileAudio.pause();
        }
    }

    public playYouTube() {
        if (this.youtubePlayer) {
            this.youtubePlayer.playVideo();
        } else if (this.youtubeAudio) {
            this.youtubeAudio.play();
        }
    }

    public pauseYouTube() {
        if (this.youtubePlayer) {
            this.youtubePlayer.pauseVideo();
        } else if (this.youtubeAudio) {
            this.youtubeAudio.pause();
        }
    }

    public disconnectYouTube() {
        console.log('🔌 Disconnecting YouTube...');

        if (this.youtubePlayer) {
            try {
                this.youtubePlayer.destroy();
                console.log('📺 YouTube player destroyed');
            } catch (error) {
                console.warn('⚠️ Error destroying YouTube player:', error);
            }
            this.youtubePlayer = null;
        }

        if (this.youtubeAudio) {
            try {
                this.youtubeAudio.pause();
                this.youtubeAudio.src = '';
            } catch (error) {
                console.warn('⚠️ Error cleaning up YouTube audio:', error);
            }
            this.youtubeAudio = null;
        }

        // Remove player element
        const playerDiv = document.getElementById('youtube-player');
        if (playerDiv) {
            playerDiv.remove();
            console.log('🗑️ YouTube player element removed');
        }

        // Reset current source if it was YouTube
        if (this.currentSource === 'youtube') {
            this.currentSource = 'internal';
            console.log('🔄 Audio source reset to internal');
        }
    }

    public playSpotify() {
        if (this.spotifyPlayer) {
            this.spotifyPlayer.resume();
        }
    }

    public pauseSpotify() {
        if (this.spotifyPlayer) {
            this.spotifyPlayer.pause();
        }
    }

    public playItunes() {
        if (window.MusicKit && window.MusicKit.getInstance()) {
            window.MusicKit.getInstance().play();
        }
    }

    public pauseItunes() {
        if (window.MusicKit && window.MusicKit.getInstance()) {
            window.MusicKit.getInstance().pause();
        }
    }

    public isAbletonConnected(): boolean {
        return this.abletonConnected;
    }
}