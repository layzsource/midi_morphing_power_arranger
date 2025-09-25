import { SkyboxCubeLayer } from '../layers/SkyboxCubeLayer';
import { mmpaLogger } from '../logging/MMPALogger';

/**
 * Theremin Control Panel
 *
 * Provides a placeholder UI for the Theremin/Webcam feature request.
 * Includes:
 * - Webcam activation hooks (placeholder until calibration pipeline is ready)
 * - Theremin proximity slider wired to the skybox morph system
 * - Quick deadband presets referencing the CC1 specification
 * - Biomimicry protocol logging via the shared logger
 */
export class ThereminControlPanel {
    private container: HTMLElement;
    private skyboxLayer: SkyboxCubeLayer;
    private panelElement: HTMLElement | null = null;
    private videoElement: HTMLVideoElement | null = null;
    private statusLabel: HTMLElement | null = null;
    private proximityReadout: HTMLElement | null = null;
    private stageReadout: HTMLElement | null = null;
    private startButton: HTMLButtonElement | null = null;
    private holdButton: HTMLButtonElement | null = null;
    private proximitySlider: HTMLInputElement | null = null;
    private holdActive = false;
    private currentProximity = 0;
    private activeStream: MediaStream | null = null;

    constructor(container: HTMLElement, skyboxLayer: SkyboxCubeLayer) {
        this.container = container;
        this.skyboxLayer = skyboxLayer;
        this.createPanel();
        this.updateReadouts();

        window.addEventListener('panelClosed', (event: any) => {
            if (event?.detail?.selector === '.theremin-webcam-panel') {
                this.stopPreview();
                this.resetHoldState();
            }
        });
    }

    private createPanel(): void {
        const panel = document.createElement('div');
        panel.className = 'theremin-webcam-panel';
        panel.style.cssText = `
            position: fixed;
            top: 120px;
            left: 380px;
            width: 340px;
            background: rgba(8, 12, 24, 0.92);
            backdrop-filter: blur(20px) saturate(140%);
            border: 1px solid rgba(0, 255, 204, 0.25);
            border-radius: 16px;
            padding: 18px;
            color: #e0fdfc;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 12px;
            z-index: 140;
            display: none;
            box-shadow:
                0 1px 0 0 rgba(0, 255, 204, 0.12) inset,
                0 12px 32px rgba(0, 0, 0, 0.55),
                0 48px 120px rgba(0, 255, 204, 0.18);
        `;

        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0, 255, 204, 0.2);
        `;

        const title = document.createElement('h3');
        title.textContent = '📡 Theremin Field Navigator';
        title.style.cssText = `
            margin: 0;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.4px;
            color: #66fff0;
            text-shadow: 0 0 10px rgba(0, 255, 204, 0.6);
        `;

        const closeButton = document.createElement('button');
        closeButton.textContent = '✕';
        closeButton.title = 'Hide panel (use toolbar to show again)';
        closeButton.style.cssText = `
            background: rgba(255, 99, 132, 0.18);
            border: 1px solid rgba(255, 99, 132, 0.4);
            color: #ff99aa;
            padding: 4px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
        `;
        closeButton.onclick = () => {
            this.setVisibility(false);
            this.stopPreview();
            window.dispatchEvent(new CustomEvent('panelClosed', {
                detail: { selector: '.theremin-webcam-panel' }
            }));
            mmpaLogger.logPanelToggle('Theremin Field Navigator', false);
        };

        header.appendChild(title);
        header.appendChild(closeButton);
        panel.appendChild(header);

        const sessionLine = document.createElement('div');
        sessionLine.style.cssText = `
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: rgba(102, 255, 240, 0.85);
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        `;
        sessionLine.innerHTML = `
            <span>naptime: ${new Date().toISOString()} - theremin_webcam_placeholder</span>
            <span>dreamstate: iteration - awaiting calibration</span>
        `;
        panel.appendChild(sessionLine);

        const videoWrapper = document.createElement('div');
        videoWrapper.style.cssText = `
            position: relative;
            height: 160px;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 14px;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(0, 255, 204, 0.12);
        `;

        const video = document.createElement('video');
        video.autoplay = true;
        video.muted = true;
        video.playsInline = true;
        video.style.cssText = `
            width: 100%;
            height: 100%;
            object-fit: cover;
            filter: saturate(0.6);
            opacity: 0.35;
        `;
        videoWrapper.appendChild(video);
        this.videoElement = video;

        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            color: rgba(102, 255, 240, 0.8);
            font-family: 'Courier New', monospace;
            font-size: 11px;
            background: linear-gradient(180deg, rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.6));
        `;
        overlay.innerHTML = `
            <span>THEREMIN FIELD PLACEHOLDER</span>
            <span style="color: rgba(255, 255, 255, 0.6);">Webcam hand tracking coming soon</span>
        `;
        videoWrapper.appendChild(overlay);
        panel.appendChild(videoWrapper);

        const stageLine = document.createElement('div');
        stageLine.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            margin-bottom: 12px;
            color: rgba(255, 255, 255, 0.72);
        `;
        stageLine.innerHTML = `
            <span>recall: theremin_field, webcam, morph_progress</span>
            <span id="theremin-stage-readout">cube</span>
        `;
        panel.appendChild(stageLine);
        this.stageReadout = stageLine.querySelector('#theremin-stage-readout');

        const proximityBlock = document.createElement('div');
        proximityBlock.style.cssText = `
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 204, 0.14);
            background: rgba(0, 40, 50, 0.45);
        `;

        const proximityHeader = document.createElement('div');
        proximityHeader.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 11px;
            letter-spacing: 0.4px;
            text-transform: uppercase;
            color: rgba(102, 255, 240, 0.85);
        `;
        proximityHeader.innerHTML = `
            <span>Theremin Proximity</span>
            <span id="theremin-proximity-readout">0%</span>
        `;
        proximityBlock.appendChild(proximityHeader);
        this.proximityReadout = proximityHeader.querySelector('#theremin-proximity-readout');

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0';
        slider.max = '100';
        slider.value = '0';
        slider.step = '1';
        slider.style.cssText = `
            width: 100%;
            accent-color: #66fff0;
            cursor: pointer;
        `;
        slider.addEventListener('input', () => {
            if (this.holdActive) return;
            const normalized = parseInt(slider.value, 10) / 100;
            this.applyProximity(normalized, false);
        });
        slider.addEventListener('change', () => {
            if (this.holdActive) return;
            const normalized = parseInt(slider.value, 10) / 100;
            this.applyProximity(normalized, true);
        });
        proximityBlock.appendChild(slider);
        this.proximitySlider = slider;

        const sliderLabels = document.createElement('div');
        sliderLabels.style.cssText = `
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 4px;
        `;
        sliderLabels.innerHTML = `
            <span>Left Sweep</span>
            <span>Deadband</span>
            <span>Right Sweep</span>
        `;
        proximityBlock.appendChild(sliderLabels);

        panel.appendChild(proximityBlock);

        const quickControls = document.createElement('div');
        quickControls.style.cssText = `
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 14px;
        `;

        const quickButtons = [
            { label: 'Left 15%', value: 0.15, hint: 'Left motion zone (0-52 CC1)' },
            { label: 'Hold 52%', value: 0.52, hint: 'Deadband neutral (CC1 53-73)' },
            { label: 'Right 88%', value: 0.88, hint: 'Right motion zone (74-127)' }
        ];

        quickButtons.forEach(config => {
            const btn = document.createElement('button');
            btn.textContent = config.label;
            btn.title = config.hint;
            btn.style.cssText = `
                padding: 8px 6px;
                border-radius: 8px;
                border: 1px solid rgba(0, 255, 204, 0.3);
                background: rgba(0, 255, 204, 0.12);
                color: #66fff0;
                font-size: 10px;
                cursor: pointer;
                font-family: inherit;
            `;
            btn.onclick = () => {
                slider.value = Math.round(config.value * 100).toString();
                this.applyProximity(config.value, true);
            };
            quickControls.appendChild(btn);
        });

        panel.appendChild(quickControls);

        const controlRow = document.createElement('div');
        controlRow.style.cssText = `
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        `;

        const holdButton = document.createElement('button');
        holdButton.textContent = 'Field Hold';
        holdButton.style.cssText = `
            flex: 1;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid rgba(255, 211, 105, 0.4);
            background: rgba(255, 211, 105, 0.15);
            color: #ffd369;
            font-size: 11px;
            cursor: pointer;
        `;
        holdButton.onclick = () => {
            this.holdActive = !this.holdActive;
            this.applyHoldState();
            if (this.holdActive) {
                mmpaLogger.logSystemEvent('Theremin field hold', 'Deadband lock engaged', 'iteration');
            } else {
                mmpaLogger.logSystemEvent('Theremin field released', 'Deadband lock disengaged', 'iteration');
            }
        };
        controlRow.appendChild(holdButton);
        this.holdButton = holdButton;

        const resetButton = document.createElement('button');
        resetButton.textContent = 'Reset Cube';
        resetButton.style.cssText = `
            flex: 1;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid rgba(255, 99, 132, 0.4);
            background: rgba(255, 99, 132, 0.18);
            color: #ff99aa;
            font-size: 11px;
            cursor: pointer;
        `;
        resetButton.onclick = () => {
            slider.value = '0';
            this.applyProximity(0, true);
        };
        controlRow.appendChild(resetButton);

        panel.appendChild(controlRow);

        const webcamControls = document.createElement('div');
        webcamControls.style.cssText = `
            display: flex;
            gap: 8px;
        `;

        const startButton = document.createElement('button');
        startButton.textContent = 'Activate Webcam Field';
        startButton.style.cssText = `
            flex: 1;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid rgba(102, 255, 240, 0.4);
            background: rgba(102, 255, 240, 0.18);
            color: #66fff0;
            font-size: 11px;
            cursor: pointer;
        `;
        startButton.onclick = () => this.startPreview(startButton);
        this.startButton = startButton;

        const stopButton = document.createElement('button');
        stopButton.textContent = 'Stop Feed';
        stopButton.style.cssText = `
            width: 110px;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid rgba(255, 99, 132, 0.35);
            background: rgba(255, 99, 132, 0.14);
            color: #ff99aa;
            font-size: 11px;
            cursor: pointer;
        `;
        stopButton.onclick = () => this.stopPreview();

        webcamControls.appendChild(startButton);
        webcamControls.appendChild(stopButton);
        panel.appendChild(webcamControls);

        const statusFooter = document.createElement('div');
        statusFooter.style.cssText = `
            margin-top: 12px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.6);
            min-height: 16px;
        `;
        statusFooter.textContent = 'Status: Awaiting field activation. Webcam integration pending biomimicry protocols.';
        panel.appendChild(statusFooter);
        this.statusLabel = statusFooter;

        this.container.appendChild(panel);
        this.panelElement = panel;

        console.log('📡 Theremin Control Panel initialized and attached to DOM');
    }

    private applyProximity(normalized: number, commit: boolean): void {
        this.currentProximity = Math.max(0, Math.min(1, normalized));
        this.skyboxLayer.setMorphProgress(this.currentProximity);
        this.updateReadouts();

        if (commit) {
            mmpaLogger.logSystemEvent(
                'Theremin field proximity',
                `Proximity ${(this.currentProximity * 100).toFixed(1)}% applied`,
                'iteration'
            );
        }
    }

    private updateReadouts(): void {
        if (this.proximityReadout) {
            this.proximityReadout.textContent = `${Math.round(this.currentProximity * 100)}%`;
        }

        if (this.stageReadout) {
            if (this.currentProximity === 0) {
                this.stageReadout.textContent = 'cube';
            } else if (this.currentProximity === 1) {
                this.stageReadout.textContent = 'sphere';
            } else if (this.currentProximity < 0.5) {
                this.stageReadout.textContent = 'cellular division';
            } else {
                this.stageReadout.textContent = 'morph cascade';
            }
        }
    }

    private async startPreview(startButton: HTMLButtonElement): Promise<void> {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.setStatus('Webcam APIs unavailable in this environment.');
            return;
        }

        try {
            startButton.disabled = true;
            this.setStatus('Requesting webcam access…');

            this.activeStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });

            if (this.videoElement) {
                this.videoElement.srcObject = this.activeStream;
                this.videoElement.style.opacity = '1';
                await this.videoElement.play().catch(() => undefined);
            }

            this.setStatus('Webcam feed active. Field mapping coming soon.');
            mmpaLogger.logSystemEvent('Theremin webcam activated', 'Live video feed streaming', 'iteration');
        } catch (error) {
            console.error('Theremin webcam activation failed', error);
            this.setStatus('Webcam access denied or unavailable.');
            mmpaLogger.logError('Theremin webcam activation failed', 'ThereminControlPanel');
            startButton.disabled = false;
        }
    }

    private stopPreview(): void {
        if (this.activeStream) {
            this.activeStream.getTracks().forEach(track => track.stop());
            this.activeStream = null;
        }

        if (this.videoElement) {
            this.videoElement.srcObject = null;
            this.videoElement.style.opacity = '0.35';
        }

        if (this.startButton) {
            this.startButton.disabled = false;
        }

        this.setStatus('Webcam feed stopped. Placeholder active.');
    }

    private setStatus(message: string): void {
        if (this.statusLabel) {
            this.statusLabel.textContent = `Status: ${message}`;
        }
    }

    private resetHoldState(): void {
        this.holdActive = false;
        this.applyHoldState();
    }

    public setVisibility(visible: boolean): void {
        if (!this.panelElement) return;
        this.panelElement.style.display = visible ? 'block' : 'none';
        if (!visible) {
            this.resetHoldState();
        }
    }

    private applyHoldState(): void {
        if (this.proximitySlider) {
            this.proximitySlider.disabled = this.holdActive;
        }

        if (this.holdButton) {
            this.holdButton.textContent = this.holdActive ? 'Release Hold' : 'Field Hold';
            this.holdButton.style.background = this.holdActive ? 'rgba(255, 211, 105, 0.3)' : 'rgba(255, 211, 105, 0.15)';
            this.holdButton.style.borderColor = this.holdActive ? 'rgba(255, 211, 105, 0.6)' : 'rgba(255, 211, 105, 0.4)';
        }
    }
}
