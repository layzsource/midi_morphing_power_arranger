/**
 * 🎭 SkyboxCubeLayer Morph Integration Patch - SMOOTH MORPH BACKUP
 *
 * This version creates smooth cube-to-sphere morphing (no subdivision)
 * Good for other purposes but not the microtonal subdivision goal
 *
 * BACKUP DATE: 2025-09-23
 * STATUS: Working smooth morphing, unified sphere at 100%
 */

import * as THREE from 'three';

export class SkyboxMorphIntegrationSmooth {
    private scene: THREE.Scene;
    private activeMorphMeshes: Map<string, THREE.Mesh> = new Map();

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        console.log('🎭 SkyboxCubeLayer smooth morph integration ready (BACKUP)');
    }

    /**
     * 🔄 Smooth cube-to-sphere morphing (BACKUP VERSION)
     */
    public applyCatmullClarkMorph(mesh: THREE.Mesh, progress: number, deweyMode: string): void {
        const meshId = mesh.uuid;

        // Remove old geometry to prevent dual visibility
        if (this.activeMorphMeshes.has(meshId)) {
            const oldMesh = this.activeMorphMeshes.get(meshId);
            if (oldMesh && oldMesh.geometry) {
                oldMesh.geometry.dispose();
            }
        }

        if (progress === 0) {
            // Pure cube state - use original geometry
            this.resetToBaseCube(mesh);
            this.activeMorphMeshes.delete(meshId);
            return;
        }

        // SMOOTH CUBE-TO-SPHERE MORPH - Same scale, no separation!
        const morphedGeometry = this.createSubdividedGeometry(mesh, progress);

        // Clean replacement - dispose old, set new
        if (mesh.geometry) {
            mesh.geometry.dispose();
        }
        mesh.geometry = morphedGeometry;
        mesh.geometry.needsUpdate = true;

        // Track for cleanup
        this.activeMorphMeshes.set(meshId, mesh);

        // Visual feedback
        this.updateMorphVisuals(mesh, progress, deweyMode);

        console.log(`🎵 Smooth cube-sphere morph: ${(progress * 100).toFixed(1)}% (${deweyMode})`);
    }

    /**
     * 🏗️ Create smooth cube-to-sphere morph geometry
     */
    private createSubdividedGeometry(originalMesh: THREE.Mesh, progress: number): THREE.BufferGeometry {
        const size = this.getBaseCubeSize(originalMesh);
        const radius = size / 2; // Same scale - sphere fits exactly in cube

        if (progress === 0) {
            // Pure cube
            return new THREE.BoxGeometry(size, size, size);
        }

        if (progress === 1) {
            // Pure sphere with same scale
            return new THREE.SphereGeometry(radius, 32, 32);
        }

        // Smooth interpolation between cube and sphere
        return this.createMorphedGeometry(size, radius, progress);
    }

    /**
     * 🌊 Create unified cube-to-sphere morph (FIXED - no bubble spheres)
     */
    private createMorphedGeometry(cubeSize: number, sphereRadius: number, progress: number): THREE.BufferGeometry {
        if (progress >= 0.95) {
            // At near 100%, return perfect unified sphere
            return new THREE.SphereGeometry(sphereRadius, 32, 16);
        }

        // Create base cube with good detail for morphing
        const segments = 6; // Reduced to prevent over-segmentation
        const cubeGeometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize, segments, segments, segments);

        const resultGeometry = cubeGeometry.clone();
        const positions = resultGeometry.attributes.position.array as Float32Array;

        // GLOBAL CENTER POINT - all panels converge here
        const centerX = 0;
        const centerY = 0;
        const centerZ = 0;

        // Apply unified spherical transformation
        for (let i = 0; i < positions.length; i += 3) {
            let x = positions[i];
            let y = positions[i + 1];
            let z = positions[i + 2];

            // Calculate distance from global center
            const distance = Math.sqrt(x * x + y * y + z * z);

            if (distance > 0) {
                // Direction from center to vertex
                const nx = x / distance;
                const ny = y / distance;
                const nz = z / distance;

                // Target position on UNIFIED SPHERE (all panels converge to same sphere)
                const sphereX = centerX + (nx * sphereRadius);
                const sphereY = centerY + (ny * sphereRadius);
                const sphereZ = centerZ + (nz * sphereRadius);

                // Progressive morphing with stronger convergence at high progress
                const convergenceProgress = this.enhancedSmoothStep(progress);

                positions[i] = x * (1 - convergenceProgress) + sphereX * convergenceProgress;
                positions[i + 1] = y * (1 - convergenceProgress) + sphereY * convergenceProgress;
                positions[i + 2] = z * (1 - convergenceProgress) + sphereZ * convergenceProgress;
            }
        }

        resultGeometry.attributes.position.needsUpdate = true;
        resultGeometry.computeVertexNormals();

        return resultGeometry;
    }

    /**
     * 🎨 Enhanced smooth step for better convergence
     */
    private enhancedSmoothStep(t: number): number {
        // Stronger curve that forces convergence near the end
        if (t > 0.8) {
            // Rapid convergence in final 20%
            const finalPhase = (t - 0.8) / 0.2;
            return 0.8 + (finalPhase * finalPhase * (3 - 2 * finalPhase)) * 0.2;
        }
        return t * t * (3 - 2 * t); // Standard smoothstep for early phases
    }

    /**
     * 🎨 Smooth step function for natural easing
     */
    private smoothStep(t: number): number {
        return t * t * (3 - 2 * t); // Smooth hermite interpolation
    }

    /**
     * 🎨 Update visual feedback for morph
     */
    private updateMorphVisuals(mesh: THREE.Mesh, progress: number, deweyMode: string): void {
        const material = mesh.material as THREE.MeshLambertMaterial;

        // Distinct color schemes for each mode
        const modeColors = {
            '6-PANEL': { h: 0.08, s: 0.9 },    // Orange-red
            '12-TONE': { h: 0.55, s: 0.9 },    // Cyan-blue
            '24-TET': { h: 0.75, s: 0.9 },     // Purple-magenta
            'HYPERMICRO': { h: 0.33, s: 1.0 }  // Pure green
        };

        const colorConfig = modeColors[deweyMode as keyof typeof modeColors] || modeColors['6-PANEL'];

        // Different lightness curves for each mode
        let lightness: number;
        switch (deweyMode) {
            case 'HYPERMICRO':
                lightness = 0.3 + (progress * 0.5); // Bright green glow
                break;
            case '24-TET':
                lightness = 0.4 + (progress * 0.4); // Purple shimmer
                break;
            case '12-TONE':
                lightness = 0.5 + (progress * 0.3); // Blue fade
                break;
            default: // 6-PANEL
                lightness = 0.6 + (progress * 0.2); // Warm orange
        }

        material.color.setHSL(colorConfig.h, colorConfig.s, lightness);

        // Keep solid surfaces for better visibility
        material.wireframe = false;
        material.transparent = false;
        material.opacity = 1.0;
    }

    /**
     * 🔄 Reset to base cube
     */
    private resetToBaseCube(mesh: THREE.Mesh): void {
        const size = this.getBaseCubeSize(mesh);

        // Clean disposal
        if (mesh.geometry) {
            mesh.geometry.dispose();
        }

        // Create fresh cube geometry
        mesh.geometry = new THREE.BoxGeometry(size, size, size);
        mesh.geometry.needsUpdate = true;

        // Reset material
        const material = mesh.material as THREE.MeshLambertMaterial;
        material.wireframe = false;
        material.color.setHex(0x444444); // Default cube color
    }

    /**
     * 📏 Get base cube size from mesh
     */
    private getBaseCubeSize(mesh: THREE.Mesh): number {
        // Try to get size from userData or compute from geometry
        if (mesh.userData.cubeSize) {
            return mesh.userData.cubeSize;
        }

        mesh.geometry.computeBoundingBox();
        const box = mesh.geometry.boundingBox!;
        return Math.max(box.max.x - box.min.x, box.max.y - box.min.y, box.max.z - box.min.z);
    }

    /**
     * 🧹 Cleanup all morph meshes
     */
    public dispose(): void {
        this.activeMorphMeshes.forEach(mesh => {
            if (mesh.geometry) {
                mesh.geometry.dispose();
            }
        });
        this.activeMorphMeshes.clear();

        console.log('🧹 SkyboxMorphIntegration smooth backup cleaned up');
    }
}