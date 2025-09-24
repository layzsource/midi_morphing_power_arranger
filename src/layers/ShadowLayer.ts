import * as THREE from 'three';

export class ShadowLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private shadowPlanes: THREE.Mesh[] = [];
    private negativeSpace: THREE.Mesh;
    private intensity = 0.5;
    private inversionActive = false;
    private opacity = 0.4;
    private inversionProbability = 0.1;

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.initShadows();
    }

    private initShadows() {
        // Create shadow planes for projection and negative space
        this.createShadowPlanes();
        this.createNegativeSpace();

        // Shadows project from and around all layers - centered
        this.group.position.set(0, 0, 0);
    }

    private createShadowPlanes() {
        // Multiple shadow planes for complex projection effects
        const planeGeometry = new THREE.PlaneGeometry(4, 4);

        for (let i = 0; i < 3; i++) {
            const planeMaterial = new THREE.MeshBasicMaterial({
                color: 0x000000,
                transparent: true,
                opacity: 0.3 + i * 0.1,
                side: THREE.DoubleSide
            });

            const shadowPlane = new THREE.Mesh(planeGeometry, planeMaterial);

            // Position planes as ground shadows and projections
            shadowPlane.position.set(0, -3 - i * 0.2, 0);
            shadowPlane.rotation.x = -Math.PI / 2;

            // Set shadow to main scene layer (layer 0) to avoid morph box rendering
            shadowPlane.layers.set(0);

            this.shadowPlanes.push(shadowPlane);
            this.group.add(shadowPlane);
        }
    }

    private createNegativeSpace() {
        // Negative space representation - inverted geometry
        const geometry = new THREE.TorusGeometry(1.5, 0.5, 8, 16);
        const material = new THREE.MeshBasicMaterial({
            color: 0x000000,
            transparent: true,
            opacity: 0.4,
            side: THREE.BackSide // Show the inside
        });

        this.negativeSpace = new THREE.Mesh(geometry, material);
        // Negative space surrounds the vessel at center
        this.negativeSpace.position.set(0, 0, 0);

        // Set negative space to main scene layer (layer 0) to avoid morph box rendering
        this.negativeSpace.layers.set(0);

        this.group.add(this.negativeSpace);
    }

    public processSignal(signal: any) {
        // Shadow layer responds to silence and absence
        if (signal.type === 'silence') {
            this.triggerShadowInversion(signal.duration || 1);
        }

        // Abbie Hoffman trickster energy - disruption and inversion
        if (signal.trigger === 'hoffman') {
            this.triggerTricksterMode();
        }

        // Les Waas absurdity - humor through absence
        if (signal.trigger === 'waas') {
            this.triggerAbsurdityMode();
        }
    }

    private triggerShadowInversion(duration: number) {
        this.inversionActive = true;

        // Invert all shadow planes
        this.shadowPlanes.forEach((plane, index) => {
            const material = plane.material as THREE.MeshBasicMaterial;
            material.color.setHex(0xffffff); // White shadows
            material.opacity = 0.8 - index * 0.2;
        });

        // Invert negative space
        const negMaterial = this.negativeSpace.material as THREE.MeshBasicMaterial;
        negMaterial.color.setHex(0xffffff);
        negMaterial.side = THREE.FrontSide;

        // Revert after duration
        setTimeout(() => {
            this.revertInversion();
        }, duration * 1000);
    }

    private revertInversion() {
        this.inversionActive = false;

        // Revert shadow planes
        this.shadowPlanes.forEach((plane, index) => {
            const material = plane.material as THREE.MeshBasicMaterial;
            material.color.setHex(0x000000);
            material.opacity = 0.3 + index * 0.1;
        });

        // Revert negative space
        const negMaterial = this.negativeSpace.material as THREE.MeshBasicMaterial;
        negMaterial.color.setHex(0x000000);
        negMaterial.side = THREE.BackSide;
    }

    private triggerTricksterMode() {
        // Hoffman's activist disruption - chaotic shadow behavior
        this.shadowPlanes.forEach((plane, index) => {
            // Random color flashes
            const material = plane.material as THREE.MeshBasicMaterial;
            material.color.setHSL(Math.random(), 0.8, 0.3);

            // Chaotic movement
            plane.rotation.z = Math.random() * Math.PI * 2;
            plane.position.x = (Math.random() - 0.5) * 2;
            plane.position.z = (Math.random() - 0.5) * 2;
        });

        // Reset after brief disruption
        setTimeout(() => {
            this.resetShadowPlanes();
        }, 500);
    }

    private triggerAbsurdityMode() {
        // Les Waas humor through absence - make shadows disappear and reappear
        this.shadowPlanes.forEach((plane, index) => {
            const material = plane.material as THREE.MeshBasicMaterial;

            // Fade out
            const fadeOut = () => {
                material.opacity *= 0.9;
                if (material.opacity > 0.01) {
                    setTimeout(fadeOut, 50);
                } else {
                    // Sudden reappearance with humor
                    material.opacity = 0.8;
                    material.color.setHex(0xff69b4); // Pink for absurdity
                }
            };

            setTimeout(fadeOut, index * 100);
        });

        // Reset to normal after absurd moment
        setTimeout(() => {
            this.resetShadowPlanes();
        }, 2000);
    }

    private resetShadowPlanes() {
        this.shadowPlanes.forEach((plane, index) => {
            const material = plane.material as THREE.MeshBasicMaterial;
            material.color.setHex(0x000000);
            material.opacity = 0.3 + index * 0.1;

            plane.rotation.z = 0;
            plane.position.set(0, -3 - index * 0.2, 0);
        });
    }

    public setIntensity(intensity: number) {
        this.intensity = intensity;

        // Adjust shadow opacity based on intensity
        this.shadowPlanes.forEach((plane, index) => {
            const material = plane.material as THREE.MeshBasicMaterial;
            material.opacity = (0.3 + index * 0.1) * intensity;
        });

        const negMaterial = this.negativeSpace.material as THREE.MeshBasicMaterial;
        negMaterial.opacity = 0.4 * intensity;
    }

    public update(deltaTime: number, elapsedTime: number) {
        // Subtle shadow movement
        this.shadowPlanes.forEach((plane, index) => {
            plane.rotation.z += deltaTime * 0.05 * this.intensity * (index + 1);

            // Breathing effect
            const breath = Math.sin(elapsedTime + index) * 0.1 + 1;
            plane.scale.setScalar(breath);
        });

        // Negative space rotation
        this.negativeSpace.rotation.y += deltaTime * 0.2 * this.intensity;
        this.negativeSpace.rotation.x += deltaTime * 0.1 * this.intensity;

        // Dynamic shadow casting based on time
        if (!this.inversionActive) {
            const shadowOpacity = (Math.sin(elapsedTime * 0.5) + 1) * 0.2 + 0.1;
            this.shadowPlanes.forEach((plane, index) => {
                const material = plane.material as THREE.MeshBasicMaterial;
                material.opacity = shadowOpacity * (index + 1) * this.intensity;
            });
        }

        // Occasional spontaneous inversions (Waas absurdity)
        if (Math.random() < 0.001 && !this.inversionActive) {
            this.triggerShadowInversion(0.5);
        }
    }

    public reset() {
        this.group.rotation.set(0, 0, 0);
        this.inversionActive = false;
        this.resetShadowPlanes();

        // Reset negative space
        this.negativeSpace.rotation.set(0, 0, 0);
        this.negativeSpace.scale.setScalar(1);
        const negMaterial = this.negativeSpace.material as THREE.MeshBasicMaterial;
        negMaterial.color.setHex(0x000000);
        negMaterial.opacity = this.opacity;
        negMaterial.side = THREE.BackSide;
    }

    // Conversation system methods
    public getCurrentIntensity(): number {
        return this.intensity;
    }

    public getCurrentOpacity(): number {
        return this.opacity;
    }

    public setOpacity(opacity: number) {
        this.opacity = opacity;

        // Apply to all shadow planes
        this.shadowPlanes.forEach(plane => {
            const material = plane.material as THREE.MeshBasicMaterial;
            material.opacity = opacity;
        });

        // Apply to negative space
        const negMaterial = this.negativeSpace.material as THREE.MeshBasicMaterial;
        negMaterial.opacity = opacity * 0.8; // Slightly less opaque
    }

    public setInversionProbability(probability: number) {
        this.inversionProbability = probability;

        // Higher probability triggers more frequent inversions
        if (Math.random() < probability) {
            this.triggerInversion();
        }
    }

    public createTransformationShadow() {
        // Create dynamic shadow transformations
        this.shadowPlanes.forEach((plane, index) => {
            const material = plane.material as THREE.MeshBasicMaterial;

            // Cycling shadow colors
            const hue = (Date.now() * 0.001 + index * 0.3) % 1;
            material.color.setHSL(hue, 0.5, 0.3);

            // Dynamic scaling
            const scale = Math.sin(Date.now() * 0.002) * 0.5 + 1.5;
            plane.scale.setScalar(scale);
        });

        // Transform negative space
        const transformScale = Math.sin(Date.now() * 0.003) * 0.3 + 1;
        this.negativeSpace.scale.setScalar(transformScale);
    }

    public triggerInversion() {
        // Hoffman-style reality inversion
        this.inversionActive = !this.inversionActive;

        if (this.inversionActive) {
            // Invert shadow colors to bright
            this.shadowPlanes.forEach(plane => {
                const material = plane.material as THREE.MeshBasicMaterial;
                material.color.setHex(0xffffff);
                material.opacity = 0.8;
            });

            // Negative space becomes positive
            const negMaterial = this.negativeSpace.material as THREE.MeshBasicMaterial;
            negMaterial.color.setHex(0xffffff);
            negMaterial.side = THREE.FrontSide;
        } else {
            // Return to normal shadow state
            this.shadowPlanes.forEach(plane => {
                const material = plane.material as THREE.MeshBasicMaterial;
                material.color.setHex(0x222222);
                material.opacity = this.opacity;
            });

            const negMaterial = this.negativeSpace.material as THREE.MeshBasicMaterial;
            negMaterial.color.setHex(0x000000);
            negMaterial.side = THREE.BackSide;
        }

        console.log(`🔄 Shadow inversion: ${this.inversionActive ? 'Active' : 'Inactive'}`);
    }
}