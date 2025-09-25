/**
 * MorphDiagnostics
 *
 * Centralized debug collector for morph progression and TET calculations.
 * Provides an in-memory log that can be inspected via the browser console.
 */

interface MorphEvent {
    timestamp: number;
    source: string;
    progress: number;
    level?: number;
    geometryMode?: string;
    detail?: Record<string, unknown>;
}

interface TETEvent {
    timestamp: number;
    mode: string;
    subdivisionLevel: number;
    panelIndex: number;
    tetDivision: number;
    tetSize: number;
    cents: number;
    discreteLevel?: number;
    fractionalLevel?: number;
}

class MorphDiagnosticsClass {
    private morphEvents: MorphEvent[] = [];
    private tetEvents: TETEvent[] = [];
    private maxEntries = 100;

    public recordMorphEvent(event: Omit<MorphEvent, 'timestamp'>): void {
        this.morphEvents.push({ ...event, timestamp: Date.now() });
        this.trim(this.morphEvents);
    }

    public recordTETEvent(event: Omit<TETEvent, 'timestamp'>): void {
        this.tetEvents.push({ ...event, timestamp: Date.now() });
        this.trim(this.tetEvents);
    }

    public getMorphEvents(): MorphEvent[] {
        return [...this.morphEvents];
    }

    public getTETEvents(): TETEvent[] {
        return [...this.tetEvents];
    }

    public reset(): void {
        this.morphEvents = [];
        this.tetEvents = [];
    }

    private trim<T>(list: T[]): void {
        if (list.length > this.maxEntries) {
            list.splice(0, list.length - this.maxEntries);
        }
    }
}

export const MorphDiagnostics = new MorphDiagnosticsClass();

// Expose helper in browser console for quick inspection
if (typeof window !== 'undefined') {
    (window as any).MorphDiagnostics = MorphDiagnostics;
}
