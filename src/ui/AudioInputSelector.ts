/**
 * Audio Input Selector UI
 *
 * Provides interface for selecting and configuring audio input sources
 */

import { AudioInputManager, AudioInputSource, AudioAnalysis } from '../audio/AudioInputManager';

export class AudioInputSelector {
    private container: HTMLElement;
    private audioInputManager: AudioInputManager;
    private selectorElement: HTMLElement | null = null;
    private isVisible: boolean = false;
    private currentAnalysis: AudioAnalysis | null = null;

    constructor(container: HTMLElement) {
        this.container = container;
        this.audioInputManager = new AudioInputManager();
        this.createSelector();
        this.setupAnalysis();
    }

    private createSelector() {
        const selector = document.createElement('div');
        selector.className = 'audio-input-selector';
        selector.style.cssText = `
            position: fixed;
            top: 20px;
            right: 400px;
            width: 320px;
            background: rgba(0, 20, 40, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 12px;
            padding: 16px;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            z-index: 150;
            display: none;
            box-shadow:
                0 1px 0 0 rgba(0, 255, 255, 0.1) inset,
                0 8px 32px 0 rgba(0, 0, 0, 0.6),
                0 32px 80px 0 rgba(0, 255, 255, 0.15);
        `;

        // Header
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0, 255, 255, 0.2);
        `;

        const title = document.createElement('h3');
        title.textContent = '🎵 AUDIO INPUT SOURCE';
        title.style.cssText = `
            margin: 0;
            color: #00ffff;
            font-size: 12px;
            font-weight: 600;
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
                detail: { selector: '.audio-input-selector' }
            }));
        };

        header.appendChild(title);
        header.appendChild(closeButton);
        selector.appendChild(header);

        // Source selection
        const sourceSection = this.createSourceSection();
        selector.appendChild(sourceSection);

        // Controls section
        const controlsSection = this.createControlsSection();
        selector.appendChild(controlsSection);

        // Analysis section
        const analysisSection = this.createAnalysisSection();
        selector.appendChild(analysisSection);

        this.container.appendChild(selector);
        this.selectorElement = selector;
    }

    private createSourceSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 16px;
            padding: 12px;
            border: 1px solid rgba(0, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 20, 40, 0.3);
        `;

        const sectionTitle = document.createElement('div');
        sectionTitle.textContent = 'INPUT SOURCE';
        sectionTitle.style.cssText = `
            font-size: 10px;
            font-weight: 600;
            color: #00ffaa;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        section.appendChild(sectionTitle);

        const sources = [
            { id: 'internal', name: 'Internal Synthesis', icon: '🎛️', description: 'Built-in sound engine' },
            { id: 'microphone', name: 'Microphone', icon: '🎤', description: 'Live microphone input' },
            { id: 'line-in', name: 'Line Input', icon: '🔌', description: 'External line input' },
            { id: 'file', name: 'Audio File', icon: '📁', description: 'Upload audio file' },
            { id: 'youtube', name: 'YouTube', icon: '📺', description: 'YouTube video audio' },
            { id: 'ableton', name: 'Ableton Live', icon: '🎚️', description: 'DAW integration' },
            { id: 'midi', name: 'MIDI Device', icon: '🎹', description: 'External MIDI controller' }
        ];

        sources.forEach(source => {
            const sourceElement = document.createElement('div');
            sourceElement.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px;
                margin: 4px 0;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s ease;
                border: 1px solid transparent;
            `;

            const sourceInfo = document.createElement('div');
            sourceInfo.style.cssText = `
                display: flex;
                align-items: center;
                gap: 8px;
                flex: 1;
            `;

            const icon = document.createElement('span');
            icon.textContent = source.icon;
            icon.style.fontSize = '14px';

            const nameAndDesc = document.createElement('div');
            nameAndDesc.innerHTML = `
                <div style="font-size: 11px; font-weight: 500; color: #00ffff;">
                    ${source.name}
                </div>
                <div style="font-size: 9px; color: #00aaaa; margin-top: 1px;">
                    ${source.description}
                </div>
            `;

            const status = document.createElement('span');
            status.id = `status-${source.id}`;
            status.textContent = source.id === 'internal' ? '●' : '○';
            status.style.cssText = `
                color: ${source.id === 'internal' ? '#00ff00' : '#666'};
                font-size: 12px;
                font-weight: bold;
            `;

            sourceInfo.appendChild(icon);
            sourceInfo.appendChild(nameAndDesc);
            sourceElement.appendChild(sourceInfo);
            sourceElement.appendChild(status);

            // Hover and click effects
            sourceElement.onmouseenter = () => {
                sourceElement.style.background = 'rgba(0, 255, 255, 0.1)';
                sourceElement.style.borderColor = 'rgba(0, 255, 255, 0.3)';
            };
            sourceElement.onmouseleave = () => {
                sourceElement.style.background = 'transparent';
                sourceElement.style.borderColor = 'transparent';
            };

            sourceElement.onclick = () => {
                this.selectAudioSource(source.id as AudioInputSource);
            };

            section.appendChild(sourceElement);
        });

        return section;
    }

    private createControlsSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 16px;
            padding: 12px;
            border: 1px solid rgba(0, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 20, 40, 0.3);
        `;

        const sectionTitle = document.createElement('div');
        sectionTitle.textContent = 'AUDIO CONTROLS';
        sectionTitle.style.cssText = `
            font-size: 10px;
            font-weight: 600;
            color: #00ffaa;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        section.appendChild(sectionTitle);

        // Master gain
        section.appendChild(this.createSlider('Master Gain', '🔊', 0, 1, 0.8, (value) => {
            this.audioInputManager.setMasterGain(value);
        }));

        // File upload for audio files
        const fileUpload = document.createElement('div');
        fileUpload.style.cssText = `
            margin: 8px 0;
            padding: 8px;
            border: 1px dashed rgba(0, 255, 255, 0.3);
            border-radius: 4px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        `;
        fileUpload.innerHTML = `
            <input type="file" accept="audio/*" style="display: none;" id="audio-file-input">
            <div style="color: #00aaaa; font-size: 10px;">
                📁 Click to select audio file
            </div>
        `;

        fileUpload.onclick = () => {
            const input = document.getElementById('audio-file-input') as HTMLInputElement;
            input?.click();
        };

        const input = fileUpload.querySelector('input') as HTMLInputElement;
        input.onchange = (event) => {
            const file = (event.target as HTMLInputElement).files?.[0];
            if (file) {
                this.audioInputManager.connectAudioFile(file);
                fileUpload.innerHTML = `
                    <div style="color: #00ff00; font-size: 10px;">
                        ✅ ${file.name}
                    </div>
                `;
            }
        };

        section.appendChild(fileUpload);

        // YouTube URL input
        const youtubeInput = document.createElement('div');
        youtubeInput.style.cssText = 'margin: 8px 0;';
        youtubeInput.innerHTML = `
            <input type="text" placeholder="Enter YouTube URL..." style="
                width: 100%;
                padding: 6px;
                background: rgba(0, 20, 40, 0.8);
                border: 1px solid rgba(0, 255, 255, 0.3);
                color: #00ffff;
                border-radius: 4px;
                font-size: 10px;
                font-family: inherit;
            ">
            <button style="
                width: 100%;
                margin-top: 4px;
                padding: 6px;
                background: rgba(255, 0, 0, 0.2);
                border: 1px solid #ff4444;
                color: #ff4444;
                border-radius: 4px;
                cursor: pointer;
                font-size: 10px;
                font-family: inherit;
            ">📺 Connect YouTube</button>
        `;

        const ytButton = youtubeInput.querySelector('button');
        const ytInput = youtubeInput.querySelector('input') as HTMLInputElement;
        ytButton?.addEventListener('click', () => {
            const url = ytInput.value;
            if (url) {
                this.audioInputManager.connectYouTube(url);
            }
        });

        section.appendChild(youtubeInput);

        // Playback controls
        const playbackControls = document.createElement('div');
        playbackControls.style.cssText = `
            display: flex;
            gap: 8px;
            margin-top: 8px;
        `;

        const playButton = document.createElement('button');
        playButton.textContent = '▶️ Play';
        playButton.style.cssText = this.getControlButtonStyle();
        playButton.onclick = () => {
            this.audioInputManager.playAudioFile();
            this.audioInputManager.playYouTube();
        };

        const pauseButton = document.createElement('button');
        pauseButton.textContent = '⏸️ Pause';
        pauseButton.style.cssText = this.getControlButtonStyle();
        pauseButton.onclick = () => {
            this.audioInputManager.pauseAudioFile();
            this.audioInputManager.pauseYouTube();
        };

        playbackControls.appendChild(playButton);
        playbackControls.appendChild(pauseButton);
        section.appendChild(playbackControls);

        return section;
    }

    private createAnalysisSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            padding: 12px;
            border: 1px solid rgba(0, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 20, 40, 0.3);
        `;

        const sectionTitle = document.createElement('div');
        sectionTitle.textContent = 'AUDIO ANALYSIS';
        sectionTitle.style.cssText = `
            font-size: 10px;
            font-weight: 600;
            color: #00ffaa;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        section.appendChild(sectionTitle);

        const analysisDisplay = document.createElement('div');
        analysisDisplay.id = 'audio-analysis-display';
        analysisDisplay.style.cssText = `
            font-size: 9px;
            color: #00aaaa;
            line-height: 1.4;
        `;
        analysisDisplay.innerHTML = `
            <div>🔊 RMS Level: <span id="rms-level">0.00</span></div>
            <div>📊 Peak: <span id="peak-level">0.00</span></div>
            <div>🎵 Pitch: <span id="pitch-detect">--- Hz</span></div>
            <div>📡 Source: <span id="current-source">Internal</span></div>
        `;

        section.appendChild(analysisDisplay);

        return section;
    }

    private createSlider(
        label: string,
        icon: string,
        min: number,
        max: number,
        defaultValue: number,
        onChange: (value: number) => void
    ): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin: 8px 0;';

        const labelEl = document.createElement('label');
        labelEl.textContent = `${icon} ${label}:`;
        labelEl.style.cssText = `
            display: block;
            margin-bottom: 4px;
            font-size: 10px;
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
        slider.min = min.toString();
        slider.max = max.toString();
        slider.value = defaultValue.toString();
        slider.step = '0.01';
        slider.style.cssText = `
            flex: 1;
            height: 4px;
            background: rgba(0, 255, 255, 0.2);
            outline: none;
            border-radius: 2px;
        `;

        const valueDisplay = document.createElement('span');
        valueDisplay.textContent = defaultValue.toFixed(2);
        valueDisplay.style.cssText = `
            color: #00ffff;
            font-size: 9px;
            font-weight: bold;
            min-width: 35px;
            text-align: right;
        `;

        slider.oninput = () => {
            const value = parseFloat(slider.value);
            valueDisplay.textContent = value.toFixed(2);
            onChange(value);
        };

        sliderContainer.appendChild(slider);
        sliderContainer.appendChild(valueDisplay);
        container.appendChild(labelEl);
        container.appendChild(sliderContainer);

        return container;
    }

    private getControlButtonStyle(): string {
        return `
            flex: 1;
            padding: 6px;
            background: rgba(0, 255, 255, 0.2);
            border: 1px solid #00ffff;
            color: #00ffff;
            border-radius: 4px;
            cursor: pointer;
            font-size: 9px;
            font-family: inherit;
            transition: all 0.2s ease;
        `;
    }

    private async selectAudioSource(source: AudioInputSource) {
        const success = await this.audioInputManager.selectAudioSource(source);

        // Update status indicators
        const allStatuses = this.selectorElement?.querySelectorAll('[id^="status-"]');
        allStatuses?.forEach(status => {
            status.textContent = '○';
            (status as HTMLElement).style.color = '#666';
        });

        if (success) {
            const statusElement = document.getElementById(`status-${source}`);
            if (statusElement) {
                statusElement.textContent = '●';
                statusElement.style.color = '#00ff00';
            }

            // Update current source display
            const currentSourceEl = document.getElementById('current-source');
            if (currentSourceEl) {
                currentSourceEl.textContent = source.charAt(0).toUpperCase() + source.slice(1);
            }
        }
    }

    private setupAnalysis() {
        this.audioInputManager.onAnalysis((analysis) => {
            this.currentAnalysis = analysis;
            this.updateAnalysisDisplay();
        });
    }

    private updateAnalysisDisplay() {
        if (!this.currentAnalysis) return;

        const rmsEl = document.getElementById('rms-level');
        const peakEl = document.getElementById('peak-level');
        const pitchEl = document.getElementById('pitch-detect');

        if (rmsEl) rmsEl.textContent = this.currentAnalysis.rms.toFixed(3);
        if (peakEl) peakEl.textContent = this.currentAnalysis.peak.toFixed(3);
        if (pitchEl) {
            const pitch = this.currentAnalysis.pitch;
            pitchEl.textContent = pitch > 0 ? `${pitch.toFixed(1)} Hz` : '--- Hz';
        }
    }

    public setVisibility(visible: boolean) {
        this.isVisible = visible;
        if (this.selectorElement) {
            this.selectorElement.style.display = visible ? 'block' : 'none';
        }
    }

    public toggleVisibility(): boolean {
        this.setVisibility(!this.isVisible);
        return this.isVisible;
    }

    public isInputSelectorVisible(): boolean {
        return this.isVisible;
    }

    public getAudioInputManager(): AudioInputManager {
        return this.audioInputManager;
    }
}