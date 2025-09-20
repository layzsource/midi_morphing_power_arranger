interface ConversationRule {
    trigger: string;
    responds: string[];
    probability: number;
    delay: number; // milliseconds
    interactionType: 'complement' | 'conflict' | 'harmony' | 'chaos' | 'transform';
    description: string;
}

interface LayerInteraction {
    sourceLayer: string;
    targetLayer: string;
    effect: {
        property: string;
        modifier: number;
        duration: number;
    };
    condition: (sourceState: any, targetState: any) => boolean;
}

export class ArchetypeConversations {
    private conversations: ConversationRule[] = [];
    private layerInteractions: LayerInteraction[] = [];
    private recentActivations: { archetype: string; timestamp: number }[] = [];
    private activeConversations: string[] = [];
    private conversationCallbacks: ((conversation: any) => void)[] = [];
    private layerStates: { [layer: string]: any } = {};

    constructor() {
        this.initializeConversationRules();
        this.initializeLayerInteractions();
        this.startInteractionEngine();
    }

    private initializeConversationRules() {
        this.conversations = [
            // Russell-Blake: Sacred geometry meets mystical vision
            {
                trigger: 'russell',
                responds: ['blake'],
                probability: 0.7,
                delay: 2000,
                interactionType: 'complement',
                description: "Blake's mysticism illuminates Russell's sacred geometry"
            },
            {
                trigger: 'blake',
                responds: ['russell'],
                probability: 0.6,
                delay: 1500,
                interactionType: 'harmony',
                description: "Russell's geometric order grounds Blake's visions"
            },

            // Tesla-Einstein: Electricity meets relativity
            {
                trigger: 'tesla',
                responds: ['einstein'],
                probability: 0.8,
                delay: 3000,
                interactionType: 'complement',
                description: "Einstein's spacetime bends around Tesla's electrical fields"
            },
            {
                trigger: 'einstein',
                responds: ['tesla'],
                probability: 0.7,
                delay: 2500,
                interactionType: 'transform',
                description: "Tesla's inventions prove Einstein's theories"
            },

            // Hawking-Russell: Cosmic physics meets cosmic philosophy
            {
                trigger: 'hawking',
                responds: ['russell'],
                probability: 0.6,
                delay: 4000,
                interactionType: 'harmony',
                description: "Russell's cosmic principles resonate with Hawking's universe"
            },

            // Beatles-Everyone: Universal harmony
            {
                trigger: 'beatles',
                responds: ['russell', 'blake', 'tesla', 'leadbelly'],
                probability: 0.5,
                delay: 1000,
                interactionType: 'harmony',
                description: "Beatles create harmonic convergence with all archetypes"
            },

            // Pranksters-Chaos triggers
            {
                trigger: 'pranksters',
                responds: ['hoffman', 'waas', 'tesla'],
                probability: 0.9,
                delay: 500,
                interactionType: 'chaos',
                description: "Pranksters amplify chaos and rebellion"
            },

            // Hoffman-Pranksters: Revolutionary alliance
            {
                trigger: 'hoffman',
                responds: ['pranksters'],
                probability: 0.8,
                delay: 800,
                interactionType: 'chaos',
                description: "Hoffman's rebellion sparks Prankster chaos"
            },

            // Lead Belly-Beatles: Musical heritage
            {
                trigger: 'leadbelly',
                responds: ['beatles'],
                probability: 0.7,
                delay: 2000,
                interactionType: 'harmony',
                description: "Lead Belly's folk roots inspire Beatles innovation"
            },

            // Waas-Everyone: Absurd responses
            {
                trigger: 'waas',
                responds: ['russell', 'blake', 'tesla', 'einstein', 'hawking'],
                probability: 0.3,
                delay: 4200, // 42 * 100ms for absurdity
                interactionType: 'chaos',
                description: "Waas responds with perfectly timed absurdity"
            },

            // Greiff-Memorial responses: Architecture remembers
            {
                trigger: 'greiff',
                responds: ['russell', 'blake', 'leadbelly'],
                probability: 0.4,
                delay: 5000,
                interactionType: 'complement',
                description: "Greiff's architecture provides lasting foundation"
            },

            // Tesla-Pranksters: Electrical chaos
            {
                trigger: 'tesla',
                responds: ['pranksters'],
                probability: 0.6,
                delay: 1200,
                interactionType: 'chaos',
                description: "Tesla's electricity goes wild with Prankster energy"
            },

            // Blake-Hawking: Mysticism meets cosmic vastness
            {
                trigger: 'blake',
                responds: ['hawking'],
                probability: 0.5,
                delay: 3500,
                interactionType: 'transform',
                description: "Blake's infinite visions expand to Hawking's cosmic scale"
            },

            // Einstein-Blake: Science meets poetry
            {
                trigger: 'einstein',
                responds: ['blake'],
                probability: 0.4,
                delay: 2800,
                interactionType: 'transform',
                description: "Einstein's physics becomes Blake's mystical poetry"
            },

            // Antagonistic relationships
            {
                trigger: 'hoffman',
                responds: ['greiff'],
                probability: 0.3,
                delay: 1000,
                interactionType: 'conflict',
                description: "Hoffman's rebellion challenges Greiff's established order"
            },

            // Cross-layer conversations: Vessel triggers Emergent
            {
                trigger: 'russell',
                responds: ['blake', 'tesla'],
                probability: 0.6,
                delay: 1000,
                interactionType: 'transform',
                description: "Russell's vessel geometry catalyzes emergent forms"
            }
        ];
    }

    private initializeLayerInteractions() {
        this.layerInteractions = [
            // Vessel influences Emergent Form
            {
                sourceLayer: 'vessel',
                targetLayer: 'emergent',
                effect: {
                    property: 'morphingSpeed',
                    modifier: 1.5,
                    duration: 3000
                },
                condition: (source, target) => source.intensity > 0.7
            },

            // Emergent Form affects Particles
            {
                sourceLayer: 'emergent',
                targetLayer: 'particles',
                effect: {
                    property: 'emissionRate',
                    modifier: 2.0,
                    duration: 2000
                },
                condition: (source, target) => source.speed > 1.0
            },

            // Particles influence Shadow
            {
                sourceLayer: 'particles',
                targetLayer: 'shadow',
                effect: {
                    property: 'opacity',
                    modifier: 0.3, // Particles make shadows lighter
                    duration: 4000
                },
                condition: (source, target) => source.intensity > 0.8
            },

            // Shadow affects Vessel (feedback loop)
            {
                sourceLayer: 'shadow',
                targetLayer: 'vessel',
                effect: {
                    property: 'pulseRate',
                    modifier: 0.5, // Shadows slow vessel pulsing
                    duration: 5000
                },
                condition: (source, target) => source.intensity > 0.6
            },

            // Cross-influences: Vessel-Particles direct connection
            {
                sourceLayer: 'vessel',
                targetLayer: 'particles',
                effect: {
                    property: 'geometricAlignment',
                    modifier: 1.8,
                    duration: 3000
                },
                condition: (source, target) => source.intensity > 0.5 && target.intensity > 0.5
            },

            // Emergent-Shadow connection
            {
                sourceLayer: 'emergent',
                targetLayer: 'shadow',
                effect: {
                    property: 'inversionProbability',
                    modifier: 2.0,
                    duration: 2500
                },
                condition: (source, target) => source.speed > 0.8
            }
        ];
    }

    private startInteractionEngine() {
        // Process interactions every 500ms
        setInterval(() => {
            this.processLayerInteractions();
            this.cleanupOldActivations();
        }, 500);
    }

    public recordActivation(archetype: string) {
        const activation = {
            archetype,
            timestamp: Date.now()
        };

        this.recentActivations.push(activation);

        // Limit history size
        if (this.recentActivations.length > 20) {
            this.recentActivations.shift();
        }

        // Check for conversation triggers
        this.checkForConversations(archetype);
    }

    private checkForConversations(triggerArchetype: string) {
        const relevantRules = this.conversations.filter(rule => rule.trigger === triggerArchetype);

        relevantRules.forEach(rule => {
            if (Math.random() < rule.probability) {
                // Schedule responses
                rule.responds.forEach((respondingArchetype, index) => {
                    const delay = rule.delay + (index * 500); // Stagger multiple responses

                    setTimeout(() => {
                        this.executeConversationResponse(rule, respondingArchetype);
                    }, delay);
                });
            }
        });
    }

    private executeConversationResponse(rule: ConversationRule, respondingArchetype: string) {
        const conversationId = `${rule.trigger}-${respondingArchetype}-${Date.now()}`;

        if (!this.activeConversations.includes(conversationId)) {
            this.activeConversations.push(conversationId);

            const conversation = {
                id: conversationId,
                trigger: rule.trigger,
                response: respondingArchetype,
                type: rule.interactionType,
                description: rule.description,
                timestamp: Date.now()
            };

            // Notify listeners
            this.conversationCallbacks.forEach(callback => callback(conversation));

            console.log(`🗣️ Conversation: ${rule.trigger} → ${respondingArchetype} (${rule.interactionType}): ${rule.description}`);

            // Remove from active conversations after some time
            setTimeout(() => {
                const index = this.activeConversations.indexOf(conversationId);
                if (index !== -1) {
                    this.activeConversations.splice(index, 1);
                }
            }, 10000);
        }
    }

    public updateLayerState(layer: string, state: any) {
        this.layerStates[layer] = { ...state, timestamp: Date.now() };
    }

    private processLayerInteractions() {
        this.layerInteractions.forEach(interaction => {
            const sourceState = this.layerStates[interaction.sourceLayer];
            const targetState = this.layerStates[interaction.targetLayer];

            if (sourceState && targetState && interaction.condition(sourceState, targetState)) {
                this.executeLayerInteraction(interaction);
            }
        });
    }

    private executeLayerInteraction(interaction: LayerInteraction) {
        const interactionId = `${interaction.sourceLayer}-${interaction.targetLayer}-${Date.now()}`;

        const layerInteractionEvent = {
            id: interactionId,
            source: interaction.sourceLayer,
            target: interaction.targetLayer,
            effect: interaction.effect,
            timestamp: Date.now()
        };

        // Notify listeners about layer interaction
        this.conversationCallbacks.forEach(callback => {
            callback({
                type: 'layer_interaction',
                ...layerInteractionEvent
            });
        });

        console.log(`🔗 Layer Interaction: ${interaction.sourceLayer} → ${interaction.targetLayer} (${interaction.effect.property})`);
    }

    private cleanupOldActivations() {
        const now = Date.now();
        const maxAge = 30000; // 30 seconds

        this.recentActivations = this.recentActivations.filter(
            activation => now - activation.timestamp < maxAge
        );
    }

    // Pattern detection methods
    public detectConversationPatterns(): string[] {
        const patterns = [];
        const recentArchetypes = this.recentActivations
            .slice(-5)
            .map(a => a.archetype);

        // Detect harmony patterns
        if (recentArchetypes.includes('beatles') && recentArchetypes.includes('leadbelly')) {
            patterns.push('musical_heritage');
        }

        // Detect chaos patterns
        if (recentArchetypes.includes('pranksters') && recentArchetypes.includes('hoffman')) {
            patterns.push('revolutionary_chaos');
        }

        // Detect scientific convergence
        if (recentArchetypes.includes('tesla') && recentArchetypes.includes('einstein')) {
            patterns.push('scientific_convergence');
        }

        // Detect mystical synthesis
        if (recentArchetypes.includes('blake') && recentArchetypes.includes('russell')) {
            patterns.push('mystical_geometry');
        }

        // Detect cosmic contemplation
        if (recentArchetypes.includes('hawking') && recentArchetypes.includes('greiff')) {
            patterns.push('cosmic_memorial');
        }

        return patterns;
    }

    public getActiveConversationChains(): string[] {
        // Analyze recent activations for conversation chains
        const chains = [];
        const recent = this.recentActivations.slice(-10);

        for (let i = 0; i < recent.length - 1; i++) {
            const current = recent[i];
            const next = recent[i + 1];
            const timeDiff = next.timestamp - current.timestamp;

            // If activations are close in time, they might be part of a conversation
            if (timeDiff < 5000) { // 5 seconds
                const rule = this.conversations.find(r =>
                    r.trigger === current.archetype &&
                    r.responds.includes(next.archetype)
                );

                if (rule) {
                    chains.push(`${current.archetype}→${next.archetype}`);
                }
            }
        }

        return chains;
    }

    // Influence calculation
    public calculateArchetypeInfluence(archetype: string): number {
        const recentCount = this.recentActivations
            .filter(a => a.archetype === archetype)
            .length;

        const conversationCount = this.activeConversations
            .filter(c => c.includes(archetype))
            .length;

        return Math.min((recentCount * 0.3) + (conversationCount * 0.5), 2.0);
    }

    public getArchetypeAffinities(archetype: string): { [archetype: string]: number } {
        const affinities: { [archetype: string]: number } = {};

        // Calculate affinities based on conversation rules
        this.conversations
            .filter(rule => rule.trigger === archetype)
            .forEach(rule => {
                rule.responds.forEach(responder => {
                    const affinity = rule.probability * this.getTypeMultiplier(rule.interactionType);
                    affinities[responder] = (affinities[responder] || 0) + affinity;
                });
            });

        return affinities;
    }

    private getTypeMultiplier(type: ConversationRule['interactionType']): number {
        switch (type) {
            case 'harmony': return 1.5;
            case 'complement': return 1.3;
            case 'transform': return 1.1;
            case 'chaos': return 0.8;
            case 'conflict': return 0.5;
            default: return 1.0;
        }
    }

    // Public interface
    public onConversation(callback: (conversation: any) => void) {
        this.conversationCallbacks.push(callback);
    }

    public getRecentActivations(): { archetype: string; timestamp: number }[] {
        return [...this.recentActivations];
    }

    public getActiveConversations(): string[] {
        return [...this.activeConversations];
    }

    public getConversationRules(): ConversationRule[] {
        return [...this.conversations];
    }

    public getLayerInteractions(): LayerInteraction[] {
        return [...this.layerInteractions];
    }

    // Manual triggers for testing
    public forceConversation(trigger: string, responder: string) {
        const rule = this.conversations.find(r =>
            r.trigger === trigger && r.responds.includes(responder)
        );

        if (rule) {
            this.executeConversationResponse(rule, responder);
        }
    }

    public addCustomConversationRule(rule: ConversationRule) {
        this.conversations.push(rule);
    }

    public removeConversationRule(trigger: string, responder: string) {
        this.conversations = this.conversations.filter(rule =>
            !(rule.trigger === trigger && rule.responds.includes(responder))
        );
    }

    // Relationship analysis
    public getArchetypeRelationshipMap(): { [key: string]: string[] } {
        const relationships: { [key: string]: string[] } = {};

        this.conversations.forEach(rule => {
            if (!relationships[rule.trigger]) {
                relationships[rule.trigger] = [];
            }
            relationships[rule.trigger] = [...relationships[rule.trigger], ...rule.responds];
        });

        // Remove duplicates
        Object.keys(relationships).forEach(key => {
            relationships[key] = [...new Set(relationships[key])];
        });

        return relationships;
    }

    public getStrongestRelationships(): { archetype1: string; archetype2: string; strength: number }[] {
        const relationships: { archetype1: string; archetype2: string; strength: number }[] = [];

        this.conversations.forEach(rule => {
            rule.responds.forEach(responder => {
                const strength = rule.probability * this.getTypeMultiplier(rule.interactionType);
                relationships.push({
                    archetype1: rule.trigger,
                    archetype2: responder,
                    strength
                });
            });
        });

        return relationships
            .sort((a, b) => b.strength - a.strength)
            .slice(0, 10); // Top 10 strongest relationships
    }
}