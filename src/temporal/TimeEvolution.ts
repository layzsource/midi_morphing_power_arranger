interface TimePhase {
    name: string;
    startHour: number;
    endHour: number;
    characteristics: {
        dominantArchetypes: string[];
        layerIntensities: { [layer: string]: number };
        colorPalette: number[];
        audioSettings: { [setting: string]: number };
        autoTriggerProbability: number;
        easterEggSensitivity: number;
    };
}

interface SeasonalInfluence {
    season: 'spring' | 'summer' | 'autumn' | 'winter';
    monthStart: number;
    monthEnd: number;
    influence: {
        archetypeWeights: { [archetype: string]: number };
        visualTendencies: string[];
        temperament: 'growing' | 'flourishing' | 'harvesting' | 'contemplating';
    };
}

interface LunarPhase {
    phase: 'new' | 'waxing' | 'full' | 'waning';
    influence: {
        mysticalIntensity: number;
        shadowEmphasis: number;
        emergentFormActivity: number;
    };
}

export class TimeEvolution {
    private currentPhase: TimePhase | null = null;
    private currentSeason: SeasonalInfluence | null = null;
    private currentLunarPhase: LunarPhase | null = null;
    private evolutionEnabled = true;
    private lastEvolutionUpdate = 0;
    private evolutionInterval = 60000; // 1 minute

    // Callbacks for evolution events
    private onPhaseChangeCallback: ((phase: TimePhase) => void) | null = null;
    private onSeasonChangeCallback: ((season: SeasonalInfluence) => void) | null = null;
    private onEvolutionUpdateCallback: ((evolution: any) => void) | null = null;

    // Installation mode specific
    private installationStartTime = 0;
    private installationDuration = 0; // minutes
    private isInstallationMode = false;
    private installationEvolutionCurve: { time: number; intensity: number }[] = [];

    constructor() {
        this.initializeTimePhases();
        this.initializeSeasonalInfluences();
        this.initializeLunarPhases();
        this.startEvolutionCycle();
    }

    private timePhases: TimePhase[] = [];
    private seasonalInfluences: SeasonalInfluence[] = [];
    private lunarPhases: LunarPhase[] = [];

    private initializeTimePhases() {
        this.timePhases = [
            {
                name: 'Night Mysticism',
                startHour: 0,
                endHour: 6,
                characteristics: {
                    dominantArchetypes: ['blake', 'hawking', 'greiff'],
                    layerIntensities: { vessel: 0.3, emergent: 0.8, particles: 0.2, shadow: 0.9 },
                    colorPalette: [0x191970, 0x483d8b, 0x9932cc, 0x8b008b],
                    audioSettings: { masterVolume: -20, reverbLevel: 0.9, delayLevel: 0.8 },
                    autoTriggerProbability: 0.1,
                    easterEggSensitivity: 1.5
                }
            },
            {
                name: 'Dawn Awakening',
                startHour: 6,
                endHour: 9,
                characteristics: {
                    dominantArchetypes: ['russell', 'einstein', 'beatles'],
                    layerIntensities: { vessel: 0.6, emergent: 0.5, particles: 0.4, shadow: 0.3 },
                    colorPalette: [0xffd700, 0xffa500, 0xff6347, 0xffc0cb],
                    audioSettings: { masterVolume: -15, reverbLevel: 0.4, delayLevel: 0.3 },
                    autoTriggerProbability: 0.3,
                    easterEggSensitivity: 1.0
                }
            },
            {
                name: 'Day Creation',
                startHour: 9,
                endHour: 17,
                characteristics: {
                    dominantArchetypes: ['tesla', 'beatles', 'pranksters'],
                    layerIntensities: { vessel: 0.7, emergent: 0.8, particles: 0.9, shadow: 0.4 },
                    colorPalette: [0x00ff00, 0x32cd32, 0x00ffff, 0x1e90ff],
                    audioSettings: { masterVolume: -8, reverbLevel: 0.3, delayLevel: 0.4 },
                    autoTriggerProbability: 0.5,
                    easterEggSensitivity: 0.8
                }
            },
            {
                name: 'Evening Reflection',
                startHour: 17,
                endHour: 21,
                characteristics: {
                    dominantArchetypes: ['leadbelly', 'greiff', 'hoffman'],
                    layerIntensities: { vessel: 0.5, emergent: 0.6, particles: 0.7, shadow: 0.8 },
                    colorPalette: [0x8b4513, 0xcd853f, 0xdaa520, 0xb8860b],
                    audioSettings: { masterVolume: -12, reverbLevel: 0.6, delayLevel: 0.5 },
                    autoTriggerProbability: 0.2,
                    easterEggSensitivity: 1.2
                }
            },
            {
                name: 'Night Energy',
                startHour: 21,
                endHour: 24,
                characteristics: {
                    dominantArchetypes: ['tesla', 'pranksters', 'hoffman'],
                    layerIntensities: { vessel: 0.8, emergent: 0.9, particles: 1.0, shadow: 0.6 },
                    colorPalette: [0xff0000, 0xff69b4, 0x00ff00, 0xffff00],
                    audioSettings: { masterVolume: -5, reverbLevel: 0.4, delayLevel: 0.6 },
                    autoTriggerProbability: 0.7,
                    easterEggSensitivity: 0.9
                }
            }
        ];
    }

    private initializeSeasonalInfluences() {
        this.seasonalInfluences = [
            {
                season: 'spring',
                monthStart: 3,
                monthEnd: 5,
                influence: {
                    archetypeWeights: { blake: 1.5, russell: 1.3, beatles: 1.4 },
                    visualTendencies: ['growth', 'emergence', 'flowering'],
                    temperament: 'growing'
                }
            },
            {
                season: 'summer',
                monthStart: 6,
                monthEnd: 8,
                influence: {
                    archetypeWeights: { tesla: 1.6, pranksters: 1.5, hoffman: 1.3 },
                    visualTendencies: ['energy', 'brightness', 'activity'],
                    temperament: 'flourishing'
                }
            },
            {
                season: 'autumn',
                monthStart: 9,
                monthEnd: 11,
                influence: {
                    archetypeWeights: { leadbelly: 1.5, greiff: 1.4, waas: 1.2 },
                    visualTendencies: ['harvest', 'reflection', 'transition'],
                    temperament: 'harvesting'
                }
            },
            {
                season: 'winter',
                monthStart: 12,
                monthEnd: 2,
                influence: {
                    archetypeWeights: { hawking: 1.6, blake: 1.3, russell: 1.4 },
                    visualTendencies: ['contemplation', 'depth', 'introspection'],
                    temperament: 'contemplating'
                }
            }
        ];
    }

    private initializeLunarPhases() {
        this.lunarPhases = [
            {
                phase: 'new',
                influence: {
                    mysticalIntensity: 0.3,
                    shadowEmphasis: 1.2,
                    emergentFormActivity: 0.4
                }
            },
            {
                phase: 'waxing',
                influence: {
                    mysticalIntensity: 0.7,
                    shadowEmphasis: 0.8,
                    emergentFormActivity: 1.1
                }
            },
            {
                phase: 'full',
                influence: {
                    mysticalIntensity: 1.5,
                    shadowEmphasis: 0.5,
                    emergentFormActivity: 1.3
                }
            },
            {
                phase: 'waning',
                influence: {
                    mysticalIntensity: 1.0,
                    shadowEmphasis: 1.0,
                    emergentFormActivity: 0.8
                }
            }
        ];
    }

    private startEvolutionCycle() {
        setInterval(() => {
            if (this.evolutionEnabled) {
                this.updateTimeBasedEvolution();
            }
        }, this.evolutionInterval);

        // Initial update
        this.updateTimeBasedEvolution();
    }

    private updateTimeBasedEvolution() {
        const now = new Date();
        const hour = now.getHours();
        const month = now.getMonth() + 1;

        // Update time phase
        const newPhase = this.timePhases.find(phase =>
            hour >= phase.startHour && (hour < phase.endHour || (phase.endHour === 24 && hour >= phase.startHour))
        );

        if (newPhase && newPhase !== this.currentPhase) {
            this.currentPhase = newPhase;
            if (this.onPhaseChangeCallback) {
                this.onPhaseChangeCallback(newPhase);
            }
            console.log(`🕐 Time phase change: ${newPhase.name}`);
        }

        // Update seasonal influence
        const newSeason = this.seasonalInfluences.find(season => {
            if (season.monthStart <= season.monthEnd) {
                return month >= season.monthStart && month <= season.monthEnd;
            } else {
                // Handle winter (Dec-Feb)
                return month >= season.monthStart || month <= season.monthEnd;
            }
        });

        if (newSeason && newSeason !== this.currentSeason) {
            this.currentSeason = newSeason;
            if (this.onSeasonChangeCallback) {
                this.onSeasonChangeCallback(newSeason);
            }
            console.log(`🌱 Seasonal change: ${newSeason.season}`);
        }

        // Update lunar phase (simplified calculation)
        this.updateLunarPhase();

        // Installation mode evolution
        if (this.isInstallationMode) {
            this.updateInstallationEvolution();
        }

        // Emit general evolution update
        if (this.onEvolutionUpdateCallback) {
            this.onEvolutionUpdateCallback({
                phase: this.currentPhase,
                season: this.currentSeason,
                lunar: this.currentLunarPhase,
                timestamp: now.getTime()
            });
        }

        this.lastEvolutionUpdate = now.getTime();
    }

    private updateLunarPhase() {
        // Simplified lunar phase calculation (in real implementation would use accurate astronomy)
        const now = new Date();
        const dayOfMonth = now.getDate();

        let phase: LunarPhase['phase'];
        if (dayOfMonth < 7) phase = 'new';
        else if (dayOfMonth < 14) phase = 'waxing';
        else if (dayOfMonth < 21) phase = 'full';
        else phase = 'waning';

        const newLunarPhase = this.lunarPhases.find(lp => lp.phase === phase)!;

        if (newLunarPhase !== this.currentLunarPhase) {
            this.currentLunarPhase = newLunarPhase;
            console.log(`🌙 Lunar phase: ${phase}`);
        }
    }

    private updateInstallationEvolution() {
        if (!this.isInstallationMode) return;

        const elapsed = (Date.now() - this.installationStartTime) / 1000 / 60; // minutes
        const progress = elapsed / this.installationDuration;

        // Find current point on evolution curve
        const curvePoint = this.installationEvolutionCurve.find((point, index) => {
            const nextPoint = this.installationEvolutionCurve[index + 1];
            return progress >= point.time && (!nextPoint || progress < nextPoint.time);
        });

        if (curvePoint && this.onEvolutionUpdateCallback) {
            this.onEvolutionUpdateCallback({
                installationProgress: progress,
                installationIntensity: curvePoint.intensity,
                installationPhase: this.getInstallationPhase(progress)
            });
        }
    }

    private getInstallationPhase(progress: number): string {
        if (progress < 0.1) return 'awakening';
        if (progress < 0.3) return 'exploration';
        if (progress < 0.6) return 'development';
        if (progress < 0.8) return 'climax';
        if (progress < 0.95) return 'resolution';
        return 'transcendence';
    }

    // Installation Mode Methods
    public startInstallationMode(durationMinutes: number) {
        this.isInstallationMode = true;
        this.installationStartTime = Date.now();
        this.installationDuration = durationMinutes;

        // Create evolution curve for installation
        this.installationEvolutionCurve = [
            { time: 0.0, intensity: 0.1 },    // Gentle awakening
            { time: 0.1, intensity: 0.3 },    // Initial exploration
            { time: 0.3, intensity: 0.5 },    // Growing engagement
            { time: 0.6, intensity: 0.8 },    // Peak development
            { time: 0.8, intensity: 1.0 },    // Climax
            { time: 0.9, intensity: 0.7 },    // Resolution begins
            { time: 0.95, intensity: 0.4 },   // Gentle conclusion
            { time: 1.0, intensity: 0.1 }     // Return to silence
        ];

        console.log(`🏛️ Installation mode started: ${durationMinutes} minutes`);
    }

    public stopInstallationMode() {
        this.isInstallationMode = false;
        this.installationStartTime = 0;
        this.installationDuration = 0;
        this.installationEvolutionCurve = [];
        console.log('🏛️ Installation mode ended');
    }

    // Auto-trigger system
    public shouldAutoTrigger(): boolean {
        if (!this.currentPhase) return false;
        return Math.random() < this.currentPhase.characteristics.autoTriggerProbability;
    }

    public getRandomArchetypeForCurrentTime(): string {
        if (!this.currentPhase) return 'russell';

        const candidates = this.currentPhase.characteristics.dominantArchetypes;

        // Apply seasonal weighting
        if (this.currentSeason) {
            const weights = this.currentSeason.influence.archetypeWeights;
            const weightedCandidates = candidates.flatMap(archetype => {
                const weight = weights[archetype] || 1.0;
                return Array(Math.floor(weight * 2)).fill(archetype);
            });
            return weightedCandidates[Math.floor(Math.random() * weightedCandidates.length)];
        }

        return candidates[Math.floor(Math.random() * candidates.length)];
    }

    // Public interface
    public getCurrentPhase(): TimePhase | null {
        return this.currentPhase;
    }

    public getCurrentSeason(): SeasonalInfluence | null {
        return this.currentSeason;
    }

    public getCurrentLunarPhase(): LunarPhase | null {
        return this.currentLunarPhase;
    }

    public isInstallationActive(): boolean {
        return this.isInstallationMode;
    }

    public getInstallationProgress(): number {
        if (!this.isInstallationMode) return 0;
        const elapsed = (Date.now() - this.installationStartTime) / 1000 / 60;
        return Math.min(elapsed / this.installationDuration, 1.0);
    }

    public setEvolutionEnabled(enabled: boolean) {
        this.evolutionEnabled = enabled;
    }

    public isEvolutionEnabled(): boolean {
        return this.evolutionEnabled;
    }

    // Event callbacks
    public onPhaseChange(callback: (phase: TimePhase) => void) {
        this.onPhaseChangeCallback = callback;
    }

    public onSeasonChange(callback: (season: SeasonalInfluence) => void) {
        this.onSeasonChangeCallback = callback;
    }

    public onEvolutionUpdate(callback: (evolution: any) => void) {
        this.onEvolutionUpdateCallback = callback;
    }

    // Manual triggers for testing
    public forcePhase(phaseName: string) {
        const phase = this.timePhases.find(p => p.name === phaseName);
        if (phase) {
            this.currentPhase = phase;
            if (this.onPhaseChangeCallback) {
                this.onPhaseChangeCallback(phase);
            }
        }
    }

    public forceSeason(seasonName: string) {
        const season = this.seasonalInfluences.find(s => s.season === seasonName);
        if (season) {
            this.currentSeason = season;
            if (this.onSeasonChangeCallback) {
                this.onSeasonChangeCallback(season);
            }
        }
    }

    public getTimeBasedLayerSettings(): { [layer: string]: number } {
        if (!this.currentPhase) return {};

        let settings = { ...this.currentPhase.characteristics.layerIntensities };

        // Apply lunar influence
        if (this.currentLunarPhase) {
            const lunar = this.currentLunarPhase.influence;
            settings.emergent = (settings.emergent || 0.5) * lunar.emergentFormActivity;
            settings.shadow = (settings.shadow || 0.5) * lunar.shadowEmphasis;
        }

        return settings;
    }

    public getTimeBasedColorPalette(): number[] {
        return this.currentPhase?.characteristics.colorPalette || [0xffffff];
    }

    public getEasterEggSensitivity(): number {
        return this.currentPhase?.characteristics.easterEggSensitivity || 1.0;
    }
}