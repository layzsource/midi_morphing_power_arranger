/**
 * Particle Physics-Based Signal Encoding System
 * Uses quantum mechanics metaphors for audiovisual signal processing
 */

export interface PhysicsProperties {
    chirality: 'left' | 'right';           // Handedness - rotation direction
    helicity: 'parallel' | 'antiparallel'; // Spin relative to momentum
    charge: number;                         // -1 to +1, affects brightness/size
    flavor: 'up' | 'down' | 'strange' | 'charm' | 'top' | 'bottom';
    spin: number;                          // Angular momentum (rotation speed)
    polarization: number;                  // 0-360 degrees, circular polarization angle
}

export interface SignalClassification {
    category: number;     // Dewey decimal main class (100s, 200s, etc.)
    subcategory: number;  // Secondary classification
    frequency: number;    // Hz for Hindu form resonance
    amplitude: number;    // Signal strength
    temporal: number;     // Time-based encoding
}

export class ParticlePhysicsEncoder {
    private yantraLibrary: Map<string, any> = new Map();
    private resonanceFrequencies: Map<number, string> = new Map();

    constructor() {
        this.initializeYantraLibrary();
        this.initializeResonanceMap();
    }

    /**
     * Convert audio signal to physics properties
     */
    public encodeSignal(signal: any): PhysicsProperties {
        const frequency = signal.frequency || 440;
        const amplitude = signal.amplitude || 0.5;
        const phase = signal.phase || 0;

        return {
            chirality: frequency > 500 ? 'right' : 'left',
            helicity: amplitude > 0.5 ? 'parallel' : 'antiparallel',
            charge: (amplitude - 0.5) * 2, // -1 to +1
            flavor: this.getQuarkFlavor(frequency),
            spin: frequency / 100, // Rotation speed from frequency
            polarization: (phase % (2 * Math.PI)) * (180 / Math.PI)
        };
    }

    /**
     * Classify signals using Dewey decimal system
     */
    public classifySignal(signal: any): SignalClassification {
        const frequency = signal.frequency || 440;
        const amplitude = signal.amplitude || 0.5;
        const type = signal.type || 'audio';

        let category = 100; // Default frequency-based

        if (type === 'midi') category = 200;
        else if (type === 'archetype') category = 300;
        else if (type === 'user') category = 400;
        else if (type === 'temporal') category = 500;

        return {
            category,
            subcategory: Math.floor(frequency / 100) * 10,
            frequency,
            amplitude,
            temporal: Date.now()
        };
    }

    /**
     * Map frequency to quark flavor for geometric complexity
     */
    private getQuarkFlavor(frequency: number): PhysicsProperties['flavor'] {
        if (frequency < 200) return 'down';      // Simple forms
        if (frequency < 400) return 'up';        // Basic forms
        if (frequency < 600) return 'strange';   // Complex geometries
        if (frequency < 800) return 'charm';     // Sacred geometries
        if (frequency < 1000) return 'bottom';   // Archetypal forms
        return 'top';                            // Transcendent forms
    }

    /**
     * Hindu form resonance mapping
     */
    private initializeResonanceMap() {
        this.resonanceFrequencies.set(256, 'sri_yantra');
        this.resonanceFrequencies.set(432, 'om_symbol');
        this.resonanceFrequencies.set(528, 'flower_of_life');
        this.resonanceFrequencies.set(741, 'merkaba');
        this.resonanceFrequencies.set(852, 'seed_of_life');
    }

    /**
     * Get yantra pattern for frequency
     */
    public getYantraPattern(frequency: number): string {
        // Find closest resonance frequency
        let closest = 256;
        let minDiff = Math.abs(frequency - 256);

        for (const [freq, pattern] of this.resonanceFrequencies) {
            const diff = Math.abs(frequency - freq);
            if (diff < minDiff) {
                minDiff = diff;
                closest = freq;
            }
        }

        return this.resonanceFrequencies.get(closest) || 'basic_circle';
    }

    /**
     * Create circularly polarized light parameters
     */
    public generatePolarizedLight(properties: PhysicsProperties) {
        return {
            rotationDirection: properties.chirality === 'left' ? -1 : 1,
            rotationSpeed: properties.spin,
            intensity: Math.abs(properties.charge),
            phase: properties.polarization,
            helicity: properties.helicity === 'parallel' ? 1 : -1
        };
    }

    /**
     * Prevent recursive noise through structured decay
     */
    public applyDecayPattern(sprite: any, age: number): any {
        const halfLife = 2.0; // 2 seconds
        const decayFactor = Math.exp(-age / halfLife);

        return {
            ...sprite,
            intensity: sprite.intensity * decayFactor,
            coherence: decayFactor > 0.5 ? 'strong' : decayFactor > 0.1 ? 'weak' : 'lepton',
            stability: decayFactor
        };
    }

    private initializeYantraLibrary() {
        // Initialize sacred geometry patterns
        // Will be expanded with actual geometric definitions
        this.yantraLibrary.set('sri_yantra', { type: 'complex_triangle_grid' });
        this.yantraLibrary.set('om_symbol', { type: 'curved_sacred_form' });
        this.yantraLibrary.set('flower_of_life', { type: 'overlapping_circles' });
    }
}