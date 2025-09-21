/**
 * Acid Reign VJ Interface
 *
 * Performance-focused interface that transforms the shadow microfiche system
 * into a live VJ tool with MIDI CC controls, portal warping, and real-time
 * signal-to-form manipulation for live performances.
 *
 * This interface treats shadow data as "sprite cartridges" that can be
 * manipulated in real-time for visual performances.
 */

import { ShadowMicroficheInterface, MicroficheControls } from '../ui/ShadowMicroficheInterface';

export interface VJPerformanceState {
    portalWarp: number;           // 0-1: Camera position/angle warping
    timeWarp: number;            // 0-1: Temporal playback speed
    shadowIntensity: number;     // 0-1: Shadow visibility multiplier
    ringMask: boolean[];         // 6 booleans for ring visibility
    cartridgeIndex: number;      // Current sprite cartridge (0-9)
    effectsChain: VJEffect[];    // Active visual effects
    beatSync: boolean;           // Sync to audio beats
    freezeFrame: boolean;        // Freeze current shadow state
}

export interface VJEffect {
    type: 'blur' | 'invert' | 'chromatic' | 'echo' | 'strobe' | 'kaleidoscope';
    intensity: number;           // 0-1
    parameter1?: number;         // Effect-specific param
    parameter2?: number;         // Effect-specific param
    active: boolean;
}

export interface MIDIMapping {
    ccNumber: number;
    parameter: keyof VJPerformanceState | string;
    min: number;
    max: number;
    curve?: 'linear' | 'exponential' | 'logarithmic';
}

export class AcidReignVJInterface {
    private container: HTMLElement;
    private engine: any;
    private microficheInterface: ShadowMicroficheInterface;
    private performanceState: VJPerformanceState;
    private midiMappings: Map<number, MIDIMapping> = new Map();

    // UI Elements
    private vjControlPanel: HTMLElement;
    private portalWarpControl: HTMLElement;
    private cartridgeSelector: HTMLElement;
    private effectsRack: HTMLElement;
    private ringMaskControls: HTMLElement;
    private performanceDisplay: HTMLElement;

    // Performance state
    private cartridgeData: Map<number, any[]> = new Map(); // Stored shadow data
    private beatDetector: BeatDetector;
    private lastBeatTime = 0;
    private isPerformanceMode = false;

    constructor(container: HTMLElement, engine: any, microficheInterface: ShadowMicroficheInterface) {
        this.container = container;
        this.engine = engine;
        this.microficheInterface = microficheInterface;

        this.performanceState = {
            portalWarp: 0.5,
            timeWarp: 1.0,
            shadowIntensity: 1.0,
            ringMask: [true, true, true, true, true, true], // All rings active
            cartridgeIndex: 0,
            effectsChain: [],
            beatSync: false,
            freezeFrame: false
        };

        this.beatDetector = new BeatDetector();
        this.initializeDefaultMIDIMappings();
        this.createVJInterface();
        this.startPerformanceLoop();
    }

    private initializeDefaultMIDIMappings() {
        // Standard Acid Reign MIDI CC mappings for VJ performance
        this.midiMappings.set(1, { ccNumber: 1, parameter: 'portalWarp', min: 0, max: 1, curve: 'exponential' });
        this.midiMappings.set(2, { ccNumber: 2, parameter: 'timeWarp', min: 0.1, max: 3.0, curve: 'logarithmic' });
        this.midiMappings.set(3, { ccNumber: 3, parameter: 'shadowIntensity', min: 0, max: 2.0 });
        this.midiMappings.set(7, { ccNumber: 7, parameter: 'cartridgeIndex', min: 0, max: 9 });

        // Ring mask controls (CC 16-21)
        for (let i = 0; i < 6; i++) {
            this.midiMappings.set(16 + i, {
                ccNumber: 16 + i,
                parameter: `ringMask_${i}`,
                min: 0,
                max: 1
            });
        }

        // Effects controls (CC 80-87)
        const effectTypes = ['blur', 'invert', 'chromatic', 'echo', 'strobe', 'kaleidoscope'];
        effectTypes.forEach((effect, index) => {
            this.midiMappings.set(80 + index, {
                ccNumber: 80 + index,
                parameter: `effect_${effect}`,
                min: 0,
                max: 1
            });
        });
    }

    private createVJInterface() {
        // Create VJ control panel
        const vjContainer = document.createElement('div');
        vjContainer.className = 'acid-reign-vj-interface';
        vjContainer.style.cssText = `
            position: absolute;
            top: 20px;
            left: 20px;
            width: 400px;
            background: linear-gradient(135deg, #0a0a0a, #1a0a1a);
            border: 2px solid #ff00ff;
            border-radius: 12px;
            padding: 20px;
            color: #ff00ff;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            z-index: 1001;
            backdrop-filter: blur(15px);
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.3);
        `;

        // VJ Interface Title with collapse button
        const titleBar = document.createElement('div');
        titleBar.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        `;

        const title = document.createElement('h2');
        title.innerHTML = '🎛️ ACID REIGN VJ PORTAL 🎛️';
        title.style.cssText = `
            margin: 0;
            color: #ff00ff;
            font-size: 16px;
            text-shadow: 0 0 10px #ff00ff;
            animation: pulse 2s infinite;
        `;

        const collapseButton = document.createElement('button');
        collapseButton.textContent = '✕';
        collapseButton.title = 'Hide panel (use toolbar to show again)';
        collapseButton.className = 'vj-button';
        collapseButton.style.cssText = `
            padding: 4px 8px;
            background: rgba(255, 100, 100, 0.2);
            border: 1px solid #ff6464;
            color: #ff6464;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
        `;

        titleBar.appendChild(title);
        titleBar.appendChild(collapseButton);
        vjContainer.appendChild(titleBar);

        // Content wrapper
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'vj-content';

        // Portal Warp Control
        this.portalWarpControl = this.createPortalWarpControl();
        contentWrapper.appendChild(this.portalWarpControl);

        // Cartridge Selector
        this.cartridgeSelector = this.createCartridgeSelector();
        contentWrapper.appendChild(this.cartridgeSelector);

        // Ring Mask Controls
        this.ringMaskControls = this.createRingMaskControls();
        contentWrapper.appendChild(this.ringMaskControls);

        // Effects Rack
        this.effectsRack = this.createEffectsRack();
        contentWrapper.appendChild(this.effectsRack);

        // Performance Display
        this.performanceDisplay = this.createPerformanceDisplay();
        contentWrapper.appendChild(this.performanceDisplay);

        vjContainer.appendChild(contentWrapper);

        // Add close functionality - hide entire panel
        collapseButton.onclick = () => {
            vjContainer.style.display = 'none';

            // Trigger a global event so the toolbar can update
            window.dispatchEvent(new CustomEvent('panelClosed', {
                detail: { selector: '.acid-reign-vj-interface' }
            }));
        };

        // Add CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.8; transform: scale(1.05); }
            }
            @keyframes acidGlow {
                0%, 100% { box-shadow: 0 0 5px #ff00ff; }
                50% { box-shadow: 0 0 20px #ff00ff, 0 0 30px #ff00ff; }
            }
            .vj-button {
                transition: all 0.2s ease;
                cursor: pointer;
            }
            .vj-button:hover {
                transform: scale(1.1);
                box-shadow: 0 0 15px #ff00ff;
            }
            .vj-button.active {
                animation: acidGlow 1s infinite;
            }
        `;
        document.head.appendChild(style);

        this.container.appendChild(vjContainer);
    }

    private createPortalWarpControl(): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin-bottom: 15px; padding: 10px; border: 1px solid rgba(255, 0, 255, 0.3); border-radius: 6px;';

        const label = document.createElement('div');
        label.innerHTML = '🌀 PORTAL WARP DRIVE 🌀';
        label.style.cssText = 'color: #ffff00; font-weight: bold; margin-bottom: 8px; text-align: center;';

        const warpSlider = document.createElement('input');
        warpSlider.type = 'range';
        warpSlider.min = '0';
        warpSlider.max = '100';
        warpSlider.value = '50';
        warpSlider.style.cssText = `
            width: 100%;
            height: 8px;
            background: linear-gradient(90deg, #ff0080, #8000ff, #0080ff);
            border-radius: 4px;
            margin-bottom: 5px;
        `;

        const warpValue = document.createElement('div');
        warpValue.textContent = 'WARP: 50%';
        warpValue.style.cssText = 'text-align: center; color: #00ffff; font-weight: bold;';

        warpSlider.oninput = () => {
            const value = parseInt(warpSlider.value) / 100;
            this.performanceState.portalWarp = value;
            warpValue.textContent = `WARP: ${Math.round(value * 100)}%`;
            this.applyPortalWarp(value);
        };

        container.appendChild(label);
        container.appendChild(warpSlider);
        container.appendChild(warpValue);

        return container;
    }

    private createCartridgeSelector(): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin-bottom: 15px; padding: 10px; border: 1px solid rgba(255, 0, 255, 0.3); border-radius: 6px;';

        const label = document.createElement('div');
        label.innerHTML = '💿 SPRITE CARTRIDGE DECK 💿';
        label.style.cssText = 'color: #ffff00; font-weight: bold; margin-bottom: 8px; text-align: center;';

        const cartridgeGrid = document.createElement('div');
        cartridgeGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 5px;
            margin-bottom: 10px;
        `;

        // Create 10 cartridge slots (0-9)
        for (let i = 0; i < 10; i++) {
            const cartridge = document.createElement('button');
            cartridge.textContent = i.toString();
            cartridge.className = 'vj-button';
            cartridge.style.cssText = `
                padding: 8px;
                background: ${i === 0 ? 'rgba(255, 0, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
                border: 1px solid #ff00ff;
                color: #ff00ff;
                border-radius: 4px;
                font-weight: bold;
            `;

            cartridge.onclick = () => {
                this.selectCartridge(i);
                this.updateCartridgeDisplay();
            };

            cartridgeGrid.appendChild(cartridge);
        }

        const actions = document.createElement('div');
        actions.style.cssText = 'display: flex; gap: 5px;';

        const recordButton = document.createElement('button');
        recordButton.innerHTML = '🔴 REC';
        recordButton.className = 'vj-button';
        recordButton.style.cssText = `
            flex: 1;
            padding: 6px;
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #ff0000;
            border-radius: 4px;
        `;
        recordButton.onclick = () => this.recordCurrentShadowState();

        const playButton = document.createElement('button');
        playButton.innerHTML = '▶️ PLAY';
        playButton.className = 'vj-button';
        playButton.style.cssText = `
            flex: 1;
            padding: 6px;
            background: rgba(0, 255, 0, 0.2);
            border: 1px solid #00ff00;
            color: #00ff00;
            border-radius: 4px;
        `;
        playButton.onclick = () => this.playCartridge();

        const clearButton = document.createElement('button');
        clearButton.innerHTML = '🗑️ CLR';
        clearButton.className = 'vj-button';
        clearButton.style.cssText = `
            flex: 1;
            padding: 6px;
            background: rgba(255, 255, 0, 0.2);
            border: 1px solid #ffff00;
            color: #ffff00;
            border-radius: 4px;
        `;
        clearButton.onclick = () => this.clearCartridge();

        actions.appendChild(recordButton);
        actions.appendChild(playButton);
        actions.appendChild(clearButton);

        container.appendChild(label);
        container.appendChild(cartridgeGrid);
        container.appendChild(actions);

        return container;
    }

    private createRingMaskControls(): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin-bottom: 15px; padding: 10px; border: 1px solid rgba(255, 0, 255, 0.3); border-radius: 6px;';

        const label = document.createElement('div');
        label.innerHTML = '🟫 RING MASK MATRIX 🟫';
        label.style.cssText = 'color: #ffff00; font-weight: bold; margin-bottom: 8px; text-align: center;';

        const ringGrid = document.createElement('div');
        ringGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 5px;
        `;

        const ringNames = ['FRONT', 'BACK', 'RIGHT', 'LEFT', 'TOP', 'BTM'];
        ringNames.forEach((name, index) => {
            const ringButton = document.createElement('button');
            ringButton.textContent = name;
            ringButton.className = 'vj-button';
            ringButton.style.cssText = `
                padding: 6px;
                background: ${this.performanceState.ringMask[index] ? 'rgba(0, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
                border: 1px solid #00ffff;
                color: #00ffff;
                border-radius: 4px;
                font-size: 9px;
            `;

            ringButton.onclick = () => {
                this.performanceState.ringMask[index] = !this.performanceState.ringMask[index];
                this.updateRingMaskDisplay();
                this.applyRingMask();
            };

            ringGrid.appendChild(ringButton);
        });

        container.appendChild(label);
        container.appendChild(ringGrid);

        return container;
    }

    private createEffectsRack(): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin-bottom: 15px; padding: 10px; border: 1px solid rgba(255, 0, 255, 0.3); border-radius: 6px;';

        const label = document.createElement('div');
        label.innerHTML = '🎚️ ACID EFFECTS RACK 🎚️';
        label.style.cssText = 'color: #ffff00; font-weight: bold; margin-bottom: 8px; text-align: center;';

        const effectsGrid = document.createElement('div');
        effectsGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 5px;
        `;

        const effects = ['BLUR', 'INVERT', 'CHROME', 'ECHO', 'STROBE', 'KALEIDO'];
        effects.forEach((effect, index) => {
            const effectButton = document.createElement('button');
            effectButton.textContent = effect;
            effectButton.className = 'vj-button';
            effectButton.style.cssText = `
                padding: 6px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid #ff8000;
                color: #ff8000;
                border-radius: 4px;
                font-size: 9px;
            `;

            effectButton.onclick = () => {
                this.toggleEffect(effect.toLowerCase());
                this.updateEffectsDisplay();
            };

            effectsGrid.appendChild(effectButton);
        });

        container.appendChild(label);
        container.appendChild(effectsGrid);

        return container;
    }

    private createPerformanceDisplay(): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'padding: 10px; border: 1px solid rgba(255, 0, 255, 0.3); border-radius: 6px;';

        const label = document.createElement('div');
        label.innerHTML = '📊 PERFORMANCE STATUS 📊';
        label.style.cssText = 'color: #ffff00; font-weight: bold; margin-bottom: 8px; text-align: center;';

        const statusDisplay = document.createElement('div');
        statusDisplay.id = 'vj-status-display';
        statusDisplay.style.cssText = `
            font-size: 10px;
            line-height: 1.4;
            color: #00ffff;
            height: 80px;
            overflow-y: auto;
        `;

        container.appendChild(label);
        container.appendChild(statusDisplay);

        return container;
    }

    private startPerformanceLoop() {
        setInterval(() => {
            this.updatePerformanceStatus();

            if (this.performanceState.beatSync) {
                this.detectBeats();
            }

            this.applyTimeWarp();
        }, 50); // 20 FPS update rate
    }

    private applyPortalWarp(warpValue: number) {
        // Transform the viewing angle based on warp
        const baseAngle = this.microficheInterface.getCurrentControls().viewAngle;
        const warpedAngle = baseAngle + (warpValue - 0.5) * Math.PI; // ±90 degree warp

        this.microficheInterface.setViewAngle(warpedAngle * 180 / Math.PI);

        // Apply camera effects to engine if available
        if (this.engine.setPortalWarp) {
            this.engine.setPortalWarp(warpValue);
        }
    }

    private selectCartridge(index: number) {
        this.performanceState.cartridgeIndex = index;
    }

    private recordCurrentShadowState() {
        const shadowData = this.engine.readShadowDataAtAngle(
            this.microficheInterface.getCurrentControls().viewAngle
        );
        this.cartridgeData.set(this.performanceState.cartridgeIndex, [...shadowData]);
        this.updatePerformanceStatus();
    }

    private playCartridge() {
        const data = this.cartridgeData.get(this.performanceState.cartridgeIndex);
        if (data) {
            // Apply stored shadow data to visualization
            this.engine.clearShadowData();
            // Note: In a full implementation, we'd replay the stored sprite data
            this.updatePerformanceStatus();
        }
    }

    private clearCartridge() {
        this.cartridgeData.delete(this.performanceState.cartridgeIndex);
        this.updatePerformanceStatus();
    }

    private toggleEffect(effectType: string) {
        const existingEffect = this.performanceState.effectsChain.find(e => e.type === effectType);
        if (existingEffect) {
            existingEffect.active = !existingEffect.active;
        } else {
            this.performanceState.effectsChain.push({
                type: effectType as any,
                intensity: 0.5,
                active: true
            });
        }
    }

    private applyRingMask() {
        // Apply ring visibility mask to the visualization
        this.performanceState.ringMask.forEach((visible, index) => {
            if (!visible) {
                this.microficheInterface.setRingIndex(index);
            }
        });
    }

    private applyTimeWarp() {
        // Modify temporal playback based on timeWarp value
        if (this.performanceState.timeWarp !== 1.0) {
            // Time manipulation would affect the temporal data reading
            const controls = this.microficheInterface.getCurrentControls();
            // Apply time scaling to the time window
        }
    }

    private detectBeats() {
        // Simple beat detection - in full implementation would use audio analysis
        const now = performance.now();
        if (now - this.lastBeatTime > 500) { // 120 BPM simulation
            this.lastBeatTime = now;
            this.onBeatDetected();
        }
    }

    private onBeatDetected() {
        if (this.performanceState.beatSync) {
            // Trigger visual effects on beat
            this.performanceState.effectsChain.forEach(effect => {
                if (effect.type === 'strobe' && effect.active) {
                    effect.intensity = 1.0;
                    setTimeout(() => effect.intensity = 0.2, 100);
                }
            });
        }
    }

    private updateCartridgeDisplay() {
        const buttons = this.cartridgeSelector.querySelectorAll('button');
        buttons.forEach((button, index) => {
            if (index < 10) { // First 10 buttons are cartridge slots
                button.style.background = index === this.performanceState.cartridgeIndex ?
                    'rgba(255, 0, 255, 0.5)' : 'rgba(255, 255, 255, 0.1)';
            }
        });
    }

    private updateRingMaskDisplay() {
        const buttons = this.ringMaskControls.querySelectorAll('button');
        buttons.forEach((button, index) => {
            button.style.background = this.performanceState.ringMask[index] ?
                'rgba(0, 255, 255, 0.5)' : 'rgba(255, 255, 255, 0.1)';
        });
    }

    private updateEffectsDisplay() {
        const buttons = this.effectsRack.querySelectorAll('button');
        buttons.forEach((button, index) => {
            const effect = this.performanceState.effectsChain[index];
            if (effect && effect.active) {
                button.classList.add('active');
                button.style.background = 'rgba(255, 128, 0, 0.5)';
            } else {
                button.classList.remove('active');
                button.style.background = 'rgba(255, 255, 255, 0.1)';
            }
        });
    }

    private updatePerformanceStatus() {
        const statusEl = document.getElementById('vj-status-display');
        if (!statusEl) return;

        const shadowStats = this.engine.getShadowStatistics();
        const cartridgeCount = this.cartridgeData.size;
        const activeEffects = this.performanceState.effectsChain.filter(e => e.active).length;

        statusEl.innerHTML = `
            <div>🎛️ Portal Warp: ${Math.round(this.performanceState.portalWarp * 100)}%</div>
            <div>💿 Cartridge: ${this.performanceState.cartridgeIndex} (${cartridgeCount} loaded)</div>
            <div>🟫 Active Rings: ${this.performanceState.ringMask.filter(Boolean).length}/6</div>
            <div>🎚️ Effects: ${activeEffects} active</div>
            <div>👁️ Shadows: ${shadowStats.totalShadows || 0} total</div>
            <div>⚡ System: ${shadowStats.systemActive ? 'LIVE' : 'IDLE'}</div>
        `;
    }

    public handleMIDICC(ccNumber: number, value: number) {
        const mapping = this.midiMappings.get(ccNumber);
        if (!mapping) return;

        const normalizedValue = value / 127; // MIDI CC is 0-127
        let scaledValue: number;

        // Apply curve transformation
        switch (mapping.curve) {
            case 'exponential':
                scaledValue = Math.pow(normalizedValue, 2);
                break;
            case 'logarithmic':
                scaledValue = Math.log(normalizedValue * 9 + 1) / Math.log(10);
                break;
            default:
                scaledValue = normalizedValue;
        }

        const finalValue = mapping.min + scaledValue * (mapping.max - mapping.min);

        // Apply the value to the appropriate parameter
        if (mapping.parameter in this.performanceState) {
            (this.performanceState as any)[mapping.parameter] = finalValue;
        } else if (mapping.parameter.startsWith('ringMask_')) {
            const ringIndex = parseInt(mapping.parameter.split('_')[1]);
            this.performanceState.ringMask[ringIndex] = finalValue > 0.5;
        } else if (mapping.parameter.startsWith('effect_')) {
            const effectType = mapping.parameter.split('_')[1];
            this.toggleEffect(effectType);
        }

        this.updateAllDisplays();
    }

    private updateAllDisplays() {
        this.updateCartridgeDisplay();
        this.updateRingMaskDisplay();
        this.updateEffectsDisplay();
        this.updatePerformanceStatus();
    }

    public getPerformanceState(): VJPerformanceState {
        return { ...this.performanceState };
    }

    public setPerformanceMode(enabled: boolean) {
        this.isPerformanceMode = enabled;
        if (enabled) {
            this.vjControlPanel.style.display = 'block';
        } else {
            this.vjControlPanel.style.display = 'none';
        }
    }
}

/**
 * Simple beat detection class for synchronization
 */
class BeatDetector {
    private threshold = 0.7;
    private lastBeat = 0;
    private samples: number[] = [];

    detectBeat(audioLevel: number): boolean {
        this.samples.push(audioLevel);
        if (this.samples.length > 10) {
            this.samples.shift();
        }

        const average = this.samples.reduce((a, b) => a + b, 0) / this.samples.length;
        const now = performance.now();

        if (audioLevel > average * this.threshold && now - this.lastBeat > 300) {
            this.lastBeat = now;
            return true;
        }

        return false;
    }
}