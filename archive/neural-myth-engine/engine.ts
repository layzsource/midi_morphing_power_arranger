import * as THREE from 'three';
import { VesselLayer } from './layers/VesselLayer';
import { EmergentFormLayer } from './layers/EmergentFormLayer';
import { ParticleLayer } from './layers/ParticleLayer';
import { ShadowLayer } from './layers/ShadowLayer';
import { SignalGrammar } from './signals/SignalGrammar';
import { CoreLibrary } from './library/CoreLibrary';
import { AudioEngine } from './audio/AudioEngine';
import { SequenceRecorder } from './performance/SequenceRecorder';
import { PresetManager } from './performance/PresetManager';
import { EasterEggRenderer } from './visuals/EasterEggRenderer';
import { TimeEvolution } from './temporal/TimeEvolution';

export type PerformanceMode = 'club' | 'installation' | 'instrument';

export class Engine {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private container: HTMLElement;

    // Archetypal Layers
    private vesselLayer: VesselLayer;
    private emergentFormLayer: EmergentFormLayer;
    private particleLayer: ParticleLayer;
    private shadowLayer: ShadowLayer;

    // Signal processing
    private signalGrammar: SignalGrammar;
    private coreLibrary: CoreLibrary;
    private audioEngine: AudioEngine;
    private sequenceRecorder: SequenceRecorder;
    private presetManager: PresetManager;
    private easterEggRenderer: EasterEggRenderer;
    private timeEvolution: TimeEvolution;

    // Performance state
    private currentMode: PerformanceMode = 'club';
    private isRunning = false;
    private clock = new THREE.Clock();

    constructor(container: HTMLElement) {
        this.container = container;
        this.initThreeJS();
        this.initLayers();
        this.initSignalProcessing();
        this.setupLighting();
    }

    private initThreeJS() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000000);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        // 2025 camera positioning - more cinematic, spatial computing inspired
        this.camera.position.set(2, 3, 10);
        this.camera.lookAt(0, 0, 0);
        this.camera.fov = 45; // Tighter field of view for more premium feel

        // Modern renderer with enhanced settings
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            powerPreference: "high-performance"
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.renderer.physicallyCorrectLights = true;

        this.container.appendChild(this.renderer.domElement);
    }

    private initLayers() {
        // Initialize the four archetypal layers
        this.vesselLayer = new VesselLayer(this.scene);
        this.emergentFormLayer = new EmergentFormLayer(this.scene);
        this.particleLayer = new ParticleLayer(this.scene);
        this.shadowLayer = new ShadowLayer(this.scene);
    }

    private initSignalProcessing() {
        this.signalGrammar = new SignalGrammar();
        this.coreLibrary = new CoreLibrary();
        this.audioEngine = new AudioEngine();
        this.sequenceRecorder = new SequenceRecorder();
        this.presetManager = new PresetManager();
        this.easterEggRenderer = new EasterEggRenderer(this.scene);
        this.timeEvolution = new TimeEvolution();

        // Connect signal grammar to layers
        this.signalGrammar.onSignal(async (signal) => {
            await this.processSignal(signal);
        });

        // Connect sequence recorder to performance system
        this.sequenceRecorder.onEvent(async (event) => {
            await this.handleSequenceEvent(event);
        });

        // Connect preset manager to apply presets
        this.presetManager.onPresetChange((preset) => {
            this.applyPreset(preset);
        });

        // Connect time evolution
        this.timeEvolution.onPhaseChange((phase) => {
            this.applyTimePhase(phase);
        });

        this.timeEvolution.onSeasonChange((season) => {
            this.applySeasonalInfluence(season);
        });

        this.timeEvolution.onEvolutionUpdate((evolution) => {
            this.handleEvolutionUpdate(evolution);
        });
    }

    private setupLighting() {
        // Modern ambient lighting with subtle color temperature
        const ambientLight = new THREE.AmbientLight(0xb3e5fc, 0.08);
        this.scene.add(ambientLight);

        // Key directional light - clean, contemporary
        const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);
        keyLight.position.set(8, 10, 5);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 4096;
        keyLight.shadow.mapSize.height = 4096;
        keyLight.shadow.camera.near = 0.1;
        keyLight.shadow.camera.far = 50;
        keyLight.shadow.camera.left = -10;
        keyLight.shadow.camera.right = 10;
        keyLight.shadow.camera.top = 10;
        keyLight.shadow.camera.bottom = -10;
        keyLight.shadow.bias = -0.0001;
        this.scene.add(keyLight);

        // Fill light - soft blue
        const fillLight = new THREE.DirectionalLight(0x64b5f6, 0.4);
        fillLight.position.set(-8, 5, -5);
        this.scene.add(fillLight);

        // Rim light for separation
        const rimLight = new THREE.DirectionalLight(0xe1bee7, 0.3);
        rimLight.position.set(0, -8, 8);
        this.scene.add(rimLight);

        // Contemporary point lights - accent lighting
        const accent1 = new THREE.PointLight(0x2196f3, 1.2, 15, 2);
        accent1.position.set(-6, 4, 3);
        this.scene.add(accent1);

        const accent2 = new THREE.PointLight(0x9c27b0, 0.8, 12, 2);
        accent2.position.set(6, -2, -3);
        this.scene.add(accent2);

        // Environment light simulation
        const hemiLight = new THREE.HemisphereLight(0xe3f2fd, 0x263238, 0.2);
        this.scene.add(hemiLight);
    }

    private async processSignal(signal: any) {
        // Route signals to appropriate layers based on type
        switch (signal.type) {
            case 'frequency':
                this.vesselLayer.processFrequency(signal);
                this.emergentFormLayer.processFrequency(signal);
                break;
            case 'midi':
                this.particleLayer.processMIDI(signal);

                // Trigger audio for MIDI archetype signals
                if (signal.trigger) {
                    const velocity = signal.amplitude || 0.8;
                    await this.audioEngine.playArchetype(signal.trigger, velocity);
                    this.updateActiveThinker(this.getArchetypeName(signal.trigger));

                    // Record archetype activation for conversations
                    this.archetypeConversations.recordActivation(signal.trigger);
                }
                break;
            case 'beat':
                this.particleLayer.processBeat(signal);
                break;
            case 'silence':
                this.shadowLayer.processSignal(signal);
                break;
        }

        // Check for Core Library easter eggs
        this.coreLibrary.checkForTriggers(signal);
    }

    private getArchetypeName(trigger: string): string {
        const names: { [key: string]: string } = {
            'russell': 'Walter Russell',
            'blake': 'William Blake',
            'tesla': 'Nikola Tesla',
            'beatles': 'The Beatles',
            'leadbelly': 'Lead Belly',
            'hawking': 'Stephen Hawking',
            'pranksters': 'Merry Pranksters',
            'hoffman': 'Abbie Hoffman',
            'waas': 'Les Waas',
            'greiff': 'Constance Greiff'
        };
        return names[trigger] || trigger;
    }

    private async handleSequenceEvent(event: any) {
        switch (event.type) {
            case 'archetype':
                this.coreLibrary.triggerArchetype(event.data.archetype);
                await this.audioEngine.playArchetype(event.data.archetype, event.data.velocity || 0.8);
                this.updateActiveThinker(this.getArchetypeName(event.data.archetype));

                // Record archetype activation for conversations
                this.archetypeConversations.recordActivation(event.data.archetype);
                break;
            case 'mode':
                this.setMode(event.data.mode);
                break;
            case 'beat':
                this.signalGrammar.triggerBeat(event.data.velocity || 0.8);
                break;
            case 'stop':
                this.audioEngine.stopAll();
                break;
        }
    }

    private applyPreset(preset: any) {
        console.log(`🎭 Applying preset: ${preset.name}`);

        // Apply mode
        this.setMode(preset.mode);

        // Apply layer intensities
        this.vesselLayer.setIntensity(preset.vesselLayer.intensity);
        this.emergentFormLayer.setSpeed(preset.emergentFormLayer.speed || 0.8);
        this.emergentFormLayer.setIntensity(preset.emergentFormLayer.intensity);
        this.particleLayer.setIntensity(preset.particleLayer.intensity);
        this.shadowLayer.setIntensity(preset.shadowLayer.intensity);

        // Apply audio settings
        this.audioEngine.setMasterVolume(preset.audioSettings.masterVolume);

        // Update BPM for sequences
        this.sequenceRecorder.setBPM(preset.bpm);

        // Auto-play sequences if specified
        if (preset.sequences && preset.sequences.length > 0) {
            setTimeout(() => {
                preset.sequences.forEach((sequenceId: string, index: number) => {
                    setTimeout(() => {
                        this.sequenceRecorder.playSequence(sequenceId);
                    }, index * 100);
                });
            }, 500);
        }

        this.updateActiveThinker(`Loaded: ${preset.name}`);
    }

    private displayHALMessage(response: any) {
        // Display HAL's message in the UI
        const halMessageEl = document.getElementById('hal-message');
        if (halMessageEl) {
            halMessageEl.textContent = response.message;
            halMessageEl.style.color = this.getPersonaColor(response.persona);
            halMessageEl.style.display = 'block';

            // Hide after duration
            setTimeout(() => {
                halMessageEl.style.display = 'none';
            }, response.duration);
        }

        console.log(`🤖 HAL (${response.persona}): ${response.message}`);
    }

    private executeHALAction(action: any) {
        switch (action.type) {
            case 'trigger_archetype':
                this.coreLibrary.triggerArchetype(action.data.archetype);
                this.audioEngine.playArchetype(action.data.archetype, 0.7);
                this.updateActiveThinker(`HAL → ${this.getArchetypeName(action.data.archetype)}`);

                // Record archetype activation for conversations
                this.archetypeConversations.recordActivation(action.data.archetype);
                break;
            case 'create_silence':
                this.audioEngine.stopAll();
                setTimeout(() => {
                    this.halPersonas.updateContext({ silenceDetected: true });
                }, action.data.duration);
                break;
            case 'modify_layers':
                // HAL adjusts layer parameters
                if (action.data.layer && action.data.parameter) {
                    this.adjustLayerParameter(action.data.layer, action.data.parameter, action.data.value);
                }
                break;
        }
    }

    private getPersonaColor(persona: string): string {
        const colors: { [key: string]: string } = {
            'oracle': '#ffd700',        // Gold
            'trickster': '#ff69b4',     // Hot pink
            'cosmic_narrator': '#9370db', // Medium purple
            'silent_shadow': '#696969'   // Dim gray
        };
        return colors[persona] || '#ffffff';
    }

    private adjustLayerParameter(layer: string, parameter: string, value: number) {
        switch (layer) {
            case 'vessel':
                if (parameter === 'intensity') this.vesselLayer.setIntensity(value);
                break;
            case 'emergent':
                if (parameter === 'speed') this.emergentFormLayer.setSpeed(value);
                break;
            case 'particles':
                if (parameter === 'intensity') this.particleLayer.setIntensity(value);
                break;
            case 'shadow':
                if (parameter === 'intensity') this.shadowLayer.setIntensity(value);
                break;
        }
    }

    public setMode(mode: PerformanceMode) {
        this.currentMode = mode;

        // Adjust layers based on performance mode
        switch (mode) {
            case 'club':
                this.setupClubMode();
                break;
            case 'installation':
                this.setupInstallationMode();
                break;
            case 'instrument':
                this.setupInstrumentMode();
                break;
        }

        this.updateUI();
    }

    private setupClubMode() {
        // High energy, rhythmic, strobing
        this.vesselLayer.setIntensity(0.8);
        this.particleLayer.setIntensity(1.0);
        this.emergentFormLayer.setSpeed(1.5);
        this.shadowLayer.setIntensity(0.6);
    }

    private setupInstallationMode() {
        // Ambient, contemplative, slow morphing
        this.vesselLayer.setIntensity(0.4);
        this.particleLayer.setIntensity(0.3);
        this.emergentFormLayer.setSpeed(0.3);
        this.shadowLayer.setIntensity(0.8);
    }

    private setupInstrumentMode() {
        // Expressive, responsive, intimate
        this.vesselLayer.setIntensity(0.6);
        this.particleLayer.setIntensity(0.7);
        this.emergentFormLayer.setSpeed(0.8);
        this.shadowLayer.setIntensity(0.5);
    }

    public async handleKeyPress(key: string) {
        const archetypeMap: { [key: string]: string } = {
            '1': 'russell', '2': 'blake', '3': 'tesla', '4': 'beatles', '5': 'leadbelly',
            '6': 'hawking', '7': 'pranksters', '8': 'hoffman', '9': 'waas', '0': 'greiff'
        };

        // Record the event if recording
        if (archetypeMap[key]) {
            const archetype = archetypeMap[key];
            this.sequenceRecorder.recordEvent('archetype', { archetype, velocity: 0.8 });

            this.coreLibrary.triggerArchetype(archetype);
            await this.audioEngine.playArchetype(archetype);
            this.updateActiveThinker(this.getArchetypeName(archetype));

            // Record archetype activation for conversations
            this.archetypeConversations.recordActivation(archetype);

            // Notify HAL about archetype activation
            this.halPersonas.triggerArchetypeResponse(archetype);
            return;
        }

        // Live performance controls
        switch (key.toLowerCase()) {
            case ' ':
                this.sequenceRecorder.recordEvent('beat', { velocity: 0.8 });
                this.signalGrammar.triggerBeat();
                this.updateActiveThinker('Beat Trigger');
                break;
            case 'r':
                this.resetScene();
                this.audioEngine.stopAll();
                this.sequenceRecorder.stopPlayback();
                this.updateActiveThinker('Reset');
                break;
            case 's':
                this.audioEngine.stopAll();
                this.sequenceRecorder.stopPlayback();
                this.updateActiveThinker('Stop All Audio');
                break;
            // Sequence controls
            case 'f1':
                if (this.sequenceRecorder.isCurrentlyRecording()) {
                    const recorded = this.sequenceRecorder.stopRecording();
                    this.updateActiveThinker(`Saved: ${recorded?.name || 'Sequence'}`);
                } else {
                    this.sequenceRecorder.startRecording('New Sequence', 120);
                    this.updateActiveThinker('Recording...');
                }
                break;
            case 'f2':
                this.sequenceRecorder.playSequence('welcome');
                this.updateActiveThinker('Playing: Welcome');
                break;
            case 'f3':
                this.sequenceRecorder.playSequence('cosmic');
                this.updateActiveThinker('Playing: Cosmic');
                break;
            case 'f4':
                this.sequenceRecorder.layerSequence('welcome');
                this.updateActiveThinker('Layering: Welcome');
                break;
            case 'f5':
                this.sequenceRecorder.playSequence('welcome', true);
                this.updateActiveThinker('Looping: Welcome');
                break;
            // Preset controls
            case 'f6':
                this.presetManager.loadPreset('club-default');
                break;
            case 'f7':
                this.presetManager.loadPreset('installation-default');
                break;
            case 'f8':
                this.presetManager.loadPreset('instrument-default');
                break;
            case 'f9':
                this.presetManager.loadPreset('chaos-experiment');
                break;
            case 'f10':
                const presetId = this.presetManager.saveCurrentAsPreset(
                    `Performance ${new Date().toLocaleTimeString()}`,
                    'Live performance capture',
                    ['live', 'captured']
                );
                this.updateActiveThinker('Preset Saved');
                break;
            // HAL controls
            case 'h':
                this.halPersonas.forcePersonaShift('trickster');
                this.updateActiveThinker('HAL → Trickster');
                break;
            case 'j':
                this.halPersonas.forcePersonaShift('oracle');
                this.updateActiveThinker('HAL → Oracle');
                break;
            case 'k':
                this.halPersonas.forcePersonaShift('cosmic_narrator');
                this.updateActiveThinker('HAL → Cosmic Narrator');
                break;
            case 'l':
                this.halPersonas.forcePersonaShift('silent_shadow');
                this.updateActiveThinker('HAL → Silent Shadow');
                break;
            case 'u':
                this.halPersonas.createSpontaneousResponse();
                break;
            // Time evolution controls
            case 'i':
                if (this.currentMode === 'installation') {
                    if (this.timeEvolution.isInstallationActive()) {
                        this.timeEvolution.stopInstallationMode();
                        this.updateActiveThinker('Installation Stopped');
                    } else {
                        this.timeEvolution.startInstallationMode(10); // 10 minute installation
                        this.updateActiveThinker('Installation Started (10 min)');
                    }
                }
                break;
            case 'o':
                const isEnabled = this.timeEvolution.isEvolutionEnabled();
                this.timeEvolution.setEvolutionEnabled(!isEnabled);
                this.updateActiveThinker(`Time Evolution: ${!isEnabled ? 'On' : 'Off'}`);
                break;
        }
    }

    public connectMIDI(midiAccess: MIDIAccess) {
        this.signalGrammar.connectMIDI(midiAccess);
    }

    private resetScene() {
        this.vesselLayer.reset();
        this.emergentFormLayer.reset();
        this.particleLayer.reset();
        this.shadowLayer.reset();
        this.easterEggRenderer.clearAllEasterEggs();
    }

    private updateUI() {
        const currentModeEl = document.getElementById('current-mode');
        if (currentModeEl) {
            currentModeEl.textContent = this.currentMode.charAt(0).toUpperCase() + this.currentMode.slice(1);
        }

        // Update easter egg count
        const easterEggCountEl = document.getElementById('easter-egg-count');
        if (easterEggCountEl) {
            easterEggCountEl.textContent = this.coreLibrary.getActiveEasterEggs().length.toString();
        }

        // Update signal status
        const signalStatusEl = document.getElementById('signal-status');
        if (signalStatusEl) {
            signalStatusEl.textContent = this.isRunning ? 'Listening...' : 'Ready';
        }

        // Update recording status
        const recordingStatusEl = document.getElementById('recording-status');
        if (recordingStatusEl) {
            if (this.sequenceRecorder.isCurrentlyRecording()) {
                recordingStatusEl.textContent = `Recording: ${this.sequenceRecorder.getCurrentSequenceName()}`;
                recordingStatusEl.style.color = '#ff4444';
            } else if (this.sequenceRecorder.isCurrentlyPlaying()) {
                recordingStatusEl.textContent = 'Playing';
                recordingStatusEl.style.color = '#44ff44';
            } else {
                recordingStatusEl.textContent = 'Off';
                recordingStatusEl.style.color = '#ffffff';
            }
        }

        // Update current preset
        const currentPresetEl = document.getElementById('current-preset');
        if (currentPresetEl) {
            const currentPreset = this.presetManager.getCurrentPreset();
            currentPresetEl.textContent = currentPreset ? currentPreset.name : 'None';
        }

        // Update active easter eggs
        const activeEggsEl = document.getElementById('active-eggs');
        if (activeEggsEl) {
            const activeEggs = this.easterEggRenderer.getActiveEasterEggs();
            activeEggsEl.textContent = activeEggs.length > 0 ? activeEggs.join(', ') : 'None';
        }

        // Update time evolution status
        const timePhaseEl = document.getElementById('time-phase');
        if (timePhaseEl) {
            const currentPhase = this.timeEvolution.getCurrentPhase();
            timePhaseEl.textContent = currentPhase ? currentPhase.name : 'Unknown';
        }

        const currentSeasonEl = document.getElementById('current-season');
        if (currentSeasonEl) {
            const currentSeason = this.timeEvolution.getCurrentSeason();
            currentSeasonEl.textContent = currentSeason ? currentSeason.season : 'Unknown';
        }
    }

    private updateActiveThinker(thinkerName: string) {
        const activeThinkerEl = document.getElementById('active-thinker');
        if (activeThinkerEl) {
            activeThinkerEl.textContent = thinkerName;

            // Clear after 3 seconds
            setTimeout(() => {
                if (activeThinkerEl) {
                    activeThinkerEl.textContent = 'None';
                }
            }, 3000);
        }
    }

    public start() {
        this.isRunning = true;
        this.signalGrammar.start();
        this.animate();
    }

    public stop() {
        this.isRunning = false;
        this.signalGrammar.stop();
    }

    private animate = () => {
        if (!this.isRunning) return;

        requestAnimationFrame(this.animate);

        const deltaTime = this.clock.getDelta();
        const elapsedTime = this.clock.getElapsedTime();

        // Update all layers
        this.vesselLayer.update(deltaTime, elapsedTime);
        this.emergentFormLayer.update(deltaTime, elapsedTime);
        this.particleLayer.update(deltaTime, elapsedTime);
        this.shadowLayer.update(deltaTime, elapsedTime);
        this.easterEggRenderer.update(deltaTime, elapsedTime);

        // Update HAL context
        this.halPersonas.updateContext({
            currentMode: this.currentMode,
            timeElapsed: elapsedTime * 1000,
            easterEggsActive: this.easterEggRenderer.getActiveEasterEggs().length,
            performanceIntensity: this.calculatePerformanceIntensity(),
            silenceDetected: false // Would be updated by audio analysis
        });

        // Update UI
        this.updateUI();

        // Render
        this.renderer.render(this.scene, this.camera);
    };

    public resize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    public setVesselMotion(enabled: boolean) {
        this.vesselLayer.setMotion(enabled);
    }

    private calculatePerformanceIntensity(): number {
        // Calculate overall performance intensity based on various factors
        let intensity = 0;

        // Factor in mode intensity
        switch (this.currentMode) {
            case 'club': intensity += 0.8; break;
            case 'installation': intensity += 0.3; break;
            case 'instrument': intensity += 0.6; break;
        }

        // Factor in active easter eggs
        intensity += this.easterEggRenderer.getActiveEasterEggs().length * 0.1;

        // Factor in recording/playback activity
        if (this.sequenceRecorder.isCurrentlyRecording()) intensity += 0.3;
        if (this.sequenceRecorder.isCurrentlyPlaying()) intensity += 0.2;

        return Math.min(intensity, 1.0);
    }

    private applyTimePhase(phase: any) {
        console.log(`🕐 Applying time phase: ${phase.name}`);

        // Apply layer intensities based on time
        const layerSettings = this.timeEvolution.getTimeBasedLayerSettings();
        this.vesselLayer.setIntensity(layerSettings.vessel || 0.5);
        this.emergentFormLayer.setSpeed(layerSettings.emergent || 0.5);
        this.particleLayer.setIntensity(layerSettings.particles || 0.5);
        this.shadowLayer.setIntensity(layerSettings.shadow || 0.5);

        // Apply audio settings
        const audioSettings = phase.characteristics.audioSettings;
        this.audioEngine.setMasterVolume(audioSettings.masterVolume || -10);

        // Update HAL personality based on time
        if (phase.name.includes('Night')) {
            this.halPersonas.forcePersonaShift('oracle');
        } else if (phase.name.includes('Day')) {
            this.halPersonas.forcePersonaShift('trickster');
        }

        this.updateActiveThinker(`Time: ${phase.name}`);
    }

    private applySeasonalInfluence(season: any) {
        console.log(`🌱 Applying seasonal influence: ${season.season}`);

        // Seasonal influences are more subtle - affect probabilities and tendencies
        this.updateActiveThinker(`Season: ${season.season}`);
    }

    private handleEvolutionUpdate(evolution: any) {
        // Handle installation mode evolution
        if (evolution.installationProgress !== undefined) {
            this.handleInstallationEvolution(evolution);
        }

        // Auto-trigger based on time
        if (this.timeEvolution.shouldAutoTrigger()) {
            const archetype = this.timeEvolution.getRandomArchetypeForCurrentTime();
            setTimeout(() => {
                this.triggerArchetypeAutomatically(archetype);
            }, Math.random() * 5000); // Random delay up to 5 seconds
        }
    }

    private handleInstallationEvolution(evolution: any) {
        const progress = evolution.installationProgress;
        const intensity = evolution.installationIntensity;
        const phase = evolution.installationPhase;

        // Adjust layers based on installation evolution
        this.vesselLayer.setIntensity(intensity * 0.6);
        this.emergentFormLayer.setSpeed(intensity * 0.8);
        this.particleLayer.setIntensity(intensity * 0.4);
        this.shadowLayer.setIntensity((1 - intensity) * 0.8); // Inverse for shadows

        // Auto-trigger archetypes based on installation phase
        switch (phase) {
            case 'awakening':
                if (Math.random() < 0.1) this.triggerArchetypeAutomatically('russell');
                break;
            case 'exploration':
                if (Math.random() < 0.2) this.triggerArchetypeAutomatically('blake');
                break;
            case 'development':
                if (Math.random() < 0.3) this.triggerArchetypeAutomatically('tesla');
                break;
            case 'climax':
                if (Math.random() < 0.4) this.triggerArchetypeAutomatically('hawking');
                break;
            case 'resolution':
                if (Math.random() < 0.2) this.triggerArchetypeAutomatically('beatles');
                break;
            case 'transcendence':
                if (Math.random() < 0.1) this.triggerArchetypeAutomatically('greiff');
                break;
        }

        this.updateActiveThinker(`Installation: ${phase} (${Math.round(progress * 100)}%)`);
    }

    private async triggerArchetypeAutomatically(archetype: string) {
        // Auto-trigger with visual indication
        this.coreLibrary.triggerArchetype(archetype);
        await this.audioEngine.playArchetype(archetype, 0.6); // Quieter for auto-triggers
        this.halPersonas.triggerArchetypeResponse(archetype);

        // Record archetype activation for conversations
        this.archetypeConversations.recordActivation(archetype);

        this.updateActiveThinker(`Auto: ${this.getArchetypeName(archetype)}`);
    }

    private setupArchetypeConversations() {
        // Set up conversation callbacks
        this.archetypeConversations.onConversation((conversation: any) => {
            if (conversation.type === 'layer_interaction') {
                // Handle layer interactions
                this.handleLayerInteraction(conversation);
            } else {
                // Handle archetype conversations
                this.handleArchetypeConversation(conversation);
            }
        });

        // Start periodic layer state updates
        setInterval(() => {
            this.updateLayerStates();
        }, 1000); // Update every second
    }

    private async handleArchetypeConversation(conversation: any) {
        const { response, trigger, type, description } = conversation;

        // Trigger the responding archetype with conversation context
        this.coreLibrary.triggerArchetype(response);
        await this.audioEngine.playArchetype(response, 0.5); // Softer for conversations

        // Update UI to show conversation
        this.updateActiveThinker(`${this.getArchetypeName(trigger)} → ${this.getArchetypeName(response)}`);

        // Apply interaction effects based on type
        this.applyConversationEffects(type, trigger, response);

        console.log(`🗣️ Conversation: ${description}`);
    }

    private handleLayerInteraction(interaction: any) {
        const { source, target, effect } = interaction;

        // Apply layer interaction effects
        switch (target) {
            case 'emergent':
                if (effect.property === 'morphingSpeed') {
                    this.emergentFormLayer.setMorphingSpeed(effect.modifier);
                }
                break;
            case 'particles':
                if (effect.property === 'emissionRate') {
                    this.particleLayer.setEmissionRate(effect.modifier);
                } else if (effect.property === 'geometricAlignment') {
                    this.particleLayer.setGeometricAlignment(effect.modifier);
                }
                break;
            case 'shadow':
                if (effect.property === 'opacity') {
                    this.shadowLayer.setOpacity(effect.modifier);
                } else if (effect.property === 'inversionProbability') {
                    this.shadowLayer.setInversionProbability(effect.modifier);
                }
                break;
            case 'vessel':
                if (effect.property === 'pulseRate') {
                    this.vesselLayer.setPulseRate(effect.modifier);
                }
                break;
        }

        console.log(`🔗 Layer Interaction: ${source} → ${target} (${effect.property})`);
    }

    private updateLayerStates() {
        // Update layer states for interaction processing
        this.archetypeConversations.updateLayerState('vessel', {
            intensity: this.vesselLayer.getCurrentIntensity(),
            pulseRate: this.vesselLayer.getCurrentPulseRate()
        });

        this.archetypeConversations.updateLayerState('emergent', {
            speed: this.emergentFormLayer.getCurrentSpeed(),
            intensity: this.emergentFormLayer.getCurrentIntensity()
        });

        this.archetypeConversations.updateLayerState('particles', {
            intensity: this.particleLayer.getCurrentIntensity(),
            emissionRate: this.particleLayer.getCurrentEmissionRate()
        });

        this.archetypeConversations.updateLayerState('shadow', {
            intensity: this.shadowLayer.getCurrentIntensity(),
            opacity: this.shadowLayer.getCurrentOpacity()
        });
    }

    private applyConversationEffects(interactionType: string, trigger: string, response: string) {
        // Apply visual and audio effects based on conversation type
        switch (interactionType) {
            case 'harmony':
                // Create harmonic resonance effects
                this.vesselLayer.triggerHarmony();
                this.emergentFormLayer.createHarmonicResonance();
                break;
            case 'complement':
                // Create complementary visual patterns
                this.particleLayer.createComplementaryPattern(trigger, response);
                break;
            case 'transform':
                // Trigger transformation sequences
                this.emergentFormLayer.triggerTransformation();
                this.shadowLayer.createTransformationShadow();
                break;
            case 'chaos':
                // Create chaotic disruption
                this.particleLayer.triggerChaos();
                this.shadowLayer.triggerInversion();
                break;
            case 'conflict':
                // Create conflicting patterns
                this.vesselLayer.triggerConflict();
                this.emergentFormLayer.createConflictPattern();
                break;
        }
    }

    /**
     * Shadow Casting System Access for Microfiche Interface
     */
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
}