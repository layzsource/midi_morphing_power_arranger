/**
 * MMPA Engine - MIDI Morphing Power Arranger
 *
 * Focused, professional audiovisual performance engine
 * Built for real-time MIDI-driven morphing and VJ performance
 */

import * as THREE from 'three';
import { VesselLayer } from './layers/VesselLayer';
import { EmergentFormLayer } from './layers/EmergentFormLayer';
import { ParticleLayer } from './layers/ParticleLayer';
import { ShadowLayer } from './layers/ShadowLayer';
import { AudioEngine } from './audio/AudioEngine';

export type PerformanceMode = 'vj' | 'installation' | 'studio';

export class MMPAEngine {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private container: HTMLElement;

    // Core visual layers
    private vesselLayer: VesselLayer;
    private emergentFormLayer: EmergentFormLayer;
    private particleLayer: ParticleLayer;
    private shadowLayer: ShadowLayer;

    // Audio and MIDI
    private audioEngine: AudioEngine;

    // Performance state
    private currentMode: PerformanceMode = 'vj';
    private isRunning = false;
    private clock = new THREE.Clock();

    // MIDI state
    private midiAccess: any = null;
    private activeThinker = 'MMPA ready';

    constructor(container: HTMLElement) {
        console.log('🎛️ MMPA Engine starting...');
        this.container = container;
        console.log('📦 Container:', container);

        try {
            this.initThreeJS();
            console.log('✅ Three.js initialized');

            this.initLayers();
            console.log('✅ Layers initialized');

            this.initAudio();
            console.log('✅ Audio initialized');

            this.updateActiveThinker('MIDI morphing engine ready');
            console.log('🚀 MMPA Engine ready!');

        console.log('🚀 MMPA Engine fully restored to working state');
        } catch (error) {
            console.error('❌ MMPA Engine failed to initialize:', error);
        }
    }

    private initThreeJS() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000000);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / window.innerHeight,
            0.1,
            100
        );
        this.camera.position.set(0, 0, 8);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            powerPreference: 'high-performance',
            alpha: false
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.setClearColor(0x000011, 1.0); // Dark blue background instead of white

        this.container.appendChild(this.renderer.domElement);
        console.log('🎯 Canvas element added to container:', this.container);
        console.log('🎨 Canvas element:', this.renderer.domElement);
        console.log('📏 Canvas actual size:', this.renderer.domElement.width, 'x', this.renderer.domElement.height);

        // Add essential lighting for materials
        this.initLighting();
    }

    private initLighting() {
        // Ambient light for overall illumination
        const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
        this.scene.add(ambientLight);

        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
        directionalLight.position.set(5, 5, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);

        // Additional point light for vessel illumination
        const pointLight = new THREE.PointLight(0x00ffff, 0.5, 10);
        pointLight.position.set(0, 0, 3);
        this.scene.add(pointLight);

        // Rim light for depth
        const rimLight = new THREE.DirectionalLight(0xff00ff, 0.3);
        rimLight.position.set(-5, -5, -5);
        this.scene.add(rimLight);
    }

    private initLayers() {
        // Initialize core layers
        this.vesselLayer = new VesselLayer(this.scene);
        this.emergentFormLayer = new EmergentFormLayer(this.scene);
        this.particleLayer = new ParticleLayer(this.scene);
        this.shadowLayer = new ShadowLayer(this.scene);
    }

    private initAudio() {
        this.audioEngine = new AudioEngine();
    }

    public start() {
        console.log('🎬 Starting MMPA animation loop...');
        this.isRunning = true;
        this.animate();
        this.updateActiveThinker('MMPA performance engine started');
    }

    public stop() {
        this.isRunning = false;
        this.updateActiveThinker('MMPA engine stopped');
    }

    private animate() {
        if (!this.isRunning) return;

        requestAnimationFrame(() => this.animate());

        const deltaTime = this.clock.getDelta();
        const elapsedTime = this.clock.getElapsedTime();

        try {
            // Update all layers
            this.vesselLayer.update(deltaTime, elapsedTime);
            this.emergentFormLayer.update(deltaTime, elapsedTime);
            this.particleLayer.update(deltaTime, elapsedTime);
            this.shadowLayer.update(deltaTime, elapsedTime);

            // Render main scene
            this.renderer.render(this.scene, this.camera);

            // Render morph box if enabled
            if (this.morphBoxEnabled && this.morphBoxRenderer && this.morphBoxCamera) {
                this.morphBoxRenderer.render(this.scene, this.morphBoxCamera);
            }
        } catch (error) {
            console.error('❌ Animation loop error:', error);
        }
    }

    public setMode(mode: PerformanceMode) {
        this.currentMode = mode;
        this.updateActiveThinker(`MMPA mode: ${mode}`);

        // Adjust settings based on mode
        switch (mode) {
            case 'vj':
                // Fast, responsive settings for live performance
                this.vesselLayer.setIntensity(0.8);
                break;
            case 'installation':
                // Slower, more meditative settings
                this.vesselLayer.setIntensity(0.5);
                break;
            case 'studio':
                // Precise control settings
                this.vesselLayer.setIntensity(0.7);
                break;
        }
    }

    public setVesselMotion(enabled: boolean) {
        this.vesselLayer.setMotion(enabled);
        this.updateActiveThinker(`Shadow morphing: ${enabled ? 'ON' : 'OFF'}`);
    }

    public async handleKeyPress(key: string) {
        switch (key) {
            case '1':
                this.morphToForm(0); // Blake
                break;
            case '2':
                this.morphToForm(1); // Tesla
                break;
            case '3':
                this.morphToForm(2); // Beatles
                break;
            case '4':
                this.morphToForm(3); // Green Bean - The beloved one returns!
                break;
            case ' ':
                this.triggerMorphEvent();
                break;
            case 'r':
            case 'R':
                this.reset();
                break;
        }
    }

    private morphToForm(formIndex: number) {
        const formNames = ['Blake', 'Tesla', 'Beatles', 'Green Bean'];
        this.emergentFormLayer.triggerMorph(formIndex);
        this.updateActiveThinker(`Morphing to ${formNames[formIndex]} form`);
    }

    private triggerMorphEvent() {
        // Trigger synchronized morphing across all layers
        this.vesselLayer.triggerHarmony();
        this.particleLayer.triggerFlow();
        this.updateActiveThinker('Morphing event triggered');
    }

    public connectMIDI(midiAccess: any) {
        this.midiAccess = midiAccess;

        for (const input of midiAccess.inputs.values()) {
            input.addEventListener('midimessage', (event: any) => {
                this.handleMIDIMessage(event);
            });
        }

        this.updateActiveThinker('MIDI controller connected');
    }

    private handleMIDIMessage(event: any) {
        const [status, data1, data2] = event.data;

        // Note on/off (144/128)
        if (status === 144 || status === 128) {
            this.handleMIDINote(data1, data2, status === 144);
        }

        // Control change (176)
        if (status === 176) {
            this.handleMIDICC(data1, data2);
        }
    }

    private handleMIDINote(note: number, velocity: number, isNoteOn: boolean) {
        if (!isNoteOn) return;

        // Map notes to morphing
        const normalizedNote = note % 12;

        if (normalizedNote < 4) {
            this.morphToForm(0); // Blake
        } else if (normalizedNote < 8) {
            this.morphToForm(1); // Tesla
        } else {
            this.morphToForm(2); // Beatles
        }

        // Adjust intensity based on velocity
        const intensity = velocity / 127;
        this.vesselLayer.setIntensity(intensity);
        this.particleLayer.setIntensity(intensity);
    }

    private handleMIDICC(ccNumber: number, value: number) {
        const normalizedValue = value / 127;

        switch (ccNumber) {
            case 1: // Modulation wheel - portal warp
                this.setPortalWarp(normalizedValue);
                break;
            case 7: // Volume - overall intensity
                this.setGlobalIntensity(normalizedValue);
                break;
            case 10: // Pan - form selection
                if (normalizedValue < 0.33) {
                    this.morphToForm(0);
                } else if (normalizedValue < 0.66) {
                    this.morphToForm(1);
                } else {
                    this.morphToForm(2);
                }
                break;
            case 74: // Filter cutoff - particle intensity
                this.particleLayer.setIntensity(normalizedValue);
                break;
        }
    }

    public setPortalWarp(value: number) {
        // Apply portal warp effect to camera or viewing angle
        const angle = (value - 0.5) * Math.PI; // ±90 degrees
        this.camera.position.x = Math.sin(angle) * 8;
        this.camera.position.z = Math.cos(angle) * 8;
        this.camera.lookAt(0, 0, 0);

        this.updateActiveThinker(`Portal warp: ${Math.round(value * 100)}%`);
    }

    private setGlobalIntensity(intensity: number) {
        this.vesselLayer.setIntensity(intensity);
        this.emergentFormLayer.setIntensity(intensity);
        this.particleLayer.setIntensity(intensity);
        this.shadowLayer.setIntensity(intensity);

        this.updateActiveThinker(`Global intensity: ${Math.round(intensity * 100)}%`);
    }

    public reset() {
        this.vesselLayer.reset();
        this.emergentFormLayer.reset();
        this.particleLayer.reset();
        this.shadowLayer.reset();

        this.camera.position.set(0, 0, 8);
        this.camera.lookAt(0, 0, 0);

        this.updateActiveThinker('MMPA engine reset');
    }

    public resize() {
        const width = window.innerWidth;
        const height = window.innerHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(width, height);
    }

    private updateActiveThinker(message: string) {
        this.activeThinker = message;

        const activeThinkerEl = document.getElementById('active-thinker');
        if (activeThinkerEl) {
            activeThinkerEl.textContent = message;
        }

        console.log(`🎛️ MMPA: ${message}`);
    }

    // Shadow casting system access methods
    public getShadowCastingSystem() {
        return this.emergentFormLayer.getShadowCastingSystem();
    }

    public readShadowDataAtAngle(viewAngle: number, ringIndex?: number) {
        return this.emergentFormLayer.readShadowDataAtAngle(viewAngle, ringIndex);
    }

    public getShadowStatistics() {
        return this.emergentFormLayer.getShadowStatistics();
    }

    public clearShadowData() {
        this.emergentFormLayer.clearShadowData();
    }

    // Performance getters
    public getCurrentMode(): PerformanceMode {
        return this.currentMode;
    }

    public getActiveThinker(): string {
        return this.activeThinker;
    }

    public isEngineRunning(): boolean {
        return this.isRunning;
    }

    // Morph box functionality
    private morphBoxRenderer: THREE.WebGLRenderer | null = null;
    private morphBoxCamera: THREE.PerspectiveCamera | null = null;
    private morphBoxEnabled = false;

    public enableMorphBox(container: HTMLElement) {
        if (this.morphBoxEnabled) return;

        // Create separate renderer for the morph box
        this.morphBoxRenderer = new THREE.WebGLRenderer({
            antialias: true,
            powerPreference: 'high-performance',
            alpha: false
        });
        this.morphBoxRenderer.setSize(350, 350);
        this.morphBoxRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.morphBoxRenderer.shadowMap.enabled = true;
        this.morphBoxRenderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.morphBoxRenderer.setClearColor(0x000011, 1.0);

        // Create separate camera for the morph box with closer view
        this.morphBoxCamera = new THREE.PerspectiveCamera(
            60,
            1, // Square aspect ratio
            0.1,
            100
        );
        this.morphBoxCamera.position.set(0, 0, 5); // Closer view

        container.appendChild(this.morphBoxRenderer.domElement);
        this.morphBoxEnabled = true;

        this.updateActiveThinker('Morph box enabled');
        console.log('📦 Morph box renderer created');
    }

    public disableMorphBox() {
        if (!this.morphBoxEnabled || !this.morphBoxRenderer) return;

        // Remove canvas from container
        if (this.morphBoxRenderer.domElement.parentNode) {
            this.morphBoxRenderer.domElement.parentNode.removeChild(this.morphBoxRenderer.domElement);
        }

        // Dispose renderer
        this.morphBoxRenderer.dispose();
        this.morphBoxRenderer = null;
        this.morphBoxCamera = null;
        this.morphBoxEnabled = false;

        this.updateActiveThinker('Morph box disabled');
        console.log('📦 Morph box renderer removed');
    }
}