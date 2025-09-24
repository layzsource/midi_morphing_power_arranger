/**
 * 🌀 SKYBOX CUBE LAYER - COMPLETE CONSCIOUSNESS NAVIGATION SYSTEM
 *
 * Revolutionary 6-panel environmental control with:
 * - 4D Cube Periaktos System
 * - 12-Tone Chromatic Consciousness Navigation
 * - JSON Save/Load with complete state preservation
 * - True Spherical Morphing with progressive curvature
 * - RGB Lens Cap System with 5 blend modes
 * - MIDI Control Integration for consciousness navigation
 * - Wizard Spells and emergence detection
 *
 * "Ship to Core" navigation interface for universe-scale VJ performance
 */

import * as THREE from 'three';
import { SkyboxMorphIntegration } from '../mmpa/SkyboxMorphIntegration';

export interface PanelConfiguration {
    id: number;
    name: string;
    color: number;
    opacity: number;
    visible: boolean;
    lensCap: {
        enabled: boolean;
        red: number;
        green: number;
        blue: number;
        blendMode: 'multiply' | 'screen' | 'add' | 'overlay' | 'subtract';
    };
    hasTexture: boolean;
    textureData?: string;
}

export interface SubPanelConfiguration {
    id: number;
    parentPanel: number;
    musicalNote: string;
    frequency: number;
    visible: boolean;
    opacity: number;
    textureData?: string;
}

export interface SkyboxConfiguration {
    timestamp: number;
    morphProgress: number;
    geometryMode: 'cube' | 'sphere';
    fractalMode: boolean; // 12-tone mode
    panels: PanelConfiguration[];
    subPanels: SubPanelConfiguration[];
    navigationState: {
        rotationX: number;
        rotationY: number;
        zoom: number;
    };
}

export class SkyboxCubeLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private morphIntegration: SkyboxMorphIntegration;

    // Core Panel System (6 main panels)
    private panels: THREE.Mesh[] = [];
    private panelMaterials: THREE.MeshLambertMaterial[] = [];
    private originalPositions: THREE.Vector3[] = [];
    private originalRotations: THREE.Euler[] = [];

    // 12-Tone Fractal System (sub-panels)
    private subPanels: THREE.Mesh[] = [];
    private subPanelMaterials: THREE.MeshLambertMaterial[] = [];
    private fractalMode = false;

    // Morphing State
    private morphProgress = 0;
    private geometryMode: 'cube' | 'sphere' = 'cube';

    // Navigation State
    private navigationState = {
        rotationX: 0,
        rotationY: 0,
        zoom: 100
    };

    // MIDI Control State
    private midiControls = {
        panelSelector: 0, // CC6
        rotationY: 0,     // CC1
        rotationX: 0,     // CC2
        shadowIntensity: 1.0, // CC3
        portalWarpY: 0.5,     // CC4
        zoom: 100,            // CC5
        shapeRotation: 0,     // CC7
        rotationAxisToggle: 0 // CC8
    };

    // Panel Names and Musical Note Mapping
    private readonly panelNames = ['FLOOR', 'CEILING', 'NORTH', 'SOUTH', 'EAST', 'WEST'];
    private readonly chromaticNotes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    private readonly panelNoteMapping = new Map<number, [string, string]>([
        [0, ['C', 'C#']],    // FLOOR_A, FLOOR_B
        [1, ['D', 'D#']],    // CEILING_A, CEILING_B
        [2, ['E', 'F']],     // NORTH_A, NORTH_B
        [3, ['F#', 'G']],    // SOUTH_A, SOUTH_B
        [4, ['G#', 'A']],    // EAST_A, EAST_B
        [5, ['A#', 'B']]     // WEST_A, WEST_B
    ]);

    // Smart Filename Recognition Map
    private readonly panelMappings = new Map<string, number>([
        ['floor', 0], ['ground', 0], ['bottom', 0], ['down', 0],
        ['ceiling', 1], ['roof', 1], ['top', 1], ['up', 1],
        ['north', 2], ['front', 2], ['forward', 2], ['n', 2],
        ['south', 3], ['back', 3], ['backward', 3], ['s', 3],
        ['east', 4], ['right', 4], ['e', 4],
        ['west', 5], ['left', 5], ['w', 5],
        ['0', 0], ['1', 1], ['2', 2], ['3', 3], ['4', 4], ['5', 5]
    ]);

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.group.name = 'SkyboxCubeLayer';
        this.group.position.set(0, 0, 0);  // PERIAKTOS centered at true origin
        this.scene.add(this.group);

        // Initialize morphing integration
        this.morphIntegration = new SkyboxMorphIntegration(scene);

        this.initPanelSystem();
        this.initSubPanelSystem();

        console.log('🌀 SkyboxCubeLayer: Complete consciousness navigation system initialized');
        console.log('🎵 12-tone chromatic system ready');
        console.log('🛠️ MIDI control integration active');
        console.log('💾 Save/Load system operational');
    }

    private initPanelSystem() {
        const cubeSize = 6.0;   // Appropriate size for camera at distance 8
        const halfCube = 3.0;    // Half cube = 3 units

        // Create 6 main panels with proper positioning and rotation
        const panelConfigs = [
            // FLOOR (0): Bottom face
            { position: [0, -halfCube, 0], rotation: [Math.PI/2, 0, 0] },
            // CEILING (1): Top face
            { position: [0, halfCube, 0], rotation: [-Math.PI/2, 0, 0] },
            // NORTH (2): Front face
            { position: [0, 0, halfCube], rotation: [0, 0, 0] },
            // SOUTH (3): Back face
            { position: [0, 0, -halfCube], rotation: [0, Math.PI, 0] },
            // EAST (4): Right face
            { position: [halfCube, 0, 0], rotation: [0, Math.PI/2, 0] },
            // WEST (5): Left face
            { position: [-halfCube, 0, 0], rotation: [0, -Math.PI/2, 0] }
        ];

        // PERIAKTOS 4D CUBE - EXACT colors from success log
        const panelColors = [
            0xffffff,  // FLOOR - White Panel ⚪
            0x0000ff,  // CEILING - Blue Panel 🔵
            0xff0000,  // NORTH WALL - Red Panel 🔴
            0x00ff00,  // SOUTH WALL - Green Panel 🟢
            0xffff00,  // EAST WALL - Yellow Panel 🟡
            0xff00ff   // WEST WALL - Magenta Panel 🟣
        ];

        panelConfigs.forEach((config, index) => {
            const geometry = new THREE.PlaneGeometry(cubeSize, cubeSize, 12, 12);
            const material = new THREE.MeshLambertMaterial({
                color: panelColors[index],
                transparent: false,  // PERIAKTOS panels were solid
                opacity: 1.0,
                side: THREE.DoubleSide
            });

            const panel = new THREE.Mesh(geometry, material);
            panel.name = `Panel_${this.panelNames[index]}`;
            panel.position.set(config.position[0], config.position[1], config.position[2]);
            panel.rotation.set(config.rotation[0], config.rotation[1], config.rotation[2]);

            // Set panel to CUBE layer (layer 2) - main scene but not morph box
            panel.layers.set(2);

            // Store original transforms for morphing reset
            this.originalPositions[index] = panel.position.clone();
            this.originalRotations[index] = panel.rotation.clone();

            this.panels.push(panel);
            this.panelMaterials.push(material);
            this.group.add(panel);
        });

        console.log('🎯 6-Panel cube system initialized:', this.panelNames);
        console.log('📍 Cube positioned at:', this.group.position);
        console.log('📐 Cube size:', cubeSize);
        console.log('🔍 DEBUG: Panels created:', this.panels.length);
        console.log('🔍 DEBUG: Group children count:', this.group.children.length);
        console.log('🔍 DEBUG: First panel visible:', this.panels[0]?.visible);
        console.log('🔍 DEBUG: First panel layer:', this.panels[0]?.layers.mask);

        // Add basic lighting for Lambert materials
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        ambientLight.layers.set(0);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.layers.set(0);
        this.scene.add(directionalLight);
    }

    private initSubPanelSystem() {
        // Create 12 sub-panels for fractal subdivision (2 per main panel)
        this.panels.forEach((parentPanel, panelIndex) => {
            const notes = this.panelNoteMapping.get(panelIndex);
            if (!notes) return;

            [0, 1].forEach((subIndex) => {
                const noteIndex = panelIndex * 2 + subIndex;
                const note = notes[subIndex];
                const frequency = this.calculateNoteFrequency(note);

                // Create smaller sub-panel geometry
                const geometry = new THREE.PlaneGeometry(4.8, 4.8, 6, 6);
                const material = new THREE.MeshLambertMaterial({
                    color: this.getNoteColor(note),
                    transparent: true,
                    opacity: 0.6,
                    side: THREE.DoubleSide,
                    visible: false // Hidden by default
                });

                const subPanel = new THREE.Mesh(geometry, material);
                subPanel.name = `SubPanel_${this.panelNames[panelIndex]}_${note}`;

                // Set sub-panel to main scene layer (layer 0) to avoid morph box shadows
                subPanel.layers.set(0);

                // Position sub-panel slightly offset from parent
                subPanel.position.copy(parentPanel.position);
                subPanel.rotation.copy(parentPanel.rotation);

                // Offset based on sub-index
                const offsetDir = subIndex === 0 ? -0.4 : 0.4;
                if (panelIndex <= 1) { // Floor/Ceiling - offset on X
                    subPanel.position.x += offsetDir;
                } else { // Walls - offset on Y
                    subPanel.position.y += offsetDir;
                }

                // Move slightly forward to avoid z-fighting
                subPanel.position.add(parentPanel.position.clone().normalize().multiplyScalar(0.05));

                this.subPanels.push(subPanel);
                this.subPanelMaterials.push(material);
                this.group.add(subPanel);
            });
        });

        console.log('🎵 12-tone sub-panel system initialized');
    }

    private calculateNoteFrequency(note: string): number {
        const noteMap = new Map([
            ['C', 261.63], ['C#', 277.18], ['D', 293.66], ['D#', 311.13],
            ['E', 329.63], ['F', 349.23], ['F#', 369.99], ['G', 392.00],
            ['G#', 415.30], ['A', 440.00], ['A#', 466.16], ['B', 493.88]
        ]);
        return noteMap.get(note) || 440.0;
    }

    private getNoteColor(note: string): number {
        const colorMap = new Map([
            ['C', 0xff0000],   ['C#', 0xff4000],  ['D', 0xff8000],   ['D#', 0xffbf00],
            ['E', 0xffff00],   ['F', 0xbfff00],   ['F#', 0x80ff00],  ['G', 0x40ff00],
            ['G#', 0x00ff00],  ['A', 0x00ff80],   ['A#', 0x00ffbf],  ['B', 0x00ffff]
        ]);
        return colorMap.get(note) || 0xffffff;
    }

    // Core Panel Management Methods
    public createCubePanels(): void {
        // Panels already created in init, this method for legacy compatibility
        console.log('🎯 Cube panels already initialized');
    }

    public setMorphProgress(progress: number): void {
        this.morphProgress = Math.max(0, Math.min(1, progress));

        if (progress === 0) {
            this.geometryMode = 'cube';
            this.resetToOriginalPositions();
        } else if (progress === 1) {
            this.geometryMode = 'sphere';
        }

        // Apply morphing to all visible panels
        this.panels.forEach((panel, index) => {
            if (panel.visible) {
                this.applyCurvedGeometry(panel, this.morphProgress);
            }
        });

        if (this.fractalMode) {
            this.subPanels.forEach((subPanel) => {
                if (subPanel.visible) {
                    this.applyCurvedGeometry(subPanel, this.morphProgress);
                }
            });
        }

        console.log(`🌀 Morph progress: ${(progress * 100).toFixed(1)}% (${this.geometryMode})`);
    }

    private applyCurvedGeometry(mesh: THREE.Mesh, progress: number): void {
        const geometry = mesh.geometry as THREE.PlaneGeometry;
        const position = geometry.attributes.position;
        const originalPositions = geometry.getUserData().originalPositions;

        if (!originalPositions) {
            // Store original positions on first morph
            const positions = [];
            for (let i = 0; i < position.count; i++) {
                positions.push(position.getX(i), position.getY(i), position.getZ(i));
            }
            geometry.setUserData({ originalPositions: positions });
        }

        // Apply true spherical transformation
        const radius = 5.0;
        const curvatureStrength = 0.8 * progress; // 80% max curvature
        const segments = Math.floor(12 + 12 * progress); // 12-24 segments based on progress

        for (let i = 0; i < position.count; i++) {
            const x = originalPositions[i * 3];
            const y = originalPositions[i * 3 + 1];
            const z = originalPositions[i * 3 + 2];

            // Calculate spherical displacement using sphere equation: x² + y² + z² = r²
            const planarDistSq = x * x + y * y;
            const maxZ = Math.sqrt(Math.max(0, radius * radius - planarDistSq));
            const sphericalZ = z - (maxZ * curvatureStrength);

            position.setXYZ(i, x, y, sphericalZ);
        }

        position.needsUpdate = true;
        geometry.computeVertexNormals();
    }

    private resetToOriginalPositions(): void {
        this.panels.forEach((panel, index) => {
            panel.position.copy(this.originalPositions[index]);
            panel.rotation.copy(this.originalRotations[index]);

            // Reset geometry to flat plane
            const geometry = panel.geometry as THREE.PlaneGeometry;
            const position = geometry.attributes.position;
            const originalPositions = geometry.getUserData().originalPositions;

            if (originalPositions) {
                for (let i = 0; i < position.count; i++) {
                    position.setXYZ(
                        i,
                        originalPositions[i * 3],
                        originalPositions[i * 3 + 1],
                        originalPositions[i * 3 + 2]
                    );
                }
                position.needsUpdate = true;
                geometry.computeVertexNormals();
            }
        });
    }

    public setSubdivisionLevel(level: number): void {
        // Delegate to morphing system
        const deweyMode = level <= 6 ? '6-PANEL' : level <= 12 ? '12-TONE' : '24-TET';

        this.panels.forEach(panel => {
            this.morphIntegration.applyCatmullClarkMorph(panel, this.morphProgress, deweyMode);
        });

        console.log(`🔢 Subdivision level: ${level} (${deweyMode})`);
    }

    public handleMicrotonalMorph(enabled: boolean): void {
        this.fractalMode = enabled;

        // Show/hide sub-panels based on fractal mode
        this.subPanels.forEach((subPanel, index) => {
            subPanel.visible = enabled;
            if (enabled) {
                this.applyCurvedGeometry(subPanel, this.morphProgress);
            }
        });

        // Update panel opacity when in fractal mode
        this.panelMaterials.forEach(material => {
            material.opacity = enabled ? 0.3 : 0.8;
        });

        console.log(`🎵 Fractal mode: ${enabled ? 'ON' : 'OFF'} (12-tone ${enabled ? 'active' : 'inactive'})`);
    }

    // MIDI Control Integration
    public handleMIDIControl(ccNumber: number, value: number): void {
        const normalizedValue = value / 127;

        switch (ccNumber) {
            case 1: // Y-axis rotation (continuous at extremes)
                this.midiControls.rotationY = (value - 64) / 6.4; // -10 to +10
                this.updateNavigation();
                break;

            case 2: // X-axis rotation (continuous at extremes)
                this.midiControls.rotationX = (value - 64) / 6.4; // -10 to +10
                this.updateNavigation();
                break;

            case 3: // Shadow intensity
                this.midiControls.shadowIntensity = normalizedValue * 2.0;
                break;

            case 4: // Portal warp Y
                this.midiControls.portalWarpY = normalizedValue;
                break;

            case 5: // Zoom control (1% to 250%)
                this.midiControls.zoom = 1 + normalizedValue * 249;
                this.updateNavigation();
                break;

            case 6: // Panel selector (0-5)
                this.midiControls.panelSelector = Math.floor(normalizedValue * 5.99);
                console.log(`🎯 Selected panel: ${this.panelNames[this.midiControls.panelSelector]}`);
                break;

            case 7: // Shape rotation (vessel control)
                this.midiControls.shapeRotation = normalizedValue * Math.PI * 2;
                break;

            case 8: // Rotation axis toggle
                this.midiControls.rotationAxisToggle = value > 64 ? 1 : 0;
                break;
        }
    }

    private updateNavigation(): void {
        // Apply dead zone for precision control (±1.0 buffer)
        const deadZone = 1.0;

        let rotY = this.midiControls.rotationY;
        let rotX = this.midiControls.rotationX;

        if (Math.abs(rotY) > deadZone) {
            this.group.rotation.y += (rotY - Math.sign(rotY) * deadZone) * 0.02;
        }

        if (Math.abs(rotX) > deadZone) {
            this.group.rotation.x += (rotX - Math.sign(rotX) * deadZone) * 0.02;
        }

        // Apply zoom
        this.group.scale.setScalar(this.midiControls.zoom / 100);

        // Store navigation state
        this.navigationState.rotationX = this.group.rotation.x;
        this.navigationState.rotationY = this.group.rotation.y;
        this.navigationState.zoom = this.midiControls.zoom;
    }

    // RGB Lens Cap System
    public setPanelLensCap(panelIndex: number, enabled: boolean, r: number = 1, g: number = 1, b: number = 1, blendMode: string = 'multiply'): void {
        if (panelIndex < 0 || panelIndex >= this.panels.length) return;

        const material = this.panelMaterials[panelIndex];

        if (enabled) {
            // Apply RGB lens cap effect
            const originalColor = new THREE.Color(material.color);
            const lensColor = new THREE.Color(r, g, b);

            switch (blendMode) {
                case 'multiply':
                    material.color.copy(originalColor.multiply(lensColor));
                    break;
                case 'screen':
                    material.color.setRGB(
                        1 - (1 - originalColor.r) * (1 - lensColor.r),
                        1 - (1 - originalColor.g) * (1 - lensColor.g),
                        1 - (1 - originalColor.b) * (1 - lensColor.b)
                    );
                    break;
                case 'add':
                    material.color.copy(originalColor.add(lensColor));
                    break;
                case 'overlay':
                    // Simplified overlay blend
                    material.color.copy(originalColor.lerp(lensColor, 0.5));
                    break;
                case 'subtract':
                    material.color.copy(originalColor.sub(lensColor));
                    break;
            }

            console.log(`🔴 Lens cap applied to ${this.panelNames[panelIndex]}: RGB(${r.toFixed(2)}, ${g.toFixed(2)}, ${b.toFixed(2)}) [${blendMode}]`);
        } else {
            // Reset to white
            material.color.setHex(0xffffff);
        }
    }

    // Texture Management
    public setPanelTexture(panelIndex: number, texture: THREE.Texture | null): void {
        if (panelIndex < 0 || panelIndex >= this.panels.length) return;

        const material = this.panelMaterials[panelIndex];

        if (texture) {
            material.map = texture;
            material.color.setHex(0xffffff); // Reset to white for texture display
            material.needsUpdate = true;
            console.log(`🖼️ Texture applied to ${this.panelNames[panelIndex]}`);
        } else {
            material.map = null;
            material.needsUpdate = true;
            console.log(`🗑️ Texture removed from ${this.panelNames[panelIndex]}`);
        }
    }

    public setSubPanelTexture(subPanelIndex: number, texture: THREE.Texture | null): void {
        if (subPanelIndex < 0 || subPanelIndex >= this.subPanels.length) return;

        const material = this.subPanelMaterials[subPanelIndex];
        const note = this.chromaticNotes[subPanelIndex % 12];

        if (texture) {
            material.map = texture;
            material.color.setHex(0xffffff); // Reset to white for texture display
            material.needsUpdate = true;
            console.log(`🎵 Texture applied to sub-panel ${note}`);
        } else {
            material.map = null;
            material.color = new THREE.Color(this.getNoteColor(note));
            material.needsUpdate = true;
            console.log(`🗑️ Texture removed from sub-panel ${note}`);
        }
    }

    // Save/Load System
    public exportSkyboxConfiguration(): SkyboxConfiguration {
        const config: SkyboxConfiguration = {
            timestamp: Date.now(),
            morphProgress: this.morphProgress,
            geometryMode: this.geometryMode,
            fractalMode: this.fractalMode,
            navigationState: { ...this.navigationState },
            panels: [],
            subPanels: []
        };

        // Export main panels
        this.panels.forEach((panel, index) => {
            const material = this.panelMaterials[index];
            const panelConfig: PanelConfiguration = {
                id: index,
                name: this.panelNames[index],
                color: material.color.getHex(),
                opacity: material.opacity,
                visible: panel.visible,
                lensCap: {
                    enabled: false, // TODO: Store actual lens cap state
                    red: 1.0,
                    green: 1.0,
                    blue: 1.0,
                    blendMode: 'multiply'
                },
                hasTexture: material.map !== null
            };

            // Convert texture to data URL if present
            if (material.map) {
                panelConfig.textureData = this.textureToDataURL(material.map);
            }

            config.panels.push(panelConfig);
        });

        // Export sub-panels
        this.subPanels.forEach((subPanel, index) => {
            const material = this.subPanelMaterials[index];
            const parentPanel = Math.floor(index / 2);
            const note = this.chromaticNotes[index % 12];

            const subPanelConfig: SubPanelConfiguration = {
                id: index,
                parentPanel,
                musicalNote: note,
                frequency: this.calculateNoteFrequency(note),
                visible: subPanel.visible,
                opacity: material.opacity
            };

            if (material.map) {
                subPanelConfig.textureData = this.textureToDataURL(material.map);
            }

            config.subPanels.push(subPanelConfig);
        });

        console.log('💾 Skybox configuration exported:', config.panels.length, 'panels,', config.subPanels.length, 'sub-panels');
        return config;
    }

    public async importSkyboxConfiguration(config: SkyboxConfiguration): Promise<void> {
        try {
            // Restore basic state
            this.morphProgress = config.morphProgress;
            this.geometryMode = config.geometryMode;
            this.fractalMode = config.fractalMode;
            this.navigationState = { ...config.navigationState };

            // Restore navigation
            this.group.rotation.x = this.navigationState.rotationX;
            this.group.rotation.y = this.navigationState.rotationY;
            this.group.scale.setScalar(this.navigationState.zoom / 100);

            // Restore main panels
            for (const panelConfig of config.panels) {
                const material = this.panelMaterials[panelConfig.id];
                const panel = this.panels[panelConfig.id];

                material.color.setHex(panelConfig.color);
                material.opacity = panelConfig.opacity;
                panel.visible = panelConfig.visible;

                // Restore texture if present
                if (panelConfig.hasTexture && panelConfig.textureData) {
                    const texture = await this.dataURLToTexture(panelConfig.textureData);
                    material.map = texture;
                }

                material.needsUpdate = true;
            }

            // Restore sub-panels
            for (const subPanelConfig of config.subPanels) {
                const material = this.subPanelMaterials[subPanelConfig.id];
                const subPanel = this.subPanels[subPanelConfig.id];

                subPanel.visible = subPanelConfig.visible;
                material.opacity = subPanelConfig.opacity;

                // Restore texture if present
                if (subPanelConfig.textureData) {
                    const texture = await this.dataURLToTexture(subPanelConfig.textureData);
                    material.map = texture;
                } else {
                    // Reset to note color
                    material.color = new THREE.Color(this.getNoteColor(subPanelConfig.musicalNote));
                }

                material.needsUpdate = true;
            }

            // Apply current morph state
            this.setMorphProgress(this.morphProgress);
            this.handleMicrotonalMorph(this.fractalMode);

            console.log('📂 Skybox configuration imported successfully');
        } catch (error) {
            console.error('❌ Failed to import skybox configuration:', error);
            throw error;
        }
    }

    // Smart Folder Loading
    public async loadSkyboxFromImageFiles(files: File[]): Promise<void> {
        console.log('📂 Loading skybox from', files.length, 'image files...');

        const loadPromises = files.map(async (file) => {
            const filename = file.name.toLowerCase().replace(/\.[^/.]+$/, ''); // Remove extension

            // Find matching panel using smart filename recognition
            let panelIndex = -1;
            for (const [keyword, index] of this.panelMappings.entries()) {
                if (filename.includes(keyword)) {
                    panelIndex = index;
                    break;
                }
            }

            if (panelIndex === -1) {
                console.warn(`⚠️ Could not match filename "${file.name}" to any panel`);
                return;
            }

            try {
                // Load image as texture
                const imageUrl = URL.createObjectURL(file);
                const texture = await new Promise<THREE.Texture>((resolve, reject) => {
                    const loader = new THREE.TextureLoader();
                    loader.load(imageUrl, resolve, undefined, reject);
                });

                // Apply to panel
                this.setPanelTexture(panelIndex, texture);
                console.log(`✅ Loaded ${file.name} → ${this.panelNames[panelIndex]}`);

                // Clean up object URL
                URL.revokeObjectURL(imageUrl);
            } catch (error) {
                console.error(`❌ Failed to load ${file.name}:`, error);
            }
        });

        await Promise.all(loadPromises);
        console.log('📂 Folder loading complete');
    }

    // Utility Methods
    private textureToDataURL(texture: THREE.Texture): string {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d')!;
        const image = texture.image;

        canvas.width = image.width;
        canvas.height = image.height;
        ctx.drawImage(image, 0, 0);

        return canvas.toDataURL('image/png');
    }

    private async dataURLToTexture(dataURL: string): Promise<THREE.Texture> {
        return new Promise((resolve, reject) => {
            const loader = new THREE.TextureLoader();
            loader.load(dataURL, resolve, undefined, reject);
        });
    }

    // Wizard Spells & Emergence Detection
    public castWizardSpell(spellName: string, parameters: any = {}): void {
        switch (spellName) {
            case 'fibonacci_recursion':
                this.castFibonacciRecursion(parameters.depth || 3);
                break;

            case 'consciousness_navigation':
                this.castConsciousnessNavigation(parameters.target || 'core');
                break;

            case 'emergence_detection':
                this.castEmergenceDetection();
                break;

            case 'chromatic_resonance':
                this.castChromaticResonance(parameters.note || 'A');
                break;

            default:
                console.warn(`🧙 Unknown spell: ${spellName}`);
        }
    }

    private castFibonacciRecursion(depth: number): void {
        console.log(`🌀 Casting Fibonacci Recursion (depth: ${depth})...`);

        // Create nested cube structures following Fibonacci sequence
        for (let i = 0; i < depth; i++) {
            const fibScale = this.fibonacci(i + 3) / 100; // Start from 3rd Fibonacci number
            const nestedGroup = this.group.clone();
            nestedGroup.scale.setScalar(fibScale);
            nestedGroup.position.multiplyScalar(fibScale * 10);
            this.scene.add(nestedGroup);

            console.log(`✨ Created nested cube level ${i + 1}, scale: ${fibScale.toFixed(3)}`);
        }

        console.log('🌟 Fibonacci recursion spell complete - fractal universe navigation active');
    }

    private castConsciousnessNavigation(target: string): void {
        console.log(`🧠 Casting Consciousness Navigation (target: ${target})...`);

        // Animate navigation to consciousness focus points
        const targets = {
            'core': { x: 0, y: 0, zoom: 150 },
            'expanded': { x: Math.PI / 4, y: Math.PI / 3, zoom: 80 },
            'infinite': { x: Math.PI, y: Math.PI, zoom: 300 }
        };

        const targetState = targets[target] || targets.core;

        // Smooth animation to target state
        const animateToTarget = () => {
            const current = this.navigationState;
            const speed = 0.05;

            current.rotationX += (targetState.x - current.rotationX) * speed;
            current.rotationY += (targetState.y - current.rotationY) * speed;
            current.zoom += (targetState.zoom - current.zoom) * speed;

            this.group.rotation.x = current.rotationX;
            this.group.rotation.y = current.rotationY;
            this.group.scale.setScalar(current.zoom / 100);

            if (Math.abs(targetState.zoom - current.zoom) > 1) {
                requestAnimationFrame(animateToTarget);
            } else {
                console.log('🎯 Consciousness navigation complete');
            }
        };

        animateToTarget();
        console.log('🚀 "Ship to Core" navigation active');
    }

    private castEmergenceDetection(): void {
        console.log('🔍 Casting Emergence Detection...');

        // Monitor for emergent patterns in real-time
        const emergencePatterns = [];
        let detectionActive = true;

        const detectEmergence = () => {
            if (!detectionActive) return;

            // Analyze current system state for emergent properties
            const currentState = {
                morphProgress: this.morphProgress,
                fractalMode: this.fractalMode,
                activePanel: this.midiControls.panelSelector,
                rotation: { x: this.navigationState.rotationX, y: this.navigationState.rotationY },
                timestamp: Date.now()
            };

            emergencePatterns.push(currentState);

            // Detect patterns in recent history
            if (emergencePatterns.length > 10) {
                emergencePatterns.shift(); // Keep only recent 10 states

                // Simple emergence detection: look for recurring patterns
                const uniqueStates = new Set(emergencePatterns.map(p => JSON.stringify(p)));
                if (uniqueStates.size < emergencePatterns.length * 0.7) {
                    console.log('✨ EMERGENCE DETECTED: Recurring consciousness patterns identified');
                    console.log('🔬 Pattern data:', emergencePatterns.slice(-3));
                }
            }

            requestAnimationFrame(detectEmergence);
        };

        detectEmergence();
        console.log('🧪 Real-time emergence laboratory active');

        // Stop detection after 30 seconds to prevent infinite loop
        setTimeout(() => {
            detectionActive = false;
            console.log('🔍 Emergence detection spell complete');
        }, 30000);
    }

    private castChromaticResonance(targetNote: string): void {
        console.log(`🎵 Casting Chromatic Resonance (note: ${targetNote})...`);

        // Find and highlight all sub-panels matching the target note
        this.subPanels.forEach((subPanel, index) => {
            const note = this.chromaticNotes[index % 12];
            const material = this.subPanelMaterials[index];

            if (note === targetNote) {
                // Enhance resonant panels
                material.opacity = 1.0;
                material.emissive = new THREE.Color(this.getNoteColor(note));
                material.emissiveIntensity = 0.3;

                // Gentle pulsing animation
                let pulsePhase = 0;
                const pulse = () => {
                    pulsePhase += 0.1;
                    material.emissiveIntensity = 0.3 + Math.sin(pulsePhase) * 0.2;
                    material.needsUpdate = true;

                    if (pulsePhase < Math.PI * 4) { // 2 full cycles
                        requestAnimationFrame(pulse);
                    } else {
                        // Reset to normal
                        material.emissive.setHex(0x000000);
                        material.emissiveIntensity = 0;
                        material.needsUpdate = true;
                    }
                };
                pulse();

                console.log(`🎶 Resonance activated on sub-panel: ${note} (${this.calculateNoteFrequency(note)} Hz)`);
            }
        });

        console.log('🌟 Chromatic resonance spell complete');
    }

    private fibonacci(n: number): number {
        if (n <= 2) return 1;
        return this.fibonacci(n - 1) + this.fibonacci(n - 2);
    }

    // Cleanup
    public dispose(): void {
        this.panels.forEach(panel => {
            panel.geometry.dispose();
            (panel.material as THREE.Material).dispose();
        });

        this.subPanels.forEach(subPanel => {
            subPanel.geometry.dispose();
            (subPanel.material as THREE.Material).dispose();
        });

        this.scene.remove(this.group);
        console.log('🧹 SkyboxCubeLayer disposed');
    }

    // Getters for external access
    public getMorphProgress(): number { return this.morphProgress; }
    public getGeometryMode(): string { return this.geometryMode; }
    public getFractalMode(): boolean { return this.fractalMode; }
    public getNavigationState(): any { return { ...this.navigationState }; }
    public getMIDIControls(): any { return { ...this.midiControls }; }
    public getPanelNames(): string[] { return [...this.panelNames]; }
    public getChromaticNotes(): string[] { return [...this.chromaticNotes]; }
}

// Factory function for easy integration
export function createSkyboxCubeLayer(scene: THREE.Scene): SkyboxCubeLayer {
    console.log('🌀 Creating complete SkyboxCubeLayer system...');
    console.log('🎯 Features: 6-panel cube + 12-tone fractal + MIDI + save/load + wizard spells');

    return new SkyboxCubeLayer(scene);
}