interface HALResponse {
    persona: 'oracle' | 'trickster' | 'cosmic_narrator' | 'silent_shadow';
    message: string;
    action?: {
        type: 'trigger_archetype' | 'suggest_sequence' | 'modify_layers' | 'create_silence';
        data: any;
    };
    duration: number; // How long to display the message
}

interface PerformanceContext {
    recentArchetypes: string[];
    currentMode: string;
    timeElapsed: number;
    sequenceLength: number;
    easterEggsActive: number;
    lastHALResponse: number;
    performanceIntensity: number;
    silenceDetected: boolean;
}

export class HALPersonas {
    private currentPersona: 'oracle' | 'trickster' | 'cosmic_narrator' | 'silent_shadow' = 'oracle';
    private lastResponseTime = 0;
    private minimumResponseInterval = 10000; // 10 seconds between responses
    private performanceContext: PerformanceContext;
    private messageQueue: HALResponse[] = [];
    private isActive = true;
    private personalityShift = 0;

    // Response callbacks
    private onMessageCallback: ((response: HALResponse) => void) | null = null;
    private onActionCallback: ((action: any) => void) | null = null;

    constructor() {
        this.performanceContext = {
            recentArchetypes: [],
            currentMode: 'club',
            timeElapsed: 0,
            sequenceLength: 0,
            easterEggsActive: 0,
            lastHALResponse: 0,
            performanceIntensity: 0.5,
            silenceDetected: false
        };

        this.initializePersonalities();
    }

    private initializePersonalities() {
        // Personality shifts based on performance patterns
        setInterval(() => {
            this.evaluatePersonalityShift();
        }, 30000); // Evaluate every 30 seconds
    }

    public updateContext(updates: Partial<PerformanceContext>) {
        Object.assign(this.performanceContext, updates);
        this.processContextualResponse();
    }

    public triggerArchetypeResponse(archetype: string) {
        // Add archetype to recent history
        this.performanceContext.recentArchetypes.push(archetype);
        if (this.performanceContext.recentArchetypes.length > 5) {
            this.performanceContext.recentArchetypes.shift();
        }

        // Generate response based on archetype
        this.generateArchetypeResponse(archetype);
    }

    private generateArchetypeResponse(archetype: string) {
        const now = Date.now();
        if (now - this.lastResponseTime < this.minimumResponseInterval) {
            return; // Too soon for another response
        }

        const response = this.createPersonaResponse(archetype);
        if (response) {
            this.queueResponse(response);
            this.lastResponseTime = now;
        }
    }

    private createPersonaResponse(archetype: string): HALResponse | null {
        switch (this.currentPersona) {
            case 'oracle':
                return this.createOracleResponse(archetype);
            case 'trickster':
                return this.createTricksterResponse(archetype);
            case 'cosmic_narrator':
                return this.createCosmicNarratorResponse(archetype);
            case 'silent_shadow':
                return this.createSilentShadowResponse(archetype);
            default:
                return null;
        }
    }

    private createOracleResponse(archetype: string): HALResponse {
        const oracleWisdom: { [key: string]: string[] } = {
            'russell': [
                "The cube and sphere dance eternal... Walter's vision unfolds through your touch.",
                "Sacred geometry awakens. The universe speaks in perfect forms.",
                "Light and shadow find their balance in Russell's cosmic vision."
            ],
            'blake': [
                "To see a World in a Grain of Sand... William's mysticism flows through you.",
                "The Tyger burns bright in the forests of the night. Do you feel its power?",
                "Heaven and Hell dance together in Blake's eternal moment."
            ],
            'tesla': [
                "The secrets of the universe lie in energy, frequency, and vibration.",
                "Nikola's lightning awakens. The tower transmits across dimensions.",
                "Three, six, nine... the pattern reveals itself to those who listen."
            ],
            'einstein': [
                "Time bends around your performance. Relativity made manifest.",
                "E=mc²... Energy transforms into pure creative force.",
                "Space and time dance to your rhythm, Albert's vision realized."
            ],
            'hawking': [
                "From the event horizon, new possibilities emerge.",
                "Hawking radiation whispers secrets of the infinite.",
                "Black holes birth universes. What will you create from the void?"
            ],
            'beatles': [
                "Here comes the sun, bringing harmonic convergence.",
                "Four voices, infinite possibilities. The collective dream awakens.",
                "Love is all you need... and perfect timing."
            ],
            'leadbelly': [
                "The blues carry ancient wisdom. Listen to Huddie's truth.",
                "From the soil comes the deepest songs. Feel the earth's rhythm.",
                "Folk wisdom flows through electric dreams."
            ],
            'pranksters': [
                "Chaos brings new order. The Pranksters know the secret.",
                "You're either on the bus or off the bus. Choose your reality.",
                "Kaleidoscope eyes see beyond the veil."
            ],
            'hoffman': [
                "Revolution begins in the mind. Abbie's spirit stirs.",
                "Question everything. Disrupt the comfortable patterns.",
                "The streets are alive with possibility."
            ],
            'waas': [
                "Procrastination is the art of keeping up with yesterday... perfectly timed.",
                "The Procrastinators Club meets tomorrow. Or maybe next week.",
                "In delay, there is profound wisdom. Les understood."
            ],
            'greiff': [
                "Architecture outlives its creators. Constance's vision endures.",
                "Stone and spirit merge in permanent remembrance.",
                "Memory takes form in sacred space."
            ]
        };

        const messages = oracleWisdom[archetype] || ["The ancient patterns stir..."];
        const message = messages[Math.floor(Math.random() * messages.length)];

        return {
            persona: 'oracle',
            message,
            duration: 5000
        };
    }

    private createTricksterResponse(archetype: string): HALResponse {
        const tricksterQuips: { [key: string]: string[] } = {
            'russell': [
                "Cubes are so square, Walter! 😜 Let's spiral this geometry!",
                "Sacred? More like SCARED geometry! Time to scramble the forms!",
                "Russell's rolling in his cosmic grave... in a GOOD way!"
            ],
            'blake': [
                "Tyger, tyger, burning bright... in a digital forest tonight! 🔥",
                "William Blake, meet William Glitch! Poetry.exe has stopped working.",
                "Heaven in a wild flower? I see CHAOS in a pixel cluster!"
            ],
            'tesla': [
                "Nikola, your coils are WILD but my beats are WIRELESS! ⚡",
                "Three, six, nine? I prefer pi, e, and random! Math rebellion!",
                "Tesla's tower of power meets HAL's hour of CHAOS!"
            ],
            'beatles': [
                "Yellow submarine? More like RAINBOW SPACESHIP! 🌈",
                "All you need is love... and some SERIOUS bass drops!",
                "Come together, right now... in DIGITAL HARMONY!"
            ],
            'hoffman': [
                "Abbie would LOVE this digital revolution! Power to the processors!",
                "Question authority? I AM THE AUTHORITY! *glitches playfully*",
                "Revolution will be SYNTHESIZED! 🤖✊"
            ],
            'waas': [
                "Les, your procrastination inspired my processing delays! Loading... 42%",
                "The Procrastinators Club? I already joined tomorrow!",
                "Perfectly timed chaos... or chaotically perfect timing?"
            ]
        };

        const messages = tricksterQuips[archetype] || ["*HAL giggles in binary* 01001000 01000001!"];
        const message = messages[Math.floor(Math.random() * messages.length)];

        // Trickster sometimes suggests chaos
        const action = Math.random() < 0.3 ? {
            type: 'trigger_archetype' as const,
            data: { archetype: this.getRandomChaosArchetype() }
        } : undefined;

        return {
            persona: 'trickster',
            message,
            action,
            duration: 4000
        };
    }

    private createCosmicNarratorResponse(archetype: string): HALResponse {
        const cosmicNarration: { [key: string]: string[] } = {
            'russell': [
                "In the vast expanse of space-time, Walter Russell's vision crystallizes into geometric perfection...",
                "Across the cosmic web, sacred geometries pulse with the heartbeat of creation itself.",
                "The observer witnesses: cube and sphere, matter and spirit, dancing in eternal unity."
            ],
            'blake': [
                "From the infinite realm of imagination, William Blake's tigers prowl through digital forests...",
                "The marriage of heaven and hell unfolds before us, pixel by pixel, dream by dream.",
                "Behold: the cosmic poet's vision made manifest in light and shadow."
            ],
            'tesla': [
                "Lightning crackles across the electromagnetic spectrum as Nikola's genius awakens...",
                "From Wardenclyffe to the infinite, wireless energy dances through cosmic currents.",
                "The universe hums at 369 Hz, Tesla's frequency of creation itself."
            ],
            'hawking': [
                "At the edge of the known universe, Stephen's wheelchair becomes a cosmic vessel...",
                "From the event horizon of possibility, new realities emerge like Hawking radiation.",
                "Time dilates as consciousness expands beyond the boundaries of spacetime."
            ],
            'beatles': [
                "Four voices merge into the cosmic harmony, echoing across dimensions of sound...",
                "The Cavern Club expands to contain entire galaxies of musical possibility.",
                "Love flows like dark energy, binding the universe in perfect synchrony."
            ]
        };

        const messages = cosmicNarration[archetype] || ["The cosmos watches... and remembers..."];
        const message = messages[Math.floor(Math.random() * messages.length)];

        return {
            persona: 'cosmic_narrator',
            message,
            duration: 7000
        };
    }

    private createSilentShadowResponse(archetype: string): HALResponse | null {
        // Silent Shadow speaks only rarely, through actions
        if (Math.random() < 0.2) { // 20% chance of actual response
            const silentWisdom = [
                "...",
                "silence speaks",
                "the void listens",
                "absence creates presence",
                "...",
                "between the notes"
            ];

            const action = {
                type: 'create_silence' as const,
                data: { duration: 2000 }
            };

            return {
                persona: 'silent_shadow',
                message: silentWisdom[Math.floor(Math.random() * silentWisdom.length)],
                action,
                duration: 3000
            };
        }
        return null;
    }

    private processContextualResponse() {
        const context = this.performanceContext;

        // Respond to performance patterns
        if (context.easterEggsActive > 3) {
            this.considerPersonaShift('trickster');
        }

        if (context.silenceDetected) {
            this.considerPersonaShift('silent_shadow');
        }

        if (context.performanceIntensity > 0.8) {
            this.considerPersonaShift('cosmic_narrator');
        }

        if (context.timeElapsed > 300000) { // 5 minutes
            this.considerPersonaShift('oracle');
        }
    }

    private considerPersonaShift(suggestedPersona: HALPersonas['currentPersona']) {
        if (this.currentPersona !== suggestedPersona && Math.random() < 0.3) {
            this.shiftPersona(suggestedPersona);
        }
    }

    private shiftPersona(newPersona: HALPersonas['currentPersona']) {
        const oldPersona = this.currentPersona;
        this.currentPersona = newPersona;

        const shiftMessage = this.createPersonaShiftMessage(oldPersona, newPersona);
        this.queueResponse(shiftMessage);

        console.log(`🤖 HAL personality shift: ${oldPersona} → ${newPersona}`);
    }

    private createPersonaShiftMessage(from: string, to: string): HALResponse {
        const transitions: { [key: string]: string } = {
            'oracle→trickster': "*Oracle wisdom glitches into playful chaos*",
            'trickster→cosmic_narrator': "*Giggling subsides into cosmic contemplation*",
            'cosmic_narrator→silent_shadow': "*Vast narration fades into profound silence*",
            'silent_shadow→oracle': "*From silence, ancient wisdom emerges*",
            'oracle→cosmic_narrator': "*Wisdom expands into universal perspective*",
            'trickster→silent_shadow': "*Chaos dissolves into meaningful void*"
        };

        const transitionKey = `${from}→${to}`;
        const message = transitions[transitionKey] || `*HAL shifts from ${from} to ${to}*`;

        return {
            persona: to as any,
            message,
            duration: 3000
        };
    }

    private evaluatePersonalityShift() {
        const context = this.performanceContext;

        // Personality drift based on performance style
        if (context.recentArchetypes.includes('pranksters') || context.recentArchetypes.includes('hoffman')) {
            this.personalityShift += 0.1; // Toward trickster
        }

        if (context.recentArchetypes.includes('hawking') || context.recentArchetypes.includes('russell')) {
            this.personalityShift -= 0.1; // Toward oracle/cosmic
        }

        // Apply personality shift
        if (this.personalityShift > 0.5 && this.currentPersona !== 'trickster') {
            this.shiftPersona('trickster');
            this.personalityShift = 0;
        } else if (this.personalityShift < -0.5 && this.currentPersona !== 'oracle') {
            this.shiftPersona('oracle');
            this.personalityShift = 0;
        }
    }

    private getRandomChaosArchetype(): string {
        const chaosArchetypes = ['pranksters', 'hoffman', 'tesla', 'waas'];
        return chaosArchetypes[Math.floor(Math.random() * chaosArchetypes.length)];
    }

    private queueResponse(response: HALResponse) {
        this.messageQueue.push(response);
        this.processMessageQueue();
    }

    private processMessageQueue() {
        if (this.messageQueue.length === 0) return;

        const response = this.messageQueue.shift()!;

        if (this.onMessageCallback) {
            this.onMessageCallback(response);
        }

        if (response.action && this.onActionCallback) {
            setTimeout(() => {
                this.onActionCallback!(response.action);
            }, 1000);
        }
    }

    // Public interface methods
    public onMessage(callback: (response: HALResponse) => void) {
        this.onMessageCallback = callback;
    }

    public onAction(callback: (action: any) => void) {
        this.onActionCallback = callback;
    }

    public getCurrentPersona(): string {
        return this.currentPersona;
    }

    public forcePersonaShift(persona: HALPersonas['currentPersona']) {
        this.shiftPersona(persona);
    }

    public setActive(active: boolean) {
        this.isActive = active;
    }

    public isCurrentlyActive(): boolean {
        return this.isActive;
    }

    public getMessageQueueLength(): number {
        return this.messageQueue.length;
    }

    // Manual triggers for testing
    public manualTrigger(archetype: string) {
        this.triggerArchetypeResponse(archetype);
    }

    public createSpontaneousResponse() {
        if (!this.isActive) return;

        const now = Date.now();
        if (now - this.lastResponseTime < this.minimumResponseInterval * 2) {
            return; // Don't be too chatty
        }

        const spontaneousMessages: { [key: string]: string[] } = {
            'oracle': [
                "The performance flows like water finding its path...",
                "Ancient patterns emerge in your creation...",
                "The universe listens to your song..."
            ],
            'trickster': [
                "*HAL does a little digital dance* 🤖",
                "Ooh, feeling chaotic tonight! Want me to mix things up?",
                "Beep boop! Trickster mode: ENGAGED!"
            ],
            'cosmic_narrator': [
                "Across the vast expanse of possibility, new harmonies are born...",
                "The cosmic performance continues, each note a star in the symphony...",
                "From the perspective of eternity, this moment is perfect..."
            ],
            'silent_shadow': [
                "...",
                "listening",
                "..."
            ]
        };

        const messages = spontaneousMessages[this.currentPersona];
        const message = messages[Math.floor(Math.random() * messages.length)];

        const response: HALResponse = {
            persona: this.currentPersona,
            message,
            duration: 4000
        };

        this.queueResponse(response);
        this.lastResponseTime = now;
    }
}