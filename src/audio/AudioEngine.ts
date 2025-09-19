import * as Tone from 'tone';

interface ArchetypeSound {
    name: string;
    instruments: Tone.ToneAudioNode[];
    play: (velocity?: number) => void;
    stop: () => void;
}

export class AudioEngine {
    private initialized = false;
    private archetypeSounds: Map<string, ArchetypeSound> = new Map();
    private masterVolume: Tone.Volume;
    private reverb: Tone.Reverb;
    private delay: Tone.FeedbackDelay;

    constructor() {
        this.masterVolume = new Tone.Volume(-10);
        this.reverb = new Tone.Reverb(2);
        this.delay = new Tone.FeedbackDelay('8n', 0.3);

        // Connect effects chain
        this.delay.connect(this.reverb);
        this.reverb.connect(this.masterVolume);
        this.masterVolume.toDestination();
    }

    public async initialize() {
        if (this.initialized) return;

        await Tone.start();
        this.initializeArchetypeSounds();
        this.initialized = true;
        console.log('🎵 Audio Engine initialized');
    }

    private initializeArchetypeSounds() {
        // VESSEL LAYER - Geometric, foundational tones
        this.createRussellSound();
        this.createGreiffSound();
        this.createEinsteinSound();

        // EMERGENT FORM LAYER - Dynamic, evolving sounds
        this.createBlakeSound();
        this.createTeslaSound();
        this.createBeatlesSound();

        // PARTICLE LAYER - Rhythmic, textural sounds
        this.createLeadBellySound();
        this.createHawkingSound();
        this.createPrankstersSound();

        // SHADOW LAYER - Ambient, inverted sounds
        this.createHoffmanSound();
        this.createWaasSound();
    }

    // VESSEL LAYER SOUNDS
    private createRussellSound() {
        // Cosmic geometry - perfect harmonics
        const synth = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: 'sine' },
            envelope: { attack: 0.5, decay: 1, sustain: 0.3, release: 2 }
        });

        const filter = new Tone.Filter(800, 'lowpass');
        synth.connect(filter);
        filter.connect(this.delay);

        this.archetypeSounds.set('russell', {
            name: 'Walter Russell',
            instruments: [synth],
            play: (velocity = 0.8) => {
                // Perfect harmonic series: C, G, C octave
                const chords = [['C4', 'G4', 'C5'], ['F4', 'C5', 'F5'], ['G4', 'D5', 'G5']];
                const chord = chords[Math.floor(Math.random() * chords.length)];
                synth.triggerAttackRelease(chord, '2n', undefined, velocity);
            },
            stop: () => synth.releaseAll()
        });
    }

    private createGreiffSound() {
        // Architectural memory - cathedral reverb
        const synth = new Tone.Synth({
            oscillator: { type: 'triangle' },
            envelope: { attack: 2, decay: 1, sustain: 0.8, release: 4 }
        });

        const reverb = new Tone.Reverb(4);
        synth.connect(reverb);
        reverb.connect(this.masterVolume);

        this.archetypeSounds.set('greiff', {
            name: 'Constance Greiff',
            instruments: [synth],
            play: (velocity = 0.6) => {
                // Solfeggio healing frequencies
                const frequencies = [174, 285, 396];
                const freq = frequencies[Math.floor(Math.random() * frequencies.length)];
                synth.triggerAttackRelease(freq, '1n', undefined, velocity);
            },
            stop: () => synth.triggerRelease()
        });
    }

    private createEinsteinSound() {
        // Relativistic - time-dilated effects
        const synth = new Tone.Synth({
            oscillator: { type: 'sawtooth' },
            envelope: { attack: 0.1, decay: 0.2, sustain: 0.5, release: 1 }
        });

        const pitchShift = new Tone.PitchShift(0);
        const tremolo = new Tone.Tremolo(0.5, 0.3);

        synth.connect(pitchShift);
        pitchShift.connect(tremolo);
        tremolo.connect(this.delay);

        this.archetypeSounds.set('einstein', {
            name: 'Albert Einstein',
            instruments: [synth],
            play: (velocity = 0.7) => {
                // Universal healing frequencies with Doppler effects
                const frequencies = [432, 528, 741];
                const freq = frequencies[Math.floor(Math.random() * frequencies.length)];

                // Simulate relativity with pitch bending
                pitchShift.pitch = (Math.random() - 0.5) * 12;
                synth.triggerAttackRelease(freq, '4n', undefined, velocity);
            },
            stop: () => synth.triggerRelease()
        });
    }

    // EMERGENT FORM LAYER SOUNDS
    private createBlakeSound() {
        // Mystical, visionary chants
        const voices = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: 'triangle' },
            envelope: { attack: 1, decay: 0.5, sustain: 0.7, release: 2 }
        });

        const chorus = new Tone.Chorus(4, 2.5, 0.5);
        voices.connect(chorus);
        chorus.connect(this.reverb);

        this.archetypeSounds.set('blake', {
            name: 'William Blake',
            instruments: [voices],
            play: (velocity = 0.8) => {
                // Ancient mystical frequencies in modal harmony
                const modes = [
                    ['D4', 'F4', 'G4', 'A4', 'C5'], // Dorian-like
                    ['E4', 'G4', 'A4', 'B4', 'D5'], // Mystical
                    ['F4', 'Ab4', 'Bb4', 'C5', 'Eb5'] // Dark modal
                ];
                const mode = modes[Math.floor(Math.random() * modes.length)];
                const chord = mode.slice(0, 3);
                voices.triggerAttackRelease(chord, '1n', undefined, velocity);
            },
            stop: () => voices.releaseAll()
        });
    }

    private createTeslaSound() {
        // Electrical resonance, 3-6-9 patterns
        const osc = new Tone.Oscillator(369, 'square');
        const filter = new Tone.Filter(1000, 'bandpass');
        const tremolo = new Tone.Tremolo(9, 0.6);

        osc.connect(filter);
        filter.connect(tremolo);
        tremolo.connect(this.delay);

        this.archetypeSounds.set('tesla', {
            name: 'Nikola Tesla',
            instruments: [osc],
            play: (velocity = 0.9) => {
                // Tesla's obsession with 3, 6, 9
                const frequencies = [369, 639, 963, 147, 258];
                const freq = frequencies[Math.floor(Math.random() * frequencies.length)];

                osc.frequency.setValueAtTime(freq, Tone.now());
                osc.start();

                // Auto-stop after electrical arc duration
                setTimeout(() => osc.stop(), 500);
            },
            stop: () => osc.stop()
        });
    }

    private createBeatlesSound() {
        // Harmonic collaboration, psychedelic
        const synth1 = new Tone.Synth({ oscillator: { type: 'sine' } });
        const synth2 = new Tone.Synth({ oscillator: { type: 'sawtooth' } });
        const synth3 = new Tone.Synth({ oscillator: { type: 'triangle' } });
        const synth4 = new Tone.Synth({ oscillator: { type: 'square' } });

        const phaser = new Tone.Phaser(0.5, 3, 440);

        [synth1, synth2, synth3, synth4].forEach(synth => {
            synth.connect(phaser);
        });
        phaser.connect(this.reverb);

        this.archetypeSounds.set('beatles', {
            name: 'The Beatles',
            instruments: [synth1, synth2, synth3, synth4],
            play: (velocity = 0.7) => {
                // Harmonic series in A (440Hz)
                const harmonics = ['A4', 'A5', 'E6', 'A6'];

                harmonics.forEach((note, i) => {
                    const synths = [synth1, synth2, synth3, synth4];
                    setTimeout(() => {
                        synths[i].triggerAttackRelease(note, '8n', undefined, velocity);
                    }, i * 100);
                });
            },
            stop: () => {
                [synth1, synth2, synth3, synth4].forEach(synth => synth.triggerRelease());
            }
        });
    }

    // PARTICLE LAYER SOUNDS
    private createLeadBellySound() {
        // Blues, folk, raw expression
        const bass = new Tone.Synth({
            oscillator: { type: 'sawtooth' },
            envelope: { attack: 0.01, decay: 0.2, sustain: 0.3, release: 0.5 }
        });

        const distortion = new Tone.Distortion(0.4);
        bass.connect(distortion);
        distortion.connect(this.masterVolume);

        this.archetypeSounds.set('leadbelly', {
            name: 'Lead Belly',
            instruments: [bass],
            play: (velocity = 0.9) => {
                // Blues scale fundamentals
                const bluesNotes = ['E2', 'G2', 'A2', 'Bb2', 'B2', 'D3', 'E3'];
                const note = bluesNotes[Math.floor(Math.random() * bluesNotes.length)];
                bass.triggerAttackRelease(note, '4n', undefined, velocity);
            },
            stop: () => bass.triggerRelease()
        });
    }

    private createHawkingSound() {
        // Cosmic, black hole sounds
        const noise = new Tone.Noise('brown');
        const filter = new Tone.Filter(50, 'lowpass');
        const envelope = new Tone.AmplitudeEnvelope(2, 1, 0.5, 4);

        noise.connect(filter);
        filter.connect(envelope);
        envelope.connect(this.reverb);

        this.archetypeSounds.set('hawking', {
            name: 'Stephen Hawking',
            instruments: [noise],
            play: (velocity = 0.6) => {
                // Simulate Hawking radiation as filtered noise
                filter.frequency.setValueAtTime(20 + Math.random() * 80, Tone.now());
                envelope.triggerAttackRelease('2n');
                noise.start();
                setTimeout(() => noise.stop(), 2000);
            },
            stop: () => noise.stop()
        });
    }

    private createPrankstersSound() {
        // Chaotic, kaleidoscopic sounds
        const feedback = new Tone.FeedbackDelay('16n', 0.8);
        const bitCrusher = new Tone.BitCrusher(4);
        const randomOsc = new Tone.Oscillator(Math.random() * 1000 + 200, 'square');

        randomOsc.connect(bitCrusher);
        bitCrusher.connect(feedback);
        feedback.connect(this.masterVolume);

        this.archetypeSounds.set('pranksters', {
            name: 'Merry Pranksters',
            instruments: [randomOsc],
            play: (velocity = 0.8) => {
                // Chaotic frequency sequence
                const frequencies = [111, 222, 333, 444, 555, 666, 777];
                const freq = frequencies[Math.floor(Math.random() * frequencies.length)];

                randomOsc.frequency.setValueAtTime(freq, Tone.now());
                randomOsc.start();

                // Random duration
                setTimeout(() => randomOsc.stop(), Math.random() * 1000 + 200);
            },
            stop: () => randomOsc.stop()
        });
    }

    // SHADOW LAYER SOUNDS
    private createHoffmanSound() {
        // Disruptive, rebellious noise bursts
        const noise = new Tone.Noise('white');
        const gate = new Tone.Gate(-20, 0.1);
        const distortion = new Tone.Distortion(0.8);

        noise.connect(gate);
        gate.connect(distortion);
        distortion.connect(this.masterVolume);

        this.archetypeSounds.set('hoffman', {
            name: 'Abbie Hoffman',
            instruments: [noise],
            play: (velocity = 1.0) => {
                // Sudden disruptive burst
                noise.start();
                setTimeout(() => noise.stop(), 200 + Math.random() * 300);
            },
            stop: () => noise.stop()
        });
    }

    private createWaasSound() {
        // Absurd, comic timing
        const osc = new Tone.Oscillator(420, 'sine'); // 420 for absurdity
        const tremolo = new Tone.Tremolo(0.5, 1);

        osc.connect(tremolo);
        tremolo.connect(this.masterVolume);

        this.archetypeSounds.set('waas', {
            name: 'Les Waas',
            instruments: [osc],
            play: (velocity = 0.5) => {
                // Absurd timing and frequency
                osc.frequency.setValueAtTime(42 * 10, Tone.now()); // 420Hz
                osc.start();

                // Comic pause, then stop
                setTimeout(() => {
                    osc.frequency.setValueAtTime(42 * 100, Tone.now()); // 4200Hz
                }, 420); // Absurd timing

                setTimeout(() => osc.stop(), 1000);
            },
            stop: () => osc.stop()
        });
    }

    public async playArchetype(name: string, velocity = 0.8) {
        if (!this.initialized) {
            await this.initialize();
        }

        const sound = this.archetypeSounds.get(name);
        if (sound) {
            sound.play(velocity);
            return true;
        }
        return false;
    }

    public stopArchetype(name: string) {
        const sound = this.archetypeSounds.get(name);
        if (sound) {
            sound.stop();
        }
    }

    public stopAll() {
        for (const sound of this.archetypeSounds.values()) {
            sound.stop();
        }
    }

    public setMasterVolume(volume: number) {
        this.masterVolume.volume.setValueAtTime(volume, Tone.now());
    }

    public getArchetypeNames(): string[] {
        return Array.from(this.archetypeSounds.keys());
    }
}