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
    baseDivisions: number;     // Starting divisions per octave
    maxLevels: number;         // Number of subdivision steps available (integer)
    color: { h: number; s: number; l: number }; // HSL color scheme
}

export interface TETLevelInfo {
    system: TETSystem;
    rawLevel: number;
    clampedLevel: number;
    discreteLevel: number;
    fractionalLevel: number;
    tetSize: number;
    nextTetSize: number;
    maxTetSize: number;
}

import { MorphDiagnostics } from './MorphDiagnostics';

export class MicrotonalFrequencyCalculator {
    private baseFrequency: number = 440.0; // A4 = 440 Hz reference
    private referenceNote: string = 'A4';

    // TET Systems mapping to Dewey modes
    public readonly tetSystems: Map<string, TETSystem> = new Map([
        ['6-PANEL', {
            name: '6-TET Cellular Sequence',
            baseDivisions: 6,
            maxLevels: 2,
            color: { h: 0.08, s: 0.9, l: 0.6 }
        }],
        ['12-TONE', {
            name: '12-TET Fractal Expansion',
            baseDivisions: 12,
            maxLevels: 3,
            color: { h: 0.55, s: 0.9, l: 0.5 }
        }],
        ['24-TET', {
            name: '24-TET Cellular Hypercube',
            baseDivisions: 24,
            maxLevels: 4,
            color: { h: 0.75, s: 0.9, l: 0.4 }
        }],
        ['HYPERMICRO', {
            name: 'Hypermicrotonal Continuum',
            baseDivisions: 48,
            maxLevels: 3,
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

        const levelInfo = this.resolveLevelInfo(subdivisionLevel, tetSystem);
        const actualDivisions = levelInfo.tetSize;

        // Calculate division number for this panel/layer
        const divisionNumber = this.calculateDivisionNumber(panelIndex, actualDivisions, levelInfo);

        // Calculate frequency
        const frequency = this.calculateTETFrequency(divisionNumber, actualDivisions);

        // Calculate cents from reference
        const cents = this.frequencyToCents(frequency);

        // Calculate harmonic ratio
        const harmonicRatio = frequency / this.baseFrequency;

        // Generate Dewey classification code
        const deweyCode = this.generateDeweyCode(deweyMode, subdivisionLevel, panelIndex);

        MorphDiagnostics.recordTETEvent({
            mode: deweyMode,
            subdivisionLevel,
            panelIndex,
            tetDivision: divisionNumber,
            tetSize: actualDivisions,
            cents,
            discreteLevel: levelInfo.discreteLevel,
            fractionalLevel: levelInfo.fractionalLevel
        });

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
     * 🎯 Calculate division number for specific panel/layer
     */
    private calculateDivisionNumber(
        panelIndex: number,
        totalDivisions: number,
        levelInfo: TETLevelInfo
    ): number {
        const step = totalDivisions / 6;
        const fractional = levelInfo.fractionalLevel;

        let division = Math.round(panelIndex * step + fractional * step);

        if (panelIndex === 5) {
            division = totalDivisions - 1;
        }

        return Math.min(Math.max(division, 0), totalDivisions - 1);
    }

    /**
     * 📏 Convert frequency to cents relative to base frequency
     */
    public frequencyToCents(frequency: number): number {
        const ratio = frequency / this.baseFrequency;
        const cents = 1200 * Math.log2(ratio);
        return cents;
    }

    private resolveLevelInfo(subdivisionLevel: number, tetSystem: TETSystem): TETLevelInfo {
        const clampedLevel = Math.max(0, Math.min(subdivisionLevel, tetSystem.maxLevels));
        const discreteLevel = Math.floor(clampedLevel);
        const fractionalLevel = clampedLevel - discreteLevel;

        const tetSize = tetSystem.baseDivisions * Math.pow(2, discreteLevel);
        const nextTetSize = tetSystem.baseDivisions * Math.pow(2, Math.min(discreteLevel + 1, tetSystem.maxLevels));
        const maxTetSize = tetSystem.baseDivisions * Math.pow(2, tetSystem.maxLevels);

        return {
            system: tetSystem,
            rawLevel: subdivisionLevel,
            clampedLevel,
            discreteLevel,
            fractionalLevel,
            tetSize,
            nextTetSize,
            maxTetSize
        };
    }

    public describeLevel(deweyMode: string, subdivisionLevel: number): TETLevelInfo | null {
        const system = this.tetSystems.get(deweyMode);
        if (!system) return null;
        return this.resolveLevelInfo(subdivisionLevel, system);
    }

    public getTETSystem(deweyMode: string): TETSystem | undefined {
        return this.tetSystems.get(deweyMode);
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
