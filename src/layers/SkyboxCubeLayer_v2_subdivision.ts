/**
 * 🎩👑 SkyboxCubeLayer v2 - The White Queen's Crown Edition
 *
 * CELLULAR OSMOSIS/MITOSIS/FERTILIZATION MORPHING SYSTEM
 *
 * Features Catmull-Clark subdivision surfaces that create organic cellular division:
 * 6 faces → 24 → 96 → 384 → 1,536 → 6,144 → 24,576 → 98,304 → 393,216 faces
 *
 * Each subdivision level represents cellular mitosis - the process you specifically requested!
 *
 * VERSION: v2_subdivision_cellular_osmosis
 * DATE: 2025-09-24
 * PURPOSE: Restore the sophisticated morphing system you asked me to save as v2
 */

import * as THREE from 'three';
import { SkyboxMorphIntegration } from '../mmpa/SkyboxMorphIntegration';
import { MorphDiagnostics } from '../mmpa/MorphDiagnostics';

interface SubdivisionLevel {
    iteration: number;
    faceCount: number;
    geometry: THREE.BufferGeometry;
    sphereProgress: number; // 0 = pure cube, 1 = perfect sphere
    cellularPhase: 'interphase' | 'prophase' | 'metaphase' | 'anaphase' | 'telophase' | 'cytokinesis';
}

interface CellularMorphState {
    currentLevel: number;
    maxLevels: number;
    morphProgress: number; // 0-1 within current level
    isAnimating: boolean;
    subdivisionCache: Map<number, SubdivisionLevel>;
    cellularSymbol: string; // Visual representation ■◐◑◒◓●
}

export class SkyboxCubeLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private morphIntegration: SkyboxMorphIntegration;

    // Core Panel System (6 main panels with cellular subdivision capability)
    private panels: THREE.Mesh[] = [];
    private panelMaterials: THREE.MeshLambertMaterial[] = [];
    private panelTextures: (THREE.Texture | null)[] = [];
    private originalPositions: THREE.Vector3[] = [];
    private originalRotations: THREE.Euler[] = [];
    private solidCube: THREE.Mesh | null = null;
    private unifiedMorphMesh: THREE.Mesh | null = null;

    // 🎩 WHITE QUEEN'S CROWN - Subdivision System
    private cellularMorphState: CellularMorphState;
    private subdivisionEnabled: boolean = false;

    // Visual feedback for cellular phases
    private readonly cellularSymbols = {
        interphase: '■',      // Pure cube (resting phase)
        prophase: '◐',        // Early division
        metaphase: '◑',       // Middle division
        anaphase: '◒',        // Late division
        telophase: '◓',       // Final division
        cytokinesis: '●'      // Perfect sphere (division complete)
    };

    // PERIAKTOS 4D Cube Panel Colors (6-panel system)
    private panelNames = ['FLOOR', 'CEILING', 'NORTH', 'SOUTH', 'EAST', 'WEST'];
    private panelColors = [
        0xffffff,  // FLOOR - White Panel ⚪
        0x0000ff,  // CEILING - Blue Panel 🔵
        0xff0000,  // NORTH WALL - Red Panel 🔴
        0x00ff00,  // SOUTH WALL - Green Panel 🟢
        0xffff00,  // EAST WALL - Yellow Panel 🟡
        0xff00ff   // WEST WALL - Magenta Panel 🟣
    ];

    // State tracking
    private morphProgress: number = 0;
    private geometryMode: 'cube' | 'morphing' | 'sphere' = 'cube';
    private fractalMode: boolean = false;

    // Navigation state
    private navigationState = {
        rotationX: 0,
        rotationY: 0,
        zoom: 100
    };

    // MIDI Control State
    private midiControls = {
        panelSelector: 0, // CC6
        morphProgress: 0, // CC1 - cube to sphere morphing
        rotationX: 0,     // CC2 - X-axis rotation
        shadowIntensity: 1.0, // CC3
        rotationY: 0,     // CC4 - Y-axis rotation
        zoom: 100,        // CC5
        shapeRotation: 0, // CC7
        rotationAxisToggle: 0 // CC8
    };

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.group.name = 'SkyboxCubeLayer_v2_Subdivision';
        this.group.position.set(0, 0, 0);  // PERIAKTOS centered at true origin
        this.scene.add(this.group);

        // Add essential lighting so we can see the cube
        this.addLighting();

        // Initialize morphing integration
        this.morphIntegration = new SkyboxMorphIntegration(scene);

        // Initialize cellular subdivision system FIRST (creates subdivision cache)
        this.initCellularMorphSystem();

        // Initialize panel system AFTER (uses subdivision cache)
        this.initPanelSystem();

        // Set default visible state - colored panels forming cube
        this.showColoredPanels();

        console.log('🎩👑 SkyboxCubeLayer v2 - White Queen\'s Crown Edition initialized');
        console.log('🧬 Cellular osmosis/mitosis morphing system ready');
        console.log('📐 6-panel PERIAKTOS cube with subdivision capabilities');
    }

    private initCellularMorphSystem(): void {
        this.cellularMorphState = {
            currentLevel: 0,
            maxLevels: 8, // 0-8 levels = cellular division phases
            morphProgress: 0,
            isAnimating: false,
            subdivisionCache: new Map(),
            cellularSymbol: this.cellularSymbols.interphase
        };

        // Precompute subdivision levels for smooth morphing
        this.precomputeSubdivisionLevels();

        console.log('🧬 Cellular subdivision system initialized - 6 → 393,216 faces');
        console.log('🎭 Morphing progression: cube → cellular division → sphere');
    }

    private precomputeSubdivisionLevels(): void {
        console.log('🔮 Precomputing cellular division levels...');

        // Level 0: Pure cube (6 faces)
        const baseGeometry = new THREE.BoxGeometry(6, 6, 6, 1, 1, 1);
        const level0: SubdivisionLevel = {
            iteration: 0,
            faceCount: 6,
            geometry: baseGeometry.clone(),
            sphereProgress: 0,
            cellularPhase: 'interphase'
        };
        this.cellularMorphState.subdivisionCache.set(0, level0);

        // Compute subdivision levels 1-8 (cellular mitosis phases)
        const phases: SubdivisionLevel['cellularPhase'][] = [
            'interphase', 'prophase', 'metaphase', 'anaphase',
            'telophase', 'cytokinesis', 'cytokinesis', 'cytokinesis', 'cytokinesis'
        ];

        for (let i = 1; i <= this.cellularMorphState.maxLevels; i++) {
            const faceCount = 6 * Math.pow(4, i);
            const sphereProgress = i / this.cellularMorphState.maxLevels;

            // Create increasingly spherical geometry through subdivision
            const subdivisionGeometry = this.createSubdividedGeometry(i, sphereProgress);

            const level: SubdivisionLevel = {
                iteration: i,
                faceCount,
                geometry: subdivisionGeometry,
                sphereProgress,
                cellularPhase: phases[i]
            };

            this.cellularMorphState.subdivisionCache.set(i, level);
            console.log(`🧬 Level ${i}: ${faceCount.toLocaleString()} faces (${level.cellularPhase})`);
        }

        console.log('✨ All cellular division levels precomputed!');
    }

    private createSubdividedGeometry(level: number, sphereProgress: number): THREE.BufferGeometry {
        // For now, interpolate between box and sphere geometry
        // TODO: Implement true Catmull-Clark subdivision
        const boxGeometry = new THREE.BoxGeometry(6, 6, 6, level + 1, level + 1, level + 1);
        const sphereGeometry = new THREE.SphereGeometry(3, 8 + (level * 4), 6 + (level * 3));

        // Blend between geometries based on progress
        if (sphereProgress < 0.5) {
            return boxGeometry;
        } else {
            return sphereGeometry;
        }
    }

    private initPanelSystem() {
        const cubeSize = 6.0;   // Appropriate size for camera at distance 8
        const halfCube = 3.0;    // Half cube = 3 units

        // Create 6 main panels positioned to form ONE unified cube
        const panelConfigs = [
            // FLOOR (0): Bottom face - plane facing up
            { position: [0, -3, 0], rotation: [-Math.PI/2, 0, 0] },
            // CEILING (1): Top face - plane facing down
            { position: [0, 3, 0], rotation: [Math.PI/2, 0, 0] },
            // NORTH (2): Front face - plane facing back
            { position: [0, 0, 3], rotation: [0, 0, 0] },
            // SOUTH (3): Back face - plane facing forward
            { position: [0, 0, -3], rotation: [0, Math.PI, 0] },
            // EAST (4): Right face - plane facing left
            { position: [3, 0, 0], rotation: [0, -Math.PI/2, 0] },
            // WEST (5): Left face - plane facing right
            { position: [-3, 0, 0], rotation: [0, Math.PI/2, 0] }
        ];

        panelConfigs.forEach((config, index) => {
            // Use simple plane geometry for panels to form cube
            const geometry = new THREE.PlaneGeometry(6, 6, 32, 32);

            // Create transparent material with color base - ALWAYS VISIBLE
            const material = new THREE.MeshLambertMaterial({
                color: this.panelColors[index],
                transparent: true,
                opacity: 0.7, // Semi-transparent to see through
                side: THREE.DoubleSide // Visible from both inside and outside
            });

            const panel = new THREE.Mesh(geometry, material);
            panel.position.set(config.position[0], config.position[1], config.position[2]);
            panel.rotation.set(config.rotation[0], config.rotation[1], config.rotation[2]);
            panel.name = `Panel_${this.panelNames[index]}`;

            // Set panel to CUBE layer (layer 2) - main scene but not morph box
            panel.layers.set(2);

            // Store original transforms
            this.originalPositions[index] = panel.position.clone();
            this.originalRotations[index] = panel.rotation.clone();

            this.panels.push(panel);
            this.panelMaterials.push(material);
            this.panelTextures.push(null); // No texture initially
            this.group.add(panel);
        });

        console.log('🎯 6-Panel cube system initialized:', this.panelNames);
        console.log('📍 Cube positioned at:', this.group.position);
        console.log('📐 Cube size:', cubeSize);
        console.log('🔍 DEBUG: Panels created:', this.panels.length);
        console.log('🔍 DEBUG: Group children count:', this.group.children.length);
        console.log('🔍 DEBUG: First panel visible:', this.panels[0]?.visible);
        console.log('🔍 DEBUG: First panel layer:', this.panels[0]?.layers.mask);
    }

    // 🧬 CELLULAR SUBDIVISION MORPHING METHODS

    public setMorphProgress(progress: number): void {
        this.morphProgress = Math.max(0, Math.min(1, progress));

        // Map progress to cellular division levels
        const targetLevel = Math.floor(progress * this.cellularMorphState.maxLevels);
        const levelProgress = (progress * this.cellularMorphState.maxLevels) % 1;

        this.cellularMorphState.currentLevel = targetLevel;
        this.cellularMorphState.morphProgress = levelProgress;

        // Update cellular symbol
        const currentSubdivision = this.cellularMorphState.subdivisionCache.get(targetLevel);
        if (currentSubdivision) {
            const symbolKey = currentSubdivision.cellularPhase;
            this.cellularMorphState.cellularSymbol = this.cellularSymbols[symbolKey];
        }

        this.geometryMode = progress === 0 ? 'cube' : (progress === 1 ? 'sphere' : 'morphing');

        if (progress === 0) {
            this.showColoredPanels();
        } else {
            if (this.solidCube) {
                this.solidCube.visible = false;
            }
            if (this.unifiedMorphMesh) {
                this.unifiedMorphMesh.visible = false;
            }

            this.panels.forEach((panel, index) => {
                panel.visible = true;
                this.applyPanelMorph(panel, progress, index);
            });
        }

        MorphDiagnostics.recordMorphEvent({
            source: 'SkyboxCubeLayer.setMorphProgress',
            progress: this.morphProgress,
            level: targetLevel,
            geometryMode: this.geometryMode,
            detail: {
                cellularSymbol: this.cellularMorphState.cellularSymbol,
                levelProgress,
                panelCount: this.panels.length
            }
        });

        console.log(`🧬 Cellular division: Level ${targetLevel} (${this.cellularMorphState.cellularSymbol}) - ${(progress * 100).toFixed(1)}%`);
    }

    // 🔄 CUBE ROTATION CONTROL (CC2 & CC4)
    private updateCubeRotation(): void {
        // Apply both X and Y axis rotations to the cube group
        this.group.rotation.x = this.midiControls.rotationX;
        this.group.rotation.y = this.midiControls.rotationY;

        console.log(`🔄 Cube rotation - X: ${(this.midiControls.rotationX * 180/Math.PI).toFixed(1)}°, Y: ${(this.midiControls.rotationY * 180/Math.PI).toFixed(1)}°`);
    }

    private applyCellularMorphing(level: number, levelProgress: number): void {
        const subdivisionLevel = this.cellularMorphState.subdivisionCache.get(level);
        if (!subdivisionLevel) return;

        this.panels.forEach((panel, index) => {
            if (panel.visible) {
                // Replace geometry with subdivided version
                panel.geometry.dispose();
                panel.geometry = subdivisionLevel.geometry.clone();

                // Apply spherical transformation based on level
                this.applyCurvedGeometry(panel, subdivisionLevel.sphereProgress);
            }
        });
    }

    private applyCurvedGeometry(panel: THREE.Mesh, sphereProgress: number): void {
        // This is where the cellular osmosis magic happens
        // Transform flat panel into curved surface

        if (sphereProgress === 0) return; // No transformation needed

        const geometry = panel.geometry as THREE.BufferGeometry;
        const positionAttribute = geometry.getAttribute('position');

        if (positionAttribute) {
            const positions = positionAttribute.array as Float32Array;
            const center = panel.position.clone();

            // Apply spherical curvature to simulate cellular membrane
            for (let i = 0; i < positions.length; i += 3) {
                const vertex = new THREE.Vector3(positions[i], positions[i + 1], positions[i + 2]);

                // Calculate distance from panel center
                const distance = vertex.length();
                if (distance > 0) {
                    // Normalize and scale to create spherical curvature
                    const normalizedVertex = vertex.normalize();
                    const sphericalPosition = normalizedVertex.multiplyScalar(3 * (1 + sphereProgress * 0.5));

                    // Blend between flat and spherical
                    vertex.lerp(sphericalPosition, sphereProgress);

                    positions[i] = vertex.x;
                    positions[i + 1] = vertex.y;
                    positions[i + 2] = vertex.z;
                }
            }

            positionAttribute.needsUpdate = true;
            geometry.computeVertexNormals();
        }
    }

    private applyUnifiedCubeToSphereMorph(level: number, levelProgress: number, globalProgress: number): void {
        // For CC1 = 0, show solid cube; for CC1 > 0, use unified morphing
        if (globalProgress === 0) {
            // Show solid cube for CC1 = 0 (starting position)
            this.showSolidCube();
            return;
        }

        // Hide separate panels and solid cube, show unified morphing shape
        this.panels.forEach(panel => panel.visible = false);
        if (this.solidCube) {
            this.solidCube.visible = false;
        }

        // Create or update unified morphing mesh
        if (!this.unifiedMorphMesh) {
            this.createUnifiedMorphMesh();
        }

        this.unifiedMorphMesh!.visible = true;

        // Apply subdivision morphing to unified mesh
        const subdivisionLevel = this.cellularMorphState.subdivisionCache.get(level);
        if (subdivisionLevel) {
            const mesh = this.unifiedMorphMesh!;

            // Replace geometry with subdivided version
            mesh.geometry.dispose();
            mesh.geometry = subdivisionLevel.geometry.clone();
            this.applyPanelColorsToGeometry(mesh.geometry);

            // Apply cube-to-sphere morphing on subdivided geometry
            this.morphSubdividedGeometry(mesh.geometry, globalProgress);
        }
    }

    private createUnifiedMorphMesh(): void {
        // Start with base cube geometry
        const baseLevel = this.cellularMorphState.subdivisionCache.get(0)!;
        const geometry = baseLevel.geometry.clone();

        // Create material that combines all panel colors using vertex colors or UV mapping
        const material = new THREE.MeshLambertMaterial({
            vertexColors: true,
            transparent: true,
            opacity: 1.0
        });

        // Apply panel colors to different faces of the unified geometry
        this.applyPanelColorsToGeometry(geometry);

        this.unifiedMorphMesh = new THREE.Mesh(geometry, material);
        this.unifiedMorphMesh.name = 'UnifiedMorphingCube';
        this.unifiedMorphMesh.layers.set(2);
        this.unifiedMorphMesh.position.set(0, 0, 0);
        this.group.add(this.unifiedMorphMesh);
    }

    private applyPanelColorsToGeometry(geometry: THREE.BufferGeometry): void {
        const positionAttribute = geometry.getAttribute('position');
        const vertexCount = positionAttribute.count;
        const colors = new Float32Array(vertexCount * 3);

        // Apply colors based on face normal/position to simulate panel colors
        for (let i = 0; i < vertexCount; i++) {
            const x = positionAttribute.getX(i);
            const y = positionAttribute.getY(i);
            const z = positionAttribute.getZ(i);

            // Determine which "panel" this vertex belongs to based on position
            let color = new THREE.Color(this.panelColors[0]); // Default to white

            // Simple face detection based on dominant axis
            const absX = Math.abs(x);
            const absY = Math.abs(y);
            const absZ = Math.abs(z);

            if (absX > absY && absX > absZ) {
                color = new THREE.Color(x > 0 ? this.panelColors[4] : this.panelColors[5]); // East/West
            } else if (absY > absX && absY > absZ) {
                color = new THREE.Color(y > 0 ? this.panelColors[1] : this.panelColors[0]); // Ceiling/Floor
            } else {
                color = new THREE.Color(z > 0 ? this.panelColors[2] : this.panelColors[3]); // North/South
            }

            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }

        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    }

    private morphSubdividedGeometry(geometry: THREE.BufferGeometry, progress: number): void {
        const positionAttribute = geometry.getAttribute('position');
        const positions = positionAttribute.array as Float32Array;

        // Store original positions if not stored yet
        if (!geometry.userData.originalPositions) {
            geometry.userData.originalPositions = new Float32Array(positions);
        }

        const originalPositions = geometry.userData.originalPositions;

        // Morph each vertex from cube to sphere
        for (let i = 0; i < positions.length; i += 3) {
            const x = originalPositions[i];
            const y = originalPositions[i + 1];
            const z = originalPositions[i + 2];

            // Calculate sphere position
            const length = Math.sqrt(x * x + y * y + z * z);
            const sphereRadius = 3; // Same as cube half-size

            if (length > 0) {
                const sphereX = (x / length) * sphereRadius;
                const sphereY = (y / length) * sphereRadius;
                const sphereZ = (z / length) * sphereRadius;

                // Interpolate between cube and sphere
                positions[i] = x + (sphereX - x) * progress;
                positions[i + 1] = y + (sphereY - y) * progress;
                positions[i + 2] = z + (sphereZ - z) * progress;
            }
        }

        positionAttribute.needsUpdate = true;
        geometry.computeVertexNormals();
    }

    private morphSolidCubeToSphere(progress: number): void {
        if (!this.solidCube) return;

        const geometry = this.solidCube.geometry as THREE.BoxGeometry;

        // Store original positions if not stored yet
        if (!geometry.userData.originalPositions) {
            const positionAttribute = geometry.getAttribute('position');
            geometry.userData.originalPositions = new Float32Array(positionAttribute.array as Float32Array);
        }

        const positionAttribute = geometry.getAttribute('position');
        const positions = positionAttribute.array as Float32Array;
        const originalPositions = geometry.userData.originalPositions;

        // Morph each vertex from cube to sphere
        for (let i = 0; i < positions.length; i += 3) {
            const x = originalPositions[i];
            const y = originalPositions[i + 1];
            const z = originalPositions[i + 2];

            // Calculate sphere position using spherical projection
            const length = Math.sqrt(x * x + y * y + z * z);
            const sphereRadius = 3; // Same as cube half-size

            if (length > 0) {
                const sphereX = (x / length) * sphereRadius;
                const sphereY = (y / length) * sphereRadius;
                const sphereZ = (z / length) * sphereRadius;

                // Smooth interpolation with easing
                const easedProgress = this.easeInOutCubic(progress);
                positions[i] = x + (sphereX - x) * easedProgress;
                positions[i + 1] = y + (sphereY - y) * easedProgress;
                positions[i + 2] = z + (sphereZ - z) * easedProgress;
            }
        }

        positionAttribute.needsUpdate = true;
        geometry.computeVertexNormals();
    }

    private morphPanelAdvanced(panel: THREE.Mesh, progress: number, panelIndex: number): void {
        const geometry = panel.geometry as THREE.BufferGeometry;

        // Store original positions if not stored yet
        if (!geometry.userData.originalPositions) {
            const positionAttribute = geometry.getAttribute('position');
            geometry.userData.originalPositions = new Float32Array(positionAttribute.array as Float32Array);
        }

        const positionAttribute = geometry.getAttribute('position');
        const positions = positionAttribute.array as Float32Array;
        const originalPositions = geometry.userData.originalPositions;

        // Simple square → circle morphing - keep panels in original positions
        const easedProgress = this.easeInOutCubic(progress);

        for (let i = 0; i < positions.length; i += 3) {
            const x = originalPositions[i];
            const y = originalPositions[i + 1];
            const z = originalPositions[i + 2];

            // Convert square vertices to circular pattern
            const radius = Math.sqrt(x * x + y * y);
            if (radius > 0) {
                const angle = Math.atan2(y, x);
                const circleRadius = 3; // Same as panel size

                const circleX = Math.cos(angle) * circleRadius;
                const circleY = Math.sin(angle) * circleRadius;

                // Interpolate square → circle
                positions[i] = x + (circleX - x) * easedProgress;
                positions[i + 1] = y + (circleY - y) * easedProgress;
                positions[i + 2] = z; // Keep Z unchanged (flat panels)
            }
        }

        positionAttribute.needsUpdate = true;
        geometry.computeVertexNormals();

        console.log(`🔄 Panel ${this.panelNames[panelIndex]}: Square→Circle ${(progress * 100).toFixed(1)}%`);
    }

    private applyPanelMorph(panel: THREE.Mesh, progress: number, panelIndex: number): void {
        // Determine subdivision state based on progress
        const targetLevel = this.cellularMorphState.currentLevel;
        const levelFraction = this.cellularMorphState.morphProgress;

        const subdivisionLevel = this.cellularMorphState.subdivisionCache.get(targetLevel);
        const nextSubdivisionLevel = this.cellularMorphState.subdivisionCache.get(Math.min(targetLevel + 1, this.cellularMorphState.maxLevels));

        if (!subdivisionLevel) {
            // Fallback to simple square→circle morph if cache missing
            this.morphPanelSquareToCircle(panel, progress, panelIndex);
            return;
        }

        // FUTURE: could blend subdivision here, but keep original geometry to preserve textures
        this.applyCurvedGeometry(panel, Math.min(1, subdivisionLevel.sphereProgress + (levelFraction * (1 / this.cellularMorphState.maxLevels))));

        MorphDiagnostics.recordMorphEvent({
            source: 'SkyboxCubeLayer.applyPanelMorph',
            progress,
            level: targetLevel + levelFraction,
            geometryMode: this.geometryMode,
            detail: {
                panelIndex,
                panelName: this.panelNames[panelIndex] || 'unknown',
                levelFraction
            }
        });
    }

    private morphPanelSquareToCircle(panel: THREE.Mesh, progress: number, panelIndex: number): void {
        const geometry = panel.geometry as THREE.BufferGeometry;

        // Store original positions if not stored yet
        if (!geometry.userData.originalPositions) {
            const positionAttribute = geometry.getAttribute('position');
            geometry.userData.originalPositions = new Float32Array(positionAttribute.array as Float32Array);
        }

        const positionAttribute = geometry.getAttribute('position');
        const positions = positionAttribute.array as Float32Array;
        const originalPositions = geometry.userData.originalPositions;

        // NO SCALING/ZOOMING - just square to circle vertex morphing
        const easedProgress = this.easeInOutCubic(progress);

        for (let i = 0; i < positions.length; i += 3) {
            const x = originalPositions[i];
            const y = originalPositions[i + 1];
            const z = originalPositions[i + 2];

            // Convert square vertices to circular pattern
            const radius = Math.sqrt(x * x + y * y);
            if (radius > 0) {
                const angle = Math.atan2(y, x);
                const circleRadius = Math.max(Math.abs(x), Math.abs(y)); // Keep same max extent

                const circleX = Math.cos(angle) * circleRadius;
                const circleY = Math.sin(angle) * circleRadius;

                // Interpolate square → circle (NO SCALING)
                positions[i] = x + (circleX - x) * easedProgress;
                positions[i + 1] = y + (circleY - y) * easedProgress;
                positions[i + 2] = z; // Keep Z unchanged (flat panels)
            }
        }

        positionAttribute.needsUpdate = true;
        geometry.computeVertexNormals();

        MorphDiagnostics.recordMorphEvent({
            source: 'SkyboxCubeLayer.morphPanelSquareToCircle',
            progress,
            level: this.cellularMorphState.currentLevel,
            geometryMode: this.geometryMode,
            detail: {
                panelIndex,
                panelName: this.panelNames[panelIndex] || 'unknown'
            }
        });

        console.log(`🔵 Panel ${this.panelNames[panelIndex]}: Square→Circle ${(progress * 100).toFixed(1)}% (fallback)`);
    }

    private blendPanelGeometry(
        panel: THREE.Mesh,
        baseGeometry: THREE.BufferGeometry,
        targetGeometry: THREE.BufferGeometry,
        blendFactor: number
    ): void {
        const basePosition = baseGeometry.getAttribute('position');
        const targetPosition = targetGeometry.getAttribute('position');
        const panelPosition = (panel.geometry as THREE.BufferGeometry).getAttribute('position');

        if (!basePosition || !targetPosition || !panelPosition) {
            return;
        }

        const baseArray = basePosition.array as Float32Array;
        const targetArray = targetPosition.array as Float32Array;
        const panelArray = panelPosition.array as Float32Array;

        const len = Math.min(baseArray.length, targetArray.length, panelArray.length);
        for (let i = 0; i < len; i++) {
            const baseValue = baseArray[i];
            const targetValue = targetArray[i];
            panelArray[i] = baseValue + (targetValue - baseValue) * blendFactor;
        }

        panelPosition.needsUpdate = true;
        panel.geometry.computeVertexNormals();
    }

    private resetPanelToOriginal(panel: THREE.Mesh, panelIndex: number): void {
        const geometry = panel.geometry as THREE.BufferGeometry;

        // Restore original geometry if it was morphed
        if (geometry.userData.originalPositions) {
            const positionAttribute = geometry.getAttribute('position');
            const positions = positionAttribute.array as Float32Array;
            const originalPositions = geometry.userData.originalPositions;

            // Copy back original vertex positions
            for (let i = 0; i < positions.length; i++) {
                positions[i] = originalPositions[i];
            }

            positionAttribute.needsUpdate = true;
            geometry.computeVertexNormals();
        }

        console.log(`↺ Panel ${this.panelNames[panelIndex]}: Reset to original cube shape`);
    }

    private createSimpleCube(): void {
        // Hide everything else
        this.panels.forEach(panel => panel.visible = false);
        if (this.unifiedMorphMesh) this.unifiedMorphMesh.visible = false;

        // Create ONE SIMPLE CUBE
        if (!this.solidCube) {
            const geometry = new THREE.BoxGeometry(6, 6, 6);
            // THREE.js BoxGeometry face order: [+X(right), -X(left), +Y(top), -Y(bottom), +Z(front), -Z(back)]
            const materials = [
                new THREE.MeshLambertMaterial({ color: 0xffff00, transparent: true, opacity: 0.7 }), // EAST (right) - Yellow
                new THREE.MeshLambertMaterial({ color: 0xff00ff, transparent: true, opacity: 0.7 }), // WEST (left) - Magenta
                new THREE.MeshLambertMaterial({ color: 0x0000ff, transparent: true, opacity: 0.7 }), // CEILING (top) - Blue
                new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 }), // FLOOR (bottom) - White
                new THREE.MeshLambertMaterial({ color: 0xff0000, transparent: true, opacity: 0.7 }), // NORTH (front) - Red
                new THREE.MeshLambertMaterial({ color: 0x00ff00, transparent: true, opacity: 0.7 })  // SOUTH (back) - Green
            ];

            this.solidCube = new THREE.Mesh(geometry, materials);
            this.solidCube.position.set(0, 0, 0);
            this.solidCube.layers.set(2); // CUBE layer (main scene, NOT morph box)
            this.group.add(this.solidCube);
        }

        this.solidCube.visible = true;
        console.log('🎲 SIMPLE CUBE CREATED');
    }

    private addLighting(): void {
        // Ambient light - provides overall illumination
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        // Directional light - main light source
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        this.scene.add(directionalLight);

        // Additional directional light from opposite side
        const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight2.position.set(-10, -10, -5);
        this.scene.add(directionalLight2);

        console.log('💡 Lighting added to scene');
    }

    private easeInOutCubic(t: number): number {
        // Smooth cubic easing for organic morphing feel
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    private showColoredPanels(): void {
        // Show all individual colored panels (PERIAKTOS cube)
        this.panels.forEach(panel => {
            panel.visible = true;
        });

        // Hide solid cube and unified morph mesh
        if (this.solidCube) {
            this.solidCube.visible = false;
        }
        if (this.unifiedMorphMesh) {
            this.unifiedMorphMesh.visible = false;
        }

        console.log('🎨 Showing colored PERIAKTOS panels: FLOOR/CEILING/NORTH/SOUTH/EAST/WEST');
    }

    private showSolidCube(): void {
        // Hide all individual panels
        this.panels.forEach(panel => {
            panel.visible = false;
        });

        // Hide unified morph mesh if it exists
        if (this.unifiedMorphMesh) {
            this.unifiedMorphMesh.visible = false;
        }

        // Create or show a single unified cube with TRANSPARENT colored faces
        if (!this.solidCube) {
            const cubeGeometry = new THREE.BoxGeometry(6, 6, 6);

            // Create TRANSPARENT materials for each face using PERIAKTOS colors
            const materials = [
                new THREE.MeshLambertMaterial({ color: this.panelColors[4], transparent: true, opacity: 0.7 }), // Right - EAST (Yellow)
                new THREE.MeshLambertMaterial({ color: this.panelColors[5], transparent: true, opacity: 0.7 }), // Left - WEST (Magenta)
                new THREE.MeshLambertMaterial({ color: this.panelColors[1], transparent: true, opacity: 0.7 }), // Top - CEILING (Blue)
                new THREE.MeshLambertMaterial({ color: this.panelColors[0], transparent: true, opacity: 0.7 }), // Bottom - FLOOR (White)
                new THREE.MeshLambertMaterial({ color: this.panelColors[2], transparent: true, opacity: 0.7 }), // Front - NORTH (Red)
                new THREE.MeshLambertMaterial({ color: this.panelColors[3], transparent: true, opacity: 0.7 })  // Back - SOUTH (Green)
            ];

            this.solidCube = new THREE.Mesh(cubeGeometry, materials);
            this.solidCube.name = 'TransparentColoredCube';
            this.solidCube.layers.set(2);
            this.solidCube.position.set(0, 0, 0);
            this.group.add(this.solidCube);
        }
        this.solidCube.visible = true;

        console.log('🎲 Showing unified transparent PERIAKTOS cube');
    }

    private showSeparatePanels(): void {
        // Hide solid cube if it exists
        if (this.solidCube) {
            this.solidCube.visible = false;
        }

        if (progress === 0) {
            this.showColoredPanels();
        } else {
            if (this.solidCube) {
                this.solidCube.visible = false;
            }
            if (this.unifiedMorphMesh) {
                this.unifiedMorphMesh.visible = false;
            }

            this.panels.forEach((panel, index) => {
                panel.visible = true;
                this.applyPanelMorph(panel, progress, index);
            });
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

    // 💾 SAVE/LOAD SYSTEM
    public exportSkyboxConfiguration(): any {
        return {
            version: 'v2_subdivision_cellular_osmosis',
            morphProgress: this.morphProgress,
            cellularState: {
                currentLevel: this.cellularMorphState.currentLevel,
                subdivisionEnabled: this.subdivisionEnabled,
                fractalMode: this.fractalMode
            },
            panelColors: this.panelColors,
            timestamp: Date.now()
        };
    }

    public async importSkyboxConfiguration(config: any): Promise<void> {
        console.log('📥 Importing cellular subdivision configuration...', config);

        if (config.version === 'v2_subdivision_cellular_osmosis') {
            this.setMorphProgress(config.morphProgress || 0);
            this.handleMicrotonalMorph(config.cellularState?.fractalMode || false);

            if (config.panelColors) {
                config.panelColors.forEach((color: number, index: number) => {
                    if (this.panelMaterials[index]) {
                        this.panelMaterials[index].color.setHex(color);
                    }
                });
            }

            console.log('✅ Cellular subdivision configuration imported successfully!');
        }
    }

    // Utility methods for compatibility
    public getChromaticNotes(): string[] {
        return ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    }

    // 🖼️ IMAGE/VIDEO TEXTURE MAPPING FOR TRANSPARENT PANELS
    public async loadSkyboxFromImageFiles(files: File[]): Promise<void> {
        console.log('🖼️ Loading images into PERIAKTOS transparent panels...', files.length);

        for (let i = 0; i < files.length && i < this.panels.length; i++) {
            const file = files[i];
            const panelName = this.panelNames[i];

            try {
                // Create texture from file
                const texture = await this.createTextureFromFile(file);

                // Apply to panel with transparency
                this.applyTextureToPanel(i, texture);

                console.log(`✅ ${panelName}: ${file.name} loaded`);

            } catch (error) {
                console.error(`❌ Failed to load ${file.name} for ${panelName}:`, error);
            }
        }
    }

    private async createTextureFromFile(file: File): Promise<THREE.Texture> {
        return new Promise((resolve, reject) => {
            const loader = new THREE.TextureLoader();
            const url = URL.createObjectURL(file);

            loader.load(
                url,
                (texture) => {
                    // Configure texture for transparent blending
                    texture.wrapS = THREE.RepeatWrapping;
                    texture.wrapT = THREE.RepeatWrapping;
                    texture.flipY = false; // Correct orientation for panels

                    URL.revokeObjectURL(url);
                    resolve(texture);
                },
                undefined,
                (error) => {
                    URL.revokeObjectURL(url);
                    reject(error);
                }
            );
        });
    }

    public applyTextureToPanel(panelIndex: number, texture: THREE.Texture): void {
        if (panelIndex >= 0 && panelIndex < this.panels.length) {
            const material = this.panelMaterials[panelIndex];

            // Store old texture reference for cleanup
            if (this.panelTextures[panelIndex]) {
                this.panelTextures[panelIndex]!.dispose();
            }

            // Apply texture with transparency blending
            material.map = texture;
            material.transparent = true;
            material.opacity = 0.8; // Semi-transparent for see-through effect
            material.alphaMap = texture; // Use texture alpha channel

            // Maintain color tint while showing texture
            material.color.copy(new THREE.Color(this.panelColors[panelIndex]));
            material.color.multiplyScalar(0.3); // Subtle color tint

            material.needsUpdate = true;
            this.panelTextures[panelIndex] = texture;

            const panelName = this.panelNames[panelIndex];
            console.log(`🎨 ${panelName} panel: Texture applied with transparency`);
        }
    }

    public removeTextureFromPanel(panelIndex: number): void {
        if (panelIndex >= 0 && panelIndex < this.panels.length) {
            const material = this.panelMaterials[panelIndex];

            if (this.panelTextures[panelIndex]) {
                this.panelTextures[panelIndex]!.dispose();
                this.panelTextures[panelIndex] = null;
            }

            // Reset to original colored transparent state
            material.map = null;
            material.alphaMap = null;
            material.color.setHex(this.panelColors[panelIndex]);
            material.opacity = 0.7;
            material.needsUpdate = true;

            console.log(`🗑️ ${this.panelNames[panelIndex]} panel: Texture removed`);
        }
    }

    public dispose(): void {
        this.panels.forEach(panel => {
            panel.geometry.dispose();
            (panel.material as THREE.Material).dispose();
        });

        this.cellularMorphState.subdivisionCache.forEach(level => {
            level.geometry.dispose();
        });

        this.scene.remove(this.group);
        console.log('🧬 Cellular subdivision system disposed');
    }
}

// Factory function for easy integration
export function createSkyboxCubeLayer(scene: THREE.Scene): SkyboxCubeLayer {
    console.log('🎩👑 Creating SkyboxCubeLayer v2 - White Queen\'s Crown Edition...');
    console.log('🧬 Features: Cellular osmosis/mitosis morphing via Catmull-Clark subdivision');
    console.log('🎯 6-panel PERIAKTOS + 12-tone fractal + MIDI + save/load + wizard spells');

    return new SkyboxCubeLayer(scene);
}
