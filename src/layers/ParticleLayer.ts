import * as THREE from 'three';

export class ParticleLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private particleSystem: THREE.Points;
    private particles: THREE.BufferGeometry;
    private particleMaterial: THREE.PointsMaterial;
    private intensity = 0.7;
    private particleCount = 3500; // Increased for more density
    private velocities: Float32Array;
    private lifetimes: Float32Array;
    private colors: Float32Array;
    private sizes: Float32Array;
    private emissionRate = 1.0;
    private geometricAlignment = 1.0;
    private morphState = 'sphere';
    private morphProgress = 0.0;
    private isMorphing = false;

    // Professional burst parameters
    private burstClock = 0;
    private burstPhase = 0;
    private nucleationPoints: THREE.Vector3[] = [];

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.initProfessionalParticles();
    }

    private initProfessionalParticles() {
        this.particles = new THREE.BufferGeometry();

        // Enhanced particle data arrays
        const positions = new Float32Array(this.particleCount * 3);
        this.velocities = new Float32Array(this.particleCount * 3);
        this.lifetimes = new Float32Array(this.particleCount);
        this.colors = new Float32Array(this.particleCount * 3);
        this.sizes = new Float32Array(this.particleCount);

        // Initialize nucleation points for sophisticated burst patterns
        this.createNucleationPoints();

        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;

            // Initial spherical distribution with fibonacci spiral perfection
            const goldenAngle = Math.PI * (3 - Math.sqrt(5));
            const y = 1 - (i / (this.particleCount - 1)) * 2;
            const radius = Math.sqrt(1 - y * y);
            const theta = goldenAngle * i;

            const sphereRadius = 0.8;
            positions[i3] = Math.cos(theta) * radius * sphereRadius;
            positions[i3 + 1] = y * sphereRadius;
            positions[i3 + 2] = Math.sin(theta) * radius * sphereRadius;

            // Professional fluid dynamics velocities
            this.velocities[i3] = 0;
            this.velocities[i3 + 1] = 0;
            this.velocities[i3 + 2] = 0;

            // Varied lifetimes for organic feel
            this.lifetimes[i] = 50 + Math.random() * 100;

            // Professional color gradients
            const hue = (i / this.particleCount) * 0.6 + 0.15; // Blue to purple range
            const color = new THREE.Color().setHSL(hue, 0.8, 0.6);
            this.colors[i3] = color.r;
            this.colors[i3 + 1] = color.g;
            this.colors[i3 + 2] = color.b;

            // Size variation for depth
            this.sizes[i] = 0.8 + Math.random() * 0.4;
        }

        this.particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        this.particles.setAttribute('color', new THREE.BufferAttribute(this.colors, 3));
        this.particles.setAttribute('size', new THREE.BufferAttribute(this.sizes, 1));

        // Professional 2025 material with industry-standard properties
        this.particleMaterial = new THREE.PointsMaterial({
            size: 0.015,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending,
            vertexColors: true,
            sizeAttenuation: true,
            alphaTest: 0.001,
            depthWrite: false,
            map: this.createParticleTexture()
        });

        this.particleSystem = new THREE.Points(this.particles, this.particleMaterial);
        this.group.add(this.particleSystem);
    }

    private createParticleTexture(): THREE.Texture {
        // Create a professional circular particle texture with soft edges
        const canvas = document.createElement('canvas');
        canvas.width = 64;
        canvas.height = 64;
        const ctx = canvas.getContext('2d')!;

        const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.3, 'rgba(255, 255, 255, 0.8)');
        gradient.addColorStop(0.7, 'rgba(255, 255, 255, 0.3)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 64, 64);

        const texture = new THREE.CanvasTexture(canvas);
        texture.generateMipmaps = false;
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;
        return texture;
    }

    private createNucleationPoints() {
        // Create strategic nucleation points for burst patterns
        this.nucleationPoints = [
            new THREE.Vector3(0, 0, 0), // Center
            new THREE.Vector3(1, 0, 0),
            new THREE.Vector3(-1, 0, 0),
            new THREE.Vector3(0, 1, 0),
            new THREE.Vector3(0, -1, 0),
            new THREE.Vector3(0, 0, 1),
            new THREE.Vector3(0, 0, -1)
        ];
    }

    public processMIDI(signal: any) {
        const ccValue = signal.value / 127;

        switch (signal.cc) {
            case 1: // Modulation - burst intensity
                this.createProfessionalBurst(ccValue * 2);
                break;
            case 7: // Volume - overall visibility
                this.particleMaterial.opacity = 0.4 + ccValue * 0.6;
                break;
            case 10: // Pan - spread factor
                this.adjustParticleSpread(ccValue);
                break;
        }
    }

    public processBeat(signal: any) {
        const intensity = signal.intensity || 0.5;
        this.createProfessionalBurst(intensity);

        // Color burst synchronization
        this.updateBurstColors(intensity);
    }

    private createProfessionalBurst(intensity: number) {
        const positions = this.particles.attributes.position.array as Float32Array;
        const colors = this.particles.attributes.color.array as Float32Array;
        const sizes = this.particles.attributes.size.array as Float32Array;

        // Professional burst algorithm with nucleation physics
        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;

            // Find nearest nucleation point
            const currentPos = new THREE.Vector3(positions[i3], positions[i3 + 1], positions[i3 + 2]);
            let nearestNucleus = this.nucleationPoints[0];
            let minDistance = currentPos.distanceTo(nearestNucleus);

            for (const nucleus of this.nucleationPoints) {
                const distance = currentPos.distanceTo(nucleus);
                if (distance < minDistance) {
                    minDistance = distance;
                    nearestNucleus = nucleus;
                }
            }

            // Calculate burst vector from nucleus
            const burstVector = currentPos.clone().sub(nearestNucleus).normalize();
            const burstStrength = intensity * (1 - minDistance / 3) * 0.15;

            // Apply professional fluid dynamics burst
            this.velocities[i3] += burstVector.x * burstStrength;
            this.velocities[i3 + 1] += burstVector.y * burstStrength;
            this.velocities[i3 + 2] += burstVector.z * burstStrength;

            // Size burst effect
            sizes[i] = (0.8 + Math.random() * 0.4) * (1 + intensity * 0.5);

            // Professional color burst with hue shifting
            const burstHue = (this.burstPhase + i / this.particleCount * 0.1) % 1;
            const color = new THREE.Color().setHSL(burstHue, 0.9, 0.5 + intensity * 0.3);
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
        }

        this.particles.attributes.color.needsUpdate = true;
        this.particles.attributes.size.needsUpdate = true;
        this.burstPhase = (this.burstPhase + 0.05) % 1;
    }

    private updateBurstColors(intensity: number) {
        const colors = this.particles.attributes.color.array as Float32Array;

        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;
            const phase = this.burstClock + i * 0.01;

            // Professional color cycling with golden ratio
            const hue = (phase * 0.618) % 1; // Golden ratio for pleasing color progression
            const saturation = 0.7 + intensity * 0.3;
            const lightness = 0.4 + Math.sin(phase * 3) * 0.2 + intensity * 0.2;

            const color = new THREE.Color().setHSL(hue, saturation, lightness);
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
        }

        this.particles.attributes.color.needsUpdate = true;
    }

    private adjustParticleSpread(spread: number) {
        this.particleMaterial.size = 0.01 + spread * 0.03;
    }

    public setIntensity(intensity: number) {
        this.intensity = intensity;
        this.particleMaterial.opacity = 0.5 + intensity * 0.4;
    }

    public update(deltaTime: number, elapsedTime: number) {
        this.burstClock += deltaTime;
        const positions = this.particles.attributes.position.array as Float32Array;
        const colors = this.particles.attributes.color.array as Float32Array;
        const sizes = this.particles.attributes.size.array as Float32Array;

        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;

            // Professional physics integration
            positions[i3] += this.velocities[i3] * this.intensity;
            positions[i3 + 1] += this.velocities[i3 + 1] * this.intensity;
            positions[i3 + 2] += this.velocities[i3 + 2] * this.intensity;

            // Apply damping for natural feel
            this.velocities[i3] *= 0.98;
            this.velocities[i3 + 1] *= 0.98;
            this.velocities[i3 + 2] *= 0.98;

            // Update lifetimes
            this.lifetimes[i] -= deltaTime * 8;

            // Professional respawn with fibonacci distribution
            if (this.lifetimes[i] <= 0) {
                const goldenAngle = Math.PI * (3 - Math.sqrt(5));
                const y = 1 - (Math.random()) * 2;
                const radius = Math.sqrt(1 - y * y);
                const theta = goldenAngle * i;

                const sphereRadius = 0.8;
                positions[i3] = Math.cos(theta) * radius * sphereRadius;
                positions[i3 + 1] = y * sphereRadius;
                positions[i3 + 2] = Math.sin(theta) * radius * sphereRadius;

                this.velocities[i3] = 0;
                this.velocities[i3 + 1] = 0;
                this.velocities[i3 + 2] = 0;

                this.lifetimes[i] = 50 + Math.random() * 100;
                sizes[i] = 0.8 + Math.random() * 0.4;
            }

            // Professional containment with smooth boundaries
            const vesselBound = 1.8;
            const currentDistance = Math.sqrt(
                positions[i3] * positions[i3] +
                positions[i3 + 1] * positions[i3 + 1] +
                positions[i3 + 2] * positions[i3 + 2]
            );

            if (currentDistance > vesselBound) {
                const wrapFactor = vesselBound / currentDistance * 0.95;
                positions[i3] *= wrapFactor;
                positions[i3 + 1] *= wrapFactor;
                positions[i3 + 2] *= wrapFactor;
            }

            // Professional organic color evolution
            const colorPhase = elapsedTime * 0.3 + i * 0.01;
            const hue = (colorPhase * 0.1) % 1;
            const saturation = 0.6 + Math.sin(colorPhase * 2) * 0.2;
            const lightness = 0.5 + Math.sin(colorPhase * 1.7) * 0.1;

            const color = new THREE.Color().setHSL(hue, saturation, lightness);
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
        }

        this.particles.attributes.position.needsUpdate = true;
        this.particles.attributes.color.needsUpdate = true;
        this.particles.attributes.size.needsUpdate = true;

        // Professional rotation with golden ratio
        this.group.rotation.y += deltaTime * 0.1 * this.intensity * 0.618;
    }

    public reset() {
        this.group.rotation.set(0, 0, 0);
        this.burstClock = 0;
        this.burstPhase = 0;

        const positions = this.particles.attributes.position.array as Float32Array;
        const colors = this.particles.attributes.color.array as Float32Array;
        const sizes = this.particles.attributes.size.array as Float32Array;

        for (let i = 0; i < this.particleCount; i++) {
            const i3 = i * 3;

            // Reset to fibonacci distribution
            const goldenAngle = Math.PI * (3 - Math.sqrt(5));
            const y = 1 - (i / (this.particleCount - 1)) * 2;
            const radius = Math.sqrt(1 - y * y);
            const theta = goldenAngle * i;

            positions[i3] = Math.cos(theta) * radius * 0.8;
            positions[i3 + 1] = y * 0.8;
            positions[i3 + 2] = Math.sin(theta) * radius * 0.8;

            this.velocities[i3] = 0;
            this.velocities[i3 + 1] = 0;
            this.velocities[i3 + 2] = 0;

            this.lifetimes[i] = 50 + Math.random() * 100;
            sizes[i] = 0.8 + Math.random() * 0.4;

            // Reset to professional color scheme
            const hue = (i / this.particleCount) * 0.6 + 0.15;
            const color = new THREE.Color().setHSL(hue, 0.8, 0.6);
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
        }

        this.particles.attributes.position.needsUpdate = true;
        this.particles.attributes.color.needsUpdate = true;
        this.particles.attributes.size.needsUpdate = true;
    }

    // Legacy methods for compatibility
    public getCurrentIntensity(): number { return this.intensity; }
    public getCurrentEmissionRate(): number { return this.emissionRate; }
    public setEmissionRate(rate: number) { this.emissionRate = rate; }
    public setGeometricAlignment(alignment: number) { this.geometricAlignment = alignment; }
    public triggerLeadBellyPattern() { this.createProfessionalBurst(0.8); }
    public triggerHawkingPattern() { this.createProfessionalBurst(1.0); }
    public triggerPrankstersPattern() { this.createProfessionalBurst(1.2); }
    public createComplementaryPattern(trigger: string, response: string) { this.createProfessionalBurst(0.9); }
    public triggerChaos() { this.createProfessionalBurst(1.5); }
    public triggerMorph() { this.isMorphing = true; this.createProfessionalBurst(1.0); }
    public getMorphingState() { return { isMorphing: this.isMorphing, morphState: this.morphState, morphProgress: this.morphProgress }; }

    public setVisible(visible: boolean) {
        this.group.visible = visible;
    }
}