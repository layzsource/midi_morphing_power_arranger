/**
 * Virtual MIDI Keyboard for Touch Devices
 *
 * Provides touch-friendly MIDI input controls for tablets and mobile devices
 * Maps to existing MIDI CC and note functionality
 */

export interface VirtualMIDIConfig {
    octaveRange: number;
    velocity: number;
    ccMappings: { [key: string]: number };
}

export class VirtualMIDIKeyboard {
    private container: HTMLElement;
    private engine: any;
    private keyboardElement: HTMLElement | null = null;
    private isVisible: boolean = false;
    private config: VirtualMIDIConfig;
    private activeNotes: Set<number> = new Set();

    constructor(container: HTMLElement, engine: any) {
        this.container = container;
        this.engine = engine;
        this.config = {
            octaveRange: 2, // 2 octaves
            velocity: 100,
            ccMappings: {
                'mod': 1,      // Modulation wheel
                'volume': 7,   // Volume
                'pan': 10,     // Pan
                'filter': 74,  // Filter cutoff
                'reverb': 91,  // Reverb
                'delay': 92    // Delay
            }
        };

        this.createKeyboard();
    }

    private createKeyboard() {
        const keyboard = document.createElement('div');
        keyboard.className = 'virtual-midi-keyboard';
        keyboard.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(20px);
            border-top: 2px solid rgba(0, 255, 255, 0.3);
            z-index: 200;
            display: none;
            padding: 12px;
            box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.8);
            user-select: none;
            -webkit-user-select: none;
            touch-action: manipulation;
        `;

        // Header with close button
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding: 0 8px;
        `;

        const title = document.createElement('h3');
        title.textContent = '🎹 VIRTUAL MIDI CONTROLLER';
        title.style.cssText = `
            margin: 0;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            text-shadow: 0 0 8px #00ffff;
        `;

        const closeButton = document.createElement('button');
        closeButton.textContent = '✕';
        closeButton.title = 'Hide panel (use toolbar to show again)';
        closeButton.style.cssText = `
            background: rgba(255, 100, 100, 0.2);
            border: 1px solid #ff6464;
            color: #ff6464;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
        `;
        closeButton.onclick = () => {
            this.setVisibility(false);

            // Trigger a global event so the toolbar can update
            window.dispatchEvent(new CustomEvent('panelClosed', {
                detail: { selector: '.virtual-midi-keyboard' }
            }));
        };

        header.appendChild(title);
        header.appendChild(closeButton);
        keyboard.appendChild(header);

        // Controls section
        const controlsSection = document.createElement('div');
        controlsSection.style.cssText = `
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
            padding: 8px;
            background: rgba(0, 20, 40, 0.5);
            border-radius: 8px;
            border: 1px solid rgba(0, 255, 255, 0.2);
        `;

        // CC Controls
        Object.entries(this.config.ccMappings).forEach(([name, ccNumber]) => {
            controlsSection.appendChild(this.createCCSlider(name, ccNumber));
        });

        keyboard.appendChild(controlsSection);

        // Piano keys section
        const pianoSection = document.createElement('div');
        pianoSection.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 8px;
        `;

        // Octave controls
        const octaveControls = document.createElement('div');
        octaveControls.style.cssText = `
            display: flex;
            justify-content: center;
            gap: 12px;
            align-items: center;
            margin-bottom: 8px;
        `;

        const octaveDown = document.createElement('button');
        octaveDown.textContent = '🔽 OCT';
        octaveDown.style.cssText = this.getButtonStyle();
        octaveDown.onclick = () => this.changeOctave(-1);

        const octaveDisplay = document.createElement('span');
        octaveDisplay.id = 'octave-display';
        octaveDisplay.textContent = 'C4';
        octaveDisplay.style.cssText = `
            color: #00ffff;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: bold;
            min-width: 30px;
            text-align: center;
        `;

        const octaveUp = document.createElement('button');
        octaveUp.textContent = '🔼 OCT';
        octaveUp.style.cssText = this.getButtonStyle();
        octaveUp.onclick = () => this.changeOctave(1);

        octaveControls.appendChild(octaveDown);
        octaveControls.appendChild(octaveDisplay);
        octaveControls.appendChild(octaveUp);

        // Piano keyboard
        const pianoKeys = document.createElement('div');
        pianoKeys.style.cssText = `
            display: flex;
            height: 80px;
            background: #333;
            border: 1px solid #666;
            border-radius: 4px;
            overflow-x: auto;
            padding: 4px;
        `;

        this.createPianoKeys(pianoKeys);

        pianoSection.appendChild(octaveControls);
        pianoSection.appendChild(pianoKeys);
        keyboard.appendChild(pianoSection);

        this.container.appendChild(keyboard);
        this.keyboardElement = keyboard;
    }

    private createCCSlider(name: string, ccNumber: number): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 60px;
        `;

        const label = document.createElement('label');
        label.textContent = name.toUpperCase();
        label.style.cssText = `
            font-size: 9px;
            color: #00aaaa;
            margin-bottom: 4px;
            font-family: 'Courier New', monospace;
        `;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0';
        slider.max = '127';
        slider.value = '64';
        slider.style.cssText = `
            writing-mode: bt-lr;
            -webkit-appearance: slider-vertical;
            width: 20px;
            height: 60px;
            background: rgba(0, 255, 255, 0.2);
            outline: none;
        `;

        const value = document.createElement('span');
        value.textContent = '64';
        value.style.cssText = `
            font-size: 8px;
            color: #00ffff;
            margin-top: 4px;
            font-family: 'Courier New', monospace;
        `;

        slider.oninput = () => {
            const val = parseInt(slider.value);
            value.textContent = val.toString();
            this.sendMIDICC(ccNumber, val);
        };

        container.appendChild(label);
        container.appendChild(slider);
        container.appendChild(value);

        return container;
    }

    private createPianoKeys(container: HTMLElement) {
        const whiteKeys = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];
        const blackKeys = ['C#', 'D#', '', 'F#', 'G#', 'A#', ''];

        for (let octave = 0; octave < this.config.octaveRange; octave++) {
            for (let i = 0; i < 7; i++) {
                const note = whiteKeys[i];
                const noteNumber = 60 + (octave * 12) + this.getNoteOffset(note); // C4 = 60

                // White key
                const whiteKey = document.createElement('button');
                whiteKey.textContent = note + (4 + octave);
                whiteKey.style.cssText = `
                    background: linear-gradient(to bottom, #f8f8f8, #e0e0e0);
                    border: 1px solid #999;
                    color: #333;
                    width: 40px;
                    height: 70px;
                    margin: 0 1px;
                    border-radius: 0 0 4px 4px;
                    font-size: 8px;
                    cursor: pointer;
                    position: relative;
                    touch-action: manipulation;
                `;

                this.addKeyEvents(whiteKey, noteNumber);
                container.appendChild(whiteKey);

                // Black key (if exists)
                if (blackKeys[i]) {
                    const blackNote = blackKeys[i];
                    const blackNoteNumber = noteNumber + 1;

                    const blackKey = document.createElement('button');
                    blackKey.textContent = blackNote + (4 + octave);
                    blackKey.style.cssText = `
                        background: linear-gradient(to bottom, #333, #111);
                        border: 1px solid #000;
                        color: #fff;
                        width: 24px;
                        height: 45px;
                        position: absolute;
                        margin-left: -12px;
                        z-index: 10;
                        border-radius: 0 0 2px 2px;
                        font-size: 7px;
                        cursor: pointer;
                        touch-action: manipulation;
                    `;

                    this.addKeyEvents(blackKey, blackNoteNumber);
                    container.appendChild(blackKey);
                }
            }
        }
    }

    private getNoteOffset(note: string): number {
        const offsets: { [key: string]: number } = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
        };
        return offsets[note] || 0;
    }

    private addKeyEvents(key: HTMLElement, noteNumber: number) {
        const pressKey = () => {
            if (!this.activeNotes.has(noteNumber)) {
                this.activeNotes.add(noteNumber);
                this.sendMIDINote(noteNumber, this.config.velocity, true);
                key.style.filter = 'brightness(0.7)';
            }
        };

        const releaseKey = () => {
            if (this.activeNotes.has(noteNumber)) {
                this.activeNotes.delete(noteNumber);
                this.sendMIDINote(noteNumber, 0, false);
                key.style.filter = 'brightness(1)';
            }
        };

        // Touch events
        key.addEventListener('touchstart', (e) => {
            e.preventDefault();
            pressKey();
        });

        key.addEventListener('touchend', (e) => {
            e.preventDefault();
            releaseKey();
        });

        // Mouse events (fallback)
        key.addEventListener('mousedown', pressKey);
        key.addEventListener('mouseup', releaseKey);
        key.addEventListener('mouseleave', releaseKey);
    }

    private changeOctave(direction: number) {
        // Implementation would shift the base octave
        const display = document.getElementById('octave-display');
        if (display) {
            const currentOctave = parseInt(display.textContent?.replace('C', '') || '4');
            const newOctave = Math.max(0, Math.min(8, currentOctave + direction));
            display.textContent = `C${newOctave}`;
        }
    }

    private sendMIDINote(note: number, velocity: number, isNoteOn: boolean) {
        // Send MIDI note through engine
        const midiData = [
            isNoteOn ? 144 : 128, // Note on/off on channel 1
            note,
            velocity
        ];
        this.engine.processMIDIMessage({ data: midiData });
    }

    private sendMIDICC(ccNumber: number, value: number) {
        // Send MIDI CC through engine
        const midiData = [176, ccNumber, value]; // CC on channel 1
        this.engine.processMIDIMessage({ data: midiData });
    }

    private getButtonStyle(): string {
        return `
            background: rgba(0, 255, 255, 0.2);
            border: 1px solid #00ffff;
            color: #00ffff;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
            font-family: 'Courier New', monospace;
            transition: all 0.2s ease;
        `;
    }

    public setVisibility(visible: boolean) {
        this.isVisible = visible;
        if (this.keyboardElement) {
            this.keyboardElement.style.display = visible ? 'block' : 'none';

            // Stop all notes when hiding
            if (!visible) {
                this.activeNotes.forEach(note => {
                    this.sendMIDINote(note, 0, false);
                });
                this.activeNotes.clear();
            }
        }
    }

    public toggleVisibility(): boolean {
        this.setVisibility(!this.isVisible);
        return this.isVisible;
    }

    public isKeyboardVisible(): boolean {
        return this.isVisible;
    }
}