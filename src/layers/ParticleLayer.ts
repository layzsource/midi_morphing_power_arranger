import * as THREE from 'three';

export class ParticleLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private particleSystem: THREE.Points;
    private particles: THREE.BufferGeometry;
    private particleMaterial: THREE.PointsMaterial;
    private intensity = 0.7;
    private particleCount = 1000;
    private velocities: Float32Array;
    private lifetimes: Float32Array;
    private emissionRate = 1.0;
    private geometricAlignment = 1.0;

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.initParticles();
    }

    private initParticles() {
        this.particles = new THREE.BufferGeometry();

        // Create particle positions
        const positions = new Float32Array(this.particleCount * 3);
        this.velocities = new Float32Array(this.particleCount * 3);
        this.lifetimes = new Float32Array(this.particleCount);

        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;

            // 2026+ Quantum probability field distribution
            const quantumState = Math.random();
            const radius = 2 + Math.pow(Math.random(), 0.4) * 3; // Non-linear quantum distribution
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;

            // Quantum uncertainty principle
            const uncertainty = (Math.random() - 0.5) * 0.15;

            positions[i3] = radius * Math.sin(phi) * Math.cos(theta) + uncertainty;
            positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta) + uncertainty;
            positions[i3 + 2] = radius * Math.cos(phi) + uncertainty;

            // Random velocities
            this.velocities[i3] = (Math.random() - 0.5) * 0.02;
            this.velocities[i3 + 1] = (Math.random() - 0.5) * 0.02;
            this.velocities[i3 + 2] = (Math.random() - 0.5) * 0.02;

            // Random lifetimes
            this.lifetimes[i] = Math.random() * 100;
        }

        this.particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        // 2025 volumetric particle material
        this.particleMaterial = new THREE.PointsMaterial({
            color: 0xa78bfa,
            size: 0.008,
            transparent: true,
            opacity: 0.95,
            blending: THREE.AdditiveBlending,
            vertexColors: false,
            sizeAttenuation: true,
            alphaTest: 0.0001,
            depthWrite: false
        });

        this.particleSystem = new THREE.Points(this.particles, this.particleMaterial);
        this.group.add(this.particleSystem);

        // Particles exist within and around all other layers
        this.group.position.set(0, 0, 0);
    }

    public processMIDI(signal: any) {
        // MIDI CC controls particle behavior
        const ccValue = signal.value / 127; // Normalize MIDI CC value

        switch (signal.cc) {
            case 1: // Modulation wheel - affects particle speed
                this.adjustParticleSpeed(ccValue);
                break;
            case 7: // Volume - affects particle count visibility
                this.particleMaterial.opacity = ccValue;
                break;
            case 10: // Pan - affects particle spread
                this.adjustParticleSpread(ccValue);
                break;
        }
    }

    public processBeat(signal: any) {
        // Beat triggers particle bursts
        const intensity = signal.intensity || 0.5;
        this.createBeatBurst(intensity);
    }

    private adjustParticleSpeed(speed: number) {
        // Adjust velocity based on speed input
        const positions = this.particles.attributes.position.array as Float32Array;

        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;
            this.velocities[i3] *= speed * 2;
            this.velocities[i3 + 1] *= speed * 2;
            this.velocities[i3 + 2] *= speed * 2;
        }
    }

    private adjustParticleSpread(spread: number) {
        // Adjust particle distribution
        this.particleMaterial.size = 0.05 + spread * 0.15;
    }

    private createBeatBurst(intensity: number) {
        // Create explosive particle movement on beat
        const positions = this.particles.attributes.position.array as Float32Array;

        // Make the beat effect much more dramatic and visible
        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;

            // Add radial velocity burst
            const x = positions[i3];
            const y = positions[i3 + 1];
            const z = positions[i3 + 2];

            const distance = Math.sqrt(x * x + y * y + z * z);
            if (distance > 0) {
                const burstStrength = intensity * 0.2; // Much stronger burst
                this.velocities[i3] += (x / distance) * burstStrength;
                this.velocities[i3 + 1] += (y / distance) * burstStrength;
                this.velocities[i3 + 2] += (z / distance) * burstStrength;
            }
        }

        // Add color flash effect
        this.particleMaterial.color.setHSL(Math.random(), 1.0, 0.8);
        this.particleMaterial.size = 0.3; // Bigger particles on beat

        // Reset after short duration
        setTimeout(() => {
            this.particleMaterial.color.setHex(0xffffff);
            this.particleMaterial.size = 0.1;
        }, 200);

        // Flash effect
        this.particleMaterial.color.setHSL(Math.random(), 0.8, 0.6);
    }

    // Core Library archetype triggers
    public triggerLeadBellyPattern() {
        // Blues rhythm particle pattern
        this.particleMaterial.color.setHex(0x8b4513); // Brown/earth tones
        this.createRhythmicPattern(4/4); // 4/4 blues pattern
    }

    public triggerHawkingPattern() {
        // Cosmic, black hole-inspired particles
        this.particleMaterial.color.setHex(0x000080); // Deep space blue
        this.createSpiralPattern();
    }

    public triggerPrankstersPattern() {
        // Chaotic, kaleidoscopic particles
        this.createKaleidoscopePattern();
    }

    private createRhythmicPattern(rhythm: number) {
        // Create rhythmic particle emissions
        const positions = this.particles.attributes.position.array as Float32Array;

        for (let i = 0; i < this.particleCount; i += Math.floor(this.particleCount / rhythm)) {
            const i3 = i * 3;
            this.velocities[i3] *= 2;
            this.velocities[i3 + 1] *= 2;
            this.velocities[i3 + 2] *= 2;
        }
    }

    private createSpiralPattern() {
        // Create spiral galaxy-like motion
        const positions = this.particles.attributes.position.array as Float32Array;

        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;
            const angle = i / this.particleCount * Math.PI * 2;

            this.velocities[i3] = Math.cos(angle) * 0.02;
            this.velocities[i3 + 1] = Math.sin(angle) * 0.01;
            this.velocities[i3 + 2] = Math.sin(angle) * 0.02;
        }
    }

    private createKaleidoscopePattern() {
        // Chaotic, colorful particle behavior
        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;
            this.velocities[i3] = (Math.random() - 0.5) * 0.1;
            this.velocities[i3 + 1] = (Math.random() - 0.5) * 0.1;
            this.velocities[i3 + 2] = (Math.random() - 0.5) * 0.1;
        }

        // Rapid color cycling
        this.particleMaterial.color.setHSL(Math.random(), 1, 0.5);
    }

    public setIntensity(intensity: number) {
        this.intensity = intensity;
        this.particleMaterial.opacity = 0.8 * intensity;
        this.particleMaterial.size = 0.1 * (0.5 + intensity);
    }

    public update(deltaTime: number, elapsedTime: number) {
        const positions = this.particles.attributes.position.array as Float32Array;

        // Update particle positions and lifetimes
        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;

            // Update positions
            positions[i3] += this.velocities[i3] * this.intensity;
            positions[i3 + 1] += this.velocities[i3 + 1] * this.intensity;
            positions[i3 + 2] += this.velocities[i3 + 2] * this.intensity;

            // Update lifetimes
            this.lifetimes[i] -= deltaTime * 10;

            // Reset particles that have died
            if (this.lifetimes[i] <= 0) {
                // Reset to center with random offset
                positions[i3] = (Math.random() - 0.5) * 2;
                positions[i3 + 1] = (Math.random() - 0.5) * 2;
                positions[i3 + 2] = (Math.random() - 0.5) * 2;

                // Reset velocity
                this.velocities[i3] = (Math.random() - 0.5) * 0.02;
                this.velocities[i3 + 1] = (Math.random() - 0.5) * 0.02;
                this.velocities[i3 + 2] = (Math.random() - 0.5) * 0.02;

                // Reset lifetime
                this.lifetimes[i] = Math.random() * 100;
            }

            // Apply gravity/attraction to center
            const centerAttraction = 0.0001 * this.intensity;
            positions[i3] *= (1 - centerAttraction);
            positions[i3 + 1] *= (1 - centerAttraction);
            positions[i3 + 2] *= (1 - centerAttraction);
        }

        this.particles.attributes.position.needsUpdate = true;

        // Rotate particle system
        this.group.rotation.y += deltaTime * 0.1 * this.intensity;

        // Color evolution
        const hue = (elapsedTime * 0.2) % 1;
        this.particleMaterial.color.setHSL(hue, 0.6, 0.5);
    }

    public reset() {
        this.group.rotation.set(0, 0, 0);
        this.particleMaterial.color.setHex(0xffffff);

        // Reset all particles to center
        const positions = this.particles.attributes.position.array as Float32Array;
        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;
            positions[i3] = (Math.random() - 0.5) * 2;
            positions[i3 + 1] = (Math.random() - 0.5) * 2;
            positions[i3 + 2] = (Math.random() - 0.5) * 2;
            this.lifetimes[i] = Math.random() * 100;
        }
        this.particles.attributes.position.needsUpdate = true;
    }

    // Conversation system methods
    public getCurrentIntensity(): number {
        return this.intensity;
    }

    public getCurrentEmissionRate(): number {
        return this.emissionRate;
    }

    public setEmissionRate(rate: number) {
        this.emissionRate = rate;
        this.particleMaterial.size = 2 * rate; // Larger particles with higher emission
    }

    public setGeometricAlignment(alignment: number) {
        this.geometricAlignment = alignment;

        // Apply geometric order to particle positions
        const positions = this.particles.attributes.position.array as Float32Array;
        if (alignment > 1.5) {
            // High alignment - create geometric patterns
            for (let i = 0; i < this.particleCount; i++) {
                const i3 = i * 3;
                const angle = (i / this.particleCount) * Math.PI * 2;
                const radius = 2 + Math.sin(angle * 3) * 0.5;

                positions[i3] = Math.cos(angle) * radius;
                positions[i3 + 1] = Math.sin(angle) * radius;
                positions[i3 + 2] = Math.sin(angle * 2) * 0.5;
            }
            this.particles.attributes.position.needsUpdate = true;
        }
    }

    public createComplementaryPattern(trigger: string, response: string) {
        // Create visual pattern based on archetype relationship
        const positions = this.particles.attributes.position.array as Float32Array;

        // Different patterns for different archetype pairs
        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;
            const t = i / this.particleCount;

            if (trigger === 'russell' && response === 'blake') {
                // Sacred geometry meets mysticism - spiral pattern
                const angle = t * Math.PI * 8;
                const radius = t * 3;
                positions[i3] = Math.cos(angle) * radius;
                positions[i3 + 1] = Math.sin(angle) * radius;
                positions[i3 + 2] = Math.sin(t * Math.PI * 4) * 2;
            } else if (trigger === 'tesla' && response === 'einstein') {
                // Electricity meets relativity - wave interference
                const wave1 = Math.sin(t * Math.PI * 6) * 2;
                const wave2 = Math.sin(t * Math.PI * 9) * 1.5;
                positions[i3] = t * 4 - 2;
                positions[i3 + 1] = wave1 + wave2;
                positions[i3 + 2] = wave1 - wave2;
            } else {
                // Default complementary pattern
                const angle = t * Math.PI * 4;
                positions[i3] = Math.cos(angle) * 2;
                positions[i3 + 1] = Math.sin(angle) * 2;
                positions[i3 + 2] = Math.sin(t * Math.PI * 2) * 1;
            }
        }

        this.particles.attributes.position.needsUpdate = true;
        this.particleMaterial.color.setHSL(0.6, 0.8, 0.7); // Complementary color
    }

    public triggerChaos() {
        // Create chaotic particle behavior
        this.emissionRate = 3.0; // High emission
        this.particleMaterial.size = 4;
        this.particleMaterial.color.setHSL(0.0, 1.0, 0.6); // Chaotic red

        // Randomize all particle positions and velocities
        const positions = this.particles.attributes.position.array as Float32Array;
        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;
            positions[i3] = (Math.random() - 0.5) * 10;
            positions[i3 + 1] = (Math.random() - 0.5) * 10;
            positions[i3 + 2] = (Math.random() - 0.5) * 10;

            // Chaotic velocities
            this.velocities[i3] = (Math.random() - 0.5) * 0.2;
            this.velocities[i3 + 1] = (Math.random() - 0.5) * 0.2;
            this.velocities[i3 + 2] = (Math.random() - 0.5) * 0.2;
        }

        this.particles.attributes.position.needsUpdate = true;
    }
}