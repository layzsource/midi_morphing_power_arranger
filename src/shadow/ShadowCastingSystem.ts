/**
 * Shadow Casting System for Universal Signal Engine
 *
 * This system captures sprites from the EmergentFormLayer and casts their shadows
 * onto the vessel scaffolding rings, creating temporal data encoding that can be
 * read from different viewing angles like a wax cylinder recording.
 *
 * Core concepts:
 * - Sprites act as light sources casting shadows onto vessel rings
 * - Shadow patterns encode temporal information and sprite properties
 * - Multiple viewing angles reveal different encoded data layers
 * - Shadows accumulate over time creating persistent data records
 */

import * as THREE from 'three';

export interface ShadowData {
    position: THREE.Vector3;
    intensity: number;
    timestamp: number;
    spriteId: string;
    physicsProperties: any;
    temporalEncoding: any;
}

export interface RingShadowMap {
    ringIndex: number;
    ringPosition: THREE.Vector3;
    ringNormal: THREE.Vector3;
    shadowTexture: THREE.DataTexture;
    shadowData: ShadowData[];
    lastUpdate: number;
}

export class ShadowCastingSystem {
    private scene: THREE.Scene;
    private shadowMaps: Map<number, RingShadowMap> = new Map();
    private shadowResolution = 256; // Shadow texture resolution
    private virtualLightSources: THREE.PointLight[] = [];
    private shadowGeometry: THREE.PlaneGeometry;
    private temporalDataTexture: THREE.DataTexture;
    private waxCylinderData: Float32Array;

    // Ring reference data (should match VesselLayer configuration)
    private readonly ringConfiguration = [
        { position: [0, 0, 1.5], normal: [0, 0, -1], name: 'front' },   // Front face
        { position: [0, 0, -1.5], normal: [0, 0, 1], name: 'back' },   // Back face
        { position: [1.5, 0, 0], normal: [-1, 0, 0], name: 'right' },  // Right face
        { position: [-1.5, 0, 0], normal: [1, 0, 0], name: 'left' },   // Left face
        { position: [0, 1.5, 0], normal: [0, -1, 0], name: 'top' },    // Top face
        { position: [0, -1.5, 0], normal: [0, 1, 0], name: 'bottom' }  // Bottom face
    ];

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.initializeShadowSystem();
        this.initializeWaxCylinderData();
    }

    /**
     * Initialize shadow casting system with ring shadow maps
     */
    private initializeShadowSystem() {
        // Create shadow maps for each vessel ring
        this.ringConfiguration.forEach((ring, index) => {
            const ringPos = new THREE.Vector3(...ring.position);
            const ringNormal = new THREE.Vector3(...ring.normal);

            // Create shadow texture for this ring
            const shadowTextureData = new Uint8Array(this.shadowResolution * this.shadowResolution * 4);
            shadowTextureData.fill(0); // Start with black (no shadows)

            const shadowTexture = new THREE.DataTexture(
                shadowTextureData,
                this.shadowResolution,
                this.shadowResolution,
                THREE.RGBAFormat
            );
            shadowTexture.needsUpdate = true;

            const ringShadowMap: RingShadowMap = {
                ringIndex: index,
                ringPosition: ringPos,
                ringNormal: ringNormal,
                shadowTexture: shadowTexture,
                shadowData: [],
                lastUpdate: 0
            };

            this.shadowMaps.set(index, ringShadowMap);
        });

        // Create geometry for shadow projection
        this.shadowGeometry = new THREE.PlaneGeometry(3, 3); // Match ring size
    }

    /**
     * Initialize wax cylinder-style temporal data storage
     */
    private initializeWaxCylinderData() {
        // Create temporal data texture for time-based encoding
        const dataSize = 1024; // Temporal resolution
        this.waxCylinderData = new Float32Array(dataSize * 4); // RGBA data
        this.waxCylinderData.fill(0);

        this.temporalDataTexture = new THREE.DataTexture(
            this.waxCylinderData,
            dataSize,
            1,
            THREE.RGBAFormat,
            THREE.FloatType
        );
        this.temporalDataTexture.needsUpdate = true;
    }

    /**
     * Cast shadows from a sprite onto vessel rings
     */
    public castSpritesShadows(sprites: any[]) {
        if (!sprites || sprites.length === 0) return;

        const currentTime = performance.now();

        sprites.forEach(sprite => {
            this.castSingleSpriteShadow(sprite, currentTime);
        });

        // Update temporal encoding
        this.updateTemporalEncoding(currentTime);
    }

    /**
     * Cast shadow from individual sprite onto all visible rings
     */
    private castSingleSpriteShadow(sprite: any, timestamp: number) {
        const spritePosition = new THREE.Vector3();
        if (sprite.position) {
            spritePosition.copy(sprite.position);
        }

        // Cast shadow onto each ring
        this.shadowMaps.forEach((ringMap, ringIndex) => {
            const shadowHit = this.calculateShadowProjection(
                spritePosition,
                ringMap.ringPosition,
                ringMap.ringNormal
            );

            if (shadowHit.isHit) {
                const shadowData: ShadowData = {
                    position: shadowHit.hitPoint,
                    intensity: this.calculateShadowIntensity(sprite),
                    timestamp: timestamp,
                    spriteId: sprite.userData?.spriteId || `sprite_${Date.now()}`,
                    physicsProperties: sprite.userData?.physicsProperties || {},
                    temporalEncoding: sprite.userData?.temporalEncoding || {}
                };

                this.addShadowToRing(ringIndex, shadowData);
            }
        });
    }

    /**
     * Calculate shadow projection from sprite onto ring plane
     */
    private calculateShadowProjection(
        spritePos: THREE.Vector3,
        ringPos: THREE.Vector3,
        ringNormal: THREE.Vector3
    ): { isHit: boolean; hitPoint: THREE.Vector3; distance: number } {
        // Create ray from sprite position toward ring
        const rayDirection = new THREE.Vector3().subVectors(ringPos, spritePos).normalize();
        const ray = new THREE.Ray(spritePos, rayDirection);

        // Create plane for ring
        const plane = new THREE.Plane(ringNormal, -ringPos.dot(ringNormal));

        // Calculate intersection
        const hitPoint = new THREE.Vector3();
        const hit = ray.intersectPlane(plane, hitPoint);

        if (hit) {
            const distance = spritePos.distanceTo(hitPoint);
            const ringDistance = hitPoint.distanceTo(ringPos);

            // Check if hit is within ring radius (1.5 units)
            const isWithinRing = ringDistance <= 1.5;

            return {
                isHit: isWithinRing && distance > 0.1, // Avoid self-intersection
                hitPoint: hitPoint,
                distance: distance
            };
        }

        return { isHit: false, hitPoint: new THREE.Vector3(), distance: 0 };
    }

    /**
     * Calculate shadow intensity based on sprite properties
     */
    private calculateShadowIntensity(sprite: any): number {
        let intensity = 0.5; // Base intensity

        // Physics-based intensity modulation
        if (sprite.userData?.physicsProperties) {
            const physics = sprite.userData.physicsProperties;

            // Charge affects brightness
            if (physics.charge !== undefined) {
                intensity *= (0.5 + Math.abs(physics.charge) * 0.5);
            }

            // Spin affects intensity variation
            if (physics.spin !== undefined) {
                intensity *= (0.8 + Math.sin(physics.spin) * 0.2);
            }
        }

        // Distance affects intensity (closer = stronger shadow)
        if (sprite.position) {
            const distance = sprite.position.length();
            intensity *= Math.max(0.1, 1.0 - distance / 10.0);
        }

        return Math.max(0.1, Math.min(1.0, intensity));
    }

    /**
     * Add shadow data to specific ring's shadow map
     */
    private addShadowToRing(ringIndex: number, shadowData: ShadowData) {
        const ringMap = this.shadowMaps.get(ringIndex);
        if (!ringMap) return;

        // Add to shadow data array
        ringMap.shadowData.push(shadowData);

        // Keep only recent shadows (last 100 for performance)
        if (ringMap.shadowData.length > 100) {
            ringMap.shadowData = ringMap.shadowData.slice(-100);
        }

        // Update shadow texture
        this.updateRingShadowTexture(ringIndex, shadowData);

        ringMap.lastUpdate = shadowData.timestamp;
    }

    /**
     * Update ring's shadow texture with new shadow data
     */
    private updateRingShadowTexture(ringIndex: number, shadowData: ShadowData) {
        const ringMap = this.shadowMaps.get(ringIndex);
        if (!ringMap) return;

        const texture = ringMap.shadowTexture;
        const data = texture.image.data as Uint8Array;

        // Convert world position to texture coordinates
        const localPos = shadowData.position.clone().sub(ringMap.ringPosition);
        const u = (localPos.x + 1.5) / 3.0; // Normalize to 0-1
        const v = (localPos.y + 1.5) / 3.0; // Normalize to 0-1

        if (u >= 0 && u <= 1 && v >= 0 && v <= 1) {
            const x = Math.floor(u * this.shadowResolution);
            const y = Math.floor(v * this.shadowResolution);
            const index = (y * this.shadowResolution + x) * 4;

            if (index >= 0 && index < data.length - 3) {
                // Encode shadow data into RGBA channels
                data[index] = Math.floor(shadowData.intensity * 255);     // R: Intensity
                data[index + 1] = ringIndex * 42;                        // G: Ring ID
                data[index + 2] = (shadowData.timestamp % 1000) / 4;     // B: Temporal
                data[index + 3] = 255;                                   // A: Active
            }
        }

        texture.needsUpdate = true;
    }

    /**
     * Update temporal encoding for wax cylinder effect
     */
    private updateTemporalEncoding(currentTime: number) {
        const timeIndex = Math.floor((currentTime % 10000) / 10); // 10ms resolution
        if (timeIndex >= 0 && timeIndex < this.waxCylinderData.length / 4) {
            const baseIndex = timeIndex * 4;

            // Encode current shadow activity
            let totalShadowActivity = 0;
            this.shadowMaps.forEach(ringMap => {
                totalShadowActivity += ringMap.shadowData.length;
            });

            this.waxCylinderData[baseIndex] = totalShadowActivity / 600.0;     // R: Activity
            this.waxCylinderData[baseIndex + 1] = currentTime % 1000 / 1000;  // G: Time
            this.waxCylinderData[baseIndex + 2] = this.shadowMaps.size / 10;  // B: Ring count
            this.waxCylinderData[baseIndex + 3] = 1.0;                        // A: Valid
        }

        this.temporalDataTexture.needsUpdate = true;
    }

    /**
     * Get shadow data for specific viewing angle (microfiche reading)
     */
    public readShadowDataAtAngle(viewAngle: number, ringIndex?: number): ShadowData[] {
        const targetRings = ringIndex !== undefined ? [ringIndex] : Array.from(this.shadowMaps.keys());
        const shadowData: ShadowData[] = [];

        targetRings.forEach(index => {
            const ringMap = this.shadowMaps.get(index);
            if (ringMap) {
                // Filter shadows based on viewing angle
                const visibleShadows = ringMap.shadowData.filter(shadow => {
                    return this.isShadowVisibleFromAngle(shadow, viewAngle, ringMap);
                });
                shadowData.push(...visibleShadows);
            }
        });

        return shadowData.sort((a, b) => b.timestamp - a.timestamp); // Most recent first
    }

    /**
     * Check if shadow is visible from specific viewing angle
     */
    private isShadowVisibleFromAngle(
        shadow: ShadowData,
        viewAngle: number,
        ringMap: RingShadowMap
    ): boolean {
        // Calculate shadow visibility based on viewing angle
        const shadowAngle = Math.atan2(shadow.position.z, shadow.position.x);
        const angleDiff = Math.abs(shadowAngle - viewAngle);

        // Visible if within 90 degrees of view direction
        return angleDiff <= Math.PI / 2;
    }

    /**
     * Get all ring shadow textures for visualization
     */
    public getRingShadowTextures(): Map<number, THREE.DataTexture> {
        const textures = new Map<number, THREE.DataTexture>();
        this.shadowMaps.forEach((ringMap, index) => {
            textures.set(index, ringMap.shadowTexture);
        });
        return textures;
    }

    /**
     * Get temporal data texture for time-based analysis
     */
    public getTemporalDataTexture(): THREE.DataTexture {
        return this.temporalDataTexture;
    }

    /**
     * Clear all shadow data (reset system)
     */
    public clearAllShadows() {
        this.shadowMaps.forEach(ringMap => {
            ringMap.shadowData = [];
            const data = ringMap.shadowTexture.image.data as Uint8Array;
            data.fill(0);
            ringMap.shadowTexture.needsUpdate = true;
        });

        this.waxCylinderData.fill(0);
        this.temporalDataTexture.needsUpdate = true;
    }

    /**
     * Get shadow statistics for debugging/analysis
     */
    public getShadowStatistics() {
        let totalShadows = 0;
        const ringStats: { [key: number]: number } = {};

        this.shadowMaps.forEach((ringMap, index) => {
            const count = ringMap.shadowData.length;
            totalShadows += count;
            ringStats[index] = count;
        });

        return {
            totalShadows,
            ringStats,
            systemActive: totalShadows > 0,
            lastUpdate: Math.max(...Array.from(this.shadowMaps.values()).map(r => r.lastUpdate))
        };
    }
}