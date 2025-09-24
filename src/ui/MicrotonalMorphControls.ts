/**
 * 🎛️ Microtonal Morph Controls - UI Panel
 *
 * Provides on-screen controls for the new subdivision morph system
 * Integrates with your existing PanelToolbar system
 */

export class MicrotonalMorphControls {
    private container: HTMLElement;
    private panel: HTMLElement;
    private isVisible: boolean = false;
    private morphIntegration: any; // Will be injected

    // Current state
    private currentLevel: number = 0;
    private currentMode: string = '6-PANEL';
    private currentProgress: number = 0;

    constructor(container: HTMLElement, skyboxLayer?: any) {
        this.container = container;
        this.morphIntegration = skyboxLayer;
        this.createPanel();
    }

    private createPanel(): void {
        this.panel = document.createElement('div');
        this.panel.className = 'microtonal-morph-controls';
        this.panel.id = 'microtonal-morph-panel';
        this.panel.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            max-height: 80vh;
            overflow-y: auto;
            width: 320px;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 65, 0.3);
            border-radius: 12px;
            padding: 20px;
            color: #00ff41;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            z-index: 1000;
            display: none;
            box-shadow: 0 8px 32px rgba(0, 255, 65, 0.2);
        `;

        // Title bar
        const titleBar = document.createElement('div');
        titleBar.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(0, 255, 65, 0.2);
        `;

        const title = document.createElement('h3');
        title.textContent = '🎼 Microtonal Morph Controls';
        title.style.cssText = `
            margin: 0;
            color: #00ff41;
            font-size: 14px;
            font-weight: bold;
        `;

        const closeBtn = document.createElement('button');
        closeBtn.textContent = '×';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: #00ff41;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
        `;
        closeBtn.onclick = () => this.hide();

        titleBar.appendChild(title);
        titleBar.appendChild(closeBtn);

        // Mode selection
        const modeSection = this.createModeSection();

        // Subdivision level control
        const levelSection = this.createLevelSection();

        // Progress control
        const progressSection = this.createProgressSection();

        // Musical controls
        const musicalSection = this.createMusicalSection();

        // Frequency display section (NEW - real Hz values)
        const frequencySection = this.createFrequencySection();

        // Reset button section
        const resetSection = this.createResetSection();

        // Status display
        const statusSection = this.createStatusSection();

        this.panel.appendChild(titleBar);
        this.panel.appendChild(modeSection);
        this.panel.appendChild(levelSection);
        this.panel.appendChild(progressSection);
        this.panel.appendChild(musicalSection);
        this.panel.appendChild(frequencySection);
        this.panel.appendChild(resetSection);
        this.panel.appendChild(statusSection);

        this.container.appendChild(this.panel);
    }

    private createModeSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.marginBottom = '15px';

        const label = document.createElement('label');
        label.textContent = '🎯 Dewey Mode:';
        label.style.cssText = `
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        `;

        const select = document.createElement('select');
        select.style.cssText = `
            width: 100%;
            background: rgba(0, 255, 65, 0.1);
            border: 1px solid rgba(0, 255, 65, 0.3);
            color: #00ff41;
            padding: 8px;
            border-radius: 6px;
            font-family: inherit;
            font-size: 12px;
        `;

        const modes = [
            { value: '6-PANEL', label: '6-PANEL (Ancient Greek Modes)' },
            { value: '12-TONE', label: '12-TONE (Chromatic)' },
            { value: '24-TET', label: '24-TET (Quarter-tones)' },
            { value: 'HYPERMICRO', label: 'HYPERMICRO (393,216 faces)' }
        ];

        modes.forEach(mode => {
            const option = document.createElement('option');
            option.value = mode.value;
            option.textContent = mode.label;
            select.appendChild(option);
        });

        select.onchange = () => {
            this.currentMode = select.value;
            this.updateMorphMode();
        };

        section.appendChild(label);
        section.appendChild(select);
        return section;
    }

    private createLevelSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.marginBottom = '15px';

        const label = document.createElement('label');
        label.textContent = '🌌 Subdivision Level (0-8):';
        label.style.cssText = `
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        `;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0';
        slider.max = '8';
        slider.step = '0.1';
        slider.value = '0';
        slider.style.cssText = `
            width: 100%;
            margin-bottom: 8px;
        `;

        const display = document.createElement('div');
        display.style.cssText = `
            font-size: 11px;
            color: rgba(0, 255, 65, 0.7);
        `;
        this.updateLevelDisplay(display, 0);

        slider.oninput = () => {
            const level = parseFloat(slider.value);
            this.currentLevel = level;
            this.updateLevelDisplay(display, level);
            this.updateMorphLevel();
        };

        section.appendChild(label);
        section.appendChild(slider);
        section.appendChild(display);
        return section;
    }

    private createProgressSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.marginBottom = '15px';

        const label = document.createElement('label');
        label.textContent = '📊 Morph Progress:';
        label.style.cssText = `
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        `;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0';
        slider.max = '1';
        slider.step = '0.01';
        slider.value = '0';
        slider.style.cssText = `
            width: 100%;
            margin-bottom: 8px;
        `;

        const display = document.createElement('div');
        display.style.cssText = `
            font-size: 11px;
            color: rgba(0, 255, 65, 0.7);
        `;
        display.textContent = 'Progress: 0% (Pure cube)';

        slider.oninput = () => {
            const progress = parseFloat(slider.value);
            this.currentProgress = progress;
            display.textContent = `Progress: ${(progress * 100).toFixed(1)}% ${progress === 0 ? '(Pure cube)' : progress === 1 ? '(Perfect sphere)' : '(Morphing)'}`;
            this.updateMorphProgress();
        };

        section.appendChild(label);
        section.appendChild(slider);
        section.appendChild(display);
        return section;
    }

    private createMusicalSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.marginBottom = '15px';

        const label = document.createElement('label');
        label.textContent = '🎵 Musical Control:';
        label.style.cssText = `
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        `;

        const buttonRow = document.createElement('div');
        buttonRow.style.cssText = `
            display: flex;
            gap: 8px;
            margin-bottom: 8px;
        `;

        const presets = [
            { name: 'C', cents: 0 },
            { name: 'C#', cents: 100 },
            { name: 'D', cents: 200 },
            { name: 'D#', cents: 300 },
            { name: 'E', cents: 400 },
            { name: 'F', cents: 500 }
        ];

        presets.forEach(preset => {
            const btn = document.createElement('button');
            btn.textContent = preset.name;
            btn.style.cssText = `
                flex: 1;
                background: rgba(0, 255, 65, 0.1);
                border: 1px solid rgba(0, 255, 65, 0.3);
                color: #00ff41;
                padding: 6px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 10px;
            `;
            btn.onclick = () => this.morphToMusicalInterval(preset.cents);
            buttonRow.appendChild(btn);
        });

        const centsInput = document.createElement('input');
        centsInput.type = 'number';
        centsInput.placeholder = 'Custom cents (0-1200)';
        centsInput.style.cssText = `
            width: 100%;
            background: rgba(0, 255, 65, 0.1);
            border: 1px solid rgba(0, 255, 65, 0.3);
            color: #00ff41;
            padding: 8px;
            border-radius: 6px;
            font-family: inherit;
            font-size: 12px;
        `;
        centsInput.onchange = () => {
            const cents = parseFloat(centsInput.value) || 0;
            this.morphToMusicalInterval(cents);
        };

        section.appendChild(label);
        section.appendChild(buttonRow);
        section.appendChild(centsInput);
        return section;
    }

    private createFrequencySection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 15px;
            padding: 12px;
            background: rgba(0, 100, 255, 0.1);
            border: 1px solid rgba(0, 100, 255, 0.3);
            border-radius: 6px;
        `;

        const label = document.createElement('label');
        label.textContent = '🎵 Real Frequency Data:';
        label.style.cssText = `
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #0099ff;
        `;

        const display = document.createElement('div');
        display.id = 'frequency-data-display';
        display.style.cssText = `
            font-size: 11px;
            color: rgba(0, 153, 255, 0.9);
            background: rgba(0, 0, 0, 0.3);
            padding: 8px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            line-height: 1.4;
            white-space: pre-line;
        `;

        this.updateFrequencyDisplay(display);

        section.appendChild(label);
        section.appendChild(display);
        return section;
    }

    private createResetSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 15px;
            padding: 12px;
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid rgba(255, 0, 0, 0.3);
            border-radius: 6px;
        `;

        const label = document.createElement('label');
        label.textContent = '🔄 Reset Controls:';
        label.style.cssText = `
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #ff4444;
        `;

        const resetBtn = document.createElement('button');
        resetBtn.textContent = 'RESET TO ORIGINAL CUBE';
        resetBtn.style.cssText = `
            width: 100%;
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid rgba(255, 0, 0, 0.5);
            color: #ff6666;
            padding: 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            font-family: inherit;
            font-weight: bold;
            transition: all 0.2s ease;
        `;

        resetBtn.onmouseover = () => {
            resetBtn.style.background = 'rgba(255, 0, 0, 0.3)';
            resetBtn.style.color = '#ff8888';
        };

        resetBtn.onmouseout = () => {
            resetBtn.style.background = 'rgba(255, 0, 0, 0.2)';
            resetBtn.style.color = '#ff6666';
        };

        resetBtn.onclick = () => this.resetToOriginal();

        section.appendChild(label);
        section.appendChild(resetBtn);
        return section;
    }

    private createStatusSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            background: rgba(0, 255, 65, 0.05);
            border: 1px solid rgba(0, 255, 65, 0.2);
            border-radius: 6px;
            padding: 12px;
            font-size: 10px;
            line-height: 1.4;
        `;

        const title = document.createElement('div');
        title.textContent = '📊 Current Status:';
        title.style.cssText = `
            font-weight: bold;
            margin-bottom: 8px;
        `;

        const statusDisplay = document.createElement('div');
        statusDisplay.id = 'morph-status-display';
        this.updateStatusDisplay(statusDisplay);

        section.appendChild(title);
        section.appendChild(statusDisplay);
        return section;
    }

    private updateLevelDisplay(display: HTMLElement, level: number): void {
        const faceCount = 6 * Math.pow(4, Math.floor(level));
        const tetDivisions = Math.pow(2, Math.floor(level) + 1) * 6;
        const centsPerStep = 1200 / tetDivisions;

        display.innerHTML = `
            Level: ${level.toFixed(1)}<br>
            Faces: ${faceCount.toLocaleString()}<br>
            ${tetDivisions}-TET (${centsPerStep.toFixed(3)}¢/step)
        `;
    }

    private updateStatusDisplay(display: HTMLElement): void {
        display.innerHTML = `
            Mode: ${this.currentMode}<br>
            Level: ${this.currentLevel.toFixed(2)}<br>
            Progress: ${(this.currentProgress * 100).toFixed(1)}%<br>
            State: ${this.currentProgress === 0 ? 'Pure Cube' : this.currentProgress === 1 ? 'Perfect Sphere' : 'Subdividing'}
        `;
    }

    private updateFrequencyDisplay(display: HTMLElement): void {
        if (!this.morphIntegration || !this.morphIntegration.getAllFrequencyData) {
            display.textContent = 'Waiting for frequency data...\nReal Hz calculations will appear here when morphing.';
            return;
        }

        try {
            // Get frequency data from the morph integration
            const allFreqData = this.morphIntegration.getAllFrequencyData();

            if (allFreqData.size === 0) {
                display.textContent = `Base: 440.0Hz (A4 Reference)\nMode: ${this.currentMode}\nProgress: ${(this.currentProgress * 100).toFixed(1)}%\n\nNo active frequencies - start morphing to see real Hz values!`;
                return;
            }

            let displayText = `🎼 REAL FREQUENCY CALCULATIONS:\n\n`;

            // Get system status for base frequency
            const systemStatus = this.morphIntegration.frequencyCalculator?.getSystemStatus();
            if (systemStatus) {
                displayText += `Base: ${systemStatus.baseFrequency}Hz (${systemStatus.referenceNote})\n`;
                displayText += `Range: ${systemStatus.minFrequency.toFixed(1)}Hz - ${systemStatus.maxFrequency.toFixed(1)}Hz\n\n`;
            }

            // Show current active frequencies
            displayText += `ACTIVE PANEL FREQUENCIES:\n`;
            let panelCount = 0;
            allFreqData.forEach((freqDataArray, meshId) => {
                if (freqDataArray && freqDataArray.length > 0) {
                    const freqData = freqDataArray[0];
                    panelCount++;
                    displayText += `Panel ${panelCount}: ${freqData.frequency.toFixed(3)}Hz\n`;
                    displayText += `  ↳ ${freqData.cents.toFixed(1)}¢ | ${freqData.tetSize}-TET\n`;
                    displayText += `  ↳ Ratio: ${freqData.harmonicRatio.toFixed(4)}:1\n`;
                    displayText += `  ↳ [${freqData.deweyCode}]\n\n`;
                }
            });

            if (panelCount === 0) {
                displayText += '(No active panels - morph progress = 0%)\n\n';
            }

            displayText += `Current TET System: ${this.currentMode}\n`;
            displayText += `Subdivision Level: ${this.currentLevel.toFixed(2)}\n`;
            displayText += `Morph Progress: ${(this.currentProgress * 100).toFixed(1)}%`;

            display.textContent = displayText;

        } catch (error) {
            display.textContent = `Error: ${error.message}\n\nFrequency calculations temporarily unavailable.`;
            console.error('Frequency display update error:', error);
        }
    }

    // Control methods
    private updateMorphMode(): void {
        console.log(`🎯 Switched to ${this.currentMode} mode`);
        // Update skybox cube layer Dewey mode
        if (this.morphIntegration && this.morphIntegration.setDeweyDecimalMode) {
            this.morphIntegration.setDeweyDecimalMode(this.currentMode);
        }
        this.updateFrequencyDisplay(document.getElementById('frequency-data-display')!);
    }

    private updateMorphLevel(): void {
        console.log(`🌌 Set subdivision level: ${this.currentLevel}`);
        this.updateStatusDisplay(document.getElementById('morph-status-display')!);
        this.updateFrequencyDisplay(document.getElementById('frequency-data-display')!);
    }

    private updateMorphProgress(): void {
        console.log(`📊 Set morph progress: ${(this.currentProgress * 100).toFixed(1)}%`);
        // Update skybox cube layer morph progress
        if (this.morphIntegration && this.morphIntegration.setMorphProgress) {
            this.morphIntegration.setMorphProgress(this.currentProgress);
        }
        this.updateStatusDisplay(document.getElementById('morph-status-display')!);
        this.updateFrequencyDisplay(document.getElementById('frequency-data-display')!);
    }

    private morphToMusicalInterval(cents: number): void {
        console.log(`🎵 Morphing to ${cents} cents`);
        // Convert cents to progress for current mode
        const progress = Math.min(cents / 1200, 1.0);
        this.currentProgress = progress;

        // Update UI
        const progressSlider = this.panel.querySelector('input[type="range"]:nth-of-type(2)') as HTMLInputElement;
        if (progressSlider) {
            progressSlider.value = progress.toString();
        }

        this.updateMorphProgress();
        this.updateFrequencyDisplay(document.getElementById('frequency-data-display')!);
    }

    private resetToOriginal(): void {
        console.log('🔄 Resetting to original cube state');

        // Reset all internal state
        this.currentLevel = 0;
        this.currentMode = '6-PANEL';
        this.currentProgress = 0;

        // Reset UI controls
        const modeSelect = this.panel.querySelector('select') as HTMLSelectElement;
        if (modeSelect) {
            modeSelect.value = '6-PANEL';
        }

        const levelSlider = this.panel.querySelector('input[type="range"]') as HTMLInputElement;
        if (levelSlider) {
            levelSlider.value = '0';
        }

        const progressSlider = this.panel.querySelector('input[type="range"]:nth-of-type(2)') as HTMLInputElement;
        if (progressSlider) {
            progressSlider.value = '0';
        }

        // Update displays
        const levelDisplay = levelSlider?.nextElementSibling as HTMLElement;
        if (levelDisplay) {
            this.updateLevelDisplay(levelDisplay, 0);
        }

        const progressDisplay = progressSlider?.nextElementSibling as HTMLElement;
        if (progressDisplay) {
            progressDisplay.textContent = 'Progress: 0% (Pure cube)';
        }

        // Reset the actual geometry
        if (this.morphIntegration && this.morphIntegration.setMorphProgress) {
            this.morphIntegration.setMorphProgress(0);
        }

        if (this.morphIntegration && this.morphIntegration.setDeweyDecimalMode) {
            this.morphIntegration.setDeweyDecimalMode('6-PANEL');
        }

        this.updateStatusDisplay(document.getElementById('morph-status-display')!);

        console.log('🔄 Reset complete - back to original 6-face cube');
    }

    // Public interface
    public show(): void {
        this.isVisible = true;
        this.panel.style.display = 'block';
        console.log('🎛️ Microtonal Morph Controls shown');
    }

    public hide(): void {
        this.isVisible = false;
        this.panel.style.display = 'none';
        console.log('🎛️ Microtonal Morph Controls hidden');
    }

    public toggle(): void {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    public get visible(): boolean {
        return this.isVisible;
    }

    public setMorphIntegration(morphIntegration: any): void {
        this.morphIntegration = morphIntegration;
        console.log('🔧 Morph integration connected');
    }

    public getCurrentSettings() {
        return {
            mode: this.currentMode,
            level: this.currentLevel,
            progress: this.currentProgress
        };
    }
}

/**
 * 🚀 Factory function for easy integration
 */
export function createMicrotonalMorphControls(container: HTMLElement): MicrotonalMorphControls {
    console.log('🎛️ Creating Microtonal Morph Controls UI...');
    return new MicrotonalMorphControls(container);
}