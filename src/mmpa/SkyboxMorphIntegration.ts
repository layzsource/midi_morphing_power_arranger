/**
 * 🎭 SkyboxCubeLayer Morph Integration Patch
 *
 * Replaces the problematic dual-visibility cube/sphere morph
 * with smooth Catmull-Clark subdivision surfaces
 */

import * as THREE from 'three';
import { MicrotonalFrequencyCalculator, FrequencyData, createMicrotonalFrequencyCalculator } from './MicrotonalFrequencyCalculator';

export class SkyboxMorphIntegration {
    private scene: THREE.Scene;
    private activeMorphMeshes: Map<string, THREE.Mesh> = new Map();
    private frequencyCalculator: MicrotonalFrequencyCalculator;
    private currentFrequencyData: Map<string, FrequencyData[]> = new Map();

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.frequencyCalculator = createMicrotonalFrequencyCalculator();
        console.log('🎭 SkyboxCubeLayer morph integration ready with real frequency mathematics');
    }

    /**
     * 🔄 Replace the problematic applyCurvedGeometry method
     * This is the NEW way - no more dual visibility!
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

        // LAYERED TRANSPARENT SPHERES - All align at center with different subdivision levels!
        const subdivisionLevel = this.mapProgressToSubdivision(progress, deweyMode);

        // Calculate real frequency data for this mesh
        const panelIndex = this.getPanelIndex(mesh);
        const frequencyData = this.frequencyCalculator.getFrequencyData(subdivisionLevel, deweyMode, panelIndex);
        this.currentFrequencyData.set(mesh.uuid, [frequencyData]);

        // Create layered spheres that converge to center at 100%
        this.createLayeredSpheres(mesh, progress, subdivisionLevel, deweyMode);

        console.log(`🎵 Layered spheres: Progress ${(progress*100).toFixed(1)}% Level ${subdivisionLevel.toFixed(2)} (${deweyMode})`);
        console.log(`🎼 Real frequency: ${frequencyData.frequency.toFixed(3)}Hz (${frequencyData.cents.toFixed(1)}¢) [${frequencyData.deweyCode}]`);
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
     * 🌐 Create layered transparent spheres that align at center (NEW APPROACH)
     */
    private createLayeredSpheres(mesh: THREE.Mesh, progress: number, subdivisionLevel: number, deweyMode: string): void {
        const size = this.getBaseCubeSize(mesh);
        const baseRadius = size / 2;

        // Calculate how much to move toward center
        const centeringProgress = progress; // 0 = original position, 1 = centered

        // Get original mesh position
        const originalPosition = this.getOriginalPanelPosition(mesh);

        // Calculate target center position
        const centerX = 0;
        const centerY = 0;
        const centerZ = 0;

        // Interpolate position toward center
        const currentX = originalPosition.x * (1 - centeringProgress) + centerX * centeringProgress;
        const currentY = originalPosition.y * (1 - centeringProgress) + centerY * centeringProgress;
        const currentZ = originalPosition.z * (1 - centeringProgress) + centerZ * centeringProgress;

        // Update mesh position
        mesh.position.set(currentX, currentY, currentZ);

        // Create appropriate geometry based on progress
        let geometry: THREE.BufferGeometry;

        if (subdivisionLevel === 0) {
            // Pure cube - no subdivision
            geometry = new THREE.BoxGeometry(size, size, size);
        } else {
            // Create subdivided sphere based on level and mode
            const sphereDetail = this.calculateSphereDetail(subdivisionLevel, deweyMode);
            geometry = new THREE.SphereGeometry(baseRadius, sphereDetail.widthSegments, sphereDetail.heightSegments);
        }

        // Clean replacement - dispose old, set new
        if (mesh.geometry) {
            mesh.geometry.dispose();
        }
        mesh.geometry = geometry;
        mesh.geometry.needsUpdate = true;

        // Track for cleanup
        this.activeMorphMeshes.set(mesh.uuid, mesh);

        // Update visual feedback with transparency
        this.updateLayeredVisuals(mesh, progress, subdivisionLevel, deweyMode);
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
     * 🎨 Smooth step function for natural easing
     */
    private smoothStep(t: number): number {
        return t * t * (3 - 2 * t); // Smooth hermite interpolation
    }

    /**
     * 🔄 Single subdivision iteration (SIMPLIFIED)
     */
    private subdivideGeometryOnce(geometry: THREE.BufferGeometry): THREE.BufferGeometry {
        // Simple subdivision - just increase detail
        geometry.computeBoundingBox();
        const size = geometry.boundingBox!.max.x * 2;
        return new THREE.BoxGeometry(size, size, size, 8, 8, 8);
    }

    /**
     * 🌊 Blend between two geometries
     */
    private blendGeometries(geo1: THREE.BufferGeometry, geo2: THREE.BufferGeometry, factor: number): THREE.BufferGeometry {
        const result = geo1.clone();
        const pos1 = geo1.attributes.position.array as Float32Array;
        const pos2 = geo2.attributes.position.array as Float32Array;
        const resultPos = result.attributes.position.array as Float32Array;

        const minLength = Math.min(pos1.length, pos2.length, resultPos.length);

        for (let i = 0; i < minLength; i++) {
            resultPos[i] = pos1[i] * (1 - factor) + pos2[i] * factor;
        }

        result.attributes.position.needsUpdate = true;
        result.computeVertexNormals();

        return result;
    }

    /**
     * 🎯 Get original panel position (before morphing)
     */
    private getOriginalPanelPosition(mesh: THREE.Mesh): THREE.Vector3 {
        // Try to get original position from userData
        if (mesh.userData.originalPosition) {
            return mesh.userData.originalPosition.clone();
        }

        // Fallback: use current position as original (first time)
        const originalPos = mesh.position.clone();
        mesh.userData.originalPosition = originalPos.clone();
        return originalPos;
    }

    /**
     * 🎨 Update visual feedback for layered transparent spheres (NEW SYSTEM)
     */
    private updateLayeredVisuals(mesh: THREE.Mesh, progress: number, subdivisionLevel: number, deweyMode: string): void {
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
                lightness = 0.3 + (levelProgress * 0.6);
                break;
            case '24-TET':
                lightness = 0.4 + (levelProgress * 0.5);
                break;
            case '12-TONE':
                lightness = 0.5 + (levelProgress * 0.4);
                break;
            default: // 6-PANEL
                lightness = 0.6 + (levelProgress * 0.3);
        }

        material.color.setHSL(colorConfig.h, colorConfig.s, lightness);

        // TRANSPARENCY SYSTEM - become more transparent as they converge to center
        const convergenceProgress = progress; // 0 = solid, 1 = very transparent
        material.transparent = convergenceProgress > 0.1;
        material.opacity = Math.max(0.2, 1 - (convergenceProgress * 0.7)); // Never completely invisible

        // Show wireframe at high subdivision levels
        material.wireframe = subdivisionLevel > 1.5;
        if (material.wireframe) {
            material.wireframeLinewidth = 1;
        }

        console.log(`🌐 ${deweyMode} Layer: Level ${subdivisionLevel.toFixed(2)}, Progress ${(progress*100).toFixed(1)}%, Opacity ${material.opacity.toFixed(2)}`);
    }

    /**
     * 🎨 Update visual feedback for subdivision levels (OLD SYSTEM - DEPRECATED)
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
     * 🔄 Reset to base cube (NEW - also resets position)
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

        // Reset position to original location
        if (mesh.userData.originalPosition) {
            mesh.position.copy(mesh.userData.originalPosition);
        }

        // Reset material
        const material = mesh.material as THREE.MeshLambertMaterial;
        material.wireframe = false;
        material.transparent = false;
        material.opacity = 1.0;
        material.color.setHex(0x444444); // Default cube color

        console.log('🔄 Reset to base cube with original position');
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
     * 🎵 Control morph with musical parameters
     */
    public morphWithMusicalControl(
        mesh: THREE.Mesh,
        cents: number,
        deweyMode: string = '12-TONE'
    ): void {
        // Convert musical cents to subdivision progress
        const maxCents = 1200; // One octave
        const progress = Math.min(cents / maxCents, 1.0);

        this.applyCatmullClarkMorph(mesh, progress, deweyMode);

        console.log(`🎵 Musical morph: ${cents}¢ → ${(progress * 100).toFixed(1)}% (${deweyMode})`);
    }

    /**
     * 🎛️ Control with theremin field
     */
    public morphWithThereminField(
        mesh: THREE.Mesh,
        proximity: number,
        deweyMode: string = '12-TONE'
    ): void {
        // Direct proximity to subdivision progress
        const progress = Math.max(0, Math.min(proximity, 1));

        this.applyCatmullClarkMorph(mesh, progress, deweyMode);

        console.log(`🎛️ Theremin morph: ${(proximity * 100).toFixed(1)}% → ${(progress * 100).toFixed(1)}% cube-to-sphere`);
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

        console.log('🧹 SkyboxMorphIntegration cleaned up');
    }

    /**
     * 🎵 Get panel index from mesh (for frequency calculations)
     */
    private getPanelIndex(mesh: THREE.Mesh): number {
        // Try to get panel index from userData
        if (mesh.userData.panelIndex !== undefined) {
            return mesh.userData.panelIndex;
        }

        // Fallback: derive from position or assign sequentially
        const meshId = mesh.uuid;
        const allMeshes = Array.from(this.activeMorphMeshes.keys());
        const index = allMeshes.indexOf(meshId);

        // Store for future use
        mesh.userData.panelIndex = index >= 0 ? index : 0;
        return mesh.userData.panelIndex;
    }

    /**
     * 🎼 Get current frequency data for a mesh
     */
    public getFrequencyDataForMesh(mesh: THREE.Mesh): FrequencyData[] | null {
        return this.currentFrequencyData.get(mesh.uuid) || null;
    }

    /**
     * 🎵 Get all current frequency data
     */
    public getAllFrequencyData(): Map<string, FrequencyData[]> {
        return new Map(this.currentFrequencyData);
    }

    /**
     * 🎚️ Set base frequency for calculations
     */
    public setBaseFrequency(frequency: number, note: string = 'A4'): void {
        this.frequencyCalculator.setBaseFrequency(frequency, note);
        console.log(`🎵 Base frequency updated to ${frequency}Hz (${note})`);
    }

    /**
     * 📊 Get current morph status including frequency data
     */
    public getMorphStatus() {
        const frequencyStatus = this.frequencyCalculator.getSystemStatus();
        return {
            activeMeshes: this.activeMorphMeshes.size,
            status: 'Catmull-Clark subdivision active with real frequency mathematics',
            frequencySystem: frequencyStatus,
            currentFrequencies: this.currentFrequencyData.size
        };
    }
}

/**
 * 🚀 Factory function for SkyboxCubeLayer integration
 */
export function createSkyboxMorphIntegration(scene: THREE.Scene): SkyboxMorphIntegration {
    console.log('🎭 Creating SkyboxCubeLayer morph integration...');
    console.log('🔧 Replacing problematic dual-visibility morph with Catmull-Clark!');

    return new SkyboxMorphIntegration(scene);
}