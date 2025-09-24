import { MMPAEngine } from '../mmpa-engine';

export class GlobalMorphControls {
    private container: HTMLElement;
    private engine: MMPAEngine;
    private targetShapeSelector!: HTMLSelectElement;
    private morphSlider!: HTMLInputElement;
    private morphValueDisplay!: HTMLElement;
    private clearNotesButton!: HTMLButtonElement;
    private midiReconnectButton!: HTMLButtonElement;
    private audioAnalysisToggle!: HTMLInputElement;
    private activeNotesDisplay!: HTMLElement;
    private midiStatusDisplay!: HTMLElement;
    private audioStatusDisplay!: HTMLElement;

    private currentMorphTarget: string = 'cube';
    private currentMorphAmount: number = 0;

    constructor(container: HTMLElement, engine: MMPAEngine) {
        this.container = container;
        this.engine = engine;
        this.initializeControls();
        this.setupEventListeners();
    }

    private initializeControls(): void {
        // Get all the UI elements
        this.targetShapeSelector = document.getElementById('target-shape-selector') as HTMLSelectElement;
        this.morphSlider = document.getElementById('global-morph-slider') as HTMLInputElement;
        this.morphValueDisplay = document.getElementById('morph-value-display') as HTMLElement;
        this.clearNotesButton = document.getElementById('clear-all-notes') as HTMLButtonElement;
        this.midiReconnectButton = document.getElementById('midi-reconnect') as HTMLButtonElement;
        this.audioAnalysisToggle = document.getElementById('audio-analysis-toggle') as HTMLInputElement;
        this.activeNotesDisplay = document.getElementById('active-notes-display') as HTMLElement;
        this.midiStatusDisplay = document.getElementById('midi-status-display') as HTMLElement;
        this.audioStatusDisplay = document.getElementById('audio-status-display') as HTMLElement;

        // Initialize status displays
        this.updateStatusDisplays();
    }

    private setupEventListeners(): void {
        // Target Shape Selector
        this.targetShapeSelector.addEventListener('change', (e) => {
            const target = e.target as HTMLSelectElement;
            this.currentMorphTarget = target.value;
            this.applyGlobalMorph();
            console.log(`Target shape changed to: ${this.currentMorphTarget}`);
        });

        // Morph Slider
        this.morphSlider.addEventListener('input', (e) => {
            const target = e.target as HTMLInputElement;
            this.currentMorphAmount = parseInt(target.value);
            this.morphValueDisplay.textContent = `${this.currentMorphAmount}%`;
            this.applyGlobalMorph();
        });

        // Clear Notes Button
        this.clearNotesButton.addEventListener('click', () => {
            this.clearAllNotes();
        });

        // MIDI Reconnect Button
        this.midiReconnectButton.addEventListener('click', () => {
            this.reconnectMIDI();
        });

        // Audio Analysis Toggle
        this.audioAnalysisToggle.addEventListener('change', (e) => {
            const target = e.target as HTMLInputElement;
            this.toggleAudioAnalysis(target.checked);
        });

        // Listen to engine events for status updates
        this.setupEngineEventListeners();
    }

    private setupEngineEventListeners(): void {
        // Listen for MIDI events
        this.engine.onMIDIStatusChange = (status: string) => {
            this.updateMIDIStatus(status);
        };

        // Listen for audio analysis events
        this.engine.onAudioAnalysisStatusChange = (enabled: boolean) => {
            this.updateAudioStatus(enabled);
        };

        // Listen for active notes changes
        this.engine.onActiveNotesChange = (notes: number[]) => {
            this.updateActiveNotes(notes);
        };
    }

    private applyGlobalMorph(): void {
        const morphAmount = this.currentMorphAmount / 100.0;
        const targetShape = this.currentMorphTarget;

        console.log(`Applying global morph: ${targetShape} @ ${morphAmount * 100}%`);

        // Get the skybox layer and apply morphing
        const skyboxLayer = this.engine.getSkyboxLayer();
        if (skyboxLayer && skyboxLayer.morphPanelSquareToCircle) {
            skyboxLayer.morphPanelSquareToCircle(morphAmount);
        }

        // Update engine with current morph state
        this.engine.setGlobalMorphTarget(targetShape, morphAmount);

        // Update status
        this.updateStatusMessage(`Global morph: → ${targetShape} (${this.currentMorphAmount}%)`);
    }

    private clearAllNotes(): void {
        console.log('Clearing all active notes');
        this.engine.clearAllActiveNotes();
        this.updateActiveNotes([]);
        this.updateStatusMessage('All notes cleared');
    }

    private reconnectMIDI(): void {
        console.log('Reconnecting MIDI...');
        this.updateMIDIStatus('Connecting...');

        // Trigger MIDI reconnection in engine
        this.engine.reconnectMIDI().then((success) => {
            if (success) {
                this.updateMIDIStatus('Connected');
                this.updateStatusMessage('MIDI reconnected successfully');
            } else {
                this.updateMIDIStatus('Connection failed');
                this.updateStatusMessage('MIDI reconnection failed');
            }
        }).catch(() => {
            this.updateMIDIStatus('Error');
            this.updateStatusMessage('MIDI reconnection error');
        });
    }

    private toggleAudioAnalysis(enabled: boolean): void {
        console.log(`Audio analysis ${enabled ? 'enabled' : 'disabled'}`);

        this.engine.setAudioAnalysisEnabled(enabled);
        this.updateAudioStatus(enabled);
        this.updateStatusMessage(`Audio analysis ${enabled ? 'enabled' : 'disabled'}`);
    }

    private updateActiveNotes(notes: number[]): void {
        if (notes.length === 0) {
            this.activeNotesDisplay.textContent = 'Active Notes: None';
        } else {
            const noteNames = notes.map(note => this.noteNumberToName(note)).join(', ');
            this.activeNotesDisplay.textContent = `Active Notes: ${noteNames}`;
        }
    }

    private updateMIDIStatus(status: string): void {
        this.midiStatusDisplay.textContent = `MIDI: ${status}`;

        // Update button state based on status
        if (status === 'Connected') {
            this.midiReconnectButton.style.background = 'rgba(64, 255, 64, 0.1)';
            this.midiReconnectButton.style.color = '#6bcf7f';
        } else if (status === 'Connecting...') {
            this.midiReconnectButton.style.background = 'rgba(255, 255, 64, 0.1)';
            this.midiReconnectButton.style.color = '#ffff6b';
        } else {
            this.midiReconnectButton.style.background = 'rgba(255, 64, 64, 0.1)';
            this.midiReconnectButton.style.color = '#ff6b6b';
        }
    }

    private updateAudioStatus(enabled: boolean): void {
        this.audioStatusDisplay.textContent = `Audio: ${enabled ? 'Active' : 'Disabled'}`;
        this.audioAnalysisToggle.checked = enabled;
    }

    private updateStatusDisplays(): void {
        this.updateActiveNotes([]);
        this.updateMIDIStatus('Ready');
        this.updateAudioStatus(false);
    }

    private updateStatusMessage(message: string): void {
        // Update the main status message in the MMPA interface if available
        console.log(`Status: ${message}`);

        // Also trigger visual feedback
        this.showTemporaryFeedback(message);
    }

    private showTemporaryFeedback(message: string): void {
        // Create temporary feedback element
        const feedback = document.createElement('div');
        feedback.textContent = message;
        feedback.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 255, 255, 0.1);
            color: #00ffff;
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid rgba(0, 255, 255, 0.3);
            font-size: 14px;
            font-weight: 500;
            z-index: 1000;
            backdrop-filter: blur(10px);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        document.body.appendChild(feedback);

        // Animate in
        requestAnimationFrame(() => {
            feedback.style.opacity = '1';
        });

        // Remove after 2 seconds
        setTimeout(() => {
            feedback.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(feedback);
            }, 300);
        }, 2000);
    }

    private noteNumberToName(noteNumber: number): string {
        const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
        const octave = Math.floor(noteNumber / 12) - 1;
        const noteIndex = noteNumber % 12;
        return `${noteNames[noteIndex]}${octave}`;
    }

    // Public methods for external control
    public setMorphTarget(target: string): void {
        this.currentMorphTarget = target;
        this.targetShapeSelector.value = target;
        this.applyGlobalMorph();
    }

    public setMorphAmount(amount: number): void {
        this.currentMorphAmount = Math.max(0, Math.min(100, amount));
        this.morphSlider.value = this.currentMorphAmount.toString();
        this.morphValueDisplay.textContent = `${this.currentMorphAmount}%`;
        this.applyGlobalMorph();
    }

    public getMorphTarget(): string {
        return this.currentMorphTarget;
    }

    public getMorphAmount(): number {
        return this.currentMorphAmount;
    }
}