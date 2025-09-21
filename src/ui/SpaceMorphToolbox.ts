/**
 * Space Morph Contextual Toolbox
 *
 * Provides mode-specific UI controls for Space Morph (installation mode),
 * showing only relevant analysis and visualization tools.
 */

export interface SpaceMorphTools {
    microficheReader: boolean;
    shadowAnalysis: boolean;
    spatialMapping: boolean;
    temporalWindow: boolean;
    vesselScaffolding: boolean;
    virtualMIDI: boolean;
    audioInput: boolean;
}

export class SpaceMorphToolbox {
    private container: HTMLElement;
    private engine: any;
    private microficheInterface: any;
    private virtualMIDIKeyboard: any;
    private audioInputSelector: any;
    private toolboxElement: HTMLElement | null = null;
    private isVisible: boolean = false;
    private tools: SpaceMorphTools;

    constructor(container: HTMLElement, engine: any, microficheInterface: any, virtualMIDIKeyboard?: any, audioInputSelector?: any) {
        this.container = container;
        this.engine = engine;
        this.microficheInterface = microficheInterface;
        this.virtualMIDIKeyboard = virtualMIDIKeyboard;
        this.audioInputSelector = audioInputSelector;
        this.tools = {
            microficheReader: true,
            shadowAnalysis: true,
            spatialMapping: false,
            temporalWindow: false,
            vesselScaffolding: false,
            virtualMIDI: false,
            audioInput: false
        };

        this.createToolbox();
    }

    private createToolbox() {
        const toolbox = document.createElement('div');
        toolbox.className = 'space-morph-toolbox';
        toolbox.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 30px;
            background: rgba(3, 7, 18, 0.9);
            backdrop-filter: blur(20px) saturate(120%);
            border: 1px solid rgba(0, 255, 255, 0.2);
            border-radius: 16px;
            padding: 16px;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            z-index: 90;
            min-width: 280px;
            box-shadow:
                0 1px 0 0 rgba(0, 255, 255, 0.1) inset,
                0 8px 32px 0 rgba(0, 0, 0, 0.6),
                0 32px 80px 0 rgba(0, 255, 255, 0.15);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: none;
        `;

        // Title bar
        const titleBar = document.createElement('div');
        titleBar.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0, 255, 255, 0.2);
        `;

        const title = document.createElement('h3');
        title.textContent = '🛠️ SPACE MORPH TOOLS';
        title.style.cssText = `
            margin: 0;
            color: #00ffff;
            font-size: 12px;
            font-weight: 600;
            text-shadow: 0 0 8px #00ffff;
        `;

        const collapseButton = document.createElement('button');
        collapseButton.textContent = '✕';
        collapseButton.title = 'Hide panel (use toolbar to show again)';
        collapseButton.style.cssText = `
            background: rgba(255, 100, 100, 0.2);
            border: 1px solid #ff6464;
            color: #ff6464;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
            transition: all 0.2s ease;
        `;

        titleBar.appendChild(title);
        titleBar.appendChild(collapseButton);
        toolbox.appendChild(titleBar);

        // Tools content
        const toolsContent = document.createElement('div');
        toolsContent.className = 'tools-content';

        // Tool sections
        toolsContent.appendChild(this.createToolSection('Analysis Tools', [
            {
                id: 'microfiche-reader',
                name: 'Microfiche Reader',
                icon: '🔍',
                key: 'V',
                description: 'Shadow data analysis interface',
                enabled: this.tools.microficheReader,
                action: () => this.toggleMicroficheReader()
            },
            {
                id: 'shadow-analysis',
                name: 'Shadow Analysis',
                icon: '👤',
                key: 'S',
                description: 'Real-time shadow tracking',
                enabled: this.tools.shadowAnalysis,
                action: () => this.toggleShadowAnalysis()
            }
        ]));

        toolsContent.appendChild(this.createToolSection('Spatial Tools', [
            {
                id: 'spatial-mapping',
                name: 'Spatial Mapping',
                icon: '🗺️',
                key: 'M',
                description: 'Environmental spatial analysis',
                enabled: this.tools.spatialMapping,
                action: () => this.toggleSpatialMapping()
            },
            {
                id: 'temporal-window',
                name: 'Temporal Window',
                icon: '⏰',
                key: 'T',
                description: 'Time-based data filtering',
                enabled: this.tools.temporalWindow,
                action: () => this.toggleTemporalWindow()
            }
        ]));

        toolsContent.appendChild(this.createToolSection('Structure Tools', [
            {
                id: 'vessel-scaffolding',
                name: 'Vessel Scaffolding',
                icon: '🏗️',
                key: 'B',
                description: '6-way light port structure',
                enabled: this.tools.vesselScaffolding,
                action: () => this.toggleVesselScaffolding()
            }
        ]));

        toolsContent.appendChild(this.createToolSection('Input Tools', [
            {
                id: 'virtual-midi',
                name: 'Virtual MIDI Keyboard',
                icon: '🎹',
                key: 'K',
                description: 'Touch-friendly MIDI controls',
                enabled: this.tools.virtualMIDI,
                action: () => this.toggleVirtualMIDI()
            },
            {
                id: 'audio-input',
                name: 'Audio Input Source',
                icon: '🎵',
                key: 'A',
                description: 'Mic, YouTube, Ableton, files',
                enabled: this.tools.audioInput,
                action: () => this.toggleAudioInput()
            }
        ]));

        // Add rotation controls
        toolsContent.appendChild(this.createRotationControls());

        toolbox.appendChild(toolsContent);

        // Close functionality - hide entire panel
        collapseButton.onclick = () => {
            toolbox.style.display = 'none';

            // Trigger a global event so the toolbar can update
            window.dispatchEvent(new CustomEvent('panelClosed', {
                detail: { selector: '.space-morph-toolbox' }
            }));
        };

        this.container.appendChild(toolbox);
        this.toolboxElement = toolbox;
    }

    private createToolSection(title: string, tools: any[]): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 12px;
            padding: 8px;
            border: 1px solid rgba(0, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 20, 40, 0.3);
        `;

        const sectionTitle = document.createElement('div');
        sectionTitle.textContent = title;
        sectionTitle.style.cssText = `
            font-size: 10px;
            font-weight: 600;
            color: #00ffaa;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        section.appendChild(sectionTitle);

        tools.forEach(tool => {
            const toolElement = document.createElement('div');
            toolElement.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 4px 0;
                cursor: pointer;
                transition: all 0.2s ease;
                border-radius: 4px;
                padding: 6px 8px;
                margin: 2px 0;
            `;

            const toolInfo = document.createElement('div');
            toolInfo.style.cssText = `
                display: flex;
                align-items: center;
                gap: 6px;
                flex: 1;
            `;

            const icon = document.createElement('span');
            icon.textContent = tool.icon;
            icon.style.fontSize = '12px';

            const nameAndDesc = document.createElement('div');
            nameAndDesc.innerHTML = `
                <div style="font-size: 11px; font-weight: 500; color: ${tool.enabled ? '#00ffff' : '#666'};">
                    ${tool.name}
                </div>
                <div style="font-size: 9px; color: ${tool.enabled ? '#00aaaa' : '#444'}; margin-top: 1px;">
                    ${tool.description}
                </div>
            `;

            const keyIndicator = document.createElement('span');
            keyIndicator.textContent = tool.key;
            keyIndicator.style.cssText = `
                background: ${tool.enabled ? 'rgba(0, 255, 255, 0.2)' : 'rgba(100, 100, 100, 0.2)'};
                color: ${tool.enabled ? '#00ffff' : '#666'};
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: 600;
                border: 1px solid ${tool.enabled ? 'rgba(0, 255, 255, 0.3)' : 'rgba(100, 100, 100, 0.3)'};
            `;

            toolInfo.appendChild(icon);
            toolInfo.appendChild(nameAndDesc);
            toolElement.appendChild(toolInfo);
            toolElement.appendChild(keyIndicator);

            // Hover and click effects
            toolElement.onmouseenter = () => {
                toolElement.style.background = tool.enabled ?
                    'rgba(0, 255, 255, 0.1)' : 'rgba(100, 100, 100, 0.05)';
            };
            toolElement.onmouseleave = () => {
                toolElement.style.background = 'transparent';
            };

            toolElement.onclick = () => {
                tool.action();
                this.updateToolStates();
            };

            section.appendChild(toolElement);
        });

        return section;
    }

    private createRotationControls(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 12px;
            padding: 12px;
            border: 1px solid rgba(0, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 20, 40, 0.3);
        `;

        const sectionTitle = document.createElement('div');
        sectionTitle.textContent = 'VESSEL ROTATION';
        sectionTitle.style.cssText = `
            font-size: 10px;
            font-weight: 600;
            color: #00ffaa;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        section.appendChild(sectionTitle);

        // X-axis rotation (pitch)
        section.appendChild(this.createRotationSlider('X-Axis (Pitch)', '⬆️⬇️', 'x'));

        // Y-axis rotation (yaw)
        section.appendChild(this.createRotationSlider('Y-Axis (Yaw)', '⬅️➡️', 'y'));

        // Z-axis rotation (roll)
        section.appendChild(this.createRotationSlider('Z-Axis (Roll)', '↩️↪️', 'z'));

        // Reset button
        const resetButton = document.createElement('button');
        resetButton.textContent = '🔄 Reset Rotation';
        resetButton.style.cssText = `
            width: 100%;
            padding: 6px;
            background: rgba(255, 165, 0, 0.2);
            border: 1px solid #ffaa00;
            color: #ffaa00;
            border-radius: 4px;
            margin-top: 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            transition: all 0.2s ease;
        `;
        resetButton.onclick = () => {
            this.engine.setVesselRotation(0, 0, 0);
            // Reset all sliders
            const sliders = section.querySelectorAll('input[type="range"]');
            sliders.forEach(slider => {
                (slider as HTMLInputElement).value = '0';
                const valueDisplay = slider.nextElementSibling as HTMLElement;
                if (valueDisplay) {
                    valueDisplay.textContent = '0°';
                }
            });
        };
        section.appendChild(resetButton);

        return section;
    }

    private createRotationSlider(label: string, icon: string, axis: 'x' | 'y' | 'z'): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin-bottom: 8px;';

        const labelEl = document.createElement('label');
        labelEl.textContent = `${icon} ${label}:`;
        labelEl.style.cssText = `
            display: block;
            margin-bottom: 2px;
            font-size: 9px;
            color: #00aaaa;
        `;

        const sliderContainer = document.createElement('div');
        sliderContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
        `;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '-180';
        slider.max = '180';
        slider.value = '0';
        slider.step = '5';
        slider.style.cssText = `
            flex: 1;
            height: 4px;
            background: rgba(0, 255, 255, 0.2);
            outline: none;
            border-radius: 2px;
        `;

        const valueDisplay = document.createElement('span');
        valueDisplay.textContent = '0°';
        valueDisplay.style.cssText = `
            color: #00ffff;
            font-size: 9px;
            font-weight: bold;
            min-width: 30px;
            text-align: right;
        `;

        slider.oninput = () => {
            const degrees = parseInt(slider.value);
            const radians = (degrees * Math.PI) / 180;
            valueDisplay.textContent = `${degrees}°`;

            // Set absolute rotation based on slider value
            const currentRotation = this.engine.getVesselRotation();
            switch (axis) {
                case 'x':
                    this.engine.setVesselRotation(radians, currentRotation.y, currentRotation.z);
                    break;
                case 'y':
                    this.engine.setVesselRotation(currentRotation.x, radians, currentRotation.z);
                    break;
                case 'z':
                    this.engine.setVesselRotation(currentRotation.x, currentRotation.y, radians);
                    break;
            }
        };

        sliderContainer.appendChild(slider);
        sliderContainer.appendChild(valueDisplay);

        container.appendChild(labelEl);
        container.appendChild(sliderContainer);

        return container;
    }

    private toggleMicroficheReader() {
        this.tools.microficheReader = !this.tools.microficheReader;
        this.microficheInterface.setVisibility(this.tools.microficheReader);
    }

    private toggleShadowAnalysis() {
        this.tools.shadowAnalysis = !this.tools.shadowAnalysis;
        // TODO: Implement shadow analysis toggle in engine
        console.log('Shadow analysis:', this.tools.shadowAnalysis);
    }

    private toggleSpatialMapping() {
        this.tools.spatialMapping = !this.tools.spatialMapping;
        // TODO: Implement spatial mapping toggle
        console.log('Spatial mapping:', this.tools.spatialMapping);
    }

    private toggleTemporalWindow() {
        this.tools.temporalWindow = !this.tools.temporalWindow;
        // TODO: Implement temporal window toggle
        console.log('Temporal window:', this.tools.temporalWindow);
    }

    private toggleVesselScaffolding() {
        this.tools.vesselScaffolding = !this.tools.vesselScaffolding;
        // TODO: Implement vessel scaffolding toggle
        console.log('Vessel scaffolding:', this.tools.vesselScaffolding);
    }

    private toggleVirtualMIDI() {
        this.tools.virtualMIDI = !this.tools.virtualMIDI;
        if (this.virtualMIDIKeyboard) {
            this.virtualMIDIKeyboard.setVisibility(this.tools.virtualMIDI);
        }
    }

    private toggleAudioInput() {
        this.tools.audioInput = !this.tools.audioInput;
        if (this.audioInputSelector) {
            this.audioInputSelector.setVisibility(this.tools.audioInput);
        }
    }

    private updateToolStates() {
        // Recreate the toolbox with updated states
        if (this.toolboxElement) {
            this.toolboxElement.remove();
        }
        this.createToolbox();

        // Restore visibility
        if (this.toolboxElement && this.isVisible) {
            this.toolboxElement.style.display = 'block';
        }
    }

    public setVisibility(visible: boolean) {
        this.isVisible = visible;
        if (this.toolboxElement) {
            this.toolboxElement.style.display = visible ? 'block' : 'none';
        }
    }

    public isToolboxVisible(): boolean {
        return this.isVisible;
    }

    public handleKeyPress(key: string): boolean {
        if (!this.isVisible) return false;

        switch (key.toUpperCase()) {
            case 'V':
                this.toggleMicroficheReader();
                this.updateToolStates();
                return true;
            case 'S':
                this.toggleShadowAnalysis();
                this.updateToolStates();
                return true;
            case 'M':
                this.toggleSpatialMapping();
                this.updateToolStates();
                return true;
            case 'T':
                this.toggleTemporalWindow();
                this.updateToolStates();
                return true;
            case 'B':
                this.toggleVesselScaffolding();
                this.updateToolStates();
                return true;
            case 'K':
                this.toggleVirtualMIDI();
                this.updateToolStates();
                return true;
            case 'A':
                this.toggleAudioInput();
                this.updateToolStates();
                return true;
        }
        return false;
    }
}