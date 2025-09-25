/**
 * 🎭 GESTURE CHOREOGRAPHY PANEL
 *
 * Professional VJ interface for managing advanced gesture choreographies:
 * - Recording/playback controls
 * - Gesture-to-preset mapping management
 * - Performance monitoring and analytics
 * - Choreography library management
 */

import { AdvancedGestureChoreographer, GestureRecording, ChoreographedMove } from '../input/AdvancedGestureChoreographer';
import { GesturePresetMapper } from '../input/GesturePresetMapper';

export class GestureChoreographyPanel {
    private container: HTMLElement;
    private choreographer: AdvancedGestureChoreographer;
    private presetMapper: GesturePresetMapper;
    private isVisible: boolean = false;

    // UI Elements
    private recordingStatus: HTMLElement;
    private playbackStatus: HTMLElement;
    private recordingsList: HTMLElement;
    private choreographyLibrary: HTMLElement;

    constructor(choreographer: AdvancedGestureChoreographer, presetMapper: GesturePresetMapper) {
        this.choreographer = choreographer;
        this.presetMapper = presetMapper;
        this.createInterface();
        this.setupEventListeners();
        this.updateStatus();
    }

    private createInterface(): void {
        this.container = document.createElement('div');
        this.container.className = 'gesture-choreography-panel';
        this.container.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: min(90vw, 400px);
            max-height: calc(100vh - 20px);
            background: rgba(0, 0, 0, 0.95);
            border: 2px solid #00ff41;
            border-radius: 12px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            color: #00ff41;
            z-index: 20000;
            display: none;
            overflow-y: auto;
            box-sizing: border-box;
        `;

        // Create main sections
        this.createHeader();
        this.createControlsSection();
        this.createRecordingsSection();
        this.createChoreographySection();
        this.createPresetsSection();
        this.createAnalyticsSection();

        document.body.appendChild(this.container);
    }

    private createHeader(): void {
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #00ff41;
        `;

        const title = document.createElement('h2');
        title.textContent = '🎭 GESTURE CHOREOGRAPHY STUDIO';
        title.style.cssText = `
            margin: 0;
            color: #00ff41;
            font-size: 18px;
            text-shadow: 0 0 10px #00ff41;
        `;

        const closeButton = document.createElement('button');
        closeButton.textContent = '×';
        closeButton.style.cssText = `
            background: none;
            border: 2px solid #ff0080;
            color: #ff0080;
            font-size: 24px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
        `;

        closeButton.onclick = () => this.hide();

        header.appendChild(title);
        header.appendChild(closeButton);
        this.container.appendChild(header);
    }

    private createControlsSection(): void {
        const section = this.createSection('🎛️ RECORDING CONTROLS');

        // Status display
        this.recordingStatus = document.createElement('div');
        this.recordingStatus.style.cssText = `
            background: rgba(255, 255, 0, 0.1);
            border: 1px solid #ffff00;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 15px;
            font-size: 12px;
        `;

        // Recording controls
        const recordingControls = document.createElement('div');
        recordingControls.style.cssText = `
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        `;

        // Record button
        const recordButton = this.createControlButton('🔴 RECORD', 'record');
        recordButton.onclick = () => this.toggleRecording();

        // Stop button
        const stopButton = this.createControlButton('⏹️ STOP', 'stop');
        stopButton.onclick = () => this.stopRecording();

        // Playback controls
        this.playbackStatus = document.createElement('div');
        this.playbackStatus.style.cssText = this.recordingStatus.style.cssText;

        const playbackControls = document.createElement('div');
        playbackControls.style.cssText = recordingControls.style.cssText;

        recordingControls.appendChild(recordButton);
        recordingControls.appendChild(stopButton);

        section.appendChild(this.recordingStatus);
        section.appendChild(recordingControls);
        section.appendChild(this.playbackStatus);
        section.appendChild(playbackControls);
    }

    private createRecordingsSection(): void {
        const section = this.createSection('📼 RECORDINGS LIBRARY');

        this.recordingsList = document.createElement('div');
        this.recordingsList.style.cssText = `
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #333;
            border-radius: 6px;
            padding: 10px;
        `;

        const refreshButton = this.createControlButton('🔄 REFRESH', 'refresh');
        refreshButton.onclick = () => this.updateRecordingsList();

        const importButton = this.createControlButton('📥 IMPORT', 'import');
        importButton.onclick = () => this.importRecording();

        const controls = document.createElement('div');
        controls.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px;';
        controls.appendChild(refreshButton);
        controls.appendChild(importButton);

        section.appendChild(controls);
        section.appendChild(this.recordingsList);
    }

    private createChoreographySection(): void {
        const section = this.createSection('🎪 CHOREOGRAPHY LIBRARY');

        this.choreographyLibrary = document.createElement('div');
        this.choreographyLibrary.style.cssText = this.recordingsList.style.cssText;

        section.appendChild(this.choreographyLibrary);
    }

    private createPresetsSection(): void {
        const section = this.createSection('🎚️ GESTURE PRESET MAPPINGS');

        const presetsList = document.createElement('div');
        presetsList.style.cssText = this.recordingsList.style.cssText;

        // Display available preset mappings
        const availablePresets = this.presetMapper.getAvailablePresets();
        availablePresets.forEach((mapping, gestureName) => {
            const presetItem = document.createElement('div');
            presetItem.style.cssText = `
                padding: 8px;
                margin: 5px 0;
                background: rgba(0, 255, 65, 0.1);
                border: 1px solid #00ff41;
                border-radius: 4px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            `;

            const info = document.createElement('div');
            info.innerHTML = `
                <strong>${gestureName}</strong><br>
                <small>${mapping.description}</small><br>
                <span style="color: #ffff00;">${mapping.presetType} • ${mapping.cooldown}ms cooldown</span>
            `;

            const testButton = this.createSmallButton('TEST');
            testButton.onclick = () => {
                this.presetMapper.processGestureDetection(gestureName);
            };

            presetItem.appendChild(info);
            presetItem.appendChild(testButton);
            presetsList.appendChild(presetItem);
        });

        section.appendChild(presetsList);
    }

    private createAnalyticsSection(): void {
        const section = this.createSection('📊 PERFORMANCE ANALYTICS');

        const analyticsDisplay = document.createElement('div');
        analyticsDisplay.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        `;

        // Gesture stats
        const gestureStats = this.presetMapper.getGestureStats();
        Object.entries(gestureStats).forEach(([gesture, stats]) => {
            const statCard = document.createElement('div');
            statCard.style.cssText = `
                background: rgba(255, 0, 128, 0.1);
                border: 1px solid #ff0080;
                padding: 10px;
                border-radius: 6px;
                text-align: center;
            `;

            statCard.innerHTML = `
                <div style="font-weight: bold; color: #ff0080;">${gesture}</div>
                <div style="font-size: 11px; margin-top: 5px;">
                    Last: ${new Date(stats.lastTriggered).toLocaleTimeString()}<br>
                    Uses: ${stats.timesTriggered}
                </div>
            `;

            analyticsDisplay.appendChild(statCard);
        });

        section.appendChild(analyticsDisplay);
    }

    private createSection(title: string): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 25px;
            padding: 15px;
            border: 1px solid #333;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.5);
        `;

        const sectionTitle = document.createElement('h3');
        sectionTitle.textContent = title;
        sectionTitle.style.cssText = `
            margin: 0 0 15px 0;
            color: #ffff00;
            font-size: 14px;
            text-shadow: 0 0 5px #ffff00;
        `;

        section.appendChild(sectionTitle);
        this.container.appendChild(section);
        return section;
    }

    private createControlButton(text: string, action: string): HTMLElement {
        const button = document.createElement('button');
        button.textContent = text;
        button.className = `choreography-btn-${action}`;
        button.style.cssText = `
            background: rgba(0, 255, 65, 0.2);
            border: 2px solid #00ff41;
            color: #00ff41;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            font-weight: bold;
            transition: all 0.3s ease;
            text-transform: uppercase;
        `;

        button.onmouseover = () => {
            button.style.background = 'rgba(0, 255, 65, 0.4)';
            button.style.boxShadow = '0 0 15px rgba(0, 255, 65, 0.5)';
        };

        button.onmouseout = () => {
            button.style.background = 'rgba(0, 255, 65, 0.2)';
            button.style.boxShadow = 'none';
        };

        return button;
    }

    private createSmallButton(text: string): HTMLElement {
        const button = document.createElement('button');
        button.textContent = text;
        button.style.cssText = `
            background: rgba(255, 255, 0, 0.2);
            border: 1px solid #ffff00;
            color: #ffff00;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            transition: all 0.3s ease;
        `;

        return button;
    }

    private setupEventListeners(): void {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (!this.isVisible) return;

            switch (e.key) {
                case 'Escape':
                    this.hide();
                    break;
                case 'r':
                case 'R':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.toggleRecording();
                    }
                    break;
                case 's':
                case 'S':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.stopRecording();
                    }
                    break;
            }
        });

        // Update status periodically
        setInterval(() => {
            if (this.isVisible) {
                this.updateStatus();
            }
        }, 1000);
    }

    private toggleRecording(): void {
        const status = this.choreographer.getRecordingStatus();

        if (status.isRecording) {
            this.choreographer.stopRecording();
        } else {
            const name = prompt('Recording name:', `Performance ${new Date().toLocaleTimeString()}`);
            const performer = prompt('Performer name:', 'VJ');
            const tags = prompt('Tags (comma-separated):', 'live,performance')?.split(',').map(t => t.trim());

            this.choreographer.startRecording(name || undefined, performer || undefined, tags);
        }

        this.updateStatus();
        this.updateRecordingsList();
    }

    private stopRecording(): void {
        this.choreographer.stopRecording();
        this.choreographer.stopPlayback();
        this.updateStatus();
        this.updateRecordingsList();
    }

    private updateStatus(): void {
        const status = this.choreographer.getRecordingStatus();

        // Update recording status
        if (status.isRecording) {
            this.recordingStatus.innerHTML = `
                <div style="color: #ff4444;">🔴 RECORDING: ${status.currentRecording}</div>
                <div style="font-size: 11px;">Duration: ${Math.floor((status.recordingDuration || 0) / 1000)}s</div>
            `;
        } else {
            this.recordingStatus.innerHTML = `
                <div style="color: #666;">⏸️ STANDBY</div>
                <div style="font-size: 11px;">Ready to record</div>
            `;
        }

        // Update playback status
        if (status.isPlaying) {
            this.playbackStatus.innerHTML = `
                <div style="color: #44ff44;">▶️ PLAYING: ${status.playbackRecording}</div>
            `;
        } else {
            this.playbackStatus.innerHTML = `
                <div style="color: #666;">⏹️ STOPPED</div>
            `;
        }
    }

    private updateRecordingsList(): void {
        this.recordingsList.innerHTML = '';

        const recordings = this.choreographer.getAllRecordings();

        if (recordings.size === 0) {
            this.recordingsList.innerHTML = '<div style="color: #666; text-align: center; padding: 20px;">No recordings available</div>';
            return;
        }

        recordings.forEach((recording, id) => {
            const item = this.createRecordingItem(recording);
            this.recordingsList.appendChild(item);
        });
    }

    private createRecordingItem(recording: GestureRecording): HTMLElement {
        const item = document.createElement('div');
        item.style.cssText = `
            padding: 10px;
            margin: 5px 0;
            background: rgba(0, 255, 65, 0.1);
            border: 1px solid #00ff41;
            border-radius: 6px;
        `;

        const header = document.createElement('div');
        header.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;';

        const info = document.createElement('div');
        info.innerHTML = `
            <strong>${recording.name}</strong><br>
            <small style="color: #ccc;">
                ${new Date(recording.timestamp).toLocaleString()} •
                ${Math.floor(recording.duration / 1000)}s •
                ${recording.frames.length} frames
            </small>
        `;

        const controls = document.createElement('div');
        controls.style.cssText = 'display: flex; gap: 5px;';

        const playButton = this.createSmallButton('▶️');
        playButton.onclick = () => this.choreographer.startPlayback(recording.id, 1.0, false);

        const loopButton = this.createSmallButton('🔄');
        loopButton.onclick = () => this.choreographer.startPlayback(recording.id, 1.0, true);

        const exportButton = this.createSmallButton('💾');
        exportButton.onclick = () => this.exportRecording(recording.id);

        const deleteButton = this.createSmallButton('🗑️');
        deleteButton.style.borderColor = '#ff4444';
        deleteButton.style.color = '#ff4444';
        deleteButton.onclick = () => {
            if (confirm(`Delete recording "${recording.name}"?`)) {
                this.choreographer.deleteRecording(recording.id);
                this.updateRecordingsList();
            }
        };

        controls.appendChild(playButton);
        controls.appendChild(loopButton);
        controls.appendChild(exportButton);
        controls.appendChild(deleteButton);

        header.appendChild(info);
        header.appendChild(controls);

        const metadata = document.createElement('div');
        metadata.style.cssText = 'font-size: 10px; color: #999; margin-top: 5px;';
        metadata.innerHTML = `
            Performer: ${recording.metadata.performer} •
            Tempo: ${recording.metadata.tempo} BPM •
            Complexity: ${(recording.metadata.complexity * 100).toFixed(0)}% •
            Tags: ${recording.metadata.tags.join(', ') || 'none'}
        `;

        item.appendChild(header);
        item.appendChild(metadata);

        return item;
    }

    private exportRecording(id: string): void {
        const jsonData = this.choreographer.exportRecording(id);
        if (!jsonData) return;

        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gesture_recording_${id}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    private importRecording(): void {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                const jsonData = e.target?.result as string;
                const id = this.choreographer.importRecording(jsonData);
                if (id) {
                    this.updateRecordingsList();
                    alert('Recording imported successfully!');
                } else {
                    alert('Failed to import recording. Please check the file format.');
                }
            };
            reader.readAsText(file);
        };
        input.click();
    }

    public show(): void {
        this.isVisible = true;
        this.container.style.display = 'block';
        this.updateStatus();
        this.updateRecordingsList();
        console.log('🎭 Gesture Choreography Panel opened');
    }

    public hide(): void {
        this.isVisible = false;
        this.container.style.display = 'none';
        console.log('🎭 Gesture Choreography Panel closed');
    }

    public toggle(): void {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    public isOpen(): boolean {
        return this.isVisible;
    }
}