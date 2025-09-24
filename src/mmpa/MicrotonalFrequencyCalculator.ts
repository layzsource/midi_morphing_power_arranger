/**
 * 🎵 Microtonal Frequency Calculator
 *
 * Real mathematical frequency calculations for TET (Tone Equal Temperament) systems
 * Implements precise frequency ratios, harmonic series, and microtonal intervals
 *
 * Based on:
 * - Equal temperament: f(n) = f₀ × 2^(n/N) where N = divisions per octave
 * - Cents: 1200 cents = 1 octave, 100 cents = 1 semitone
 * - Harmonic series: f(n) = f₀ × n (natural harmonics)
 */

export interface FrequencyData {
    frequency: number;          // Hz
    cents: number;             // Cents from reference
    tetDivision: number;       // TET division number
    tetSize: number;           // Total divisions in TET system
    harmonicRatio: number;     // Ratio to fundamental
    deweyCode: string;         // Dewey classification
}

export interface TETSystem {
    name: string;
    divisions: number;         // Divisions per octave
    stepSize: number;          // Cents per step
    maxSubdivision: number;    // Maximum safe subdivision level
    color: { h: number; s: number; l: number }; // HSL color scheme
}

export class MicrotonalFrequencyCalculator {
    private baseFrequency: number = 440.0; // A4 = 440 Hz reference
    private referenceNote: string = 'A4';

    // TET Systems mapping to Dewey modes
    public readonly tetSystems: Map<string, TETSystem> = new Map([
        ['6-PANEL', {
            name: '6-TET to 12-TET',
            divisions: 12,
            stepSize: 100,
            maxSubdivision: 1,
            color: { h: 0.08, s: 0.9, l: 0.6 }
        }],
        ['12-TONE', {
            name: '12-TET to 48-TET',
            divisions: 48,
            stepSize: 25,
            maxSubdivision: 2,
            color: { h: 0.55, s: 0.9, l: 0.5 }
        }],
        ['24-TET', {
            name: '24-TET to 192-TET',
            divisions: 192,
            stepSize: 6.25,
            maxSubdivision: 3,
            color: { h: 0.75, s: 0.9, l: 0.4 }
        }],
        ['HYPERMICRO', {
            name: 'Hypermicrotonal up to 384-TET',
            divisions: 384,
            stepSize: 3.125,
            maxSubdivision: 2,
            color: { h: 0.33, s: 1.0, l: 0.3 }
        }]
    ]);

    constructor(baseFreq: number = 440.0, refNote: string = 'A4') {
        this.baseFrequency = baseFreq;
        this.referenceNote = refNote;
        console.log(`🎵 MicrotonalFrequencyCalculator initialized: ${this.baseFrequency}Hz (${this.referenceNote})`);
    }

    /**
     * 🧮 Calculate frequency for TET system division
     *
     * Formula: f(n) = f₀ × 2^(n/N)
     * Where: n = division number, N = total divisions per octave
     */
    public calculateTETFrequency(division: number, tetSize: number): number {
        const exponent = division / tetSize;
        const frequency = this.baseFrequency * Math.pow(2, exponent);

        console.log(`🎯 TET Calculation: ${division}/${tetSize}-TET = ${frequency.toFixed(3)}Hz`);
        return frequency;
    }

    /**
     * 🎼 Calculate frequency from cents
     *
     * Formula: f = f₀ × 2^(cents/1200)
     * 1200 cents = 1 octave
     */
    public calculateFrequencyFromCents(cents: number): number {
        const frequency = this.baseFrequency * Math.pow(2, cents / 1200);
        console.log(`🎵 Cents to Hz: ${cents}¢ = ${frequency.toFixed(3)}Hz`);
        return frequency;
    }

    /**
     * 🌊 Calculate harmonic series frequency
     *
     * Natural harmonics: f(n) = f₀ × n
     */
    public calculateHarmonicFrequency(harmonicNumber: number): number {
        const frequency = this.baseFrequency * harmonicNumber;
        console.log(`🌊 Harmonic ${harmonicNumber}: ${frequency.toFixed(3)}Hz`);
        return frequency;
    }

    /**
     * 🎨 Get frequency data for current subdivision level and mode
     */
    public getFrequencyData(
        subdivisionLevel: number,
        deweyMode: string,
        panelIndex: number = 0
    ): FrequencyData {
        const tetSystem = this.tetSystems.get(deweyMode);
        if (!tetSystem) {
            throw new Error(`Unknown Dewey mode: ${deweyMode}`);
        }

        // Calculate actual TET divisions based on subdivision level
        const actualDivisions = this.calculateActualDivisions(subdivisionLevel, tetSystem);

        // Calculate division number for this panel/layer
        const divisionNumber = this.calculateDivisionNumber(panelIndex, actualDivisions, subdivisionLevel);

        // Calculate frequency
        const frequency = this.calculateTETFrequency(divisionNumber, actualDivisions);

        // Calculate cents from reference
        const cents = this.frequencyToCents(frequency);

        // Calculate harmonic ratio
        const harmonicRatio = frequency / this.baseFrequency;

        // Generate Dewey classification code
        const deweyCode = this.generateDeweyCode(deweyMode, subdivisionLevel, panelIndex);

        return {
            frequency,
            cents,
            tetDivision: divisionNumber,
            tetSize: actualDivisions,
            harmonicRatio,
            deweyCode
        };
    }

    /**
     * 🔢 Calculate actual TET divisions based on subdivision progression
     *
     * Progression: Base TET × 2^subdivisionLevel
     * 6-PANEL: 6 → 12 → 24
     * 12-TONE: 12 → 24 → 48 → 96
     * 24-TET: 24 → 48 → 96 → 192 → 384
     */
    private calculateActualDivisions(subdivisionLevel: number, tetSystem: TETSystem): number {
        const baseDivisions = tetSystem.divisions / Math.pow(2, tetSystem.maxSubdivision);
        const actualDivisions = baseDivisions * Math.pow(2, subdivisionLevel);

        // Cap to prevent computational issues
        const maxDivisions = tetSystem.divisions;
        return Math.min(actualDivisions, maxDivisions);
    }

    /**
     * 🎯 Calculate division number for specific panel/layer
     */
    private calculateDivisionNumber(
        panelIndex: number,
        totalDivisions: number,
        subdivisionLevel: number
    ): number {
        // Distribute 6 panels across TET divisions
        const divisionStep = totalDivisions / 6;
        return Math.floor(panelIndex * divisionStep);
    }

    /**
     * 📏 Convert frequency to cents relative to base frequency
     */
    public frequencyToCents(frequency: number): number {
        const ratio = frequency / this.baseFrequency;
        const cents = 1200 * Math.log2(ratio);
        return cents;
    }

    /**
     * 🏷️ Generate Dewey decimal classification code
     *
     * Format: XXX.YY where:
     * XXX = Mode base (147 = Geometric-Musical Theory)
     * YY = Subdivision.Panel encoding
     */
    private generateDeweyCode(deweyMode: string, subdivisionLevel: number, panelIndex: number): string {
        const baseCodes = {
            '6-PANEL': '147.10',
            '12-TONE': '147.20',
            '24-TET': '147.30',
            'HYPERMICRO': '147.40'
        };

        const baseCode = baseCodes[deweyMode as keyof typeof baseCodes] || '147.00';
        const subdivisionDecimal = (subdivisionLevel * 10 + panelIndex).toString().padStart(2, '0');

        return `${baseCode.split('.')[0]}.${subdivisionDecimal}`;
    }

    /**
     * 🎼 Calculate frequencies for all 6 panels at current subdivision level
     */
    public calculateAllPanelFrequencies(subdivisionLevel: number, deweyMode: string): FrequencyData[] {
        const frequencies: FrequencyData[] = [];

        for (let panelIndex = 0; panelIndex < 6; panelIndex++) {
            const freqData = this.getFrequencyData(subdivisionLevel, deweyMode, panelIndex);
            frequencies.push(freqData);
        }

        console.log(`🎵 Calculated frequencies for all 6 panels in ${deweyMode} at level ${subdivisionLevel.toFixed(2)}`);
        return frequencies;
    }

    /**
     * 🌊 Calculate harmonic series for layered spheres
     *
     * Each layer represents a harmonic of the fundamental
     */
    public calculateLayeredHarmonics(
        fundamentalFreq: number,
        numLayers: number = 6
    ): FrequencyData[] {
        const harmonics: FrequencyData[] = [];

        for (let harmonic = 1; harmonic <= numLayers; harmonic++) {
            const frequency = fundamentalFreq * harmonic;
            const cents = this.frequencyToCents(frequency);

            harmonics.push({
                frequency,
                cents,
                tetDivision: 0,
                tetSize: 12,
                harmonicRatio: harmonic,
                deweyCode: `147.H${harmonic.toString().padStart(2, '0')}`
            });
        }

        console.log(`🌊 Calculated ${numLayers} harmonic layers from ${fundamentalFreq.toFixed(3)}Hz`);
        return harmonics;
    }

    /**
     * 🎚️ Set new base frequency and reference note
     */
    public setBaseFrequency(frequency: number, note: string = 'A4'): void {
        this.baseFrequency = frequency;
        this.referenceNote = note;
        console.log(`🎵 Base frequency updated: ${this.baseFrequency}Hz (${this.referenceNote})`);
    }

    /**
     * 📊 Get current system status
     */
    public getSystemStatus() {
        return {
            baseFrequency: this.baseFrequency,
            referenceNote: this.referenceNote,
            availableTETSystems: Array.from(this.tetSystems.keys()),
            maxFrequency: this.baseFrequency * 32, // 5 octaves up
            minFrequency: this.baseFrequency / 32   // 5 octaves down
        };
    }

    /**
     * 🎵 Calculate just intonation ratios for comparison
     *
     * Perfect mathematical ratios vs equal temperament approximations
     */
    public calculateJustIntonationRatios(): Map<string, { ratio: number; frequency: number; cents: number }> {
        const justRatios = new Map([
            ['Unison', { ratio: 1/1, frequency: 0, cents: 0 }],
            ['Perfect Fifth', { ratio: 3/2, frequency: 0, cents: 0 }],
            ['Perfect Fourth', { ratio: 4/3, frequency: 0, cents: 0 }],
            ['Major Third', { ratio: 5/4, frequency: 0, cents: 0 }],
            ['Minor Third', { ratio: 6/5, frequency: 0, cents: 0 }],
            ['Major Seventh', { ratio: 15/8, frequency: 0, cents: 0 }],
            ['Octave', { ratio: 2/1, frequency: 0, cents: 0 }]
        ]);

        justRatios.forEach((data, intervalName) => {
            data.frequency = this.baseFrequency * data.ratio;
            data.cents = 1200 * Math.log2(data.ratio);
        });

        console.log('🎼 Just intonation ratios calculated for comparison with TET approximations');
        return justRatios;
    }
}

/**
 * 🚀 Factory function to create frequency calculator
 */
export function createMicrotonalFrequencyCalculator(
    baseFreq: number = 440.0,
    refNote: string = 'A4'
): MicrotonalFrequencyCalculator {
    console.log('🎵 Creating MicrotonalFrequencyCalculator...');
    return new MicrotonalFrequencyCalculator(baseFreq, refNote);
}