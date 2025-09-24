/**
 * ParamGraph UI Integration for MMPA
 *
 * Handles UI controls for the ParamGraph parameter system
 */

import { paramGraphIntegration, MMPA_PARAM_PATHS } from '../paramgraph/ParamGraphIntegration';

export class ParamGraphUI {
    private initialized = false;
    private voiceEnabled = false;

    async initialize(): Promise<void> {
        if (this.initialized) return;

        // Wait for ParamGraph to be available
        this.waitForParamGraph().then(() => {
            this.setupUIControls();
            this.setupParameterUpdates();
            this.initialized = true;
            console.log('🎛️ ParamGraph UI initialized');
        });
    }

    private async waitForParamGraph(): Promise<void> {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (window.ParamGraph && paramGraphIntegration) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
        });
    }

    private setupUIControls(): void {
        // Viewport selection buttons
        const mainBtn = document.getElementById('viewport-main');
        const auxBtn = document.getElementById('viewport-aux');

        if (mainBtn && auxBtn) {
            mainBtn.addEventListener('click', () => {
                this.setActiveViewport('main');
                this.updateViewportButtons();
            });

            auxBtn.addEventListener('click', () => {
                this.setActiveViewport('aux');
                this.updateViewportButtons();
            });
        }

        // Parameter sliders
        const morphSlider = document.getElementById('paramgraph-morph') as HTMLInputElement;
        const rotYSlider = document.getElementById('paramgraph-rot-y') as HTMLInputElement;

        if (morphSlider) {
            morphSlider.addEventListener('input', (e) => {
                const value = parseFloat((e.target as HTMLInputElement).value);
                paramGraphIntegration.setTouchInput(MMPA_PARAM_PATHS.CUBE_SPHERE, value);
                this.updateMorphDisplay(value);
            });
        }

        if (rotYSlider) {
            rotYSlider.addEventListener('input', (e) => {
                const value = parseFloat((e.target as HTMLInputElement).value);
                const activeViewport = paramGraphIntegration.getActiveViewport();
                const path = activeViewport === 'main'
                    ? MMPA_PARAM_PATHS.MAIN_VESSEL_ROT_Y
                    : MMPA_PARAM_PATHS.AUX_VESSEL_ROT_Y;

                paramGraphIntegration.setTouchInput(path, value / 360);
                this.updateRotationDisplay(value);
            });
        }

        // Voice control toggle
        const voiceToggle = document.getElementById('voice-control-toggle');
        if (voiceToggle) {
            voiceToggle.addEventListener('click', () => {
                this.toggleVoiceControl();
            });
        }

        // Preset buttons
        const saveBtn = document.getElementById('save-preset');
        const loadBtn = document.getElementById('load-preset');

        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.savePreset();
            });
        }

        if (loadBtn) {
            loadBtn.addEventListener('click', () => {
                this.loadPreset();
            });
        }
    }

    private setupParameterUpdates(): void {
        // Listen for parameter changes and update UI
        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.CUBE_SPHERE, (value) => {
            this.updateMorphSlider(value);
            this.updateMorphDisplay(value);
        });

        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.MAIN_VESSEL_ROT_Y, (value) => {
            if (paramGraphIntegration.getActiveViewport() === 'main') {
                this.updateRotationSlider(value);
                this.updateRotationDisplay(value);
            }
        });

        paramGraphIntegration.onParameterChange(MMPA_PARAM_PATHS.AUX_VESSEL_ROT_Y, (value) => {
            if (paramGraphIntegration.getActiveViewport() === 'aux') {
                this.updateRotationSlider(value);
                this.updateRotationDisplay(value);
            }
        });
    }

    private setActiveViewport(viewport: 'main' | 'aux'): void {
        paramGraphIntegration.setActiveViewport(viewport);
        this.updateViewportButtons();

        // Update rotation slider to show current viewport's value
        const path = viewport === 'main'
            ? MMPA_PARAM_PATHS.MAIN_VESSEL_ROT_Y
            : MMPA_PARAM_PATHS.AUX_VESSEL_ROT_Y;

        const currentValue = paramGraphIntegration.getParameter(path) || 0;
        this.updateRotationSlider(currentValue);
        this.updateRotationDisplay(currentValue);

        console.log(`🎛️ Active viewport: ${viewport}`);
    }

    private updateViewportButtons(): void {
        const mainBtn = document.getElementById('viewport-main');
        const auxBtn = document.getElementById('viewport-aux');
        const activeViewport = paramGraphIntegration.getActiveViewport();

        if (mainBtn && auxBtn) {
            if (activeViewport === 'main') {
                mainBtn.classList.add('active');
                auxBtn.classList.remove('active');
                mainBtn.style.background = 'rgba(33, 150, 243, 0.2)';
                mainBtn.style.color = '#2196f3';
                mainBtn.style.borderColor = 'rgba(33, 150, 243, 0.3)';
                auxBtn.style.background = 'rgba(255, 255, 255, 0.05)';
                auxBtn.style.color = 'rgba(255,255,255,0.7)';
                auxBtn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            } else {
                auxBtn.classList.add('active');
                mainBtn.classList.remove('active');
                auxBtn.style.background = 'rgba(255, 0, 128, 0.2)';
                auxBtn.style.color = '#ff6b9d';
                auxBtn.style.borderColor = 'rgba(255, 107, 157, 0.3)';
                mainBtn.style.background = 'rgba(255, 255, 255, 0.05)';
                mainBtn.style.color = 'rgba(255,255,255,0.7)';
                mainBtn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            }
        }
    }

    private updateMorphSlider(value: number): void {
        const slider = document.getElementById('paramgraph-morph') as HTMLInputElement;
        if (slider && !document.activeElement?.id.includes('paramgraph-morph')) {
            slider.value = value.toString();
        }
    }

    private updateMorphDisplay(value: number): void {
        const display = document.getElementById('morph-value');
        if (display) {
            display.textContent = `${Math.round(value * 100)}%`;
        }
    }

    private updateRotationSlider(value: number): void {
        const slider = document.getElementById('paramgraph-rot-y') as HTMLInputElement;
        if (slider && !document.activeElement?.id.includes('paramgraph-rot-y')) {
            slider.value = value.toString();
        }
    }

    private updateRotationDisplay(value: number): void {
        const display = document.getElementById('rot-y-value');
        if (display) {
            display.textContent = `${Math.round(value)}°`;
        }
    }

    private toggleVoiceControl(): void {
        this.voiceEnabled = !this.voiceEnabled;
        const button = document.getElementById('voice-control-toggle');

        if (this.voiceEnabled) {
            if (window.ParamGraphVoice) {
                window.ParamGraphVoice.start();
            }
            if (button) {
                button.textContent = '🎤 Voice Control: ON';
                button.style.background = 'rgba(255, 255, 0, 0.2)';
                button.style.borderColor = 'rgba(255, 235, 59, 0.4)';
            }
            console.log('🎤 Voice control enabled');
        } else {
            if (window.ParamGraphVoice) {
                window.ParamGraphVoice.stop();
            }
            if (button) {
                button.textContent = '🎤 Voice Control: OFF';
                button.style.background = 'rgba(255, 255, 0, 0.1)';
                button.style.borderColor = 'rgba(255, 235, 59, 0.2)';
            }
            console.log('🎤 Voice control disabled');
        }
    }

    private savePreset(): void {
        const snapshot = paramGraphIntegration.saveSnapshot();
        localStorage.setItem('mmpa_paramgraph_preset', JSON.stringify(snapshot));
        console.log('💾 ParamGraph preset saved');

        // Visual feedback
        const button = document.getElementById('save-preset');
        if (button) {
            const originalText = button.textContent;
            button.textContent = '✅ Saved';
            setTimeout(() => {
                button.textContent = originalText;
            }, 2000);
        }
    }

    private loadPreset(): void {
        const saved = localStorage.getItem('mmpa_paramgraph_preset');
        if (saved) {
            try {
                const snapshot = JSON.parse(saved);
                paramGraphIntegration.loadSnapshot(snapshot);
                console.log('📂 ParamGraph preset loaded');

                // Visual feedback
                const button = document.getElementById('load-preset');
                if (button) {
                    const originalText = button.textContent;
                    button.textContent = '✅ Loaded';
                    setTimeout(() => {
                        button.textContent = originalText;
                    }, 2000);
                }
            } catch (error) {
                console.warn('⚠️ Failed to load preset:', error);
            }
        } else {
            console.log('No saved preset found');
        }
    }

    /**
     * Update source indicators to show which input is controlling parameters
     */
    updateSourceIndicators(): void {
        // This would update the visual indicators showing which input source
        // (MIDI, Touch, Voice, Auto) is currently controlling each parameter
        // Implementation would check ParamGraph.getOwner() for each parameter
    }
}

// Create singleton instance
export const paramGraphUI = new ParamGraphUI();