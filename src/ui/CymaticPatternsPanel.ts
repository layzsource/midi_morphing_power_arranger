/**
 * Cymatic Patterns Control Panel
 *
 * Professional interface for controlling Ernst Chladni-inspired cymatic visualizations
 * - Pattern complexity and symmetry controls
 * - Frequency response tuning
 * - Real-time audio analysis display
 * - Preset management for different vibrational modes
 */

import { CymaticPatternGenerator, CymaticConfig } from '../visuals/CymaticPatterns';

export class CymaticPatternsPanel {
    private container: HTMLElement;
    private cymaticGenerator: CymaticPatternGenerator | null = null;
    private isVisible: boolean = false;

    constructor() {
        this.createInterface();
    }

    private createInterface(): void {
        this.container = document.createElement('div');
        this.container.className = 'cymatic-patterns-panel';
        this.container.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            width: min(90vw, 400px);
            max-height: calc(100vh - 100px);
            background: rgba(10, 5, 30, 0.98);
            border: 3px solid #8b5cf6;
            border-radius: 12px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            color: #a855f7;
            z-index: 9999;
            display: none;
            overflow-y: auto;
            box-sizing: border-box;
            backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4);
        `;

        this.createHeader();
        this.createFrequencyAnalysis();
        this.createPatternControls();
        this.createPresetSection();

        document.body.appendChild(this.container);
    }

    private createHeader(): void {
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(168, 85, 247, 0.3);
        `;

        const title = document.createElement('h3');
        title.textContent = '🌀 CYMATIC PATTERNS';
        title.style.cssText = `
            margin: 0;
            color: #a855f7;
            font-size: 14px;
            font-weight: 600;
            text-shadow: 0 0 8px #a855f7;
        `;

        const closeButton = document.createElement('button');
        closeButton.textContent = '✕';
        closeButton.title = 'Hide panel (use toolbar to show again)';
        closeButton.style.cssText = `
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid #ef4444;
            color: #ef4444;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
        `;

        closeButton.onclick = () => {
            this.setVisibility(false);
            window.dispatchEvent(new CustomEvent('panelClosed', {
                detail: { selector: '.cymatic-patterns-panel' }
            }));
        };

        header.appendChild(title);
        header.appendChild(closeButton);
        this.container.appendChild(header);
    }

    private createFrequencyAnalysis(): void {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 16px;
            padding: 12px;
            background: rgba(139, 92, 246, 0.1);
            border-radius: 8px;
            border: 1px solid rgba(168, 85, 247, 0.2);
        `;

        const title = document.createElement('h4');
        title.textContent = 'Frequency Analysis';
        title.style.cssText = `
            margin: 0 0 8px 0;
            font-size: 12px;
            color: #c4b5fd;
        `;

        const freqBands = document.createElement('div');
        freqBands.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 10px; color: #8b5cf6;">Low (&lt;200Hz)</span>
                <div id="low-freq-bar" style="width: 60px; height: 4px; background: #1e1b4b; border-radius: 2px; overflow: hidden;">
                    <div style="height: 100%; width: 0%; background: #3b82f6; transition: width 0.1s;"></div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 10px; color: #8b5cf6;">Mid (200-1000Hz)</span>
                <div id="mid-freq-bar" style="width: 60px; height: 4px; background: #1e1b4b; border-radius: 2px; overflow: hidden;">
                    <div style="height: 100%; width: 0%; background: #06b6d4; transition: width 0.1s;"></div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 10px; color: #8b5cf6;">High (&gt;1000Hz)</span>
                <div id="high-freq-bar" style="width: 60px; height: 4px; background: #1e1b4b; border-radius: 2px; overflow: hidden;">
                    <div style="height: 100%; width: 0%; background: #f59e0b; transition: width 0.1s;"></div>
                </div>
            </div>
        `;

        section.appendChild(title);
        section.appendChild(freqBands);
        this.container.appendChild(section);
    }

    private createPatternControls(): void {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 16px;
        `;

        const title = document.createElement('h4');
        title.textContent = 'Pattern Parameters';
        title.style.cssText = `
            margin: 0 0 12px 0;
            font-size: 12px;
            color: #c4b5fd;
        `;

        // Complexity control
        const complexityControl = this.createSliderControl('Complexity', 'complexity', 1, 8, 4);

        // Symmetry control
        const symmetryControl = this.createSliderControl('Symmetry', 'symmetry', 3, 12, 6);

        // Resonance control
        const resonanceControl = this.createSliderControl('Resonance', 'resonance', 0, 1, 0.5, 0.01);

        // Sensitivity control
        const sensitivityControl = this.createSliderControl('Sensitivity', 'sensitivity', 0.1, 3, 1, 0.1);

        section.appendChild(title);
        section.appendChild(complexityControl);
        section.appendChild(symmetryControl);
        section.appendChild(resonanceControl);
        section.appendChild(sensitivityControl);
        this.container.appendChild(section);
    }

    private createSliderControl(label: string, id: string, min: number, max: number, defaultValue: number, step: number = 1): HTMLElement {
        const control = document.createElement('div');
        control.style.cssText = `
            margin-bottom: 12px;
        `;

        const labelEl = document.createElement('label');
        labelEl.textContent = label;
        labelEl.style.cssText = `
            display: block;
            font-size: 10px;
            color: #a855f7;
            margin-bottom: 4px;
        `;

        const sliderContainer = document.createElement('div');
        sliderContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
        `;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.id = `cymatic-${id}`;
        slider.min = min.toString();
        slider.max = max.toString();
        slider.value = defaultValue.toString();
        slider.step = step.toString();
        slider.style.cssText = `
            flex: 1;
            height: 4px;
            background: #1e1b4b;
            border-radius: 2px;
            outline: none;
            -webkit-appearance: none;
        `;

        const valueDisplay = document.createElement('span');
        valueDisplay.textContent = defaultValue.toString();
        valueDisplay.style.cssText = `
            font-size: 10px;
            color: #c4b5fd;
            min-width: 30px;
            text-align: right;
        `;

        slider.oninput = () => {
            const value = parseFloat(slider.value);
            valueDisplay.textContent = value.toString();

            if (this.cymaticGenerator) {
                const config: Partial<CymaticConfig> = {};
                config[id as keyof CymaticConfig] = value;
                this.cymaticGenerator.updateConfig(config);
            }
        };

        sliderContainer.appendChild(slider);
        sliderContainer.appendChild(valueDisplay);
        control.appendChild(labelEl);
        control.appendChild(sliderContainer);

        return control;
    }

    private createPresetSection(): void {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 8px;
        `;

        const title = document.createElement('h4');
        title.textContent = 'Pattern Presets';
        title.style.cssText = `
            margin: 0 0 8px 0;
            font-size: 12px;
            color: #c4b5fd;
        `;

        const presets = [
            { name: 'Chladni Classic', config: { complexity: 4, symmetry: 6, resonance: 0.7, sensitivity: 1.2 } },
            { name: 'Sacred Geometry', config: { complexity: 8, symmetry: 12, resonance: 0.5, sensitivity: 0.8 } },
            { name: 'Wave Interference', config: { complexity: 2, symmetry: 3, resonance: 0.9, sensitivity: 1.5 } },
            { name: 'Mandala Flow', config: { complexity: 6, symmetry: 8, resonance: 0.4, sensitivity: 1.0 } }
        ];

        presets.forEach(preset => {
            const button = document.createElement('button');
            button.textContent = preset.name;
            button.style.cssText = `
                background: rgba(168, 85, 247, 0.2);
                border: 1px solid #a855f7;
                color: #a855f7;
                padding: 6px 8px;
                margin: 2px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 9px;
                font-family: inherit;
                transition: all 0.2s ease;
            `;

            button.onmouseover = () => {
                button.style.background = 'rgba(168, 85, 247, 0.4)';
            };

            button.onmouseout = () => {
                button.style.background = 'rgba(168, 85, 247, 0.2)';
            };

            button.onclick = () => {
                this.applyPreset(preset.config);
            };

            section.appendChild(button);
        });

        section.appendChild(title);
        this.container.appendChild(section);
    }

    private applyPreset(config: CymaticConfig): void {
        // Update UI sliders
        Object.entries(config).forEach(([key, value]) => {
            const slider = document.getElementById(`cymatic-${key}`) as HTMLInputElement;
            if (slider) {
                slider.value = value.toString();
                const valueDisplay = slider.nextElementSibling as HTMLSpanElement;
                if (valueDisplay) {
                    valueDisplay.textContent = value.toString();
                }
            }
        });

        // Update cymatic generator
        if (this.cymaticGenerator) {
            this.cymaticGenerator.updateConfig(config);
        }
    }

    public setCymaticGenerator(generator: CymaticPatternGenerator): void {
        this.cymaticGenerator = generator;
    }

    public updateFrequencyBars(lowFreq: number, midFreq: number, highFreq: number): void {
        const lowBar = document.querySelector('#low-freq-bar div') as HTMLElement;
        const midBar = document.querySelector('#mid-freq-bar div') as HTMLElement;
        const highBar = document.querySelector('#high-freq-bar div') as HTMLElement;

        if (lowBar) {
            const width = Math.min(lowFreq * 100, 100);
            lowBar.style.width = `${width}%`;
        }
        if (midBar) {
            const width = Math.min(midFreq * 100, 100);
            midBar.style.width = `${width}%`;
        }
        if (highBar) {
            const width = Math.min(highFreq * 100, 100);
            highBar.style.width = `${width}%`;
        }
    }

    public setVisibility(visible: boolean): void {
        this.isVisible = visible;
        this.container.style.display = visible ? 'block' : 'none';
    }

    public toggleVisibility(): boolean {
        this.setVisibility(!this.isVisible);
        return this.isVisible;
    }

    public isPanelVisible(): boolean {
        return this.isVisible;
    }
}