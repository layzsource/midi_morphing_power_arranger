/**
 * 🎭 SkyboxCubeLayer Morph Integration - SUBDIVISION BACKUP V2
 *
 * This version creates separate subdivided spheres for each panel
 * Good microtonal TET progression but creates molecular structure instead of unified layers
 *
 * BACKUP DATE: 2025-09-23
 * STATUS: Working subdivision system, separate spheres for each panel
 */

import * as THREE from 'three';

export class SkyboxMorphIntegrationSubdivision {
    private scene: THREE.Scene;
    private activeMorphMeshes: Map<string, THREE.Mesh> = new Map();

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        console.log('🎭 SkyboxCubeLayer subdivision morph integration ready (BACKUP V2)');
    }

    /**
     * 🔄 Subdivision-based microtonal morphing (BACKUP V2)
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

        // SUBDIVISION-BASED MICROTONAL MORPH - Create separate sphere for each subdivision level!
        const subdivisionLevel = this.mapProgressToSubdivision(progress, deweyMode);
        const morphedGeometry = this.createSubdividedGeometry(mesh, subdivisionLevel, deweyMode);

        // Clean replacement - dispose old, set new
        if (mesh.geometry) {
            mesh.geometry.dispose();
        }
        mesh.geometry = morphedGeometry;
        mesh.geometry.needsUpdate = true;

        // Track for cleanup
        this.activeMorphMeshes.set(meshId, mesh);

        // Visual feedback
        this.updateMorphVisuals(mesh, subdivisionLevel, deweyMode);

        console.log(`🎵 Microtonal subdivision: Level ${subdivisionLevel.toFixed(2)} (${deweyMode})`);
    }

    /**
     * 🎯 Map your Dewey modes to subdivision levels (PROPER MICROTONAL SYSTEM)
     */
    private mapProgressToSubdivision(progress: number, deweyMode: string): number {
        // Each mode creates different subdivision face counts for microtonal systems
        const subdivisionModes = {
            '6-PANEL': {
                maxLevel: 1,      // 6 → 24 faces (6-TET to 12-TET)
                baseFaces: 6
            },
            '12-TONE': {
                maxLevel: 2,      // 6 → 96 faces (12-TET to 48-TET)
                baseFaces: 6
            },
            '24-TET': {
                maxLevel: 3,      // 6 → 384 faces (24-TET to 192-TET)
                baseFaces: 6
            },
            'HYPERMICRO': {
                maxLevel: 2,      // SAFE: 6 → 96 faces (prevent crash)
                baseFaces: 6
            }
        };

        const config = subdivisionModes[deweyMode as keyof typeof subdivisionModes] || subdivisionModes['6-PANEL'];
        return progress * config.maxLevel;
    }

    /**
     * 🏗️ Create subdivided sphere geometry for microtonal TET system
     */
    private createSubdividedGeometry(originalMesh: THREE.Mesh, subdivisionLevel: number, deweyMode: string): THREE.BufferGeometry {
        const size = this.getBaseCubeSize(originalMesh);
        const radius = size / 2;

        if (subdivisionLevel === 0) {
            // Pure cube - no subdivision
            return new THREE.BoxGeometry(size, size, size);
        }

        // Create subdivided sphere based on level and mode
        const sphereDetail = this.calculateSphereDetail(subdivisionLevel, deweyMode);

        // Create sphere with calculated detail (this creates separate spheres for each panel!)
        return new THREE.SphereGeometry(radius, sphereDetail.widthSegments, sphereDetail.heightSegments);
    }

    /**
     * 🎵 Calculate sphere detail based on microtonal subdivision system
     */
    private calculateSphereDetail(subdivisionLevel: number, deweyMode: string): { widthSegments: number, heightSegments: number } {
        // Base segments for each mode (safe levels to prevent crashes)
        const baseModeSegments = {
            '6-PANEL': 8,       // Start with 8 segments
            '12-TONE': 12,      // Start with 12 segments
            '24-TET': 16,       // Start with 16 segments
            'HYPERMICRO': 8     // SAFE: Start low to prevent crash
        };

        const baseSegments = baseModeSegments[deweyMode as keyof typeof baseModeSegments] || 8;

        // Progressive subdivision (multiply by level, but cap to prevent crashes)
        const multiplier = Math.floor(subdivisionLevel) + 1;
        const widthSegments = Math.min(baseSegments * multiplier, 32);  // Cap at 32
        const heightSegments = Math.min(baseSegments * multiplier, 24); // Cap at 24

        console.log(`🎵 ${deweyMode} Level ${subdivisionLevel.toFixed(2)}: ${widthSegments}x${heightSegments} segments`);

        return { widthSegments, heightSegments };
    }

    /**
     * 🎨 Update visual feedback for subdivision levels (MICROTONAL SYSTEM)
     */
    private updateMorphVisuals(mesh: THREE.Mesh, subdivisionLevel: number, deweyMode: string): void {
        const material = mesh.material as THREE.MeshLambertMaterial;

        // Distinct color schemes for each microtonal mode
        const modeColors = {
            '6-PANEL': { h: 0.08, s: 0.9 },    // Orange-red (6-TET base)
            '12-TONE': { h: 0.55, s: 0.9 },    // Cyan-blue (12-TET base)
            '24-TET': { h: 0.75, s: 0.9 },     // Purple-magenta (24-TET base)
            'HYPERMICRO': { h: 0.33, s: 1.0 }  // Pure green (micro-intervals)
        };

        const colorConfig = modeColors[deweyMode as keyof typeof modeColors] || modeColors['6-PANEL'];

        // Brightness increases with subdivision complexity
        const maxLevels = { '6-PANEL': 1, '12-TONE': 2, '24-TET': 3, 'HYPERMICRO': 2 };
        const maxLevel = maxLevels[deweyMode as keyof typeof maxLevels] || 1;
        const levelProgress = Math.min(subdivisionLevel / maxLevel, 1);

        let lightness: number;
        switch (deweyMode) {
            case 'HYPERMICRO':
                lightness = 0.3 + (levelProgress * 0.6); // Bright green glow at high subdivisions
                break;
            case '24-TET':
                lightness = 0.4 + (levelProgress * 0.5); // Purple intensity
                break;
            case '12-TONE':
                lightness = 0.5 + (levelProgress * 0.4); // Blue brightness
                break;
            default: // 6-PANEL
                lightness = 0.6 + (levelProgress * 0.3); // Warm orange
        }

        material.color.setHSL(colorConfig.h, colorConfig.s, lightness);

        // Show wireframe at high subdivision levels to see the detail
        if (subdivisionLevel > 1.5) {
            material.wireframe = true;
            material.wireframeLinewidth = 1;
        } else {
            material.wireframe = false;
        }

        material.transparent = false;
        material.opacity = 1.0;

        console.log(`🎨 ${deweyMode} subdivision level ${subdivisionLevel.toFixed(2)}: ${lightness.toFixed(2)} lightness`);
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

        console.log('🧹 SkyboxMorphIntegration subdivision backup cleaned up');
    }
}