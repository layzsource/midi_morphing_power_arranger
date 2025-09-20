import * as THREE from 'three';
import { MaterialSystem } from './MaterialSystem';

/**
 * LightingSystem - Unified lighting design for Living Myth Engine
 * Creates atmospheric depth supporting mythological themes
 */
export class LightingSystem {
    private scene: THREE.Scene;
    private lights: Map<string, THREE.Light> = new Map();
    private intensity: number = 1.0;
    private mythologicalMode: 'default' | 'harmony' | 'conflict' | 'wisdom' | 'mystery' = 'default';

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.setupLights();
    }

    private setupLights() {
        // Primary Key Light - Sacred geometry illumination
        const keyLight = new THREE.DirectionalLight(MaterialSystem.COLORS.VESSEL_CYAN, 2.2);
        keyLight.position.set(8, 12, 6);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 4096;
        keyLight.shadow.mapSize.height = 4096;
        keyLight.shadow.camera.near = 0.1;
        keyLight.shadow.camera.far = 50;
        keyLight.shadow.camera.left = -12;
        keyLight.shadow.camera.right = 12;
        keyLight.shadow.camera.top = 12;
        keyLight.shadow.camera.bottom = -12;
        keyLight.shadow.bias = -0.0001;
        keyLight.shadow.normalBias = 0.02;
        keyLight.name = 'keyLight';
        this.scene.add(keyLight);
        this.lights.set('key', keyLight);

        // Ambient Foundation - Quantum field effect
        const ambientLight = new THREE.AmbientLight(MaterialSystem.COLORS.SACRED_PURPLE, 0.03);
        ambientLight.name = 'ambientLight';
        this.scene.add(ambientLight);
        this.lights.set('ambient', ambientLight);

        // Fill Light - Soft consciousness glow
        const fillLight = new THREE.DirectionalLight(MaterialSystem.COLORS.SACRED_PURPLE, 0.6);
        fillLight.position.set(-6, 6, -4);
        fillLight.name = 'fillLight';
        this.scene.add(fillLight);
        this.lights.set('fill', fillLight);

        // Rim Light - Edge definition
        const rimLight = new THREE.DirectionalLight(MaterialSystem.COLORS.PARTICLE_VIOLET, 0.4);
        rimLight.position.set(0, -6, 10);
        rimLight.name = 'rimLight';
        this.scene.add(rimLight);
        this.lights.set('rim', rimLight);

        // Accent Lights - Mythological atmosphere
        const accent1 = new THREE.PointLight(MaterialSystem.COLORS.VESSEL_CYAN, 1.4, 18, 1.8);
        accent1.position.set(-8, 5, 4);
        accent1.name = 'accent1';
        this.scene.add(accent1);
        this.lights.set('accent1', accent1);

        const accent2 = new THREE.PointLight(MaterialSystem.COLORS.EMERGENT_GREEN, 1.0, 15, 2);
        accent2.position.set(8, -3, -4);
        accent2.name = 'accent2';
        this.scene.add(accent2);
        this.lights.set('accent2', accent2);

        // Hemisphere Light - Environmental foundation
        const hemiLight = new THREE.HemisphereLight(
            MaterialSystem.COLORS.SACRED_PURPLE,
            MaterialSystem.COLORS.SHADOW_DEEP,
            0.25
        );
        hemiLight.name = 'hemiLight';
        this.scene.add(hemiLight);
        this.lights.set('hemisphere', hemiLight);

        // Particle Enhancement Light - Highlights cellular activity
        const particleLight = new THREE.PointLight(MaterialSystem.COLORS.PARTICLE_VIOLET, 0.8, 12, 2.5);
        particleLight.position.set(0, 0, 8);
        particleLight.name = 'particleLight';
        this.scene.add(particleLight);
        this.lights.set('particle', particleLight);
    }

    /**
     * Set overall lighting intensity while maintaining ratios
     */
    public setIntensity(intensity: number) {
        this.intensity = Math.max(0.1, Math.min(2.0, intensity));

        // Apply intensity scaling to all lights
        const keyLight = this.lights.get('key') as THREE.DirectionalLight;
        const fillLight = this.lights.get('fill') as THREE.DirectionalLight;
        const rimLight = this.lights.get('rim') as THREE.DirectionalLight;
        const accent1 = this.lights.get('accent1') as THREE.PointLight;
        const accent2 = this.lights.get('accent2') as THREE.PointLight;
        const particleLight = this.lights.get('particle') as THREE.PointLight;
        const ambientLight = this.lights.get('ambient') as THREE.AmbientLight;
        const hemiLight = this.lights.get('hemisphere') as THREE.HemisphereLight;

        if (keyLight) keyLight.intensity = 2.2 * this.intensity;
        if (fillLight) fillLight.intensity = 0.6 * this.intensity;
        if (rimLight) rimLight.intensity = 0.4 * this.intensity;
        if (accent1) accent1.intensity = 1.4 * this.intensity;
        if (accent2) accent2.intensity = 1.0 * this.intensity;
        if (particleLight) particleLight.intensity = 0.8 * this.intensity;
        if (ambientLight) ambientLight.intensity = 0.03 * this.intensity;
        if (hemiLight) hemiLight.intensity = 0.25 * this.intensity;
    }

    /**
     * Apply mythological lighting themes
     */
    public setMythologicalTheme(theme: 'default' | 'harmony' | 'conflict' | 'wisdom' | 'mystery') {
        this.mythologicalMode = theme;

        const keyLight = this.lights.get('key') as THREE.DirectionalLight;
        const fillLight = this.lights.get('fill') as THREE.DirectionalLight;
        const accent1 = this.lights.get('accent1') as THREE.PointLight;
        const accent2 = this.lights.get('accent2') as THREE.PointLight;

        switch (theme) {
            case 'harmony':
                keyLight.color.setHex(MaterialSystem.COLORS.HARMONY_BLUE);
                fillLight.color.setHex(MaterialSystem.COLORS.SACRED_PURPLE);
                accent1.color.setHex(MaterialSystem.COLORS.HARMONY_BLUE);
                accent2.color.setHex(MaterialSystem.COLORS.WISDOM_GOLD);
                break;

            case 'conflict':
                keyLight.color.setHex(MaterialSystem.COLORS.CONFLICT_RED);
                fillLight.color.setHex(MaterialSystem.COLORS.MERKABA_CRIMSON);
                accent1.color.setHex(MaterialSystem.COLORS.CONFLICT_RED);
                accent2.color.setHex(0xff4500); // Orange accent
                break;

            case 'wisdom':
                keyLight.color.setHex(MaterialSystem.COLORS.WISDOM_GOLD);
                fillLight.color.setHex(MaterialSystem.COLORS.SACRED_PURPLE);
                accent1.color.setHex(MaterialSystem.COLORS.WISDOM_GOLD);
                accent2.color.setHex(MaterialSystem.COLORS.VESSEL_CYAN);
                break;

            case 'mystery':
                keyLight.color.setHex(MaterialSystem.COLORS.SACRED_PURPLE);
                fillLight.color.setHex(MaterialSystem.COLORS.SHADOW_DEEP);
                accent1.color.setHex(0x4a148c); // Deep purple
                accent2.color.setHex(MaterialSystem.COLORS.PARTICLE_VIOLET);
                break;

            case 'default':
            default:
                keyLight.color.setHex(MaterialSystem.COLORS.VESSEL_CYAN);
                fillLight.color.setHex(MaterialSystem.COLORS.SACRED_PURPLE);
                accent1.color.setHex(MaterialSystem.COLORS.VESSEL_CYAN);
                accent2.color.setHex(MaterialSystem.COLORS.EMERGENT_GREEN);
                break;
        }
    }

    /**
     * Animate lights for living mythological atmosphere
     */
    public update(deltaTime: number, elapsedTime: number) {
        // Subtle key light movement for dynamic shadows
        const keyLight = this.lights.get('key') as THREE.DirectionalLight;
        if (keyLight) {
            const keyOffset = Math.sin(elapsedTime * 0.1) * 0.5;
            keyLight.position.x = 8 + keyOffset;
            keyLight.position.y = 12 + Math.cos(elapsedTime * 0.08) * 0.3;
        }

        // Gentle accent light pulsing
        const accent1 = this.lights.get('accent1') as THREE.PointLight;
        const accent2 = this.lights.get('accent2') as THREE.PointLight;

        if (accent1) {
            const pulse1 = Math.sin(elapsedTime * 0.6) * 0.2 + 1.0;
            accent1.intensity = (1.4 * this.intensity) * pulse1;
        }

        if (accent2) {
            const pulse2 = Math.sin(elapsedTime * 0.4 + Math.PI) * 0.15 + 1.0;
            accent2.intensity = (1.0 * this.intensity) * pulse2;
        }

        // Particle light follows particle activity
        const particleLight = this.lights.get('particle') as THREE.PointLight;
        if (particleLight) {
            const particlePulse = Math.sin(elapsedTime * 0.8) * 0.3 + 1.0;
            particleLight.intensity = (0.8 * this.intensity) * particlePulse;

            // Subtle orbital movement
            const orbitRadius = 3;
            particleLight.position.x = Math.cos(elapsedTime * 0.2) * orbitRadius;
            particleLight.position.z = 8 + Math.sin(elapsedTime * 0.2) * orbitRadius * 0.5;
        }
    }

    /**
     * Enhanced lighting for performance moments
     */
    public triggerPerformanceMode(intensity: number = 1.5) {
        this.setIntensity(intensity);

        // Increase accent light drama
        const accent1 = this.lights.get('accent1') as THREE.PointLight;
        const accent2 = this.lights.get('accent2') as THREE.PointLight;

        if (accent1) accent1.intensity *= 1.3;
        if (accent2) accent2.intensity *= 1.3;
    }

    /**
     * Return to meditative lighting
     */
    public returnToMeditative() {
        this.setIntensity(0.8);
        this.setMythologicalTheme('default');
    }

    /**
     * Get all lights for external manipulation
     */
    public getLights(): Map<string, THREE.Light> {
        return this.lights;
    }

    /**
     * Enable/disable shadow casting for performance
     */
    public setShadowsEnabled(enabled: boolean) {
        const keyLight = this.lights.get('key') as THREE.DirectionalLight;
        if (keyLight) {
            keyLight.castShadow = enabled;
        }
    }
}