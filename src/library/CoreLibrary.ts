import { Signal } from '../signals/SignalGrammar';

interface Archetype {
    name: string;
    layer: 'vessel' | 'emergent' | 'particles' | 'shadow';
    musicalSignature: {
        frequencies: number[];
        rhythm?: number;
        harmony?: string;
    };
    visualTriggers: {
        colors: number[];
        patterns: string[];
        movements: string[];
    };
    easterEgg: {
        triggerCondition: (signal: Signal) => boolean;
        activation: () => void;
    };
}

export class CoreLibrary {
    private archetypes: Map<string, Archetype> = new Map();
    private activeTriggers: Set<string> = new Set();
    private signalHistory: Signal[] = [];
    private maxHistoryLength = 100;

    constructor() {
        this.initializeArchetypes();
    }

    private initializeArchetypes() {
        // VESSEL LAYER ARCHETYPES
        this.archetypes.set('russell', {
            name: 'Walter Russell',
            layer: 'vessel',
            musicalSignature: {
                frequencies: [256, 384, 512], // Perfect harmonics (C, G, C octave)
                harmony: 'cosmic'
            },
            visualTriggers: {
                colors: [0x4a90e2, 0x50c878, 0xffd700], // Blue, green, gold
                patterns: ['cube-sphere', 'harmonic-geometry'],
                movements: ['cosmic-rotation', 'harmonic-pulsing']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    signal.type === 'frequency' &&
                    signal.frequency! >= 250 && signal.frequency! <= 260 &&
                    signal.amplitude! > 0.7,
                activation: () => this.activateRussellEasterEgg()
            }
        });

        this.archetypes.set('greiff', {
            name: 'Constance M. Greiff',
            layer: 'vessel',
            musicalSignature: {
                frequencies: [174, 285, 396], // Solfeggio healing frequencies
                harmony: 'cathedral'
            },
            visualTriggers: {
                colors: [0x8b4513, 0x654321, 0xa0522d], // Earth tones
                patterns: ['architectural', 'memorial'],
                movements: ['slow-decay', 'memory-fade']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    signal.type === 'silence' &&
                    signal.duration! > 3,
                activation: () => this.activateGreiffEasterEgg()
            }
        });

        this.archetypes.set('einstein', {
            name: 'Albert Einstein',
            layer: 'vessel',
            musicalSignature: {
                frequencies: [432, 528, 741], // Universal healing frequencies
                harmony: 'relativistic'
            },
            visualTriggers: {
                colors: [0xffffff, 0xe6e6fa, 0xb0c4de], // Light spectrum
                patterns: ['space-time-curvature', 'relativity'],
                movements: ['time-dilation', 'space-warp']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    this.detectRelativisticPattern(),
                activation: () => this.activateEinsteinEasterEgg()
            }
        });

        // EMERGENT FORM LAYER ARCHETYPES
        this.archetypes.set('blake', {
            name: 'William Blake',
            layer: 'emergent',
            musicalSignature: {
                frequencies: [227.43, 341.3, 455.1], // Ancient mystical frequencies
                harmony: 'visionary'
            },
            visualTriggers: {
                colors: [0x8b008b, 0x9932cc, 0xba55d3], // Mystical purples
                patterns: ['organic-flow', 'mythic-forms'],
                movements: ['mystical-morphing', 'prophetic-emergence']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    signal.type === 'frequency' &&
                    this.isBlakeFrequency(signal.frequency!),
                activation: () => this.activateBlakeEasterEgg()
            }
        });

        this.archetypes.set('tesla', {
            name: 'Nikola Tesla',
            layer: 'emergent',
            musicalSignature: {
                frequencies: [369, 639, 963], // Tesla's obsession with 3, 6, 9
                harmony: 'electrical'
            },
            visualTriggers: {
                colors: [0x00ffff, 0x0080ff, 0x4169e1], // Electric blues
                patterns: ['electrical-arc', 'resonance-field'],
                movements: ['electrical-pulse', 'resonant-vibration']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    this.detectTeslaPattern(),
                activation: () => this.activateTeslaEasterEgg()
            }
        });

        this.archetypes.set('beatles', {
            name: 'The Beatles',
            layer: 'emergent',
            musicalSignature: {
                frequencies: [440, 220, 880, 1760], // A harmonic series
                rhythm: 4, // 4/4 time
                harmony: 'collaborative'
            },
            visualTriggers: {
                colors: [0xffd700, 0xff6347, 0x32cd32, 0x1e90ff], // Psychedelic colors
                patterns: ['harmonic-convergence', 'collective-creation'],
                movements: ['synchronized-dance', 'harmonic-interplay']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    this.detectHarmonicSeries(),
                activation: () => this.activateBeatlesEasterEgg()
            }
        });

        // PARTICLE LAYER ARCHETYPES
        this.archetypes.set('leadbelly', {
            name: 'Lead Belly (Huddie Ledbetter)',
            layer: 'particles',
            musicalSignature: {
                frequencies: [82.4, 110, 146.8], // Blues scale fundamentals
                rhythm: 12, // 12-bar blues
                harmony: 'blues'
            },
            visualTriggers: {
                colors: [0x8b4513, 0x654321, 0xd2b48c], // Earth and wood tones
                patterns: ['rhythmic-burst', 'folk-pattern'],
                movements: ['stomping-rhythm', 'raw-expression']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    this.detectBluesPattern(),
                activation: () => this.activateLeadBellyEasterEgg()
            }
        });

        this.archetypes.set('hawking', {
            name: 'Stephen Hawking',
            layer: 'particles',
            musicalSignature: {
                frequencies: [20, 40, 80], // Sub-bass cosmic frequencies
                harmony: 'cosmic'
            },
            visualTriggers: {
                colors: [0x000080, 0x191970, 0x483d8b], // Deep space colors
                patterns: ['spiral-galaxy', 'black-hole'],
                movements: ['gravitational-pull', 'cosmic-radiation']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    signal.type === 'frequency' &&
                    signal.frequency! < 50,
                activation: () => this.activateHawkingEasterEgg()
            }
        });

        this.archetypes.set('pranksters', {
            name: 'The Merry Pranksters',
            layer: 'particles',
            musicalSignature: {
                frequencies: [111, 222, 333, 444, 555, 666, 777], // Chaotic sequence
                harmony: 'kaleidoscopic'
            },
            visualTriggers: {
                colors: [0xff69b4, 0x00ff00, 0xff0000, 0x00ffff, 0xffff00], // Vibrant chaos
                patterns: ['kaleidoscope', 'chaotic-burst'],
                movements: ['unpredictable-chaos', 'psychedelic-swirl']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    this.detectChaoticPattern(),
                activation: () => this.activatePrankstersEasterEgg()
            }
        });

        // SHADOW LAYER ARCHETYPES
        this.archetypes.set('hoffman', {
            name: 'Abbie Hoffman',
            layer: 'shadow',
            musicalSignature: {
                frequencies: [66.6, 133.2, 199.8], // Rebellious dissonance
                harmony: 'disruptive'
            },
            visualTriggers: {
                colors: [0x000000, 0xff0000, 0xffffff], // Stark contrast
                patterns: ['inversion', 'disruption'],
                movements: ['chaotic-rebellion', 'trickster-flip']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    this.detectRebellionPattern(),
                activation: () => this.activateHoffmanEasterEgg()
            }
        });

        this.archetypes.set('waas', {
            name: 'Les Waas',
            layer: 'shadow',
            musicalSignature: {
                frequencies: [42, 420, 4200], // Absurd number play
                harmony: 'absurd'
            },
            visualTriggers: {
                colors: [0xff69b4, 0x00ff00, 0xffff00], // Silly colors
                patterns: ['absurd-geometry', 'comic-timing'],
                movements: ['delayed-reaction', 'absurd-pause']
            },
            easterEgg: {
                triggerCondition: (signal) =>
                    this.detectAbsurdPattern(),
                activation: () => this.activateWaasEasterEgg()
            }
        });
    }

    public checkForTriggers(signal: Signal) {
        // Add signal to history
        this.signalHistory.push(signal);
        if (this.signalHistory.length > this.maxHistoryLength) {
            this.signalHistory.shift();
        }

        // Check each archetype for trigger conditions
        for (const [key, archetype] of this.archetypes) {
            if (archetype.easterEgg.triggerCondition(signal)) {
                if (!this.activeTriggers.has(key)) {
                    this.activeTriggers.add(key);
                    archetype.easterEgg.activation();

                    // Auto-remove trigger after activation
                    setTimeout(() => {
                        this.activeTriggers.delete(key);
                    }, 5000);
                }
            }
        }
    }

    public triggerArchetype(name: string) {
        const archetype = this.archetypes.get(name);
        if (archetype) {
            archetype.easterEgg.activation();
        }
    }

    // Pattern Detection Methods
    private detectRelativisticPattern(): boolean {
        // Look for time-dilation effects in signal timing
        if (this.signalHistory.length < 3) return false;

        const recent = this.signalHistory.slice(-3);
        const timeDeltas = [];

        for (let i = 1; i < recent.length; i++) {
            // Simulate time measurement between signals
            timeDeltas.push(Math.random()); // Placeholder for actual timing
        }

        // Check for accelerating or decelerating patterns
        return timeDeltas.every((delta, i) => i === 0 || delta > timeDeltas[i - 1] * 1.1);
    }

    private isBlakeFrequency(frequency: number): boolean {
        const blakeFreqs = [227.43, 341.3, 455.1];
        return blakeFreqs.some(freq => Math.abs(frequency - freq) < 10);
    }

    private detectTeslaPattern(): boolean {
        // Look for 3-6-9 pattern in frequencies
        const recentFreqs = this.signalHistory
            .filter(s => s.type === 'frequency')
            .slice(-6)
            .map(s => s.frequency!);

        return recentFreqs.some(freq =>
            freq % 3 === 0 || freq % 6 === 0 || freq % 9 === 0
        );
    }

    private detectHarmonicSeries(): boolean {
        const recentFreqs = this.signalHistory
            .filter(s => s.type === 'frequency')
            .slice(-4)
            .map(s => s.frequency!);

        if (recentFreqs.length < 4) return false;

        // Check for harmonic relationships
        const fundamental = recentFreqs[0];
        return recentFreqs.every((freq, i) =>
            Math.abs(freq - fundamental * (i + 1)) < 20
        );
    }

    private detectBluesPattern(): boolean {
        // Look for 12-bar blues rhythm pattern
        const recentBeats = this.signalHistory
            .filter(s => s.type === 'beat')
            .slice(-12);

        return recentBeats.length >= 8; // Sufficient rhythm activity
    }

    private detectChaoticPattern(): boolean {
        // Random chaos trigger
        return Math.random() < 0.01; // 1% chance on any signal
    }

    private detectRebellionPattern(): boolean {
        // Detect sudden amplitude spikes (disruption)
        const recent = this.signalHistory
            .filter(s => s.amplitude !== undefined)
            .slice(-5);

        return recent.some(s => s.amplitude! > 0.9);
    }

    private detectAbsurdPattern(): boolean {
        // Detect unusual timing or absurd number coincidences
        return this.signalHistory.length % 42 === 0; // Absurd timing
    }

    // Easter Egg Activation Methods
    private activateRussellEasterEgg() {
        console.log('🔮 Walter Russell Easter Egg: "The universe is not composed of matter, but of rhythmic patterns of energy."');
        // Trigger cosmic geometry visualization
        document.dispatchEvent(new CustomEvent('russell-easter-egg'));
    }

    private activateGreiffEasterEgg() {
        console.log('🏛️ Constance Greiff Easter Egg: "Architecture is the memory of the human spirit."');
        document.dispatchEvent(new CustomEvent('greiff-easter-egg'));
    }

    private activateEinsteinEasterEgg() {
        console.log('⚡ Einstein Easter Egg: "Everything is vibration, everything is music."');
        document.dispatchEvent(new CustomEvent('einstein-easter-egg'));
    }

    private activateBlakeEasterEgg() {
        console.log('✨ William Blake Easter Egg: "To see a World in a Grain of Sand..."');
        document.dispatchEvent(new CustomEvent('blake-easter-egg'));
    }

    private activateTeslaEasterEgg() {
        console.log('⚡ Tesla Easter Egg: "If you want to find the secrets of the universe, think in terms of energy, frequency, and vibration."');
        document.dispatchEvent(new CustomEvent('tesla-easter-egg'));
    }

    private activateBeatlesEasterEgg() {
        console.log('🎵 Beatles Easter Egg: "Here comes the sun, doo-doo-doo-doo..."');
        document.dispatchEvent(new CustomEvent('beatles-easter-egg'));
    }

    private activateLeadBellyEasterEgg() {
        console.log('🎸 Lead Belly Easter Egg: "Goodnight Irene, goodnight..."');
        document.dispatchEvent(new CustomEvent('leadbelly-easter-egg'));
    }

    private activateHawkingEasterEgg() {
        console.log('🌌 Stephen Hawking Easter Egg: "We are just an advanced breed of monkeys on a minor planet of a very average star."');
        document.dispatchEvent(new CustomEvent('hawking-easter-egg'));
    }

    private activatePrankstersEasterEgg() {
        console.log('🎨 Merry Pranksters Easter Egg: "You\'re either on the bus or off the bus."');
        document.dispatchEvent(new CustomEvent('pranksters-easter-egg'));
    }

    private activateHoffmanEasterEgg() {
        console.log('✊ Abbie Hoffman Easter Egg: "Revolution for the hell of it!"');
        document.dispatchEvent(new CustomEvent('hoffman-easter-egg'));
    }

    private activateWaasEasterEgg() {
        console.log('😄 Les Waas Easter Egg: "We shall never finish our task of procrastination."');
        document.dispatchEvent(new CustomEvent('waas-easter-egg'));
    }

    public getArchetype(name: string): Archetype | undefined {
        return this.archetypes.get(name);
    }

    public getAllArchetypes(): Archetype[] {
        return Array.from(this.archetypes.values());
    }

    public getActiveEasterEggs(): string[] {
        return Array.from(this.activeTriggers);
    }
}