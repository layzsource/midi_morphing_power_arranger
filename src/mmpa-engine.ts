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
import { SkyboxMorphIntegration, createSkyboxMorphIntegration } from './mmpa/SkyboxMorphIntegration';
import { SkyboxCubeLayer, createSkyboxCubeLayer } from './layers/SkyboxCubeLayer_v5_testing';
import { paramGraphIntegration, MMPA_PARAM_PATHS } from './paramgraph/ParamGraphIntegration';
import { mmpaLogger } from './logging/MMPALogger';
import { webSocketMIDI } from './midi/WebSocketMIDIClient';

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

    // Complete skybox cube system
    private skyboxCubeLayer: SkyboxCubeLayer;
    private skyboxMorphIntegration: SkyboxMorphIntegration;

    // Performance state
    private currentMode: PerformanceMode = 'vj';
    private isRunning = false;
    private clock = new THREE.Clock();

    // MIDI state
    private midiAccess: any = null;
    private midiInputs: Map<string, any> = new Map();
    private activeThinker = 'MMPA ready';

    // Cube morphing state
    private cubeMorphingActive = false;
    private morphProgress = 0;

    constructor(container: HTMLElement) {
        console.log('🎛️ MMPA Engine starting...');
        mmpaLogger.startIteration('MMPA Engine initialization');
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
            1000
        );
        this.camera.position.set(0, 0, 0); // Start inside center of cube

        // Enable layer 2 for cube visibility (main camera only, not morph box)
        this.camera.layers.enable(2);

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
        // DISABLED: this.shadowLayer = new ShadowLayer(this.scene); // REMOVED - causes issues

        // Initialize complete skybox cube system
        this.skyboxCubeLayer = createSkyboxCubeLayer(this.scene);
        this.skyboxMorphIntegration = createSkyboxMorphIntegration(this.scene);
        console.log('🌀 Complete skybox cube system connected');
        console.log('🎭 6-panel cube with 12-tone fractal system ready');
        console.log('🧙 Wizard spells and consciousness navigation active');

        // Initialize ParamGraph integration
        this.initParamGraph();
    }

    private async initParamGraph() {
        try {
            await paramGraphIntegration.initialize();

            // Set up parameter change callbacks
            this.setupParamGraphCallbacks();

            console.log('🎛️ ParamGraph system integrated with MMPA');
        } catch (error) {
            console.warn('⚠️ ParamGraph initialization failed:', error);
        }
    }

    private setupParamGraphCallbacks() {
        // Cube to sphere morphing
        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.CUBE_SPHERE, (value) => {
            this.skyboxCubeLayer.handleMIDIControl(1, value * 127);
        });

        // Main viewport morphing
        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.MAIN_MORPH_BLEND, (value) => {
            // Route to skybox layer's morph function
            if (this.skyboxCubeLayer && this.skyboxCubeLayer.morphPanelSquareToCircle) {
                mmpaLogger.logMorph(value, 'main_viewport');
                this.skyboxCubeLayer.morphPanelSquareToCircle(value);
            }
        });

        // Aux viewport morphing
        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.AUX_MORPH_BLEND, (value) => {
            // Route to aux viewport morph when active
            if (paramGraphIntegration.getActiveViewport() === 'aux') {
                if (this.skyboxCubeLayer && this.skyboxCubeLayer.morphPanelSquareToCircle) {
                    mmpaLogger.logMorph(value, 'aux_viewport');
                    this.skyboxCubeLayer.morphPanelSquareToCircle(value);
                }
            }
        });

        // Main viewport rotations
        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.MAIN_VESSEL_ROT_X, (value) => {
            this.skyboxCubeLayer.handleMIDIControl(2, (value / 360) * 127);
        });

        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.MAIN_VESSEL_ROT_Y, (value) => {
            this.skyboxCubeLayer.handleMIDIControl(4, (value / 360) * 127);
        });

        // Aux viewport rotations (morph box)
        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.AUX_VESSEL_ROT_Y, (value) => {
            // Route to aux viewport when active
            if (paramGraphIntegration.getActiveViewport() === 'aux') {
                this.skyboxCubeLayer.handleMIDIControl(4, (value / 360) * 127);
            }
        });
    }

    private initAudio() {
        this.audioEngine = new AudioEngine();
    }

    public async initializeAudio(): Promise<void> {
        if (!this.audioEngine) {
            this.audioEngine = new AudioEngine();
        }
        try {
            await this.audioEngine.initialize();
            mmpaLogger.logSystemEvent('audio_initialized', 'Audio engine ready');
        } catch (error) {
            console.error('❌ Audio engine initialization failed:', error);
            mmpaLogger.logError('Audio engine initialization failed', 'audio_engine');
        }
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
            // DISABLED: this.shadowLayer.update(deltaTime, elapsedTime); // REMOVED

            // Render main scene (hide morph shapes if box is enabled)
            // Hide all morph shapes from main scene when morph box is enabled
            if (this.morphBoxEnabled) {
                this.vesselLayer.setVisible(false);
                this.emergentFormLayer.setVisible(false);
                this.particleLayer.setVisible(false);
            } else {
                // When morph box disabled, show everything in main scene except vessel
                this.vesselLayer.setVisible(false); // Vessel never in main scene
                this.emergentFormLayer.setVisible(true);
                this.particleLayer.setVisible(true);
            }

            this.renderer.render(this.scene, this.camera);

            // Render morph box if enabled - all morph shapes appear here
            if (this.morphBoxEnabled && this.morphBoxRenderer && this.morphBoxCamera) {
                this.vesselLayer.setVisible(true);
                this.emergentFormLayer.setVisible(true);
                this.particleLayer.setVisible(true);
                this.morphBoxRenderer.render(this.scene, this.morphBoxCamera);
                // Hide them again after rendering
                this.vesselLayer.setVisible(false);
                this.emergentFormLayer.setVisible(false);
                this.particleLayer.setVisible(false);
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

        // Connect to skybox cube morphing - when vessel moves, trigger cube/sphere morph
        if (enabled) {
            this.startCubeMorphing();
        } else {
            this.stopCubeMorphing();
        }
    }

    public rotateVessel(axis: 'x' | 'y' | 'z', angle: number) {
        switch (axis) {
            case 'x':
                this.vesselLayer.rotateX(angle);
                break;
            case 'y':
                this.vesselLayer.rotateY(angle);
                break;
            case 'z':
                this.vesselLayer.rotateZ(angle);
                break;
        }
    }

    public setVesselRotation(x: number, y: number, z: number) {
        this.vesselLayer.setRotation(x, y, z);
    }

    public getVesselRotation() {
        return this.vesselLayer.getRotation();
    }

    public processMIDIMessage(event: { data: number[] }) {
        this.handleMIDIMessage(event);
    }

    public processAudioAnalysis(analysis: { frequency: Float32Array, waveform: Float32Array, rms: number, peak: number, pitch: number }) {
        // Convert audio analysis to visual parameters
        const normalizedRMS = Math.min(analysis.rms * 10, 1.0); // Scale RMS for visual intensity
        const normalizedPeak = Math.min(analysis.peak, 1.0);

        // Drive vessel intensity with audio levels
        this.vesselLayer.setIntensity(0.3 + normalizedRMS * 0.7);

        // Use frequency data to drive particle effects
        if (analysis.frequency && analysis.frequency.length > 0) {
            const lowFreq = this.getFrequencyBand(analysis.frequency, 0, 0.1); // Bass
            const midFreq = this.getFrequencyBand(analysis.frequency, 0.1, 0.5); // Mids
            const highFreq = this.getFrequencyBand(analysis.frequency, 0.5, 1.0); // Highs

            // Map frequency bands to visual layers
            this.particleLayer.setIntensity(lowFreq);
            this.emergentFormLayer.setMorphProgress(midFreq);

            // Use pitch for vessel rotation speed if in motion
            if (this.vesselLayer.getMotionState() && analysis.pitch > 0) {
                const pitchNormalized = Math.log(analysis.pitch / 440) / Math.log(2); // Octaves from A4
                this.vesselLayer.setPulseRate(1.0 + pitchNormalized * 0.5);
            }
        }
    }

    private getFrequencyBand(frequencyData: Float32Array, startPercent: number, endPercent: number): number {
        const startIndex = Math.floor(startPercent * frequencyData.length);
        const endIndex = Math.floor(endPercent * frequencyData.length);

        let sum = 0;
        let count = 0;

        for (let i = startIndex; i < endIndex && i < frequencyData.length; i++) {
            // Convert from dB to linear scale
            const linearValue = Math.pow(10, frequencyData[i] / 20);
            sum += linearValue;
            count++;
        }

        return count > 0 ? Math.min(sum / count, 1.0) : 0;
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

        const attachInput = (input: any) => {
            if (!input || this.midiInputs.has(input.id)) {
                return;
            }

            if (typeof input.open === 'function') {
                input.open().catch((error: any) => {
                    console.warn('⚠️ Failed to open MIDI input:', input.name || input.id, error);
                });
            }

            input.onmidimessage = (event: any) => this.handleMIDIMessage(event);
            this.midiInputs.set(input.id, input);
            console.log(`🎚️ MIDI input connected: ${input.name || input.id}`);
        };

        midiAccess.inputs.forEach((input: any) => attachInput(input));

        midiAccess.onstatechange = (event: any) => {
            const port = event.port;
            if (!port || port.type !== 'input') {
                return;
            }

            if (port.state === 'connected') {
                attachInput(port);
            } else if (port.state === 'disconnected' && this.midiInputs.has(port.id)) {
                const existing = this.midiInputs.get(port.id);
                if (existing) {
                    existing.onmidimessage = null;
                }
                this.midiInputs.delete(port.id);
                console.log(`🔌 MIDI input disconnected: ${port.name || port.id}`);
            }
        };

        this.updateActiveThinker('MIDI controller connected');
    }

    private handleMIDIMessage(event: any) {
        const [status, data1, data2] = event.data;

        // Just make it work - process all MIDI
        console.log(`MIDI: ${status} ${data1} ${data2}`);

        // Control Change (176) - CC1 is mod wheel
        if (status === 176) {
            this.skyboxCubeLayer.handleMIDIControl(data1, data2);
            this.handleMIDICC(data1, data2);
        }

        // Notes (144=on, 128=off)
        if (status === 144 || status === 128) {
            this.handleMIDINote(data1, data2, status === 144);
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
        const windowId = webSocketMIDI.getWindowId();
        console.log(`🎛️ [${windowId}] ENGINE MIDI CC${ccNumber}: ${value} -> ${normalizedValue.toFixed(3)}`);

        // Route CC1 through ParamGraph system with window isolation
        if (ccNumber === 1) {
            const activeViewport = paramGraphIntegration.getActiveViewport();
            mmpaLogger.logMIDI(ccNumber, value, `${activeViewport}_window_${windowId}`);
            paramGraphIntegration.setMIDIInput(ccNumber, value);

            // PRESERVE DEADBAND LOGIC: Apply CC1 deadband system per MMPA baseline
            const deadbandMode = this.morphBoxEnabled ? 'morphbox' : 'main';
            this.handleCC1WithDeadband(value, deadbandMode);

            console.log(`🎛️ [${windowId}] CC1 routed with deadband to ${activeViewport} (${deadbandMode})`);
            return;
        }

        // Route MIDI CC to morph box if enabled, otherwise to main scene
        if (this.morphBoxEnabled) {
            this.handleMorphBoxMIDICC(ccNumber, normalizedValue);
        } else {
            this.handleMainSceneMIDICC(ccNumber, normalizedValue);
        }
    }

    // Public method for external MIDI input (WebSocket bridge)
    public handleExternalMIDICC(ccNumber: number, value: number) {
        console.log(`External MIDI CC${ccNumber}: ${value}`);
        this.handleMIDICC(ccNumber, value);
    }

    private handleMorphBoxMIDICC(ccNumber: number, normalizedValue: number) {
        // MIDI CC controls specifically for morph box panel
        // Only respond if morph box is properly enabled and initialized
        if (!this.morphBoxEnabled || !this.morphBoxCamera || !this.morphBoxRenderer) {
            return;
        }

        switch (ccNumber) {
            case 1: // Modulation wheel with deadband - vessel rotation (horizontal)
                this.handleCC1WithDeadband(normalizedValue * 127, 'morphbox');
                break;
            case 2: // Modulation wheel 2 - box camera vertical rotation
                if (this.morphBoxCamera) {
                    const verticalAngle = (normalizedValue - 0.5) * Math.PI; // ±90 degrees
                    const distance = 5; // Fixed distance
                    const currentHorizontalAngle = Math.atan2(this.morphBoxCamera.position.x, this.morphBoxCamera.position.z);

                    this.morphBoxCamera.position.y = Math.sin(verticalAngle) * distance;
                    this.morphBoxCamera.position.x = Math.sin(currentHorizontalAngle) * Math.cos(verticalAngle) * distance;
                    this.morphBoxCamera.position.z = Math.cos(currentHorizontalAngle) * Math.cos(verticalAngle) * distance;
                    this.morphBoxCamera.lookAt(0, 0, 0);
                }
                break;
            case 3: // CC3 - box camera roll rotation (z-axis)
                if (this.morphBoxCamera) {
                    const rollAngle = normalizedValue * Math.PI * 2; // 0-360 degrees
                    const up = new THREE.Vector3(0, 1, 0);
                    const forward = new THREE.Vector3(0, 0, 0).sub(this.morphBoxCamera.position).normalize();
                    const right = new THREE.Vector3().crossVectors(forward, up).normalize();
                    const newUp = new THREE.Vector3().crossVectors(right, forward).normalize();

                    // Apply roll rotation around the forward axis
                    const rollMatrix = new THREE.Matrix4().makeRotationAxis(forward, rollAngle);
                    newUp.applyMatrix4(rollMatrix);

                    this.morphBoxCamera.up.copy(newUp);
                    this.morphBoxCamera.lookAt(0, 0, 0);
                }
                break;
            case 7: // Volume - box scene intensity only
                this.vesselLayer.setIntensity(normalizedValue);
                this.emergentFormLayer.setIntensity(normalizedValue);
                this.particleLayer.setIntensity(normalizedValue);
                // DISABLED: this.shadowLayer.setIntensity(normalizedValue); // REMOVED SHADOW LAYER
                break;
            case 10: // Pan - form selection (affects box only)
                if (normalizedValue < 0.33) {
                    this.morphToForm(0);
                } else if (normalizedValue < 0.66) {
                    this.morphToForm(1);
                } else {
                    this.morphToForm(2);
                }
                break;
            case 74: // Filter cutoff - box camera zoom
                if (this.morphBoxCamera) {
                    const zoomDistance = 2 + (1 - normalizedValue) * 6; // 2-8 range
                    this.morphBoxCamera.position.setLength(zoomDistance);
                }
                break;
            case 8: // CC8 - Acid hue shift
                this.acidHueShift = normalizedValue * 360; // 0-360 degrees
                this.updateAcidEffects();
                break;
            case 9: // CC9 - Acid saturation boost
                this.acidSaturation = 1 + normalizedValue * 2; // 1-3x saturation
                this.updateAcidEffects();
                break;
            case 5: // CC5 - Main camera Z-axis zoom
                // Move camera along Z-axis: min = far back, max = close but not inside
                const zPosition = 999 - (normalizedValue * 998); // 999 -> 1 (stay outside cube)
                this.camera.position.z = zPosition;
                console.log(`🔍 CC5 Z-axis: ${normalizedValue.toFixed(3)} -> z=${zPosition.toFixed(1)}`);
                // Still forward to skybox layer for internal state
                this.skyboxCubeLayer.handleMIDIControl(5, normalizedValue * 127);
                break;
        }

        this.updateActiveThinker(`Morph box CC${ccNumber}: ${Math.round(normalizedValue * 100)}%`);
    }

    private handleMainSceneMIDICC(ccNumber: number, normalizedValue: number) {
        // Original MIDI CC controls for main scene
        switch (ccNumber) {
            case 1: // Modulation wheel - forward to skybox for morphing (no main engine processing)
                // Let the skybox layer handle CC1 morphing directly
                // this.handleCC1WithDeadband(normalizedValue * 127, 'main'); // DISABLED
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
            case 5: // CC5 - Main camera Z-axis zoom
                // Move camera along Z-axis: min = far back, max = close but not inside
                const zPosition = 999 - (normalizedValue * 998); // 999 -> 1 (stay outside cube)
                this.camera.position.z = zPosition;
                console.log(`🔍 CC5 Z-axis: ${normalizedValue.toFixed(3)} -> z=${zPosition.toFixed(1)}`);
                // Still forward to skybox layer for internal state
                this.skyboxCubeLayer.handleMIDIControl(5, normalizedValue * 127);
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
        this.camera.position.y = 0;
        this.camera.lookAt(0, 0, 0);

        this.updateActiveThinker(`Portal warp: ${Math.round(value * 100)}%`);
    }

    // Continuous motion state for MIDI CC1 deadband system
    private cc1ContinuousMotion: { active: boolean, speed: number, mode: 'main' | 'morphbox' | null } = { active: false, speed: 0, mode: null };
    private cc1AnimationFrame: number | null = null;

    // MMPA Baseline MIDI CC1 Deadband System
    // Based on /Users/ticegunther/Downloads/MMPA_Baseline/midi/mappings.json
    private handleCC1WithDeadband(ccValue: number, mode: 'main' | 'morphbox') {
        const windowId = webSocketMIDI.getWindowId();
        // MMPA Baseline deadband specification:
        // Left: 0-52 → negative action (continuous motion)
        // Hold: 53-73 → neutral/snap zone (stop motion)
        // Right: 74-127 → positive action (continuous motion)

        if (ccValue <= 52) {
            // Left zone - start continuous rotation/action left
            const normalizedLeft = ccValue / 52; // 0 to 1
            console.log(`🎛️ [${windowId}] CC1 deadband: LEFT (${ccValue}) -> ${normalizedLeft.toFixed(3)} (${mode})`);
            this.startCC1ContinuousMotion(-normalizedLeft, mode);
        } else if (ccValue >= 74) {
            // Right zone - start continuous rotation/action right
            const normalizedRight = (ccValue - 74) / (127 - 74); // 0 to 1
            console.log(`🎛️ [${windowId}] CC1 deadband: RIGHT (${ccValue}) -> ${normalizedRight.toFixed(3)} (${mode})`);
            this.startCC1ContinuousMotion(normalizedRight, mode);
        } else {
            // Deadband zone (53-73) - stop continuous motion
            console.log(`🎛️ [${windowId}] CC1 deadband: HOLD (${ccValue}) - stopping motion (${mode})`);
            this.stopCC1ContinuousMotion();
        }
    }

    private startCC1ContinuousMotion(speed: number, mode: 'main' | 'morphbox') {
        // Stop any existing motion
        this.stopCC1ContinuousMotion();

        // Start new continuous motion
        this.cc1ContinuousMotion = { active: true, speed, mode };

        const animate = () => {
            if (this.cc1ContinuousMotion.active) {
                this.applyCC1Action(this.cc1ContinuousMotion.speed, this.cc1ContinuousMotion.mode);
                this.cc1AnimationFrame = requestAnimationFrame(animate);
            }
        };
        animate();
    }

    private stopCC1ContinuousMotion() {
        this.cc1ContinuousMotion.active = false;
        if (this.cc1AnimationFrame !== null) {
            cancelAnimationFrame(this.cc1AnimationFrame);
            this.cc1AnimationFrame = null;
        }
    }

    private applyCC1Action(normalizedValue: number, mode: 'main' | 'morphbox') {
        if (mode === 'main') {
            // Main scene: Portal warp with deadband
            const portalValue = (normalizedValue + 1) / 2; // Convert -1,1 to 0,1
            this.setPortalWarp(portalValue);
        } else if (mode === 'morphbox') {
            // Morph box: Vessel rotation with deadband
            if (this.morphBoxCamera) {
                // Bidirectional rotation based on normalized value
                const rotationSpeed = 0.02; // Rotation speed factor
                const currentAngle = Math.atan2(this.morphBoxCamera.position.x, this.morphBoxCamera.position.z);
                const newAngle = currentAngle + (normalizedValue * rotationSpeed);
                const distance = 5;

                this.morphBoxCamera.position.x = Math.sin(newAngle) * distance;
                this.morphBoxCamera.position.z = Math.cos(newAngle) * distance;
                this.morphBoxCamera.lookAt(0, 0, 0);
            }
        }
    }

    private setGlobalIntensity(intensity: number) {
        this.vesselLayer.setIntensity(intensity);
        this.emergentFormLayer.setIntensity(intensity);
        this.particleLayer.setIntensity(intensity);
        // DISABLED: this.shadowLayer.setIntensity(intensity); // REMOVED SHADOW LAYER

        this.updateActiveThinker(`Global intensity: ${Math.round(intensity * 100)}%`);
    }

    public reset() {
        this.vesselLayer.reset();
        this.emergentFormLayer.reset();
        this.particleLayer.reset();
        // DISABLED: this.shadowLayer.reset(); // REMOVED SHADOW LAYER

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

    // Acid effects for morph box
    private acidHueShift = 0;
    private acidSaturation = 1;

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

    private updateAcidEffects() {
        if (!this.morphBoxRenderer) return;

        // Apply CSS filters to the morph box canvas for acid effects
        const canvas = this.morphBoxRenderer.domElement;
        canvas.style.filter = `
            hue-rotate(${this.acidHueShift}deg)
            saturate(${this.acidSaturation})
            contrast(${1 + this.acidSaturation * 0.2})
            brightness(${1 + this.acidSaturation * 0.1})
        `;
    }

    private hideMainSceneMorphShapes() {
        // Temporarily hide morph shapes from main scene
        this.vesselLayer.setVisible(false);
        this.emergentFormLayer.setVisible(false);
        this.particleLayer.setVisible(false);
    }

    private showMainSceneMorphShapes() {
        // Restore morph shapes to main scene
        this.vesselLayer.setVisible(true);
        this.emergentFormLayer.setVisible(true);
        this.particleLayer.setVisible(true);
    }

    private startCubeMorphing() {
        this.cubeMorphingActive = true;

        // Start immediate dramatic morphing
        const morphAnimation = () => {
            if (this.cubeMorphingActive && this.morphProgress < 1.0) {
                this.morphProgress += 0.02; // Faster morph - 2 seconds to sphere
                this.skyboxCubeLayer.setMorphProgress(this.morphProgress);
                console.log(`🌀 Morphing progress: ${(this.morphProgress * 100).toFixed(1)}%`);
                requestAnimationFrame(morphAnimation);
            } else if (this.cubeMorphingActive && this.morphProgress >= 1.0) {
                console.log('🌟 Cube→Sphere morph complete! Starting mode cycling...');
                // Start cycling between modes
                this.cycleMorphModes();
            }
        };

        morphAnimation();
        console.log('🎭 Cube→Sphere morphing started with progressive animation');
    }

    private stopCubeMorphing() {
        this.cubeMorphingActive = false;
        this.morphProgress = 0;
        this.skyboxCubeLayer.setMorphProgress(0); // Reset to cube
        console.log('🎭 Cube morphing stopped - reset to cube form');
    }

    private cycleMorphModes() {
        if (!this.cubeMorphingActive) return;

        // Cycle through different consciousness modes
        const modes = ['cube', 'morphing', 'sphere', 'fractal'];
        let currentModeIndex = 0;

        const cycleMode = () => {
            if (!this.cubeMorphingActive) return;

            const mode = modes[currentModeIndex];

            switch (mode) {
                case 'cube':
                    this.skyboxCubeLayer.setMorphProgress(0);
                    this.skyboxCubeLayer.handleMicrotonalMorph(false);
                    break;
                case 'morphing':
                    this.skyboxCubeLayer.setMorphProgress(0.5);
                    break;
                case 'sphere':
                    this.skyboxCubeLayer.setMorphProgress(1.0);
                    break;
                case 'fractal':
                    this.skyboxCubeLayer.handleMicrotonalMorph(true);
                    this.skyboxCubeLayer.castWizardSpell('chromatic_resonance', { note: 'A' });
                    break;
            }

            console.log(`🌀 Consciousness mode: ${mode}`);
            currentModeIndex = (currentModeIndex + 1) % modes.length;

            // Continue cycling every 4 seconds
            setTimeout(() => {
                if (this.cubeMorphingActive) {
                    cycleMode();
                }
            }, 4000);
        };

        cycleMode();
    }

    // Public access methods for skybox cube layer
    public getSkyboxCubeLayer(): SkyboxCubeLayer {
        return this.skyboxCubeLayer;
    }

    public getSkyboxLayer(): SkyboxCubeLayer {
        return this.skyboxCubeLayer;
    }

    // Public access method for scene
    public getScene(): THREE.Scene {
        return this.scene;
    }

    // Public access method for ParamGraph integration
    public getParamGraphIntegration() {
        return paramGraphIntegration;
    }

    public castWizardSpell(spellName: string, parameters: any = {}): void {
        this.skyboxCubeLayer.castWizardSpell(spellName, parameters);
        console.log(`🧙 Cast spell: ${spellName}`);
    }
}