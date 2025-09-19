interface LayerState {
    intensity: number;
    speed?: number;
    color?: string;
    position?: { x: number; y: number; z: number };
    rotation?: { x: number; y: number; z: number };
    scale?: { x: number; y: number; z: number };
    customData?: any;
}

interface PerformancePreset {
    id: string;
    name: string;
    description: string;
    mode: 'club' | 'installation' | 'instrument';
    timestamp: number;
    author?: string;
    tags: string[];

    // Layer states
    vesselLayer: LayerState;
    emergentFormLayer: LayerState;
    particleLayer: LayerState;
    shadowLayer: LayerState;

    // Audio settings
    audioSettings: {
        masterVolume: number;
        reverbLevel: number;
        delayLevel: number;
    };

    // Performance settings
    bpm: number;
    sequences: string[]; // IDs of included sequences
    activeArchetypes: string[];

    // Installation mode specifics
    installationSettings?: {
        duration: number; // minutes
        evolution: boolean;
        autoTriggers: boolean;
        timeBasedChanges: boolean;
    };

    // Lighting and visual settings
    lighting: {
        ambientIntensity: number;
        pointLightColors: number[];
        shadowIntensity: number;
    };
}

export class PresetManager {
    private presets: Map<string, PerformancePreset> = new Map();
    private currentPreset: PerformancePreset | null = null;
    private autoSaveEnabled = true;
    private presetChangeCallbacks: ((preset: PerformancePreset) => void)[] = [];

    constructor() {
        this.initializeDefaultPresets();
        this.loadPresetsFromStorage();
    }

    private initializeDefaultPresets() {
        // Club Mode Preset - High energy, strobing
        const clubPreset: PerformancePreset = {
            id: 'club-default',
            name: 'Electric Club',
            description: 'High-energy strobing with Tesla and Prankster chaos',
            mode: 'club',
            timestamp: Date.now(),
            tags: ['club', 'high-energy', 'default'],

            vesselLayer: {
                intensity: 0.9,
                color: '#4a90e2'
            },
            emergentFormLayer: {
                intensity: 0.8,
                speed: 1.5,
                color: '#50c878'
            },
            particleLayer: {
                intensity: 1.0,
                color: '#ff6b6b'
            },
            shadowLayer: {
                intensity: 0.6,
                color: '#000000'
            },

            audioSettings: {
                masterVolume: -5,
                reverbLevel: 0.3,
                delayLevel: 0.4
            },

            bpm: 128,
            sequences: ['welcome'],
            activeArchetypes: ['tesla', 'pranksters', 'hoffman'],

            lighting: {
                ambientIntensity: 0.1,
                pointLightColors: [0xff6b6b, 0x6b9fff, 0x50c878],
                shadowIntensity: 0.8
            }
        };

        // Installation Mode Preset - Contemplative, ambient
        const installationPreset: PerformancePreset = {
            id: 'installation-default',
            name: 'Cosmic Cathedral',
            description: 'Ambient cosmic journey with Russell geometry and Hawking radiation',
            mode: 'installation',
            timestamp: Date.now(),
            tags: ['installation', 'ambient', 'cosmic', 'default'],

            vesselLayer: {
                intensity: 0.4,
                color: '#e6e6fa'
            },
            emergentFormLayer: {
                intensity: 0.3,
                speed: 0.3,
                color: '#9932cc'
            },
            particleLayer: {
                intensity: 0.2,
                color: '#191970'
            },
            shadowLayer: {
                intensity: 0.9,
                color: '#000080'
            },

            audioSettings: {
                masterVolume: -15,
                reverbLevel: 0.8,
                delayLevel: 0.6
            },

            bpm: 60,
            sequences: ['cosmic'],
            activeArchetypes: ['russell', 'hawking', 'greiff'],

            installationSettings: {
                duration: 60,
                evolution: true,
                autoTriggers: true,
                timeBasedChanges: true
            },

            lighting: {
                ambientIntensity: 0.05,
                pointLightColors: [0x191970, 0x483d8b, 0x9932cc],
                shadowIntensity: 0.3
            }
        };

        // Instrument Mode Preset - Expressive, responsive
        const instrumentPreset: PerformancePreset = {
            id: 'instrument-default',
            name: 'Mythic Bandmate',
            description: 'Responsive instrument mode with Blake mysticism and Beatles harmony',
            mode: 'instrument',
            timestamp: Date.now(),
            tags: ['instrument', 'expressive', 'mystical', 'default'],

            vesselLayer: {
                intensity: 0.6,
                color: '#ffd700'
            },
            emergentFormLayer: {
                intensity: 0.7,
                speed: 0.8,
                color: '#8b008b'
            },
            particleLayer: {
                intensity: 0.7,
                color: '#32cd32'
            },
            shadowLayer: {
                intensity: 0.5,
                color: '#2f4f4f'
            },

            audioSettings: {
                masterVolume: -8,
                reverbLevel: 0.5,
                delayLevel: 0.3
            },

            bpm: 100,
            sequences: [],
            activeArchetypes: ['blake', 'beatles', 'russell'],

            lighting: {
                ambientIntensity: 0.2,
                pointLightColors: [0xffd700, 0x8b008b, 0x32cd32],
                shadowIntensity: 0.6
            }
        };

        // Chaos Mode - Experimental
        const chaosPreset: PerformancePreset = {
            id: 'chaos-experiment',
            name: 'Prankster Chaos',
            description: 'Experimental chaos with all trickster archetypes active',
            mode: 'club',
            timestamp: Date.now(),
            tags: ['experimental', 'chaos', 'trickster'],

            vesselLayer: {
                intensity: 0.8,
                color: '#ff1493'
            },
            emergentFormLayer: {
                intensity: 1.0,
                speed: 2.0,
                color: '#00ff00'
            },
            particleLayer: {
                intensity: 1.0,
                color: '#ffff00'
            },
            shadowLayer: {
                intensity: 0.8,
                color: '#ff0000'
            },

            audioSettings: {
                masterVolume: -3,
                reverbLevel: 0.9,
                delayLevel: 0.8
            },

            bpm: 160,
            sequences: [],
            activeArchetypes: ['pranksters', 'hoffman', 'waas', 'tesla'],

            lighting: {
                ambientIntensity: 0.3,
                pointLightColors: [0xff1493, 0x00ff00, 0xffff00],
                shadowIntensity: 1.0
            }
        };

        this.presets.set('club-default', clubPreset);
        this.presets.set('installation-default', installationPreset);
        this.presets.set('instrument-default', instrumentPreset);
        this.presets.set('chaos-experiment', chaosPreset);
    }

    public saveCurrentAsPreset(name: string, description: string, tags: string[] = []): string {
        // This would capture current engine state
        const preset: PerformancePreset = {
            id: Date.now().toString(),
            name,
            description,
            mode: 'instrument', // Would get from engine
            timestamp: Date.now(),
            tags,

            vesselLayer: { intensity: 0.6 }, // Would capture from layers
            emergentFormLayer: { intensity: 0.7, speed: 0.8 },
            particleLayer: { intensity: 0.7 },
            shadowLayer: { intensity: 0.5 },

            audioSettings: {
                masterVolume: -8,
                reverbLevel: 0.5,
                delayLevel: 0.3
            },

            bpm: 120,
            sequences: [],
            activeArchetypes: [],

            lighting: {
                ambientIntensity: 0.2,
                pointLightColors: [0xffffff],
                shadowIntensity: 0.5
            }
        };

        this.presets.set(preset.id, preset);
        this.savePresetsToStorage();

        console.log(`💾 Saved preset: ${name}`);
        return preset.id;
    }

    public loadPreset(presetId: string): boolean {
        const preset = this.presets.get(presetId);
        if (!preset) {
            console.error(`Preset not found: ${presetId}`);
            return false;
        }

        this.currentPreset = preset;

        // Notify callbacks to apply the preset
        this.presetChangeCallbacks.forEach(callback => callback(preset));

        console.log(`🎭 Loaded preset: ${preset.name}`);
        return true;
    }

    public deletePreset(presetId: string): boolean {
        if (this.presets.delete(presetId)) {
            this.savePresetsToStorage();
            console.log(`🗑️ Deleted preset: ${presetId}`);
            return true;
        }
        return false;
    }

    public duplicatePreset(presetId: string, newName: string): string | null {
        const original = this.presets.get(presetId);
        if (!original) {
            return null;
        }

        const duplicate: PerformancePreset = {
            ...original,
            id: Date.now().toString(),
            name: newName,
            timestamp: Date.now()
        };

        this.presets.set(duplicate.id, duplicate);
        this.savePresetsToStorage();

        return duplicate.id;
    }

    public getPresets(): PerformancePreset[] {
        return Array.from(this.presets.values()).sort((a, b) => b.timestamp - a.timestamp);
    }

    public getPresetsByTag(tag: string): PerformancePreset[] {
        return this.getPresets().filter(preset => preset.tags.includes(tag));
    }

    public getPresetsByMode(mode: string): PerformancePreset[] {
        return this.getPresets().filter(preset => preset.mode === mode);
    }

    public searchPresets(query: string): PerformancePreset[] {
        const lowerQuery = query.toLowerCase();
        return this.getPresets().filter(preset =>
            preset.name.toLowerCase().includes(lowerQuery) ||
            preset.description.toLowerCase().includes(lowerQuery) ||
            preset.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
        );
    }

    public exportPreset(presetId: string): string | null {
        const preset = this.presets.get(presetId);
        if (!preset) {
            return null;
        }

        return JSON.stringify(preset, null, 2);
    }

    public importPreset(jsonData: string): string | null {
        try {
            const preset: PerformancePreset = JSON.parse(jsonData);
            preset.id = Date.now().toString(); // New ID to avoid conflicts
            preset.timestamp = Date.now();

            this.presets.set(preset.id, preset);
            this.savePresetsToStorage();

            return preset.id;
        } catch (error) {
            console.error('Failed to import preset:', error);
            return null;
        }
    }

    public onPresetChange(callback: (preset: PerformancePreset) => void) {
        this.presetChangeCallbacks.push(callback);
    }

    public getCurrentPreset(): PerformancePreset | null {
        return this.currentPreset;
    }

    public getDefaultPresetForMode(mode: string): string | null {
        const defaults: { [key: string]: string } = {
            'club': 'club-default',
            'installation': 'installation-default',
            'instrument': 'instrument-default'
        };

        return defaults[mode] || null;
    }

    private savePresetsToStorage() {
        if (typeof localStorage !== 'undefined') {
            try {
                const presetData = Array.from(this.presets.entries());
                localStorage.setItem('universal-signal-presets', JSON.stringify(presetData));
            } catch (error) {
                console.error('Failed to save presets to storage:', error);
            }
        }
    }

    private loadPresetsFromStorage() {
        if (typeof localStorage !== 'undefined') {
            try {
                const stored = localStorage.getItem('universal-signal-presets');
                if (stored) {
                    const presetData = JSON.parse(stored);
                    presetData.forEach(([id, preset]: [string, PerformancePreset]) => {
                        this.presets.set(id, preset);
                    });
                }
            } catch (error) {
                console.error('Failed to load presets from storage:', error);
            }
        }
    }

    public getQuickLoadPresets(): PerformancePreset[] {
        // Return most recent presets for quick access
        return this.getPresets().slice(0, 6);
    }

    public tagPreset(presetId: string, tags: string[]): boolean {
        const preset = this.presets.get(presetId);
        if (preset) {
            preset.tags = [...new Set([...preset.tags, ...tags])];
            this.savePresetsToStorage();
            return true;
        }
        return false;
    }

    public untagPreset(presetId: string, tag: string): boolean {
        const preset = this.presets.get(presetId);
        if (preset) {
            preset.tags = preset.tags.filter(t => t !== tag);
            this.savePresetsToStorage();
            return true;
        }
        return false;
    }

    public setAutoSave(enabled: boolean) {
        this.autoSaveEnabled = enabled;
    }

    public isAutoSaveEnabled(): boolean {
        return this.autoSaveEnabled;
    }
}