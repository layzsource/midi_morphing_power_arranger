interface SequenceEvent {
    timestamp: number;
    type: 'archetype' | 'mode' | 'beat' | 'stop';
    data: {
        archetype?: string;
        mode?: string;
        velocity?: number;
        [key: string]: any;
    };
}

interface Sequence {
    id: string;
    name: string;
    events: SequenceEvent[];
    duration: number;
    bpm: number;
    quantize: boolean;
}

export class SequenceRecorder {
    private sequences: Map<string, Sequence> = new Map();
    private currentSequence: Sequence | null = null;
    private isRecording = false;
    private isPlaying = false;
    private recordStartTime = 0;
    private playStartTime = 0;
    private playbackIntervals: NodeJS.Timeout[] = [];
    private onSequenceEvent: ((event: SequenceEvent) => void) | null = null;
    private metronome: NodeJS.Timeout | null = null;
    private currentBPM = 120;
    private quantizeGrid = 16; // 16th notes

    constructor() {
        this.initializeDefaultSequences();
    }

    private initializeDefaultSequences() {
        // Create some starter sequences for inspiration
        const welcomeSequence: Sequence = {
            id: 'welcome',
            name: 'Universal Welcome',
            duration: 8000,
            bpm: 120,
            quantize: true,
            events: [
                { timestamp: 0, type: 'archetype', data: { archetype: 'russell', velocity: 0.8 } },
                { timestamp: 1000, type: 'archetype', data: { archetype: 'blake', velocity: 0.6 } },
                { timestamp: 2000, type: 'archetype', data: { archetype: 'tesla', velocity: 0.9 } },
                { timestamp: 4000, type: 'beat', data: { velocity: 1.0 } },
                { timestamp: 6000, type: 'archetype', data: { archetype: 'beatles', velocity: 0.7 } }
            ]
        };

        const cosmicSequence: Sequence = {
            id: 'cosmic',
            name: 'Cosmic Journey',
            duration: 12000,
            bpm: 90,
            quantize: true,
            events: [
                { timestamp: 0, type: 'archetype', data: { archetype: 'hawking', velocity: 0.5 } },
                { timestamp: 2000, type: 'archetype', data: { archetype: 'russell', velocity: 0.7 } },
                { timestamp: 4000, type: 'archetype', data: { archetype: 'einstein', velocity: 0.6 } },
                { timestamp: 8000, type: 'archetype', data: { archetype: 'tesla', velocity: 0.8 } },
                { timestamp: 10000, type: 'beat', data: { velocity: 0.9 } }
            ]
        };

        this.sequences.set('welcome', welcomeSequence);
        this.sequences.set('cosmic', cosmicSequence);
    }

    public startRecording(name: string, bpm = 120) {
        if (this.isRecording) {
            this.stopRecording();
        }

        this.currentSequence = {
            id: Date.now().toString(),
            name: name,
            events: [],
            duration: 0,
            bpm: bpm,
            quantize: true
        };

        this.isRecording = true;
        this.recordStartTime = Date.now();
        this.currentBPM = bpm;

        console.log(`🔴 Recording sequence: ${name} at ${bpm} BPM`);
        this.startMetronome();
    }

    public stopRecording(): Sequence | null {
        if (!this.isRecording || !this.currentSequence) {
            return null;
        }

        this.isRecording = false;
        this.currentSequence.duration = Date.now() - this.recordStartTime;

        // Save the sequence
        this.sequences.set(this.currentSequence.id, this.currentSequence);

        console.log(`⏹️ Recorded sequence: ${this.currentSequence.name} (${this.currentSequence.duration}ms, ${this.currentSequence.events.length} events)`);

        this.stopMetronome();
        const recorded = this.currentSequence;
        this.currentSequence = null;

        return recorded;
    }

    public recordEvent(type: SequenceEvent['type'], data: SequenceEvent['data']) {
        if (!this.isRecording || !this.currentSequence) {
            return;
        }

        const timestamp = Date.now() - this.recordStartTime;
        const quantizedTimestamp = this.currentSequence.quantize
            ? this.quantizeTimestamp(timestamp)
            : timestamp;

        const event: SequenceEvent = {
            timestamp: quantizedTimestamp,
            type,
            data
        };

        this.currentSequence.events.push(event);
        console.log(`📝 Recorded: ${type} at ${quantizedTimestamp}ms`, data);
    }

    private quantizeTimestamp(timestamp: number): number {
        const beatDuration = (60 / this.currentBPM) * 1000; // ms per beat
        const gridDuration = beatDuration / (this.quantizeGrid / 4); // 16th note duration

        return Math.round(timestamp / gridDuration) * gridDuration;
    }

    public playSequence(sequenceId: string, loop = false): boolean {
        const sequence = this.sequences.get(sequenceId);
        if (!sequence) {
            console.error(`Sequence not found: ${sequenceId}`);
            return false;
        }

        if (this.isPlaying) {
            this.stopPlayback();
        }

        this.isPlaying = true;
        this.playStartTime = Date.now();

        console.log(`▶️ Playing sequence: ${sequence.name} ${loop ? '(looped)' : ''}`);

        // Schedule all events
        sequence.events.forEach(event => {
            const timeout = setTimeout(() => {
                if (this.onSequenceEvent && this.isPlaying) {
                    this.onSequenceEvent(event);
                }
            }, event.timestamp);

            this.playbackIntervals.push(timeout);
        });

        // Schedule end or loop
        const endTimeout = setTimeout(() => {
            if (loop && this.isPlaying) {
                this.playSequence(sequenceId, true); // Loop
            } else {
                this.stopPlayback();
            }
        }, sequence.duration);

        this.playbackIntervals.push(endTimeout);

        return true;
    }

    public stopPlayback() {
        if (!this.isPlaying) {
            return;
        }

        this.isPlaying = false;

        // Clear all scheduled events
        this.playbackIntervals.forEach(interval => clearTimeout(interval));
        this.playbackIntervals = [];

        console.log('⏹️ Stopped playback');
    }

    public layerSequence(sequenceId: string): boolean {
        // Play sequence without stopping current playback (for layering)
        const sequence = this.sequences.get(sequenceId);
        if (!sequence) {
            console.error(`Sequence not found: ${sequenceId}`);
            return false;
        }

        console.log(`🎛️ Layering sequence: ${sequence.name}`);

        // Schedule all events as additional layer
        sequence.events.forEach(event => {
            const timeout = setTimeout(() => {
                if (this.onSequenceEvent) {
                    this.onSequenceEvent(event);
                }
            }, event.timestamp);

            this.playbackIntervals.push(timeout);
        });

        return true;
    }

    private startMetronome() {
        this.stopMetronome();

        const beatInterval = (60 / this.currentBPM) * 1000;
        let beatCount = 0;

        this.metronome = setInterval(() => {
            beatCount++;
            // Visual metronome could be added here
            console.log(`🥁 Beat ${beatCount}`);
        }, beatInterval);
    }

    private stopMetronome() {
        if (this.metronome) {
            clearInterval(this.metronome);
            this.metronome = null;
        }
    }

    public onEvent(callback: (event: SequenceEvent) => void) {
        this.onSequenceEvent = callback;
    }

    public getSequences(): Sequence[] {
        return Array.from(this.sequences.values());
    }

    public getSequence(id: string): Sequence | undefined {
        return this.sequences.get(id);
    }

    public deleteSequence(id: string): boolean {
        return this.sequences.delete(id);
    }

    public renameSequence(id: string, newName: string): boolean {
        const sequence = this.sequences.get(id);
        if (sequence) {
            sequence.name = newName;
            return true;
        }
        return false;
    }

    public duplicateSequence(id: string, newName: string): string | null {
        const original = this.sequences.get(id);
        if (!original) {
            return null;
        }

        const duplicate: Sequence = {
            ...original,
            id: Date.now().toString(),
            name: newName,
            events: [...original.events]
        };

        this.sequences.set(duplicate.id, duplicate);
        return duplicate.id;
    }

    public exportSequence(id: string): string | null {
        const sequence = this.sequences.get(id);
        if (!sequence) {
            return null;
        }

        return JSON.stringify(sequence, null, 2);
    }

    public importSequence(jsonData: string): string | null {
        try {
            const sequence: Sequence = JSON.parse(jsonData);
            sequence.id = Date.now().toString(); // New ID to avoid conflicts
            this.sequences.set(sequence.id, sequence);
            return sequence.id;
        } catch (error) {
            console.error('Failed to import sequence:', error);
            return null;
        }
    }

    public isCurrentlyRecording(): boolean {
        return this.isRecording;
    }

    public isCurrentlyPlaying(): boolean {
        return this.isPlaying;
    }

    public getCurrentSequenceName(): string | null {
        return this.currentSequence?.name || null;
    }

    public setBPM(bpm: number) {
        this.currentBPM = bpm;
        if (this.isRecording && this.currentSequence) {
            this.currentSequence.bpm = bpm;
        }
    }

    public setQuantize(enabled: boolean) {
        if (this.currentSequence) {
            this.currentSequence.quantize = enabled;
        }
    }
}