import * as THREE from 'three';

export class VesselLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private cube: THREE.Mesh;
    private sphere: THREE.Mesh;
    private wireframe: THREE.LineSegments;
    private intensity = 0.6;
    private pulseRate = 1.0;

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.initGeometry();
    }

    private initGeometry() {
        // Walter Russell's cube-sphere cosmology
        // The cube represents material form, the sphere represents spiritual essence

        // Create cube (material form) - 2026+ Quantum-state material
        const cubeGeometry = new THREE.BoxGeometry(1.8, 1.8, 1.8, 8, 8, 8);
        const cubeMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x00d4ff,
            transparent: true,
            opacity: 0.08,
            roughness: 0.0,
            metalness: 0.0,
            clearcoat: 1.0,
            clearcoatRoughness: 0.0,
            transmission: 0.95,
            thickness: 0.02,
            ior: 2.4,
            envMapIntensity: 4.0,
            emissive: 0x0099cc,
            emissiveIntensity: 0.2,
            iridescence: 1.0,
            iridescenceIOR: 2.1,
            iridescenceThicknessRange: [50, 1200],
            sheenColor: 0x00ffff,
            sheen: 1.0,
            sheenRoughness: 0.0
        });
        this.cube = new THREE.Mesh(cubeGeometry, cubeMaterial);

        // Create sphere (spiritual essence) - 2025 volumetric/holographic
        const sphereGeometry = new THREE.SphereGeometry(1.2, 128, 128);
        const sphereMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x6366f1,
            transparent: true,
            opacity: 0.04,
            roughness: 0.0,
            metalness: 0.95,
            clearcoat: 1.0,
            clearcoatRoughness: 0.0,
            transmission: 0.98,
            thickness: 0.05,
            ior: 1.52,
            envMapIntensity: 3.0,
            emissive: 0x8b5cf6,
            emissiveIntensity: 0.15,
            iridescence: 1.0,
            iridescenceIOR: 1.3,
            iridescenceThicknessRange: [100, 800]
        });
        this.sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);

        // Create wireframe - Minimal clean lines
        const wireframeGeometry = new THREE.EdgesGeometry(cubeGeometry);
        const wireframeMaterial = new THREE.LineBasicMaterial({
            color: 0x64b5f6,
            transparent: true,
            opacity: 0.3,
            linewidth: 1
        });
        this.wireframe = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);

        this.group.add(this.cube);
        this.group.add(this.sphere);
        this.group.add(this.wireframe);

        // Vessel is the container - center everything
        this.group.position.set(0, 0, 0);

        // Make cube and sphere more prominent and visible
        this.cube.scale.setScalar(0.8);
        this.sphere.scale.setScalar(0.6);
    }

    public processFrequency(signal: any) {
        // Map frequency to geometric transformations
        const frequency = signal.frequency || 440;
        const amplitude = signal.amplitude || 0.5;

        // Cube responds to low frequencies (material resonance)
        if (frequency < 200) {
            const scale = 1 + (amplitude * 0.3);
            this.cube.scale.setScalar(scale);
        }

        // Sphere responds to high frequencies (spiritual vibration)
        if (frequency > 800) {
            const scale = 1 + (amplitude * 0.2);
            this.sphere.scale.setScalar(scale);
        }

        // Wireframe responds to mid frequencies
        if (frequency >= 200 && frequency <= 800) {
            const opacity = 0.8 + (amplitude * 0.2);
            (this.wireframe.material as THREE.LineBasicMaterial).opacity = opacity;
        }
    }

    public setIntensity(intensity: number) {
        this.intensity = Math.max(0.3, intensity); // Keep minimum visibility

        // Adjust material properties based on intensity
        (this.cube.material as THREE.MeshPhongMaterial).opacity = Math.max(0.4, 0.3 * intensity);
        (this.sphere.material as THREE.MeshPhongMaterial).opacity = Math.max(0.3, 0.2 * intensity);
        (this.wireframe.material as THREE.LineBasicMaterial).opacity = Math.max(0.6, 0.8 * intensity);
    }

    public update(deltaTime: number, elapsedTime: number) {
        // Gentle rotation representing cosmic motion
        this.group.rotation.y += deltaTime * 0.1 * this.intensity;
        this.group.rotation.x += deltaTime * 0.05 * this.intensity;

        // Pulsing effect for spiritual essence
        const pulse = Math.sin(elapsedTime * 2 * this.pulseRate) * 0.1 + 1;
        this.sphere.scale.setScalar(pulse * this.intensity);

        // Subtle color shifts based on Russell's teachings about light
        const hue = (elapsedTime * 0.1) % 1;
        (this.cube.material as THREE.MeshPhongMaterial).color.setHSL(hue, 0.6, 0.5);
        (this.sphere.material as THREE.MeshPhongMaterial).color.setHSL((hue + 0.5) % 1, 0.6, 0.5);
    }

    public reset() {
        this.group.rotation.set(0, 0, 0);
        this.cube.scale.setScalar(1);
        this.sphere.scale.setScalar(1);

        // Reset to original colors
        (this.cube.material as THREE.MeshPhongMaterial).color.setHex(0x4a90e2);
        (this.sphere.material as THREE.MeshPhongMaterial).color.setHex(0xe24a90);
    }

    // Conversation system methods
    public getCurrentIntensity(): number {
        return this.intensity;
    }

    public getCurrentPulseRate(): number {
        return this.pulseRate;
    }

    public setPulseRate(rate: number) {
        this.pulseRate = rate;
    }

    public triggerHarmony() {
        // Create harmonic visual effect
        const harmonicPulse = (elapsedTime: number) => {
            const harmony = Math.sin(elapsedTime * 4) * Math.sin(elapsedTime * 6) * 0.2 + 1;
            this.sphere.scale.setScalar(harmony * this.intensity);
        };

        // Apply harmonic colors
        (this.cube.material as THREE.MeshPhongMaterial).color.setHSL(0.6, 0.8, 0.6);
        (this.sphere.material as THREE.MeshPhongMaterial).color.setHSL(0.6, 0.8, 0.8);
    }

    public triggerConflict() {
        // Create conflicting visual patterns
        this.pulseRate = 2.5; // Faster, more agitated pulsing

        // Apply conflict colors (reds and oranges)
        (this.cube.material as THREE.MeshPhongMaterial).color.setHSL(0.0, 0.8, 0.5);
        (this.sphere.material as THREE.MeshPhongMaterial).color.setHSL(0.1, 0.8, 0.6);
    }
}