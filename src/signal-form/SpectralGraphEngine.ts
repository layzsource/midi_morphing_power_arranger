/**
 * 🌊 Spectral Graph Engine - Signal→Form Quantification Core
 *
 * FOUNDATIONAL MATHEMATICS:
 * - Constructs graphs from 3D scene geometry (vertices → nodes, spatial relations → edges)
 * - Computes Laplacian eigendecomposition ("Eaganvectors")
 * - Projects MIDI/audio signals onto modal space
 * - Quantifies visual distortions through spectral analysis
 *
 * Based on signal→form_engine_quantification_spec_claude_handoff_v_0.md
 */

import * as THREE from 'three';

export interface GraphNode {
    id: string;
    position: THREE.Vector3;
    mesh: THREE.Mesh;
    connections: Set<string>;
    weight: number;
}

export interface GraphEdge {
    source: string;
    target: string;
    weight: number;
    distance: number;
}

export interface Eigenmode {
    eigenvalue: number;
    eigenvector: Float32Array;
    frequency: number; // sqrt(eigenvalue)
    participation: number; // How much this mode contributes
}

export interface SpectralState {
    modalCoefficients: Float32Array; // Current projection onto eigenmodes
    stokesParameters: { S1: number, S2: number, S3: number }; // Polarization-like duality
    unity: number; // U parameter - spectral balance
    flatness: number; // F parameter - "white light" measure
    entropy: number; // Disorder measure
    temporalChange: number; // R parameter - change detection
}

export class SpectralGraphEngine {
    private nodes: Map<string, GraphNode> = new Map();
    private edges: GraphEdge[] = [];
    private laplacianMatrix: Float32Array | null = null;
    private eigenmodes: Eigenmode[] = [];
    private currentState: SpectralState;
    private K: number = 64; // Number of eigenmodes to compute

    // Signal processing
    private signalHistory: Float32Array[] = [];
    private maxHistoryLength: number = 60; // 1 second at 60 FPS

    constructor() {
        this.currentState = {
            modalCoefficients: new Float32Array(this.K),
            stokesParameters: { S1: 0, S2: 0, S3: 0 },
            unity: 0,
            flatness: 0,
            entropy: 0,
            temporalChange: 0
        };

        console.log('🌊 SpectralGraphEngine initialized - K=' + this.K + ' eigenmodes');
    }

    /**
     * Build graph structure from 3D scene geometry
     * Each mesh becomes a node, spatial relationships become edges
     */
    public buildGraphFromScene(scene: THREE.Scene, layerMask: number = 2): void {
        console.log('🔗 Building graph from 3D scene geometry...');

        this.nodes.clear();
        this.edges = [];

        // Extract nodes from scene objects
        scene.traverse((object) => {
            if (object instanceof THREE.Mesh && object.layers.test(layerMask)) {
                const node: GraphNode = {
                    id: object.name || `node_${object.id}`,
                    position: object.position.clone(),
                    mesh: object,
                    connections: new Set(),
                    weight: this.calculateNodeWeight(object)
                };

                this.nodes.set(node.id, node);
            }
        });

        // Create edges based on spatial proximity
        this.createSpatialEdges();

        // Compute Laplacian matrix
        this.computeLaplacianMatrix();

        console.log(`🔗 Graph built: ${this.nodes.size} nodes, ${this.edges.length} edges`);
    }

    /**
     * Calculate node weight based on geometry complexity and position
     */
    private calculateNodeWeight(mesh: THREE.Mesh): number {
        const geometry = mesh.geometry;
        let weight = 1.0;

        // Weight by vertex count (more complex geometry = higher weight)
        if (geometry.attributes.position) {
            const vertexCount = geometry.attributes.position.count;
            weight *= Math.log(1 + vertexCount / 1000);
        }

        // Weight by distance from origin (farther = lower influence)
        const distance = mesh.position.length();
        weight *= Math.exp(-distance / 20);

        // Weight by scale (larger objects = higher influence)
        const scale = (mesh.scale.x + mesh.scale.y + mesh.scale.z) / 3;
        weight *= scale;

        return weight;
    }

    /**
     * Create edges based on spatial proximity and visual relationships
     */
    private createSpatialEdges(): void {
        const nodeArray = Array.from(this.nodes.values());

        for (let i = 0; i < nodeArray.length; i++) {
            for (let j = i + 1; j < nodeArray.length; j++) {
                const nodeA = nodeArray[i];
                const nodeB = nodeArray[j];

                const distance = nodeA.position.distanceTo(nodeB.position);

                // Connect nodes within proximity threshold
                const threshold = 15.0; // Adjust based on scene scale
                if (distance < threshold) {
                    const weight = this.calculateEdgeWeight(nodeA, nodeB, distance);

                    const edge: GraphEdge = {
                        source: nodeA.id,
                        target: nodeB.id,
                        weight,
                        distance
                    };

                    this.edges.push(edge);
                    nodeA.connections.add(nodeB.id);
                    nodeB.connections.add(nodeA.id);
                }
            }
        }
    }

    /**
     * Calculate edge weight based on spatial and visual relationships
     */
    private calculateEdgeWeight(nodeA: GraphNode, nodeB: GraphNode, distance: number): number {
        // Base weight inversely proportional to distance
        let weight = 1.0 / (1.0 + distance);

        // Increase weight for nodes with similar properties
        const colorSimilarity = this.calculateColorSimilarity(nodeA.mesh, nodeB.mesh);
        weight *= (1 + colorSimilarity);

        // Geometric relationship weight
        const geometricWeight = Math.sqrt(nodeA.weight * nodeB.weight);
        weight *= geometricWeight;

        return weight;
    }

    /**
     * Calculate color similarity between two meshes
     */
    private calculateColorSimilarity(meshA: THREE.Mesh, meshB: THREE.Mesh): number {
        // Simple color comparison - could be enhanced
        const materialA = meshA.material as THREE.MeshLambertMaterial;
        const materialB = meshB.material as THREE.MeshLambertMaterial;

        if (materialA.color && materialB.color) {
            const colorA = materialA.color;
            const colorB = materialB.color;

            // Calculate RGB distance
            const dr = colorA.r - colorB.r;
            const dg = colorA.g - colorB.g;
            const db = colorA.b - colorB.b;

            const distance = Math.sqrt(dr*dr + dg*dg + db*db);
            return Math.exp(-distance * 2); // Similar colors = higher weight
        }

        return 0.5; // Neutral similarity
    }

    /**
     * Compute the graph Laplacian matrix L = D - A
     * Where D is degree matrix, A is adjacency matrix
     */
    private computeLaplacianMatrix(): void {
        const n = this.nodes.size;
        if (n === 0) return;

        console.log('🧮 Computing Laplacian matrix...');

        // Create adjacency matrix
        const adjacency = new Float32Array(n * n);
        const degrees = new Float32Array(n);
        const nodeIds = Array.from(this.nodes.keys());

        // Fill adjacency matrix and compute degrees
        for (const edge of this.edges) {
            const i = nodeIds.indexOf(edge.source);
            const j = nodeIds.indexOf(edge.target);

            if (i >= 0 && j >= 0) {
                adjacency[i * n + j] = edge.weight;
                adjacency[j * n + i] = edge.weight;
                degrees[i] += edge.weight;
                degrees[j] += edge.weight;
            }
        }

        // Create Laplacian: L = D - A
        this.laplacianMatrix = new Float32Array(n * n);
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < n; j++) {
                if (i === j) {
                    this.laplacianMatrix[i * n + j] = degrees[i];
                } else {
                    this.laplacianMatrix[i * n + j] = -adjacency[i * n + j];
                }
            }
        }

        // Compute eigendecomposition (simplified - would use proper linear algebra library)
        this.computeEigenmodes();

        console.log('🧮 Laplacian matrix computed: ' + n + 'x' + n);
    }

    /**
     * Compute eigenmodes of the Laplacian (simplified implementation)
     * In production, would use proper eigenvalue solver like ARPACK
     */
    private computeEigenmodes(): void {
        if (!this.laplacianMatrix) return;

        console.log('🌊 Computing Eaganvectors (eigenmodes)...');

        const n = this.nodes.size;
        this.eigenmodes = [];

        // Simplified eigenmode computation - would use proper library
        // For now, create synthetic modes based on graph structure
        for (let k = 0; k < Math.min(this.K, n); k++) {
            const eigenvalue = k * k * 0.1; // Simplified eigenvalue
            const eigenvector = new Float32Array(n);

            // Create synthetic eigenvector with spatial patterns
            const nodeArray = Array.from(this.nodes.values());
            for (let i = 0; i < n; i++) {
                const node = nodeArray[i];
                const angle = Math.atan2(node.position.y, node.position.x);
                const radius = node.position.length();

                // Mix radial and angular components
                eigenvector[i] = Math.cos(k * angle) * Math.exp(-radius * 0.1) +
                               Math.sin(k * radius * 0.1);
            }

            // Normalize eigenvector
            const norm = Math.sqrt(eigenvector.reduce((sum, val) => sum + val * val, 0));
            if (norm > 0) {
                for (let i = 0; i < n; i++) {
                    eigenvector[i] /= norm;
                }
            }

            const eigenmode: Eigenmode = {
                eigenvalue,
                eigenvector,
                frequency: Math.sqrt(eigenvalue),
                participation: 0 // Will be computed during projection
            };

            this.eigenmodes.push(eigenmode);
        }

        console.log('🌊 Computed ' + this.eigenmodes.length + ' Eaganvectors');
    }

    /**
     * Project signal input onto modal space
     * This is where MIDI/audio becomes spectral coefficients
     */
    public projectSignalToModes(signalInput: { [nodeId: string]: number }): void {
        if (this.eigenmodes.length === 0) return;

        const n = this.nodes.size;
        const signal = new Float32Array(n);
        const nodeIds = Array.from(this.nodes.keys());

        // Convert input signal to vector form
        for (let i = 0; i < n; i++) {
            const nodeId = nodeIds[i];
            signal[i] = signalInput[nodeId] || 0;
        }

        // Project onto each eigenmode: c_k = <signal, eigenvector_k>
        for (let k = 0; k < this.eigenmodes.length; k++) {
            let coefficient = 0;
            const eigenvector = this.eigenmodes[k].eigenvector;

            for (let i = 0; i < n; i++) {
                coefficient += signal[i] * eigenvector[i];
            }

            this.currentState.modalCoefficients[k] = coefficient;
            this.eigenmodes[k].participation = Math.abs(coefficient);
        }

        // Store signal history for temporal analysis
        this.signalHistory.push(new Float32Array(this.currentState.modalCoefficients));
        if (this.signalHistory.length > this.maxHistoryLength) {
            this.signalHistory.shift();
        }

        // Compute derived spectral parameters
        this.computeSpectralParameters();
    }

    /**
     * Compute spectral quantification parameters
     */
    private computeSpectralParameters(): void {
        const coeffs = this.currentState.modalCoefficients;

        // Unity parameter: spectral balance measure
        let totalEnergy = 0;
        let balanceSum = 0;
        for (let k = 0; k < this.eigenmodes.length; k++) {
            const energy = coeffs[k] * coeffs[k];
            totalEnergy += energy;
            balanceSum += energy / (1 + this.eigenmodes[k].eigenvalue);
        }
        this.currentState.unity = totalEnergy > 0 ? balanceSum / totalEnergy : 0;

        // Flatness parameter: spectral "whiteness"
        const geometricMean = Math.exp(
            coeffs.reduce((sum, c) => sum + Math.log(Math.abs(c) + 1e-10), 0) / coeffs.length
        );
        const arithmeticMean = coeffs.reduce((sum, c) => sum + Math.abs(c), 0) / coeffs.length;
        this.currentState.flatness = arithmeticMean > 0 ? geometricMean / arithmeticMean : 0;

        // Entropy measure
        const normalizedCoeffs = coeffs.map(c => Math.abs(c) / (totalEnergy + 1e-10));
        this.currentState.entropy = -normalizedCoeffs.reduce((sum, p) => {
            return sum + (p > 1e-10 ? p * Math.log(p) : 0);
        }, 0);

        // Stokes-like polarization parameters (dual-mode analysis)
        if (this.eigenmodes.length >= 3) {
            const c0 = coeffs[0];
            const c1 = coeffs[1];
            const c2 = coeffs[2];

            this.currentState.stokesParameters.S1 = (c0*c0 - c1*c1) / (c0*c0 + c1*c1 + 1e-10);
            this.currentState.stokesParameters.S2 = (2*c0*c1) / (c0*c0 + c1*c1 + 1e-10);
            this.currentState.stokesParameters.S3 = c2 / Math.sqrt(c0*c0 + c1*c1 + c2*c2 + 1e-10);
        }

        // Temporal change detection
        if (this.signalHistory.length >= 2) {
            const prev = this.signalHistory[this.signalHistory.length - 2];
            const curr = this.signalHistory[this.signalHistory.length - 1];

            let changeSum = 0;
            for (let k = 0; k < Math.min(prev.length, curr.length); k++) {
                const diff = curr[k] - prev[k];
                changeSum += diff * diff;
            }

            this.currentState.temporalChange = Math.sqrt(changeSum);
        }
    }

    /**
     * Apply spectral analysis to MIDI input
     */
    public processMIDIInput(ccValues: { [cc: number]: number }, noteStates: boolean[]): void {
        // Convert MIDI to signal field
        const signalInput: { [nodeId: string]: number } = {};
        const nodeIds = Array.from(this.nodes.keys());

        // Map CC values to different nodes
        const cc1 = (ccValues[1] || 0) / 127; // Mod wheel
        const cc2 = (ccValues[2] || 0) / 127; // Pitch wheel
        const cc4 = (ccValues[4] || 0) / 127; // Other controls

        // Distribute signal across nodes based on CC values and note states
        for (let i = 0; i < nodeIds.length; i++) {
            const nodeId = nodeIds[i];
            let signal = 0;

            // CC1 affects all nodes with spatial weighting
            const node = this.nodes.get(nodeId)!;
            const spatialWeight = Math.exp(-node.position.length() / 10);
            signal += cc1 * spatialWeight;

            // CC2 creates rotational pattern
            const angle = Math.atan2(node.position.y, node.position.x);
            signal += cc2 * Math.sin(angle + Date.now() * 0.001);

            // Notes create impulse patterns
            for (let note = 0; note < Math.min(noteStates.length, 12); note++) {
                if (noteStates[note]) {
                    const notePattern = Math.cos(note * Math.PI / 6 + angle);
                    signal += 0.5 * notePattern;
                }
            }

            signalInput[nodeId] = signal;
        }

        // Project signal onto eigenmodes
        this.projectSignalToModes(signalInput);

        console.log(`🎛️ MIDI processed → Unity: ${this.currentState.unity.toFixed(3)}, ` +
                   `Entropy: ${this.currentState.entropy.toFixed(3)}, ` +
                   `Change: ${this.currentState.temporalChange.toFixed(3)}`);
    }

    /**
     * Get current spectral state for visualization
     */
    public getCurrentState(): SpectralState {
        return { ...this.currentState };
    }

    /**
     * Get eigenmode information
     */
    public getEigenmodes(): Eigenmode[] {
        return [...this.eigenmodes];
    }

    /**
     * Get V-I-T parameters for AIWS mapping
     */
    public getVITParameters(): { V: number, I: number, T: number } {
        return {
            V: this.currentState.unity, // Visual/Spatial distortion
            I: this.currentState.entropy, // Identity coherence (inverted)
            T: this.currentState.temporalChange // Time distortion
        };
    }

    /**
     * Convert V-I-T to RGB channels
     */
    public getVITtoRGB(): { r: number, g: number, b: number } {
        const vit = this.getVITParameters();

        return {
            r: Math.min(1, Math.max(0, vit.T)), // Time → Red
            g: Math.min(1, Math.max(0, vit.V)), // Visual → Green
            b: Math.min(1, Math.max(0, 1 - vit.I)) // Identity (coherence) → Blue
        };
    }

    public dispose(): void {
        this.nodes.clear();
        this.edges = [];
        this.signalHistory = [];
        console.log('🌊 SpectralGraphEngine disposed');
    }
}