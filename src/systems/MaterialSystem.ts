import * as THREE from 'three';

/**
 * MaterialSystem - Unified 2025+ aesthetic materials for Living Myth Engine
 * Establishes consistent visual language across all layers
 */
export class MaterialSystem {
    // Core mythological color palette
    public static readonly COLORS = {
        // Primary sacred geometry colors
        VESSEL_CYAN: 0x00d4ff,        // Vessel layer - technology/structure
        SACRED_PURPLE: 0x6366f1,      // Spiritual essence - consciousness
        PARTICLE_VIOLET: 0xa78bfa,    // Particle matter - life force
        EMERGENT_GREEN: 0x50c878,     // Growth/emergence - natural evolution
        MERKABA_CRIMSON: 0xff6b6b,    // Sacred geometry - transformation

        // Supporting accent colors
        SHADOW_DEEP: 0x111111,        // Shadow/mystery
        WISDOM_GOLD: 0xffd700,        // Knowledge/enlightenment
        HARMONY_BLUE: 0x4a90e2,       // Peace/balance
        CONFLICT_RED: 0xe24a90,       // Tension/change

        // Neutral tones
        GROUND_DARK: 0x0a0a0a,        // Background/grounding
        WIRE_BRIGHT: 0x00ffff,        // Wireframe highlights
    };

    // Standardized material properties for 2025+ aesthetic
    public static readonly MATERIAL_PRESETS = {
        // Vessel layer materials - geometric precision
        VESSEL_CUBE: {
            color: MaterialSystem.COLORS.VESSEL_CYAN,
            transparent: true,
            opacity: 0.08,
            roughness: 0.1,
            metalness: 0.9,
            transmission: 0.95,
            thickness: 1.0,
            ior: 1.5,
            clearcoat: 1.0,
            clearcoatRoughness: 0.0,
            envMapIntensity: 1.5,
            sheen: 1.0,
            sheenRoughness: 0.0
        },

        VESSEL_SPHERE: {
            color: MaterialSystem.COLORS.SACRED_PURPLE,
            transparent: true,
            opacity: 0.04,
            roughness: 0.0,
            metalness: 0.1,
            transmission: 0.98,
            thickness: 0.5,
            ior: 1.4,
            clearcoat: 1.0,
            clearcoatRoughness: 0.1,
            iridescence: 1.0,
            iridescenceIOR: 1.3,
            iridescenceThicknessRange: [100, 800]
        },

        // Wireframe materials - sacred geometry
        WIREFRAME_SACRED: {
            color: MaterialSystem.COLORS.WIRE_BRIGHT,
            transparent: true,
            opacity: 0.4,
            roughness: 0.1,
            metalness: 0.8,
            emissive: 0x002244,
            emissiveIntensity: 0.1
        },

        // Emergent form materials - organic evolution
        EMERGENT_ORGANIC: {
            color: MaterialSystem.COLORS.EMERGENT_GREEN,
            transparent: true,
            opacity: 0.8,
            roughness: 0.3,
            metalness: 0.4,
            clearcoat: 0.8,
            clearcoatRoughness: 0.2,
            sheen: 0.5,
            sheenRoughness: 0.8,
            emissiveIntensity: 0.05
        },

        // Ground/shadow materials
        SHADOW_GROUND: {
            color: MaterialSystem.COLORS.SHADOW_DEEP,
            transparent: true,
            opacity: 0.8,
            roughness: 1.0,
            metalness: 0.0
        }
    };

    /**
     * Create a standardized MeshPhysicalMaterial with 2025+ aesthetics
     */
    public static createMaterial(preset: keyof typeof MaterialSystem.MATERIAL_PRESETS): THREE.MeshPhysicalMaterial {
        const config = MaterialSystem.MATERIAL_PRESETS[preset];
        return new THREE.MeshPhysicalMaterial(config);
    }

    /**
     * Create particle material with consistent styling
     */
    public static createParticleMaterial(color: number = MaterialSystem.COLORS.PARTICLE_VIOLET): THREE.PointsMaterial {
        return new THREE.PointsMaterial({
            color: color,
            size: 0.03,
            transparent: true,
            opacity: 1.0,
            blending: THREE.AdditiveBlending,
            vertexColors: false,
            sizeAttenuation: true,
            alphaTest: 0.0001,
            depthWrite: false
        });
    }

    /**
     * Create line material for wireframes
     */
    public static createLineMaterial(color: number = MaterialSystem.COLORS.WIRE_BRIGHT): THREE.LineBasicMaterial {
        return new THREE.LineBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.8,
            linewidth: 2
        });
    }

    /**
     * Apply mythological color transformations
     */
    public static applyMythologicalTheme(material: THREE.MeshPhysicalMaterial, theme: 'harmony' | 'conflict' | 'wisdom' | 'mystery') {
        switch (theme) {
            case 'harmony':
                material.color.setHex(MaterialSystem.COLORS.HARMONY_BLUE);
                material.emissive.setHSL(0.6, 0.3, 0.1);
                break;
            case 'conflict':
                material.color.setHex(MaterialSystem.COLORS.CONFLICT_RED);
                material.emissive.setHSL(0.0, 0.8, 0.1);
                break;
            case 'wisdom':
                material.color.setHex(MaterialSystem.COLORS.WISDOM_GOLD);
                material.emissive.setHSL(0.15, 0.8, 0.05);
                break;
            case 'mystery':
                material.color.setHex(MaterialSystem.COLORS.SHADOW_DEEP);
                material.emissive.setHSL(0.8, 0.5, 0.02);
                break;
        }
    }

    /**
     * Animate material properties over time for living aesthetics
     */
    public static animateMaterial(material: THREE.MeshPhysicalMaterial, elapsedTime: number, speed: number = 1.0) {
        // Subtle color evolution
        const hue = (elapsedTime * speed * 0.02) % 1;
        const currentColor = material.color.getHSL({ h: 0, s: 0, l: 0 });

        // Very gentle hue shifting
        material.color.setHSL(
            (currentColor.h + hue * 0.1) % 1,
            currentColor.s,
            currentColor.l
        );

        // Subtle emissive pulsing
        const pulse = Math.sin(elapsedTime * speed * 0.5) * 0.02 + 0.05;
        material.emissiveIntensity = pulse;
    }

    /**
     * Set material intensity for performance responsiveness
     */
    public static setMaterialIntensity(material: THREE.MeshPhysicalMaterial, intensity: number) {
        // Clamp intensity between 0.3 and 1.0 for visibility
        const normalizedIntensity = Math.max(0.3, Math.min(1.0, intensity));

        // Adjust transmission and opacity based on intensity
        if (material.transmission !== undefined) {
            material.transmission = Math.max(0.9, 0.95 * normalizedIntensity);
        }

        if (material.opacity !== undefined) {
            material.opacity = Math.max(0.04, material.opacity * normalizedIntensity);
        }

        // Enhance emissive for higher intensities
        material.emissiveIntensity = normalizedIntensity * 0.1;
    }
}