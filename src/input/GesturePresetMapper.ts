/**
 * 🎭 GESTURE PRESET MAPPER
 *
 * Maps complex gesture combinations to visual presets and engine configurations.
 * Integrates AdvancedGestureChoreographer patterns with MMPA engine systems.
 */

import { ChoreographedMove } from './AdvancedGestureChoreographer';

export interface GesturePresetMapping {
    gestureName: string;
    presetType: 'shadow' | 'cymatic' | 'portal' | 'material' | 'ring_morph' | 'global_effect';
    presetConfig: any;
    description: string;
    triggersOn: 'sequence_complete' | 'during_sequence' | 'on_detection';
    cooldown: number; // ms between activations
}

export interface EngineCallbacks {
    setShadowPreset: (preset: 'all' | 'vessel-only' | 'forms-only' | 'particles-only' | 'none') => void;
    loadCymaticPreset: (preset: any) => void;
    setRingMorph: (ringIndex: number, config: any) => void;
    setGlobalIntensity: (intensity: number) => void;
    triggerPortalWarp: (x: number, y: number, zoom: number) => void;
    setMaterialPreset: (preset: string) => void;
}

export class GesturePresetMapper {
    private callbacks: EngineCallbacks;
    private lastTriggerTime: Map<string, number> = new Map();

    private gesturePresets: Map<string, GesturePresetMapping> = new Map([
        // ═══ SPIRAL INCEPTION GESTURE ═══
        ['spiral_inception', {
            gestureName: 'spiral_inception',
            presetType: 'ring_morph',
            presetConfig: {
                sequence: [
                    { scale: 1.0, opacity: 0.8, rotationSpeed: 0.5, distortionAmount: 0.0 },
                    { scale: 1.5, opacity: 0.9, rotationSpeed: 1.0, distortionAmount: 0.2 },
                    { scale: 2.0, opacity: 1.0, rotationSpeed: 1.5, distortionAmount: 0.4 },
                    { scale: 2.5, opacity: 0.8, rotationSpeed: 2.0, distortionAmount: 0.6 }
                ],
                duration: 3000,
                easing: 'easeInOutCubic'
            },
            description: 'Dual-hand spiral creates expanding ring morphology with increasing intensity',
            triggersOn: 'sequence_complete',
            cooldown: 4000
        }],

        // ═══ FIRE STORM GESTURE ═══
        ['fire_storm', {
            gestureName: 'fire_storm',
            presetType: 'cymatic',
            presetConfig: {
                name: 'Fire Storm',
                patternType: 'radial',
                sensitivity: 2.5,
                colorMode: 'fire',
                morphSpeed: 3.0,
                customParams: {
                    turbulence: 0.8,
                    frequency: 120,
                    amplitude: 0.9,
                    phaseShift: Math.PI / 3
                }
            },
            description: 'Rapid finger movements create high-energy fire-themed cymatic patterns',
            triggersOn: 'during_sequence',
            cooldown: 2000
        }],

        // ═══ CRYSTAL FORMATION GESTURE ═══
        ['crystal_formation', {
            gestureName: 'crystal_formation',
            presetType: 'shadow',
            presetConfig: 'all',
            description: 'Precise geometric hand positions activate full shadow casting for crystal-like forms',
            triggersOn: 'on_detection',
            cooldown: 3000
        }],

        // ═══ PORTAL WARP GESTURES ═══
        ['triangle_left', {
            gestureName: 'triangle_left',
            presetType: 'portal',
            presetConfig: { x: 0.2, y: 0.5, zoom: 1.5 },
            description: 'Left triangle gesture warps to left portal position',
            triggersOn: 'on_detection',
            cooldown: 1500
        }],

        ['triangle_right', {
            gestureName: 'triangle_right',
            presetType: 'portal',
            presetConfig: { x: 0.8, y: 0.5, zoom: 1.5 },
            description: 'Right triangle gesture warps to right portal position',
            triggersOn: 'on_detection',
            cooldown: 1500
        }],

        // ═══ DIAMOND GESTURES ═══
        ['diamond', {
            gestureName: 'diamond',
            presetType: 'material',
            presetConfig: 'crystal',
            description: 'Diamond hand shape activates crystal material preset',
            triggersOn: 'on_detection',
            cooldown: 2000
        }],

        // ═══ CIRCLE GESTURES ═══
        ['circle_small', {
            gestureName: 'circle_small',
            presetType: 'ring_morph',
            presetConfig: {
                global: { scale: 0.5, opacity: 1.0, rotationSpeed: 0.8, distortionAmount: 0.0 }
            },
            description: 'Small circle gesture morphs all rings to compact formation',
            triggersOn: 'on_detection',
            cooldown: 1000
        }],

        ['circle_large', {
            gestureName: 'circle_large',
            presetType: 'ring_morph',
            presetConfig: {
                global: { scale: 2.0, opacity: 0.7, rotationSpeed: 0.3, distortionAmount: 0.1 }
            },
            description: 'Large circle gesture expands all rings to maximum scale',
            triggersOn: 'on_detection',
            cooldown: 1000
        }],

        // ═══ TWO-HAND COMBINATIONS ═══
        ['synchronized_circles', {
            gestureName: 'synchronized_circles',
            presetType: 'global_effect',
            presetConfig: {
                intensity: 0.9,
                harmonic: 'perfect_fifth',
                resonance: 0.8
            },
            description: 'Both hands making circles creates synchronized harmonic resonance',
            triggersOn: 'during_sequence',
            cooldown: 500
        }],

        ['opposing_spirals', {
            gestureName: 'opposing_spirals',
            presetType: 'cymatic',
            presetConfig: {
                name: 'Dual Vortex',
                patternType: 'spiral',
                sensitivity: 1.8,
                colorMode: 'vortex',
                morphSpeed: 2.0,
                customParams: {
                    dualPolarity: true,
                    frequency: 80,
                    amplitude: 0.7,
                    phaseOffset: Math.PI
                }
            },
            description: 'Counter-rotating spirals create dual vortex cymatic pattern',
            triggersOn: 'during_sequence',
            cooldown: 1500
        }],

        // ═══ ENERGY LEVEL GESTURES ═══
        ['high_energy_burst', {
            gestureName: 'high_energy_burst',
            presetType: 'global_effect',
            presetConfig: {
                intensity: 1.0,
                burst: true,
                duration: 2000
            },
            description: 'Rapid multi-finger movements trigger maximum energy burst',
            triggersOn: 'on_detection',
            cooldown: 5000
        }],

        ['calm_restoration', {
            gestureName: 'calm_restoration',
            presetType: 'global_effect',
            presetConfig: {
                intensity: 0.2,
                restore: true,
                transition: 'smooth'
            },
            description: 'Slow, deliberate gestures restore calm, low-energy state',
            triggersOn: 'sequence_complete',
            cooldown: 3000
        }]
    ]);

    constructor(callbacks: EngineCallbacks) {
        this.callbacks = callbacks;
    }

    /**
     * Process gesture detection and trigger corresponding presets
     */
    public processGestureDetection(gestureName: string, gestureData?: any): boolean {
        const mapping = this.gesturePresets.get(gestureName);
        if (!mapping) {
            console.log(`🎭 No preset mapping found for gesture: ${gestureName}`);
            return false;
        }

        // Check cooldown
        const lastTrigger = this.lastTriggerTime.get(gestureName) || 0;
        const now = Date.now();
        if (now - lastTrigger < mapping.cooldown) {
            console.log(`🎭 Gesture ${gestureName} on cooldown (${mapping.cooldown}ms)`);
            return false;
        }

        // Apply the preset based on type
        const success = this.applyPreset(mapping, gestureData);

        if (success) {
            this.lastTriggerTime.set(gestureName, now);
            console.log(`🎭 Applied preset for gesture: ${gestureName} → ${mapping.description}`);
        }

        return success;
    }

    /**
     * Process choreographed move completion
     */
    public processChoreographedMove(move: ChoreographedMove): boolean {
        const gestureName = move.name.toLowerCase().replace(/\s+/g, '_');
        return this.processGestureDetection(gestureName, {
            confidence: move.minConfidence,
            duration: move.sequenceDuration,
            complexity: move.requiredGestures.length
        });
    }

    /**
     * Apply preset configuration to engine
     */
    private applyPreset(mapping: GesturePresetMapping, gestureData?: any): boolean {
        try {
            switch (mapping.presetType) {
                case 'shadow':
                    this.callbacks.setShadowPreset(mapping.presetConfig);
                    break;

                case 'cymatic':
                    this.callbacks.loadCymaticPreset(mapping.presetConfig);
                    break;

                case 'portal':
                    const { x, y, zoom } = mapping.presetConfig;
                    this.callbacks.triggerPortalWarp(x, y, zoom);
                    break;

                case 'material':
                    this.callbacks.setMaterialPreset(mapping.presetConfig);
                    break;

                case 'ring_morph':
                    this.applyRingMorphPreset(mapping.presetConfig, gestureData);
                    break;

                case 'global_effect':
                    this.applyGlobalEffectPreset(mapping.presetConfig, gestureData);
                    break;

                default:
                    console.warn(`🎭 Unknown preset type: ${mapping.presetType}`);
                    return false;
            }

            return true;
        } catch (error) {
            console.error(`🎭 Error applying preset for ${mapping.gestureName}:`, error);
            return false;
        }
    }

    /**
     * Apply ring morphing preset with sequence support
     */
    private applyRingMorphPreset(config: any, gestureData?: any): void {
        if (config.sequence) {
            // Animated sequence
            this.playRingMorphSequence(config.sequence, config.duration, config.easing);
        } else if (config.global) {
            // Apply to all rings
            for (let i = 0; i < 6; i++) {
                this.callbacks.setRingMorph(i, config.global);
            }
        } else if (config.individual) {
            // Apply to specific rings
            config.individual.forEach((ringConfig: any, index: number) => {
                this.callbacks.setRingMorph(index, ringConfig);
            });
        }
    }

    /**
     * Play animated ring morph sequence
     */
    private playRingMorphSequence(sequence: any[], duration: number, easing: string): void {
        const steps = sequence.length;
        const stepDuration = duration / steps;

        sequence.forEach((step, index) => {
            setTimeout(() => {
                for (let ringIndex = 0; ringIndex < 6; ringIndex++) {
                    this.callbacks.setRingMorph(ringIndex, step);
                }
            }, index * stepDuration);
        });
    }

    /**
     * Apply global effect preset
     */
    private applyGlobalEffectPreset(config: any, gestureData?: any): void {
        if (config.intensity !== undefined) {
            this.callbacks.setGlobalIntensity(config.intensity);
        }

        if (config.burst) {
            // Temporary intensity burst
            const originalIntensity = 0.5; // Should get current intensity
            this.callbacks.setGlobalIntensity(config.intensity);

            setTimeout(() => {
                this.callbacks.setGlobalIntensity(originalIntensity);
            }, config.duration || 2000);
        }
    }

    /**
     * Add custom gesture preset mapping
     */
    public addGesturePreset(gestureName: string, mapping: GesturePresetMapping): void {
        this.gesturePresets.set(gestureName, mapping);
        console.log(`🎭 Added custom gesture preset: ${gestureName}`);
    }

    /**
     * Get all available gesture presets
     */
    public getAvailablePresets(): Map<string, GesturePresetMapping> {
        return new Map(this.gesturePresets);
    }

    /**
     * Get gesture preset by name
     */
    public getGesturePreset(gestureName: string): GesturePresetMapping | undefined {
        return this.gesturePresets.get(gestureName);
    }

    /**
     * Remove gesture preset
     */
    public removeGesturePreset(gestureName: string): boolean {
        return this.gesturePresets.delete(gestureName);
    }

    /**
     * Clear all cooldowns (useful for testing or reset)
     */
    public clearCooldowns(): void {
        this.lastTriggerTime.clear();
        console.log('🎭 All gesture cooldowns cleared');
    }

    /**
     * Get gesture statistics
     */
    public getGestureStats(): { [key: string]: { lastTriggered: number, timesTriggered: number } } {
        const stats: { [key: string]: { lastTriggered: number, timesTriggered: number } } = {};

        this.lastTriggerTime.forEach((time, gesture) => {
            stats[gesture] = {
                lastTriggered: time,
                timesTriggered: 1 // Would need to track this separately
            };
        });

        return stats;
    }
}