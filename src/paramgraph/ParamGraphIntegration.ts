/**
 * ParamGraph Integration for MMPA Universal Signal Engine
 *
 * Integrates the ParamGraph parameter management system with MMPA's
 * dual viewport system, MIDI controls, and morphing parameters.
 */

declare global {
    interface Window {
        ParamGraph: {
            addParam(id: string, opts?: ParamOptions): void;
            ensure(id: string, opts?: ParamOptions): void;
            addMod(mod: ModulationOptions): ModulationHandle;
            setEnabled(mod: ModulationHandle, enabled: boolean): void;
            clearMods(filterFn?: (mod: ModulationHandle) => boolean): void;
            setInput(source: string, path: string, value01: number): void;
            nudge(path: string, delta: number): void;
            get(path: string): number | undefined;
            getOwner(path: string): ParameterOwner | null;
            tickOnce(dtMaxMs?: number): void;
            start(): void;
            stop(): void;
            setAuto(fn: AutoFunction | null): void;
            setOnChange(fn: ChangeFunction | null): void;
            snapshot(): Snapshot;
            loadSnapshot(snap: Snapshot): void;
            resetTargetsToValues(): void;
            setActiveWindow(id: string): void;
            getActiveWindow(): string;
        };
        ParamGraphMIDI: {
            init(): void;
        };
        ParamGraphVoice: {
            start(): void;
            stop(): void;
        };
    }
}

interface ParamOptions {
    value?: number;
    min?: number;
    max?: number;
    smoothing?: number;
    scope?: string;
    tags?: string[];
}

interface ModulationOptions {
    source?: string;
    path?: string;
    gain?: number;
    bias?: number;
    priority?: number;
    enabled?: boolean;
}

interface ModulationHandle {
    source?: string;
    path?: string;
    gain: number;
    bias: number;
    priority: number;
    enabled: boolean;
}

interface ParameterOwner {
    source: string;
    priority: number;
    ts: number;
}

type AutoFunction = (deltaTime: number) => void;
type ChangeFunction = (path: string, value: number) => void;

interface Snapshot {
    version: number;
    params: Record<string, {
        value: number;
        min: number;
        max: number;
        smoothing: number;
        scope: string;
        tags: string[];
    }>;
}

/**
 * MMPA-specific parameter paths based on the handoff specification
 */
export const MMPA_PARAM_PATHS = {
    // Root morphing
    CUBE_SPHERE: 'root/morph/cubeSphere',

    // Main viewport (primary display)
    MAIN_VESSEL_ROT_X: 'viewport/main/vessel/rotX',
    MAIN_VESSEL_ROT_Y: 'viewport/main/vessel/rotY',
    MAIN_VESSEL_ROT_Z: 'viewport/main/vessel/rotZ',
    MAIN_COMPASS_OPACITY: 'viewport/main/compass/opacity',
    MAIN_MORPH_BLEND: 'viewport/main/morph/axis_blend',

    // Aux viewport (morph box)
    AUX_VESSEL_ROT_X: 'viewport/aux/vessel/rotX',
    AUX_VESSEL_ROT_Y: 'viewport/aux/vessel/rotY',
    AUX_VESSEL_ROT_Z: 'viewport/aux/vessel/rotZ',
    AUX_COMPASS_OPACITY: 'viewport/aux/compass/opacity',
    AUX_MORPH_BLEND: 'viewport/aux/morph/axis_blend',
} as const;

/**
 * Input source priorities (higher = takes precedence)
 */
export const INPUT_PRIORITIES = {
    MIDI: 7,
    TOUCH: 6,
    VOICE: 5,
    AUTO: 1,
    AUDIO: 0,
} as const;

export class ParamGraphIntegration {
    private initialized = false;
    private changeCallbacks: Map<string, (value: number) => void> = new Map();

    async initialize(): Promise<void> {
        if (this.initialized) return;

        // Load ParamGraph scripts if not already loaded
        await this.loadParamGraphScripts();

        // Initialize parameter definitions for MMPA
        this.initializeMMPAParameters();

        // Set up MIDI integration
        this.initializeMIDIIntegration();

        // Set up change monitoring
        this.setupChangeMonitoring();

        // Start the parameter system
        window.ParamGraph.start();

        this.initialized = true;
        console.log('🎛️ ParamGraph Integration initialized for MMPA');
    }

    private async loadParamGraphScripts(): Promise<void> {
        if (window.ParamGraph) return; // Already loaded

        // In a real implementation, these would be loaded via dynamic imports
        // For now, assuming they're loaded in HTML
        return new Promise((resolve) => {
            // Check periodically for ParamGraph to be available
            const checkInterval = setInterval(() => {
                if (window.ParamGraph) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
        });
    }

    private initializeMMPAParameters(): void {
        const PG = window.ParamGraph;

        // Root morphing parameter
        PG.ensure(MMPA_PARAM_PATHS.CUBE_SPHERE, {
            min: 0,
            max: 1,
            value: 0,
            smoothing: 0.08,
            scope: 'global',
            tags: ['morph', 'hero']
        });

        // Main viewport parameters
        PG.ensure(MMPA_PARAM_PATHS.MAIN_VESSEL_ROT_X, {
            min: 0,
            max: 360,
            value: 0,
            smoothing: 0.18,
            scope: 'viewport/main',
            tags: ['rotation', 'hero']
        });

        PG.ensure(MMPA_PARAM_PATHS.MAIN_VESSEL_ROT_Y, {
            min: 0,
            max: 360,
            value: 0,
            smoothing: 0.18,
            scope: 'viewport/main',
            tags: ['rotation', 'hero']
        });

        PG.ensure(MMPA_PARAM_PATHS.MAIN_VESSEL_ROT_Z, {
            min: 0,
            max: 360,
            value: 0,
            smoothing: 0.18,
            scope: 'viewport/main',
            tags: ['rotation', 'hero']
        });

        PG.ensure(MMPA_PARAM_PATHS.MAIN_COMPASS_OPACITY, {
            min: 0,
            max: 1,
            value: 0.3,
            smoothing: 0.2,
            scope: 'viewport/main',
            tags: ['ui', 'opacity']
        });

        // Aux viewport parameters (morph box)
        PG.ensure(MMPA_PARAM_PATHS.AUX_VESSEL_ROT_X, {
            min: 0,
            max: 360,
            value: 0,
            smoothing: 0.18,
            scope: 'viewport/aux',
            tags: ['rotation', 'hero']
        });

        PG.ensure(MMPA_PARAM_PATHS.AUX_VESSEL_ROT_Y, {
            min: 0,
            max: 360,
            value: 0,
            smoothing: 0.18,
            scope: 'viewport/aux',
            tags: ['rotation', 'hero']
        });

        PG.ensure(MMPA_PARAM_PATHS.AUX_VESSEL_ROT_Z, {
            min: 0,
            max: 360,
            value: 0,
            smoothing: 0.18,
            scope: 'viewport/aux',
            tags: ['rotation', 'hero']
        });

        PG.ensure(MMPA_PARAM_PATHS.AUX_COMPASS_OPACITY, {
            min: 0,
            max: 1,
            value: 0.3,
            smoothing: 0.2,
            scope: 'viewport/aux',
            tags: ['ui', 'opacity']
        });
    }

    private initializeMIDIIntegration(): void {
        if (window.ParamGraphMIDI) {
            window.ParamGraphMIDI.init();
        }
    }

    private setupChangeMonitoring(): void {
        window.ParamGraph.setOnChange((path: string, value: number) => {
            const callback = this.changeCallbacks.get(path);
            if (callback) {
                callback(value);
            }
        });
    }

    /**
     * Register a callback for when a parameter changes
     */
    onParameterChange(path: string, callback: (value: number) => void): void {
        this.changeCallbacks.set(path, callback);
    }

    /**
     * Set input from MIDI controller
     */
    setMIDIInput(ccNumber: number, value: number): void {
        const normalizedValue = value / 127;
        const activeViewport = window.ParamGraph.getActiveWindow();

        // Map CC1 to active viewport's morph axis blend (MMPA baseline spec)
        if (ccNumber === 1) {
            const path = `${activeViewport}/morph/axis_blend`;
            window.ParamGraph.setInput('midi', path, normalizedValue);
        }

        // Add other CC mappings as needed
    }

    /**
     * Set touch/UI input
     */
    setTouchInput(path: string, value01: number): void {
        window.ParamGraph.setInput('touch', path, value01);
    }

    /**
     * Get current parameter value
     */
    getParameter(path: string): number | undefined {
        return window.ParamGraph.get(path);
    }

    /**
     * Set active viewport (main or aux)
     */
    setActiveViewport(viewport: 'main' | 'aux'): void {
        const viewportPath = `viewport/${viewport}`;
        window.ParamGraph.setActiveWindow(viewportPath);
    }

    /**
     * Get current active viewport
     */
    getActiveViewport(): 'main' | 'aux' {
        const active = window.ParamGraph.getActiveWindow();
        return active.includes('aux') ? 'aux' : 'main';
    }

    /**
     * Save current parameter state
     */
    saveSnapshot(): Snapshot {
        return window.ParamGraph.snapshot();
    }

    /**
     * Load parameter state
     */
    loadSnapshot(snapshot: Snapshot): void {
        window.ParamGraph.loadSnapshot(snapshot);
    }

    /**
     * Clean shutdown
     */
    shutdown(): void {
        if (window.ParamGraph) {
            window.ParamGraph.stop();
        }
        this.changeCallbacks.clear();
        this.initialized = false;
    }
}

// Create singleton instance
export const paramGraphIntegration = new ParamGraphIntegration();