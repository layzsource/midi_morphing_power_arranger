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
    private fileAudio: HTMLAudioElement | null = null;
    private fileSource: MediaElementAudioSourceNode | null = null;

    // Analysis
    private frequencyData: Float32Array;
    private waveformData: Float32Array;
    private isAnalyzing: boolean = false;
    private analyzeCallbacks: ((analysis: AudioAnalysis) => void)[] = [];
    private analyzeLoopCounter: number = 0;

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
    }

    private async resumeAudioContext(): Promise<void> {
        if (this.audioContext.state === 'suspended') {
            try {
                await this.audioContext.resume();
                console.log('🔊 AudioContext resumed');
            } catch (error) {
                console.warn('⚠️ Failed to resume AudioContext:', error);
            }
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
        this.inputConfigs.set('file', { ...defaultConfig, source: 'file' });
        this.inputConfigs.set('ableton', { ...defaultConfig, source: 'ableton' });
        this.inputConfigs.set('midi', { ...defaultConfig, source: 'midi' });
        this.inputConfigs.set('line-in', { ...defaultConfig, source: 'line-in' });
        this.inputConfigs.set('internal', { ...defaultConfig, source: 'internal', enabled: true });
    }

    public async selectAudioSource(source: AudioInputSource): Promise<boolean> {
        try {
            // Disconnect current source
            await this.disconnectCurrentSource();
            await this.resumeAudioContext();

            switch (source) {
                case 'microphone':
                    await this.connectMicrophone();
                    break;
                case 'youtube':
                    // YouTube connection handled separately
                    break;
                case 'file':
                    // File selection handled separately
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
            // Extract YouTube video ID
            const videoId = this.extractYouTubeVideoId(videoUrl);
            if (!videoId) {
                throw new Error('Invalid YouTube URL');
            }

            // Create hidden audio element for YouTube
            this.youtubeAudio = document.createElement('audio');
            this.youtubeAudio.crossOrigin = 'anonymous';
            this.youtubeAudio.controls = false;
            this.youtubeAudio.style.display = 'none';

            // Note: Direct YouTube audio extraction requires YouTube API or iframe player
            // For now, this is a placeholder for the UI structure
            console.warn('YouTube integration requires YouTube API setup');

            return false; // Temporarily disabled until YouTube API integration
        } catch (error) {
            console.error('YouTube connection failed:', error);
            return false;
        }
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
        const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/;
        const match = url.match(regex);
        return match ? match[1] : null;
    }

    public startAnalysis() {
        if (this.audioContext.state === 'suspended') {
            this.resumeAudioContext().catch(() => undefined);
        }

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

        // Remove spam - analysis is clearly running

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
        if (this.youtubeAudio) {
            this.youtubeAudio.play();
        }
    }

    public pauseYouTube() {
        if (this.youtubeAudio) {
            this.youtubeAudio.pause();
        }
    }

    public isAbletonConnected(): boolean {
        return this.abletonConnected;
    }
}