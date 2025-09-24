/**
 * 🎼 Extended Microtonal Subdivision System
 *
 * Maps Catmull-Clark subdivision levels to deep microtonal divisions:
 * Level 0: 6 faces → 6-TET (fundamental modes)
 * Level 1: 24 faces → 12-TET (chromatic)
 * Level 2: 96 faces → 24-TET (quarter-tones)
 * Level 3: 384 faces → 48-TET (eighth-tones)
 * Level 4: 1,536 faces → 96-TET (16th-tones)
 * Level 5: 6,144 faces → 192-TET (32nd-tones)
 * Level 6: 24,576 faces → 384-TET (64th-tones)
 * Level 7: 98,304 faces → 768-TET (128th-tones)
 * Level 8: 393,216 faces → 1536-TET (256th-tones + enharmonics)
 *
 * Enharmonic equivalents expand the musical space exponentially!
 */

import * as THREE from 'three';
import { MusicalSubdivisionMorph } from './MusicalSubdivisionMorph';

export interface EnharmonicMapping {
    cents: number;
    primaryName: string;
    enharmonicNames: string[];
    deweyCode: string;
    subdivisionLevel: number;
    faceRegion: number; // Which faces this note affects
}

export interface MicrotonalLevel {
    level: number;
    faceCount: number;
    divisions: number; // TET divisions
    centsPerStep: number;
    description: string;
    enharmonicDepth: number; // How many enharmonic spellings
}

/**
 * 🌌 Deep Microtonal Subdivision Engine
 * Reaches 393,216 faces through extreme microtonal precision
 */
export class ExtendedMicrotonalSubdivision extends MusicalSubdivisionMorph {
    private microtonalLevels: MicrotonalLevel[];
    private enharmonicMappings: Map<number, EnharmonicMapping[]>;
    private currentMicrotonalLevel: number = 0;

    // Your earlier musical architecture integration
    private readonly musicalArchitecture = {
        // Base from your existing plans
        fundamentalModes: ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian'],

        // Extended from your Dewey Decimal system
        chromaticExpansion: {
            '6-PANEL': { base: 6, multiplier: 1 },
            '12-TONE': { base: 12, multiplier: 2 },
            '24-TET': { base: 24, multiplier: 4 }
        },

        // Connection to your vessel/scaffold system
        vesselMappings: {
            'conflat': { level: 0, faces: 6 },
            'chromatic': { level: 1, faces: 24 },
            'microtonal': { level: 2, faces: 96 },
            'hypermicrotonal': { level: 3, faces: 384 }
        }
    };

    constructor(scene: THREE.Scene) {
        super(scene, 8); // 8 levels for 393,216 faces
        this.initializeMicrotonalLevels();
        this.generateEnharmonicMappings();
        this.connectToMusicalArchitecture();
    }

    private initializeMicrotonalLevels(): void {
        this.microtonalLevels = [
            {
                level: 0,
                faceCount: 6,
                divisions: 6,
                centsPerStep: 200, // 6-TET: whole tones
                description: 'Fundamental Modes (Ancient Greek)',
                enharmonicDepth: 1
            },
            {
                level: 1,
                faceCount: 24,
                divisions: 12,
                centsPerStep: 100, // 12-TET: semitones
                description: 'Chromatic (Equal Temperament)',
                enharmonicDepth: 2
            },
            {
                level: 2,
                faceCount: 96,
                divisions: 24,
                centsPerStep: 50, // 24-TET: quarter-tones
                description: 'Quarter-tones (Arabic Maqam)',
                enharmonicDepth: 3
            },
            {
                level: 3,
                faceCount: 384,
                divisions: 48,
                centsPerStep: 25, // 48-TET: eighth-tones
                description: 'Eighth-tones (Turkish Classical)',
                enharmonicDepth: 4
            },
            {
                level: 4,
                faceCount: 1536,
                divisions: 96,
                centsPerStep: 12.5, // 96-TET: 16th-tones
                description: 'Sixteenth-tones (Spectral Music)',
                enharmonicDepth: 6
            },
            {
                level: 5,
                faceCount: 6144,
                divisions: 192,
                centsPerStep: 6.25, // 192-TET: 32nd-tones
                description: 'Thirty-second-tones (Xenharmonic)',
                enharmonicDepth: 8
            },
            {
                level: 6,
                faceCount: 24576,
                divisions: 384,
                centsPerStep: 3.125, // 384-TET: 64th-tones
                description: 'Sixty-fourth-tones (Computer Music)',
                enharmonicDepth: 12
            },
            {
                level: 7,
                faceCount: 98304,
                divisions: 768,
                centsPerStep: 1.5625, // 768-TET: 128th-tones
                description: 'Sub-microtonal (Synthesis)',
                enharmonicDepth: 16
            },
            {
                level: 8,
                faceCount: 393216,
                divisions: 1536,
                centsPerStep: 0.78125, // 1536-TET: 256th-tones
                description: 'Hypermicrotonal (MMPA Maximum)',
                enharmonicDepth: 24
            }
        ];

        console.log('🎼 Extended Microtonal Levels Initialized:');
        this.logMicrotonalProgression();
    }

    private generateEnharmonicMappings(): void {
        this.enharmonicMappings = new Map();

        this.microtonalLevels.forEach(level => {
            const mappings: EnharmonicMapping[] = [];

            for (let i = 0; i < level.divisions; i++) {
                const cents = i * level.centsPerStep;
                const enharmonics = this.generateEnharmonicNames(cents, level.enharmonicDepth);
                const deweyCode = this.generateDeweyCode(level.level, i);
                const faceRegion = Math.floor((i / level.divisions) * level.faceCount);

                mappings.push({
                    cents,
                    primaryName: enharmonics[0],
                    enharmonicNames: enharmonics,
                    deweyCode,
                    subdivisionLevel: level.level,
                    faceRegion
                });
            }

            this.enharmonicMappings.set(level.level, mappings);
        });

        console.log('🎵 Enharmonic mappings generated for all levels');
    }

    private generateEnharmonicNames(cents: number, depth: number): string[] {
        const semitones = Math.round(cents / 100);
        const baseNoteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
        const enharmonicAlternatives = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];

        const names: string[] = [];
        const baseNote = baseNoteNames[semitones % 12];
        const enharmonicNote = enharmonicAlternatives[semitones % 12];

        // Primary name
        names.push(baseNote);

        // Add enharmonic spellings based on depth
        if (depth >= 2 && baseNote !== enharmonicNote) {
            names.push(enharmonicNote);
        }

        // Add microtonal variations for higher depths
        if (depth >= 4) {
            const microCents = cents % 100;
            if (microCents > 0 && microCents < 100) {
                names.push(`${baseNote}+${microCents.toFixed(0)}¢`);
                if (baseNote !== enharmonicNote) {
                    names.push(`${enharmonicNote}+${microCents.toFixed(0)}¢`);
                }
            }
        }

        // Add theoretical enharmonics for extreme depths
        if (depth >= 8) {
            names.push(`${baseNote}♯♯♭`); // Double sharp-flat
            names.push(`${baseNote}♭♭♯`); // Double flat-sharp
        }

        return names;
    }

    private generateDeweyCode(level: number, division: number): string {
        // Integrate with your existing Dewey Decimal system
        const baseCode = level * 100; // 000, 100, 200, etc.
        const subCode = Math.floor((division / this.microtonalLevels[level].divisions) * 100);
        const microCode = division % 100;

        return `${baseCode.toString().padStart(3, '0')}.${subCode.toString().padStart(3, '0')}.${microCode.toString().padStart(3, '0')}`;
    }

    /**
     * 🎵 Set subdivision level with musical context
     */
    public setMicrotonalLevel(level: number, musicalContext?: string): void {
        level = Math.max(0, Math.min(level, this.microtonalLevels.length - 1));
        const microLevel = this.microtonalLevels[level];

        this.animateToLevel(level, 1500);
        this.currentMicrotonalLevel = level;

        console.log(`🎼 Microtonal Level ${level}: ${microLevel.description}`);
        console.log(`  Faces: ${microLevel.faceCount.toLocaleString()}`);
        console.log(`  Divisions: ${microLevel.divisions}-TET`);
        console.log(`  Resolution: ${microLevel.centsPerStep}¢ per step`);
        console.log(`  Enharmonic Depth: ${microLevel.enharmonicDepth}`);

        if (musicalContext) {
            console.log(`  Context: ${musicalContext}`);
        }

        // Update visual feedback
        this.updateMicrotonalVisuals(level);
    }

    /**
     * 🎨 Update visuals based on microtonal level
     */
    private updateMicrotonalVisuals(level: number): void {
        const material = this.mesh.material as THREE.MeshBasicMaterial;
        const microLevel = this.microtonalLevels[level];

        // Color progression through spectrum as we go deeper
        const hue = (level / this.microtonalLevels.length) * 360;
        const saturation = 0.7 + (level * 0.03); // Increase saturation with complexity
        const lightness = 0.6 - (level * 0.05); // Decrease lightness with complexity

        material.color.setHSL(hue / 360, saturation, lightness);

        // Wireframe for extreme detail levels
        material.wireframe = level >= 6;

        console.log(`🎨 Visual update: HSL(${hue.toFixed(0)}°, ${(saturation*100).toFixed(0)}%, ${(lightness*100).toFixed(0)}%)`);
    }

    /**
     * 🎹 Control with extreme precision frequency
     */
    public morphToExactFrequency(frequency: number, baseFrequency: number = 440): void {
        const ratio = frequency / baseFrequency;
        const cents = 1200 * Math.log2(ratio);

        // Find the appropriate microtonal level for this precision
        const requiredPrecision = this.calculateRequiredPrecision(cents);
        const targetLevel = this.findLevelForPrecision(requiredPrecision);

        this.setMicrotonalLevel(targetLevel, `${frequency.toFixed(2)}Hz (${cents.toFixed(3)}¢)`);

        // Map to specific face region
        const mapping = this.findClosestMapping(cents, targetLevel);
        if (mapping) {
            console.log(`🎵 Mapped to: ${mapping.primaryName}`);
            console.log(`  Enharmonics: ${mapping.enharmonicNames.join(', ')}`);
            console.log(`  Dewey: ${mapping.deweyCode}`);
            console.log(`  Face Region: ${mapping.faceRegion}`);
        }
    }

    /**
     * 🎛️ Theremin control with extreme precision
     */
    public controlWithHyperPrecisionThereminField(proximity: number, sensitivity: number = 1.0): void {
        // Map proximity to microtonal level (0-8)
        const targetLevel = Math.floor(proximity * this.microtonalLevels.length * sensitivity);
        const fractionalLevel = (proximity * this.microtonalLevels.length * sensitivity) % 1;

        this.setMicrotonalLevel(targetLevel);

        // Use fractional part for fine subdivision control within level
        const microLevel = this.microtonalLevels[targetLevel];
        const divisionIndex = Math.floor(fractionalLevel * microLevel.divisions);
        const cents = divisionIndex * microLevel.centsPerStep;

        this.morphToMusicalInterval(cents);

        console.log(`🎵 Theremin: Level ${targetLevel}, Division ${divisionIndex}, ${cents.toFixed(3)}¢`);
    }

    /**
     * 🎪 Connect to your earlier musical architecture
     */
    private connectToMusicalArchitecture(): void {
        console.log('\n🏛️ Connecting to Musical Architecture:');

        // Map to your vessel system
        Object.entries(this.musicalArchitecture.vesselMappings).forEach(([name, config]) => {
            const level = this.microtonalLevels[config.level];
            console.log(`  ${name}: Level ${config.level} (${level.faceCount} faces, ${level.description})`);
        });

        // Map to your chromatic expansion
        Object.entries(this.musicalArchitecture.chromaticExpansion).forEach(([mode, config]) => {
            const level = this.findLevelForDivisions(config.base);
            console.log(`  ${mode}: ${config.base}-TET → Level ${level?.level || 'N/A'}`);
        });
    }

    // Helper methods
    private calculateRequiredPrecision(cents: number): number {
        const fractionalCents = cents % 1;
        return fractionalCents > 0 ? 1 / fractionalCents : 1;
    }

    private findLevelForPrecision(precision: number): number {
        for (let i = this.microtonalLevels.length - 1; i >= 0; i--) {
            if (this.microtonalLevels[i].centsPerStep <= 1 / precision) {
                return i;
            }
        }
        return 0;
    }

    private findLevelForDivisions(divisions: number): MicrotonalLevel | undefined {
        return this.microtonalLevels.find(level => level.divisions >= divisions);
    }

    private findClosestMapping(cents: number, level: number): EnharmonicMapping | undefined {
        const mappings = this.enharmonicMappings.get(level);
        if (!mappings) return undefined;

        return mappings.reduce((closest, current) => {
            return Math.abs(current.cents - cents) < Math.abs(closest.cents - cents) ? current : closest;
        });
    }

    private logMicrotonalProgression(): void {
        console.log('\n🎼 MICROTONAL SUBDIVISION PROGRESSION:');
        console.log('═'.repeat(80));

        this.microtonalLevels.forEach(level => {
            console.log(`Level ${level.level}: ${level.faceCount.toLocaleString()} faces | ${level.divisions}-TET | ${level.centsPerStep}¢/step`);
            console.log(`  → ${level.description} (${level.enharmonicDepth} enharmonic spellings)`);
        });

        console.log(`\n🌌 Total range: 6 → 393,216 faces (65,536x increase!)`);
        console.log(`🎵 Musical range: 6-TET → 1536-TET (256x microtonal precision!)`);
    }

    /**
     * 🎵 Get current extended musical info
     */
    public getExtendedMusicalInfo() {
        const baseInfo = this.getCurrentMusicalInfo();
        const microLevel = this.microtonalLevels[this.currentMicrotonalLevel];
        const mappings = this.enharmonicMappings.get(this.currentMicrotonalLevel) || [];

        return {
            ...baseInfo,
            microtonalLevel: this.currentMicrotonalLevel,
            divisions: microLevel.divisions,
            centsPerStep: microLevel.centsPerStep,
            description: microLevel.description,
            enharmonicDepth: microLevel.enharmonicDepth,
            totalMappings: mappings.length,
            maxPrecision: `${microLevel.centsPerStep}¢`
        };
    }
}

/**
 * 🚀 Factory function
 */
export function createExtendedMicrotonalSubdivision(scene: THREE.Scene): ExtendedMicrotonalSubdivision {
    console.log('🌌 Creating Extended Microtonal Subdivision Engine...');
    console.log('🎵 Reaching 393,216 faces through extreme microtonal precision!');

    return new ExtendedMicrotonalSubdivision(scene);
}