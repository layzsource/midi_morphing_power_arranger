/**
 * Shadow Microfiche Interface
 *
 * Provides UI controls for viewing shadow-encoded data from different angles,
 * creating the foundation for the Acid Reign VJ performance interface.
 *
 * This interface allows real-time exploration of shadow data as if examining
 * a microfiche or wax cylinder recording.
 */

export interface MicroficheControls {
    viewAngle: number;          // 0-360 degrees
    ringIndex: number;          // -1 for all rings, 0-5 for specific rings
    timeWindow: number;         // Hours to look back
    shadowIntensity: number;    // Visual intensity multiplier
    readoutMode: 'temporal' | 'spatial' | 'physics' | 'combined';
}

export class ShadowMicroficheInterface {
    private container: HTMLElement;
    private engine: any; // Reference to main engine
    private controls: MicroficheControls;
    private updateCallback?: (data: any) => void;
    private interfaceElement: HTMLElement | null = null;
    private isVisible: boolean = true;

    // UI Elements
    private shadowDataDisplay: HTMLElement;
    private controlPanel: HTMLElement;
    private statisticsPanel: HTMLElement;
    private angleSlider: HTMLInputElement;
    private ringSelector: HTMLSelectElement;
    private timeWindowSlider: HTMLInputElement;
    private intensitySlider: HTMLInputElement;
    private modeSelector: HTMLSelectElement;
    private clearButton: HTMLButtonElement;

    constructor(container: HTMLElement, engine: any) {
        this.container = container;
        this.engine = engine;
        this.controls = {
            viewAngle: 0,
            ringIndex: -1, // All rings
            timeWindow: 1, // 1 hour
            shadowIntensity: 1.0,
            readoutMode: 'combined'
        };

        this.createInterface();
        this.startDataUpdates();
    }

    private createInterface() {
        // Create main interface container
        const interfaceContainer = document.createElement('div');
        interfaceContainer.className = 'shadow-microfiche-interface';
        interfaceContainer.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            width: 350px;
            background: rgba(0, 20, 40, 0.9);
            border: 1px solid #00ffff;
            border-radius: 8px;
            padding: 15px;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            z-index: 1000;
            backdrop-filter: blur(10px);
        `;

        // Title with collapse button
        const titleBar = document.createElement('div');
        titleBar.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        `;

        const title = document.createElement('h3');
        title.textContent = '🔍 SHADOW MICROFICHE READER';
        title.style.cssText = `
            margin: 0;
            color: #00ffff;
            font-size: 14px;
            text-shadow: 0 0 5px #00ffff;
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
        `;

        titleBar.appendChild(title);
        titleBar.appendChild(collapseButton);
        interfaceContainer.appendChild(titleBar);

        // Content wrapper
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'microfiche-content';

        // Control Panel
        this.controlPanel = this.createControlPanel();
        contentWrapper.appendChild(this.controlPanel);

        // Shadow Data Display
        this.shadowDataDisplay = this.createDataDisplay();
        contentWrapper.appendChild(this.shadowDataDisplay);

        // Statistics Panel
        this.statisticsPanel = this.createStatisticsPanel();
        contentWrapper.appendChild(this.statisticsPanel);

        interfaceContainer.appendChild(contentWrapper);

        // Add collapse functionality - start collapsed
        let collapsed = true;
        contentWrapper.style.display = 'none'; // Start collapsed
        collapseButton.textContent = '⬆️'; // Start with up arrow

        collapseButton.onclick = () => {
            // Hide the entire panel instead of just collapsing
            interfaceContainer.style.display = 'none';

            // Trigger a global event so the toolbar can update
            window.dispatchEvent(new CustomEvent('panelClosed', {
                detail: { selector: '.shadow-microfiche-interface' }
            }));
        };

        this.container.appendChild(interfaceContainer);
        this.interfaceElement = interfaceContainer;
    }

    private createControlPanel(): HTMLElement {
        const panel = document.createElement('div');
        panel.className = 'control-panel';
        panel.style.cssText = `
            margin-bottom: 15px;
            padding: 10px;
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 4px;
        `;

        // View Angle Control
        panel.appendChild(this.createSliderControl(
            'View Angle',
            '🔄',
            (value) => {
                this.angleSlider = value;
                this.controls.viewAngle = parseFloat(value.value) * (Math.PI / 180); // Convert to radians
                this.updateShadowData();
            },
            0, 360, 0, '°'
        ));

        // Ring Selector
        panel.appendChild(this.createSelectControl(
            'Target Ring',
            '🟫',
            (value) => {
                this.ringSelector = value;
                this.controls.ringIndex = parseInt(value.value);
                this.updateShadowData();
            },
            [
                { value: -1, text: 'All Rings' },
                { value: 0, text: 'Front Ring' },
                { value: 1, text: 'Back Ring' },
                { value: 2, text: 'Right Ring' },
                { value: 3, text: 'Left Ring' },
                { value: 4, text: 'Top Ring' },
                { value: 5, text: 'Bottom Ring' }
            ]
        ));

        // Time Window Control
        panel.appendChild(this.createSliderControl(
            'Time Window',
            '⏰',
            (value) => {
                this.timeWindowSlider = value;
                this.controls.timeWindow = parseFloat(value.value);
                this.updateShadowData();
            },
            0.1, 24, 1, 'h'
        ));

        // Intensity Control
        panel.appendChild(this.createSliderControl(
            'Shadow Intensity',
            '💡',
            (value) => {
                this.intensitySlider = value;
                this.controls.shadowIntensity = parseFloat(value.value);
                this.updateShadowData();
            },
            0.1, 3.0, 1.0, 'x'
        ));

        // Readout Mode
        panel.appendChild(this.createSelectControl(
            'Readout Mode',
            '📊',
            (value) => {
                this.modeSelector = value;
                this.controls.readoutMode = value.value as any;
                this.updateShadowData();
            },
            [
                { value: 'combined', text: 'Combined Data' },
                { value: 'temporal', text: 'Temporal Only' },
                { value: 'spatial', text: 'Spatial Only' },
                { value: 'physics', text: 'Physics Only' }
            ]
        ));

        // Clear Button
        this.clearButton = document.createElement('button');
        this.clearButton.textContent = '🗑️ Clear Shadow Data';
        this.clearButton.style.cssText = `
            width: 100%;
            padding: 8px;
            background: rgba(255, 100, 100, 0.2);
            border: 1px solid #ff6464;
            color: #ff6464;
            border-radius: 4px;
            margin-top: 10px;
            cursor: pointer;
            font-family: inherit;
        `;
        this.clearButton.onclick = () => {
            this.engine.clearShadowData();
            this.updateShadowData();
        };
        panel.appendChild(this.clearButton);

        return panel;
    }

    private createSliderControl(
        label: string,
        icon: string,
        onChange: (input: HTMLInputElement) => void,
        min: number,
        max: number,
        defaultValue: number,
        unit: string
    ): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin-bottom: 10px;';

        const labelEl = document.createElement('label');
        labelEl.textContent = `${icon} ${label}:`;
        labelEl.style.cssText = `
            display: block;
            margin-bottom: 3px;
            font-size: 11px;
        `;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = min.toString();
        slider.max = max.toString();
        slider.value = defaultValue.toString();
        slider.step = '0.1';
        slider.style.cssText = `
            width: 70%;
            margin-right: 10px;
        `;

        const valueDisplay = document.createElement('span');
        valueDisplay.textContent = `${defaultValue}${unit}`;
        valueDisplay.style.cssText = `
            color: #ffff00;
            font-weight: bold;
        `;

        slider.oninput = () => {
            valueDisplay.textContent = `${slider.value}${unit}`;
            onChange(slider);
        };

        container.appendChild(labelEl);
        container.appendChild(slider);
        container.appendChild(valueDisplay);

        return container;
    }

    private createSelectControl(
        label: string,
        icon: string,
        onChange: (select: HTMLSelectElement) => void,
        options: { value: any, text: string }[]
    ): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin-bottom: 10px;';

        const labelEl = document.createElement('label');
        labelEl.textContent = `${icon} ${label}:`;
        labelEl.style.cssText = `
            display: block;
            margin-bottom: 3px;
            font-size: 11px;
        `;

        const select = document.createElement('select');
        select.style.cssText = `
            width: 100%;
            padding: 4px;
            background: rgba(0, 20, 40, 0.8);
            border: 1px solid #00ffff;
            color: #00ffff;
            border-radius: 2px;
        `;

        options.forEach(option => {
            const optionEl = document.createElement('option');
            optionEl.value = option.value;
            optionEl.textContent = option.text;
            select.appendChild(optionEl);
        });

        select.onchange = () => onChange(select);

        container.appendChild(labelEl);
        container.appendChild(select);

        return container;
    }

    private createDataDisplay(): HTMLElement {
        const display = document.createElement('div');
        display.className = 'shadow-data-display';
        display.style.cssText = `
            height: 200px;
            overflow-y: auto;
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 15px;
            background: rgba(0, 10, 20, 0.5);
            font-size: 10px;
            line-height: 1.3;
        `;

        display.innerHTML = '<div style="color: #888;">🔍 Initializing shadow reader...</div>';

        return display;
    }

    private createStatisticsPanel(): HTMLElement {
        const panel = document.createElement('div');
        panel.className = 'statistics-panel';
        panel.style.cssText = `
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 4px;
            padding: 10px;
            background: rgba(0, 10, 20, 0.3);
            font-size: 10px;
        `;

        panel.innerHTML = '<div style="color: #888;">📊 Shadow statistics loading...</div>';

        return panel;
    }

    private updateShadowData() {
        try {
            // Get shadow data from the engine
            const shadowData = this.engine.readShadowDataAtAngle(
                this.controls.viewAngle,
                this.controls.ringIndex === -1 ? undefined : this.controls.ringIndex
            );

            const statistics = this.engine.getShadowStatistics();

            // Update data display
            this.updateDataDisplay(shadowData);

            // Update statistics
            this.updateStatisticsDisplay(statistics);

            // Trigger callback if registered
            if (this.updateCallback) {
                this.updateCallback({
                    shadowData,
                    statistics,
                    controls: this.controls
                });
            }

        } catch (error) {
            this.shadowDataDisplay.innerHTML = `
                <div style="color: #ff6464;">
                    ⚠️ Error reading shadow data: ${error}
                </div>
            `;
        }
    }

    private updateDataDisplay(shadowData: any[]) {
        if (!shadowData || shadowData.length === 0) {
            this.shadowDataDisplay.innerHTML = `
                <div style="color: #888;">
                    🔍 No shadow data found for current viewing angle<br>
                    📐 Angle: ${Math.round(this.controls.viewAngle * 180 / Math.PI)}°<br>
                    🟫 Ring: ${this.controls.ringIndex === -1 ? 'All' : `#${this.controls.ringIndex}`}
                </div>
            `;
            return;
        }

        const now = performance.now();
        const timeWindowMs = this.controls.timeWindow * 60 * 60 * 1000; // Convert hours to ms

        // Filter by time window
        const recentShadows = shadowData.filter(shadow =>
            (now - shadow.timestamp) <= timeWindowMs
        );

        let displayHTML = `
            <div style="color: #00ff00; margin-bottom: 8px;">
                🎯 Found ${recentShadows.length} shadows (${shadowData.length} total)
            </div>
        `;

        recentShadows.slice(0, 20).forEach((shadow, index) => {
            const age = (now - shadow.timestamp) / 1000; // seconds
            const ageStr = age < 60 ? `${age.toFixed(1)}s` : `${(age/60).toFixed(1)}m`;

            displayHTML += `
                <div style="margin-bottom: 6px; padding: 4px; border-left: 2px solid #00ffff;">
                    <div style="color: #ffff00;">
                        ${shadow.spriteId} • ${ageStr} ago
                    </div>
                    <div style="color: #00ffff; font-size: 9px;">
                        📍 (${shadow.position.x.toFixed(2)}, ${shadow.position.y.toFixed(2)}, ${shadow.position.z.toFixed(2)})
                        💡 ${(shadow.intensity * 100).toFixed(0)}%
                    </div>
                    ${this.formatPhysicsData(shadow.physicsProperties)}
                </div>
            `;
        });

        if (recentShadows.length > 20) {
            displayHTML += `<div style="color: #888;">... and ${recentShadows.length - 20} more</div>`;
        }

        this.shadowDataDisplay.innerHTML = displayHTML;
    }

    private formatPhysicsData(physics: any): string {
        if (!physics || Object.keys(physics).length === 0) {
            return '<div style="color: #666; font-size: 8px;">No physics data</div>';
        }

        let physicsStr = '<div style="color: #ff88ff; font-size: 8px;">';

        if (physics.chirality) {
            physicsStr += `🌀 ${physics.chirality} `;
        }
        if (physics.charge !== undefined) {
            physicsStr += `⚡ ${physics.charge.toFixed(2)} `;
        }
        if (physics.spin !== undefined) {
            physicsStr += `🌪️ ${physics.spin.toFixed(2)} `;
        }
        if (physics.flavor) {
            physicsStr += `🎨 ${physics.flavor}`;
        }

        physicsStr += '</div>';
        return physicsStr;
    }

    private updateStatisticsDisplay(stats: any) {
        const totalShadows = stats.totalShadows || 0;
        const ringStats = stats.ringStats || {};
        const systemActive = stats.systemActive || false;

        let statsHTML = `
            <div style="color: #00ff00; font-weight: bold; margin-bottom: 5px;">
                📊 SHADOW SYSTEM STATUS
            </div>
            <div>
                🎯 Total Shadows: <span style="color: #ffff00;">${totalShadows}</span><br>
                ⚡ System Active: <span style="color: ${systemActive ? '#00ff00' : '#ff6464'};">${systemActive ? 'YES' : 'NO'}</span><br>
                🕐 Last Update: <span style="color: #00ffff;">${this.formatTimestamp(stats.lastUpdate)}</span>
            </div>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(0,255,255,0.3);">
                <div style="color: #ffff00; font-size: 9px; margin-bottom: 3px;">RING SHADOW COUNTS:</div>
        `;

        Object.entries(ringStats).forEach(([ringIndex, count]) => {
            const ringName = ['Front', 'Back', 'Right', 'Left', 'Top', 'Bottom'][parseInt(ringIndex)] || `Ring ${ringIndex}`;
            statsHTML += `
                <div style="font-size: 9px;">
                    🟫 ${ringName}: <span style="color: #00ffff;">${count}</span>
                </div>
            `;
        });

        statsHTML += '</div>';
        this.statisticsPanel.innerHTML = statsHTML;
    }

    private formatTimestamp(timestamp: number): string {
        if (!timestamp) return 'Never';

        const now = performance.now();
        const diff = (now - timestamp) / 1000;

        if (diff < 1) return 'Just now';
        if (diff < 60) return `${diff.toFixed(0)}s ago`;
        if (diff < 3600) return `${(diff/60).toFixed(0)}m ago`;
        return `${(diff/3600).toFixed(1)}h ago`;
    }

    private startDataUpdates() {
        // Update every 100ms for real-time feel
        setInterval(() => {
            this.updateShadowData();
        }, 100);
    }

    public onDataUpdate(callback: (data: any) => void) {
        this.updateCallback = callback;
    }

    public setViewAngle(degrees: number) {
        this.controls.viewAngle = degrees * (Math.PI / 180);
        if (this.angleSlider) {
            this.angleSlider.value = degrees.toString();
        }
        this.updateShadowData();
    }

    public setRingIndex(index: number) {
        this.controls.ringIndex = index;
        if (this.ringSelector) {
            this.ringSelector.value = index.toString();
        }
        this.updateShadowData();
    }

    public getCurrentControls(): MicroficheControls {
        return { ...this.controls };
    }

    public toggleVisibility(): boolean {
        this.isVisible = !this.isVisible;
        if (this.interfaceElement) {
            this.interfaceElement.style.display = this.isVisible ? 'block' : 'none';
        }
        return this.isVisible;
    }

    public setVisibility(visible: boolean): void {
        this.isVisible = visible;
        if (this.interfaceElement) {
            this.interfaceElement.style.display = this.isVisible ? 'block' : 'none';
        }
    }

    public isInterfaceVisible(): boolean {
        return this.isVisible;
    }
}