/**
 * Simplified Fluid Dynamics for Sonoluminescence Simulation
 * Focuses on cavitation, pressure fields, and sprite emission triggers
 */

export interface FluidState {
    pressure: number;        // 0-1, drives cavitation
    viscosity: number;       // 0-1, affects particle movement
    temperature: number;     // 0-1, affects bubble behavior
    density: number;         // 0-1, fluid thickness
    flowVelocity: { x: number, y: number, z: number };
}

export interface CavitationBubble {
    position: { x: number, y: number, z: number };
    radius: number;
    pressure: number;
    age: number;
    collapseThreshold: number;
    maxRadius: number;
}

export class FluidDynamics {
    private fluidState: FluidState;
    private cavitationBubbles: CavitationBubble[] = [];
    private cavitationThreshold = 0.7;  // Pressure needed to form bubbles
    private acousticField: number[][] = []; // 3D pressure grid

    constructor() {
        this.fluidState = {
            pressure: 0.5,
            viscosity: 0.3,
            temperature: 0.5,
            density: 0.5,
            flowVelocity: { x: 0, y: 0, z: 0 }
        };
        this.initializeAcousticField();
    }

    /**
     * Update fluid state based on audio signal
     */
    public updateFromAudioSignal(signal: any) {
        const frequency = signal.frequency || 440;
        const amplitude = signal.amplitude || 0.5;
        const phase = signal.phase || 0;

        // Audio pressure → fluid pressure
        this.fluidState.pressure = amplitude;

        // Frequency affects fluid properties
        this.fluidState.viscosity = Math.max(0.1, 1 - (frequency / 1000));
        this.fluidState.temperature = frequency / 1000;

        // Create acoustic pressure waves
        this.propagateAcousticWave(frequency, amplitude, phase);

        // Check for cavitation conditions
        if (this.fluidState.pressure > this.cavitationThreshold) {
            this.createCavitationBubble(amplitude, frequency);
        }
    }

    /**
     * Create cavitation bubble when pressure threshold exceeded
     */
    private createCavitationBubble(amplitude: number, frequency: number) {
        // Limit bubble creation rate
        if (this.cavitationBubbles.length > 10) return;

        const bubble: CavitationBubble = {
            position: {
                x: (Math.random() - 0.5) * 0.5, // Near heart center
                y: (Math.random() - 0.5) * 0.5,
                z: (Math.random() - 0.5) * 0.5
            },
            radius: 0.01, // Start small
            pressure: amplitude,
            age: 0,
            collapseThreshold: 0.05 + amplitude * 0.1, // Higher amplitude = larger bubble
            maxRadius: 0.02 + amplitude * 0.08
        };

        this.cavitationBubbles.push(bubble);
    }

    /**
     * Update cavitation bubbles and detect collapse events
     */
    public updateCavitation(deltaTime: number): CavitationBubble[] {
        const collapsedBubbles: CavitationBubble[] = [];

        for (let i = this.cavitationBubbles.length - 1; i >= 0; i--) {
            const bubble = this.cavitationBubbles[i];
            bubble.age += deltaTime;

            // Bubble expansion phase (first 40% of life)
            if (bubble.age < 0.2) {
                const expansionRate = bubble.pressure * 5;
                bubble.radius = Math.min(bubble.maxRadius, bubble.radius + expansionRate * deltaTime);
            }
            // Bubble collapse phase
            else {
                const collapseRate = bubble.pressure * 10;
                bubble.radius = Math.max(0, bubble.radius - collapseRate * deltaTime);

                // Bubble has collapsed - sonoluminescence event!
                if (bubble.radius <= 0.001) {
                    collapsedBubbles.push(bubble);
                    this.cavitationBubbles.splice(i, 1);
                }
            }

            // Remove old bubbles
            if (bubble.age > 1.0) {
                this.cavitationBubbles.splice(i, 1);
            }
        }

        return collapsedBubbles;
    }

    /**
     * Get fluid force at position (affects particle movement)
     */
    public getFluidForceAt(position: { x: number, y: number, z: number }): { x: number, y: number, z: number } {
        const viscosityDamping = 1 - this.fluidState.viscosity;
        const pressureGradient = this.getPressureGradientAt(position);

        return {
            x: pressureGradient.x * viscosityDamping + this.fluidState.flowVelocity.x * 0.1,
            y: pressureGradient.y * viscosityDamping + this.fluidState.flowVelocity.y * 0.1,
            z: pressureGradient.z * viscosityDamping + this.fluidState.flowVelocity.z * 0.1
        };
    }

    /**
     * Create acoustic pressure wave propagation
     */
    private propagateAcousticWave(frequency: number, amplitude: number, phase: number) {
        const waveSpeed = 343; // m/s (simplified)
        const wavelength = waveSpeed / frequency;

        // Update flow velocity based on acoustic wave
        this.fluidState.flowVelocity = {
            x: Math.sin(phase) * amplitude * 0.1,
            y: Math.cos(phase) * amplitude * 0.1,
            z: Math.sin(phase + Math.PI/2) * amplitude * 0.05
        };
    }

    /**
     * Get pressure gradient for particle forces
     */
    private getPressureGradientAt(position: { x: number, y: number, z: number }): { x: number, y: number, z: number } {
        // Simplified pressure field - pressure decreases with distance from center
        const distance = Math.sqrt(position.x ** 2 + position.y ** 2 + position.z ** 2);
        const pressureForce = (this.fluidState.pressure - 0.5) / Math.max(distance, 0.1);

        return {
            x: -position.x * pressureForce * 0.1,
            y: -position.y * pressureForce * 0.1,
            z: -position.z * pressureForce * 0.1
        };
    }

    /**
     * Initialize 3D acoustic pressure field
     */
    private initializeAcousticField() {
        // Simple 10x10x10 grid for pressure calculations
        this.acousticField = Array(10).fill(null).map(() =>
            Array(10).fill(null).map(() =>
                Array(10).fill(0.5)
            )
        );
    }

    /**
     * Get current fluid state for encoding
     */
    public getFluidState(): FluidState {
        return { ...this.fluidState };
    }

    /**
     * Get active cavitation bubbles for visualization
     */
    public getActiveBubbles(): CavitationBubble[] {
        return [...this.cavitationBubbles];
    }

    /**
     * Check if conditions are right for sonoluminescence
     */
    public isSonoluminescenceActive(): boolean {
        return this.fluidState.pressure > this.cavitationThreshold &&
               this.cavitationBubbles.length > 0;
    }

    /**
     * Reset fluid state
     */
    public reset() {
        this.fluidState = {
            pressure: 0.5,
            viscosity: 0.3,
            temperature: 0.5,
            density: 0.5,
            flowVelocity: { x: 0, y: 0, z: 0 }
        };
        this.cavitationBubbles = [];
    }

    /**
     * Update fluid dynamics simulation over time
     */
    public update(deltaTime: number) {
        // Update cavitation bubbles
        this.updateCavitation(deltaTime);

        // Apply fluid decay over time
        this.fluidState.pressure *= 0.99;
        this.fluidState.temperature *= 0.995;

        // Gentle flow velocity decay
        this.fluidState.flowVelocity.x *= 0.98;
        this.fluidState.flowVelocity.y *= 0.98;
        this.fluidState.flowVelocity.z *= 0.98;
    }
}