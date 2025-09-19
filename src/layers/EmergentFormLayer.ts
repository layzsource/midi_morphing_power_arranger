import * as THREE from 'three';

export class EmergentFormLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private morphTargets: THREE.Mesh[] = [];
    private currentForm = 0;
    private speed = 0.8;
    private intensity = 0.7;
    private morphingSpeed = 1.0;
    private blakeGeometry: THREE.BufferGeometry;
    private teslaGeometry: THREE.BufferGeometry;
    private beatlesGeometry: THREE.BufferGeometry;

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.initForms();
    }

    private initForms() {
        // William Blake - Poetry and myth made geometric
        this.blakeGeometry = this.createBlakeForm();

        // Nikola Tesla - Resonance and electrical patterns
        this.teslaGeometry = this.createTeslaForm();

        // The Beatles - Harmonic collective forms
        this.beatlesGeometry = this.createBeatlesForm();

        // Create morphing mesh
        const material = new THREE.MeshPhysicalMaterial({
            color: 0x50c878,
            transparent: true,
            opacity: 0.85,
            roughness: 0.2,
            metalness: 0.8,
            clearcoat: 0.8,
            clearcoatRoughness: 0.2,
            envMapIntensity: 1.2,
            emissive: 0x50c878,
            emissiveIntensity: 0.05
        });

        const mesh = new THREE.Mesh(this.blakeGeometry, material);
        this.morphTargets.push(mesh);
        this.group.add(mesh);

        // Emergent forms live within the vessel - centered but slightly offset
        this.group.position.set(0, 0, 0);
    }

    private createBlakeForm(): THREE.BufferGeometry {
        // Organic, flowing form inspired by Blake's vision
        const geometry = new THREE.SphereGeometry(1, 16, 16);
        const vertices = geometry.attributes.position.array as Float32Array;

        // Apply Blake-like distortions - mystical, flowing
        for (let i = 0; i < vertices.length; i += 3) {
            const x = vertices[i];
            const y = vertices[i + 1];
            const z = vertices[i + 2];

            // Create flowing, organic distortions
            const noise = Math.sin(x * 3) * Math.cos(y * 3) * Math.sin(z * 3);
            const scale = 1 + noise * 0.3;

            vertices[i] = x * scale;
            vertices[i + 1] = y * scale;
            vertices[i + 2] = z * scale;
        }

        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
        return geometry;
    }

    private createTeslaForm(): THREE.BufferGeometry {
        // Sharp, electrical, resonant patterns
        const geometry = new THREE.ConeGeometry(0.8, 2, 8);
        const vertices = geometry.attributes.position.array as Float32Array;

        // Apply Tesla-like electrical distortions
        for (let i = 0; i < vertices.length; i += 3) {
            const x = vertices[i];
            const y = vertices[i + 1];
            const z = vertices[i + 2];

            // Create electrical field-like distortions
            const distance = Math.sqrt(x * x + z * z);
            const electricField = Math.sin(distance * 8) * 0.1;

            vertices[i] = x + electricField;
            vertices[i + 2] = z + electricField;
        }

        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
        return geometry;
    }

    private createBeatlesForm(): THREE.BufferGeometry {
        // Harmonic, collective, playful geometry
        const geometry = new THREE.TorusGeometry(0.8, 0.3, 8, 16);
        const vertices = geometry.attributes.position.array as Float32Array;

        // Apply Beatles-like harmonic distortions
        for (let i = 0; i < vertices.length; i += 3) {
            const x = vertices[i];
            const y = vertices[i + 1];
            const z = vertices[i + 2];

            // Create harmonic resonance patterns
            const harmonic = Math.sin(x * 2) + Math.cos(y * 2) + Math.sin(z * 2);
            const scale = 1 + harmonic * 0.1;

            vertices[i] = x * scale;
            vertices[i + 1] = y * scale;
            vertices[i + 2] = z * scale;
        }

        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
        return geometry;
    }

    public processFrequency(signal: any) {
        const frequency = signal.frequency || 440;
        const amplitude = signal.amplitude || 0.5;

        // Different frequency ranges trigger different forms
        if (frequency < 300) {
            this.morphToForm(0); // Blake - low, mystical
        } else if (frequency < 600) {
            this.morphToForm(1); // Tesla - mid, electrical
        } else {
            this.morphToForm(2); // Beatles - high, harmonic
        }

        // Amplitude affects intensity
        const material = this.morphTargets[0].material as THREE.MeshPhongMaterial;
        material.opacity = 0.7 + (amplitude * 0.3);
    }

    private morphToForm(targetForm: number) {
        if (this.currentForm === targetForm) return;

        this.currentForm = targetForm;

        // Simple form switching for now - could be enhanced with actual morphing
        const mesh = this.morphTargets[0];

        switch (targetForm) {
            case 0:
                mesh.geometry = this.blakeGeometry;
                (mesh.material as THREE.MeshPhongMaterial).color.setHex(0x50c878); // Green
                break;
            case 1:
                mesh.geometry = this.teslaGeometry;
                (mesh.material as THREE.MeshPhongMaterial).color.setHex(0x4169e1); // Electric blue
                break;
            case 2:
                mesh.geometry = this.beatlesGeometry;
                (mesh.material as THREE.MeshPhongMaterial).color.setHex(0xffd700); // Golden
                break;
        }
    }

    public setSpeed(speed: number) {
        this.speed = speed;
    }

    public update(deltaTime: number, elapsedTime: number) {
        // Continuous evolution and morphing
        this.group.rotation.y += deltaTime * this.speed * 0.5 * this.morphingSpeed;
        this.group.rotation.z += deltaTime * this.speed * 0.2;

        // Dynamic form evolution
        const mesh = this.morphTargets[0];
        const scale = 1 + Math.sin(elapsedTime * this.speed) * 0.2;
        mesh.scale.setScalar(scale);

        // Color evolution
        const hue = (elapsedTime * this.speed * 0.1) % 1;
        (mesh.material as THREE.MeshPhongMaterial).emissive.setHSL(hue, 0.3, 0.1);
    }

    public reset() {
        this.group.rotation.set(0, 0, 0);
        this.morphTargets[0].scale.setScalar(1);
        this.morphToForm(0);
    }

    // Conversation system methods
    public getCurrentSpeed(): number {
        return this.speed;
    }

    public getCurrentIntensity(): number {
        return this.intensity;
    }

    public setMorphingSpeed(speed: number) {
        this.morphingSpeed = speed;
    }

    public createHarmonicResonance() {
        // Create visual harmony between forms
        this.morphingSpeed = 0.5; // Slower, more meditative morphing

        // Apply harmonic colors to current form
        const mesh = this.morphTargets[0];
        (mesh.material as THREE.MeshPhongMaterial).color.setHSL(0.6, 0.7, 0.7);

        // Add gentle pulsing
        const originalScale = mesh.scale.x;
        const pulseEffect = () => {
            const pulse = Math.sin(Date.now() * 0.003) * 0.1 + 1;
            mesh.scale.setScalar(originalScale * pulse);
        };

        // Apply for a duration
        setTimeout(() => {
            mesh.scale.setScalar(originalScale);
        }, 3000);
    }

    public triggerTransformation() {
        // Rapid form shifting
        this.morphingSpeed = 3.0; // Much faster morphing

        // Cycle through all forms rapidly
        let formIndex = 0;
        const transformInterval = setInterval(() => {
            this.morphToForm(formIndex % 3);
            formIndex++;

            if (formIndex >= 6) { // Cycle twice then stop
                clearInterval(transformInterval);
                this.morphingSpeed = 1.0; // Return to normal
            }
        }, 500);
    }

    public createConflictPattern() {
        // Create visual discord
        this.morphingSpeed = 2.5; // Erratic morphing speed

        // Apply conflict colors (harsh reds)
        const mesh = this.morphTargets[0];
        (mesh.material as THREE.MeshPhongMaterial).color.setHSL(0.0, 1.0, 0.5);

        // Irregular scaling
        const conflictScale = () => {
            const irregularPulse = Math.sin(Date.now() * 0.007) * Math.cos(Date.now() * 0.011) * 0.3 + 1;
            mesh.scale.setScalar(irregularPulse);
        };

        // Apply for duration
        const conflictInterval = setInterval(conflictScale, 50);
        setTimeout(() => {
            clearInterval(conflictInterval);
            mesh.scale.setScalar(1);
        }, 2000);
    }
}