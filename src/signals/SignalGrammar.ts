export interface Signal {
    type: 'frequency' | 'midi' | 'beat' | 'silence';
    frequency?: number;
    amplitude?: number;
    cc?: number;
    value?: number;
    velocity?: number;
    intensity?: number;
    duration?: number;
    trigger?: string;
}

export class SignalGrammar {
    private listeners: ((signal: Signal) => void)[] = [];
    private audioContext: AudioContext | null = null;
    private analyser: AnalyserNode | null = null;
    private dataArray: Uint8Array | null = null;
    private midiAccess: MIDIAccess | null = null;
    private isRunning = false;
    private beatDetector: BeatDetector;

    constructor() {
        this.beatDetector = new BeatDetector();
        this.initAudioContext();
    }

    private async initAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();

            // Request microphone access for audio analysis
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const source = this.audioContext.createMediaStreamSource(stream);

            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;

            source.connect(this.analyser);

            const bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(bufferLength);

        } catch (error) {
            console.log('Audio access denied:', error);
            // Continue without audio analysis
        }
    }

    public connectMIDI(midiAccess: MIDIAccess) {
        this.midiAccess = midiAccess;

        // Connect to all MIDI inputs
        for (const input of midiAccess.inputs.values()) {
            input.onmidimessage = (event) => {
                this.processMIDIMessage(event);
            };
        }
    }

    private processMIDIMessage(event: MIDIMessageEvent) {
        const [command, note, velocity] = event.data;

        // Control Change messages (CC)
        if ((command & 0xf0) === 0xb0) {
            const signal: Signal = {
                type: 'midi',
                cc: note,
                value: velocity,
                amplitude: velocity / 127
            };
            this.emitSignal(signal);
        }

        // Note On messages
        if ((command & 0xf0) === 0x90 && velocity > 0) {
            const frequency = this.midiNoteToFrequency(note);
            const signal: Signal = {
                type: 'frequency',
                frequency: frequency,
                amplitude: velocity / 127,
                velocity: velocity
            };
            this.emitSignal(signal);

            // Trigger archetype based on note ranges
            this.triggerArchetypeFromNote(note, velocity / 127);
        }
    }

    private triggerArchetypeFromNote(note: number, velocity: number) {
        // Map MIDI note ranges to archetypes
        const archetypeMap = [
            { min: 24, max: 35, name: 'hawking' },     // Low bass - cosmic
            { min: 36, max: 47, name: 'leadbelly' },   // Bass - blues
            { min: 48, max: 59, name: 'russell' },     // Mid-low - vessel
            { min: 60, max: 71, name: 'blake' },       // Mid - emergent
            { min: 72, max: 83, name: 'tesla' },       // Mid-high - electrical
            { min: 84, max: 95, name: 'beatles' },     // High - harmonic
            { min: 96, max: 127, name: 'pranksters' }  // Very high - chaotic
        ];

        for (const mapping of archetypeMap) {
            if (note >= mapping.min && note <= mapping.max) {
                const signal: Signal = {
                    type: 'midi',
                    trigger: mapping.name,
                    amplitude: velocity,
                    velocity: Math.floor(velocity * 127)
                };
                this.emitSignal(signal);
                break;
            }
        }
    }

    private midiNoteToFrequency(note: number): number {
        return 440 * Math.pow(2, (note - 69) / 12);
    }

    public onSignal(callback: (signal: Signal) => void) {
        this.listeners.push(callback);
    }

    private emitSignal(signal: Signal) {
        this.listeners.forEach(listener => listener(signal));
    }

    public start() {
        this.isRunning = true;
        this.analyzeAudio();
    }

    public stop() {
        this.isRunning = false;
    }

    private analyzeAudio = () => {
        if (!this.isRunning || !this.analyser || !this.dataArray) {
            return;
        }

        requestAnimationFrame(this.analyzeAudio);

        this.analyser.getByteFrequencyData(this.dataArray);

        // Analyze frequency spectrum
        this.analyzeFrequencies();

        // Detect beats
        this.beatDetector.process(this.dataArray);
        if (this.beatDetector.isBeat()) {
            const signal: Signal = {
                type: 'beat',
                intensity: this.beatDetector.getBeatIntensity()
            };
            this.emitSignal(signal);
        }

        // Detect silence
        const totalAmplitude = this.dataArray.reduce((sum, value) => sum + value, 0);
        if (totalAmplitude < 100) { // Threshold for silence
            const signal: Signal = {
                type: 'silence',
                duration: 1
            };
            this.emitSignal(signal);
        }
    };

    private analyzeFrequencies() {
        if (!this.dataArray) return;

        const binSize = this.audioContext!.sampleRate / (this.analyser!.fftSize * 2);

        // Analyze different frequency bands
        const bands = [
            { start: 0, end: 32, name: 'sub-bass' },      // 0-250Hz
            { start: 32, end: 64, name: 'bass' },         // 250-500Hz
            { start: 64, end: 96, name: 'low-mid' },      // 500-750Hz
            { start: 96, end: 128, name: 'mid' },         // 750-1000Hz
            { start: 128, end: 160, name: 'high-mid' },   // 1000-1250Hz
            { start: 160, end: 192, name: 'presence' },   // 1250-1500Hz
            { start: 192, end: 224, name: 'brilliance' }  // 1500-1750Hz
        ];

        bands.forEach(band => {
            let amplitude = 0;
            for (let i = band.start; i < band.end; i++) {
                amplitude += this.dataArray![i];
            }
            amplitude /= (band.end - band.start);

            if (amplitude > 50) { // Threshold for significant amplitude
                const frequency = (band.start + band.end) / 2 * binSize;
                const signal: Signal = {
                    type: 'frequency',
                    frequency: frequency,
                    amplitude: amplitude / 255
                };
                this.emitSignal(signal);
            }
        });
    }

    public triggerBeat(intensity = 0.8) {
        const signal: Signal = {
            type: 'beat',
            intensity: intensity
        };
        this.emitSignal(signal);
    }

    // Manual triggers for testing and keyboard control
    public triggerFrequency(frequency: number, amplitude = 0.5) {
        const signal: Signal = {
            type: 'frequency',
            frequency: frequency,
            amplitude: amplitude
        };
        this.emitSignal(signal);
    }

    public triggerSilence(duration = 2) {
        const signal: Signal = {
            type: 'silence',
            duration: duration
        };
        this.emitSignal(signal);
    }
}

class BeatDetector {
    private energyHistory: number[] = [];
    private historySize = 43; // ~1 second at 60fps
    private beatThreshold = 1.3;
    private lastBeatTime = 0;
    private minimumBeatInterval = 200; // ms

    public process(frequencyData: Uint8Array) {
        // Calculate current energy (focus on low frequencies for beat detection)
        let energy = 0;
        for (let i = 0; i < 64; i++) { // Low frequency range
            energy += frequencyData[i] * frequencyData[i];
        }

        this.energyHistory.push(energy);
        if (this.energyHistory.length > this.historySize) {
            this.energyHistory.shift();
        }
    }

    public isBeat(): boolean {
        if (this.energyHistory.length < this.historySize) {
            return false;
        }

        const now = Date.now();
        if (now - this.lastBeatTime < this.minimumBeatInterval) {
            return false;
        }

        const currentEnergy = this.energyHistory[this.energyHistory.length - 1];
        const averageEnergy = this.energyHistory.reduce((sum, e) => sum + e, 0) / this.energyHistory.length;

        if (currentEnergy > averageEnergy * this.beatThreshold) {
            this.lastBeatTime = now;
            return true;
        }

        return false;
    }

    public getBeatIntensity(): number {
        if (this.energyHistory.length < this.historySize) {
            return 0;
        }

        const currentEnergy = this.energyHistory[this.energyHistory.length - 1];
        const averageEnergy = this.energyHistory.reduce((sum, e) => sum + e, 0) / this.energyHistory.length;

        return Math.min((currentEnergy / averageEnergy) / this.beatThreshold, 1);
    }
}