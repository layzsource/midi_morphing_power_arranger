/**
 * 🎵 Musical Subdivision Morph - Catmull-Clark meets Dewey Decimal
 *
 * Integrates subdivision surfaces with the musical Dewey system:
 * - 6-PANEL mode: Base subdivision (6 faces)
 * - 12-TONE mode: Chromatic subdivision (6×4¹ = 24 faces)
 * - 24-TET mode: Quarter-tone subdivision (6×4² = 96 faces)
 *
 * Each subdivision level corresponds to musical intervals!
 */

import * as THREE from 'three';
import { SubdivisionMorph, SubdivisionLevel } from './SubdivisionMorph';

export interface MusicalInterval {
    cents: number;        // Musical interval in cents
    ratio: number;        // Frequency ratio
    name: string;         // Musical name (e.g., "Perfect Fifth")
    deweyCode: string;    // Dewey decimal classification
}

export interface DeweySubdivisionMapping {
    mode: '6-PANEL' | '12-TONE' | '24-TET';
    subdivisionLevel: number;    // Catmull-Clark iteration
    faceCount: number;          // 6 × 4^level
    musicalDivision: number;    // 6, 12, or 24 divisions
    intervals: MusicalInterval[];
}

/**
 * 🎼 Bridges Catmull-Clark subdivision with musical theory
 */
export class MusicalSubdivisionMorph extends SubdivisionMorph {
    private deweyMode: '6-PANEL' | '12-TONE' | '24-TET' = '6-PANEL';
    private musicalMappings: Map<string, DeweySubdivisionMapping>;
    private currentMusicalLevel: number = 0;

    // Musical intervals for each mode
    private readonly musicalIntervals = {
        '6-PANEL': [
            { cents: 0, ratio: 1/1, name: 'Unison', deweyCode: '000' },
            { cents: 200, ratio: 9/8, name: 'Major Second', deweyCode: '100' },
            { cents: 400, ratio: 5/4, name: 'Major Third', deweyCode: '200' },
            { cents: 500, ratio: 4/3, name: 'Perfect Fourth', deweyCode: '300' },
            { cents: 700, ratio: 3/2, name: 'Perfect Fifth', deweyCode: '400' },
            { cents: 900, ratio: 5/3, name: 'Major Sixth', deweyCode: '500' }
        ],
        '12-TONE': [
            // Chromatic scale (12 semitones)
            { cents: 0, ratio: 1/1, name: 'C', deweyCode: '000' },
            { cents: 100, ratio: Math.pow(2, 1/12), name: 'C#', deweyCode: '010' },
            { cents: 200, ratio: Math.pow(2, 2/12), name: 'D', deweyCode: '020' },
            { cents: 300, ratio: Math.pow(2, 3/12), name: 'D#', deweyCode: '030' },
            { cents: 400, ratio: Math.pow(2, 4/12), name: 'E', deweyCode: '040' },
            { cents: 500, ratio: Math.pow(2, 5/12), name: 'F', deweyCode: '050' },
            { cents: 600, ratio: Math.pow(2, 6/12), name: 'F#', deweyCode: '060' },
            { cents: 700, ratio: Math.pow(2, 7/12), name: 'G', deweyCode: '070' },
            { cents: 800, ratio: Math.pow(2, 8/12), name: 'G#', deweyCode: '080' },
            { cents: 900, ratio: Math.pow(2, 9/12), name: 'A', deweyCode: '090' },
            { cents: 1000, ratio: Math.pow(2, 10/12), name: 'A#', deweyCode: '100' },
            { cents: 1100, ratio: Math.pow(2, 11/12), name: 'B', deweyCode: '110' }
        ],
        '24-TET': [
            // Quarter-tone scale (24 divisions)
            // Each semitone divided into 2 parts (50 cents each)
        ]
    };

    constructor(scene: THREE.Scene, maxSubdivisionLevels: number = 6) {
        super(scene, maxSubdivisionLevels);
        this.initializeMusicalMappings();
        this.setupDeweyMode('6-PANEL');
    }

    private initializeMusicalMappings(): void {
        this.musicalMappings = new Map();

        // 6-PANEL: Level 0 (6 faces)
        this.musicalMappings.set('6-PANEL', {
            mode: '6-PANEL',
            subdivisionLevel: 0,
            faceCount: 6,
            musicalDivision: 6,
            intervals: this.musicalIntervals['6-PANEL']
        });

        // 12-TONE: Level 1 (24 faces, but mapped to 12 chromatic tones)
        this.musicalMappings.set('12-TONE', {
            mode: '12-TONE',
            subdivisionLevel: 1,
            faceCount: 24,
            musicalDivision: 12,
            intervals: this.musicalIntervals['12-TONE']
        });

        // 24-TET: Level 2 (96 faces, mapped to 24 quarter-tones)
        this.musicalMappings.set('24-TET', {
            mode: '24-TET',
            subdivisionLevel: 2,
            faceCount: 96,
            musicalDivision: 24,
            intervals: this.generate24TETIntervals()
        });

        console.log('🎼 Musical subdivision mappings initialized');
        this.logMusicalMappings();
    }

    private generate24TETIntervals(): MusicalInterval[] {
        const intervals: MusicalInterval[] = [];

        for (let i = 0; i < 24; i++) {
            const cents = i * 50; // 24-TET: 50 cents per step
            const ratio = Math.pow(2, i / 24);
            const semitone = Math.floor(i / 2);
            const quarterTone = i % 2;

            const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
            const baseName = noteNames[semitone];
            const name = quarterTone === 0 ? baseName : `${baseName}♯`;
            const deweyCode = `${semitone.toString().padStart(2, '0')}${quarterTone}`;

            intervals.push({ cents, ratio, name, deweyCode });
        }

        return intervals;
    }

    /**
     * 🎵 Switch between Dewey Decimal musical modes
     */
    public setDeweyMode(mode: '6-PANEL' | '12-TONE' | '24-TET'): void {
        this.deweyMode = mode;
        const mapping = this.musicalMappings.get(mode);

        if (mapping) {
            // Animate to the subdivision level for this musical mode
            this.animateToLevel(mapping.subdivisionLevel, 1000);
            this.currentMusicalLevel = mapping.subdivisionLevel;

            console.log(`🎵 Switched to ${mode} mode:`);
            console.log(`  Subdivision Level: ${mapping.subdivisionLevel}`);
            console.log(`  Face Count: ${mapping.faceCount}`);
            console.log(`  Musical Divisions: ${mapping.musicalDivision}`);

            // Update material color based on mode
            this.updateModeColor(mode);
        }
    }

    /**
     * 🎨 Update visual appearance based on musical mode
     */
    private updateModeColor(mode: string): void {
        const material = this.mesh.material as THREE.MeshBasicMaterial;

        switch (mode) {
            case '6-PANEL':
                material.color.setHSL(0.15, 0.8, 0.5); // Warm orange (fundamental)
                break;
            case '12-TONE':
                material.color.setHSL(0.6, 0.8, 0.5);  // Blue (chromatic)
                break;
            case '24-TET':
                material.color.setHSL(0.8, 0.8, 0.5);  // Purple (microtonal)
                break;
        }
    }

    /**
     * 🎼 Control subdivision with musical intervals
     */
    public morphToMusicalInterval(cents: number): void {
        const mapping = this.musicalMappings.get(this.deweyMode);
        if (!mapping) return;

        // Find the closest interval
        const interval = mapping.intervals.reduce((closest, current) => {
            return Math.abs(current.cents - cents) < Math.abs(closest.cents - cents) ? current : closest;
        });

        // Map interval to subdivision level (fractional)
        const maxCents = Math.max(...mapping.intervals.map(i => i.cents));
        const normalizedCents = cents / maxCents;
        const targetLevel = mapping.subdivisionLevel + (normalizedCents * 2); // Allow +2 levels of detail

        this.setMorphLevel(targetLevel);

        console.log(`🎵 Morphing to ${interval.name} (${cents} cents)`);
        console.log(`  Dewey Code: ${interval.deweyCode}`);
        console.log(`  Frequency Ratio: ${interval.ratio.toFixed(3)}`);
        console.log(`  Subdivision Level: ${targetLevel.toFixed(2)}`);
    }

    /**
     * 🎹 Control with MIDI note (0-127)
     */
    public morphToMIDINote(midiNote: number): void {
        // Convert MIDI note to cents above C0
        const cents = (midiNote % 12) * 100; // Semitone in current octave
        this.morphToMusicalInterval(cents);
    }

    /**
     * 🎛️ Control with frequency ratio
     */
    public morphToFrequencyRatio(ratio: number): void {
        // Convert ratio to cents: cents = 1200 * log2(ratio)
        const cents = 1200 * Math.log2(ratio);
        this.morphToMusicalInterval(cents);
    }

    /**
     * 🎵 Get current musical info
     */
    public getCurrentMusicalInfo() {
        const mapping = this.musicalMappings.get(this.deweyMode);
        const morphInfo = this.getMorphInfo();

        return {
            deweyMode: this.deweyMode,
            subdivisionLevel: morphInfo.level,
            faceCount: morphInfo.faceCount,
            musicalDivisions: mapping?.musicalDivision || 6,
            intervals: mapping?.intervals || [],
            sphereProgress: morphInfo.sphereProgress,
            symbol: morphInfo.symbol
        };
    }

    /**
     * 🎪 Theremin control with musical quantization
     */
    public controlWithMusicalThereminField(proximity: number): void {
        const mapping = this.musicalMappings.get(this.deweyMode);
        if (!mapping) return;

        // Quantize proximity to musical intervals
        const intervalIndex = Math.floor(proximity * mapping.intervals.length);
        const interval = mapping.intervals[Math.min(intervalIndex, mapping.intervals.length - 1)];

        this.morphToMusicalInterval(interval.cents);
    }

    /**
     * 🎵 Animate through musical sequence
     */
    public async playMusicalSequence(intervalSequence: number[], noteDuration: number = 500): Promise<void> {
        console.log('🎼 Playing musical morphing sequence...');

        for (const cents of intervalSequence) {
            this.morphToMusicalInterval(cents);
            await this.sleep(noteDuration);
        }

        console.log('🎵 Musical sequence complete!');
    }

    /**
     * 📊 Debug: Log all musical mappings
     */
    private logMusicalMappings(): void {
        console.log('\n🎼 MUSICAL SUBDIVISION MAPPINGS:');
        console.log('═'.repeat(50));

        this.musicalMappings.forEach((mapping, mode) => {
            console.log(`\n${mode}:`);
            console.log(`  Subdivision Level: ${mapping.subdivisionLevel}`);
            console.log(`  Face Count: ${mapping.faceCount}`);
            console.log(`  Musical Divisions: ${mapping.musicalDivision}`);
            console.log(`  Sample Intervals:`);

            mapping.intervals.slice(0, 6).forEach(interval => {
                console.log(`    ${interval.deweyCode}: ${interval.name} (${interval.cents}¢)`);
            });
        });
    }

    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/**
 * 🎪 Factory function for musical subdivision morph
 */
export function createMusicalSubdivisionMorph(scene: THREE.Scene): MusicalSubdivisionMorph {
    console.log('🎼 Creating Musical Subdivision Morph Engine...');
    console.log('🎵 Catmull-Clark meets Dewey Decimal musical theory!');

    return new MusicalSubdivisionMorph(scene, 6);
}