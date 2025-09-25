import { mmpaLogger } from '../logging/MMPALogger';

/**
 * Panel Toolbar - Simple View Toggle Bar
 *
 * Horizontal toolbar with panel names as clickable toggles
 * Similar to desktop application toolbars
 */

export class PanelToolbar {
    private container: HTMLElement;
    private toolbarElement: HTMLElement | null = null;

    // Panel configurations with their display names and selectors
    private panels = [
        { name: 'MMPA Power Arranger', id: 'controls', selector: '#controls' },
        { name: 'ParamGraph System', id: 'paramgraph', selector: '#paramgraph-controls' },
        { name: 'Microfiche Reader', id: 'microfiche', selector: '.shadow-microfiche-interface' },
        { name: 'VJ Interface', id: 'vj', selector: '.acid-reign-vj-interface' },
        { name: 'Space Tools', id: 'space-tools', selector: '.space-morph-toolbox' },
        { name: 'Audio Input', id: 'audio', selector: '.audio-input-selector' },
        { name: 'Virtual MIDI', id: 'midi', selector: '.virtual-midi-keyboard' },
        { name: 'Cymatic Patterns', id: 'cymatic-patterns', selector: '.cymatic-patterns-panel' },
        { name: 'Theremin Field', id: 'theremin-field', selector: '.theremin-webcam-panel' },
        { name: 'Morph Box', id: 'morph-box', selector: '#morph-box-panel' },
        { name: 'Microtonal Morph', id: 'microtonal-morph', selector: '#microtonal-morph-panel' },
        { name: 'Skybox Controls', id: 'main-display', selector: '#main-display-panel' },
        { name: 'Gesture Choreography', id: 'gesture-choreography', selector: '.gesture-choreography-panel' }
    ];

    constructor(container: HTMLElement) {
        this.container = container;
        this.createToolbar();
    }

    private createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'panel-toolbar';
        toolbar.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px;
            display: flex;
            gap: 8px;
            align-items: center;
            z-index: 10000;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 11px;
            color: #ffffff;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
            max-width: calc(100vw - 40px);
            overflow-x: auto;
            flex-wrap: wrap;
            justify-content: center;
        `;

        // Add "VIEW:" label
        const label = document.createElement('span');
        label.textContent = 'VIEW:';
        label.style.cssText = `
            color: rgba(255, 255, 255, 0.6);
            font-weight: 500;
            font-size: 10px;
            margin-right: 4px;
        `;
        toolbar.appendChild(label);

        // Create toggle buttons for each panel
        this.panels.forEach(panel => {
            const button = document.createElement('button');
            button.id = `toggle-${panel.id}`;
            button.textContent = panel.name;
            button.style.cssText = this.getButtonStyle(this.isPanelVisible(panel.selector));

            button.onclick = () => {
                console.log(`🔘 Toolbar button clicked: ${panel.name} (${panel.selector})`);

                const element = document.querySelector(panel.selector);
                console.log(`🔍 Found element:`, element);

                const wasVisible = this.isPanelVisible(panel.selector);
                console.log(`👁️ Panel was visible: ${wasVisible}`);

                this.togglePanel(panel.selector);
                this.updateButtonState(button, panel.selector);

                mmpaLogger.logPanelToggle(panel.name, !wasVisible);

                console.log(`✅ Toggle completed for: ${panel.name}`);
            };

            toolbar.appendChild(button);
            console.log('🔧 Created toolbar button:', panel.name, 'ID:', button.id, 'Selector:', panel.selector);
        });

        this.container.appendChild(toolbar);
        this.toolbarElement = toolbar;

        // Update button states initially
        this.updateAllButtonStates();

        // Listen for panel close events
        window.addEventListener('panelClosed', (event: any) => {
            this.refreshButtonStates();
        });
    }

    private getButtonStyle(isActive: boolean): string {
        return `
            background: ${isActive ? 'rgba(59, 130, 246, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
            border: 1px solid ${isActive ? 'rgba(59, 130, 246, 0.6)' : 'rgba(255, 255, 255, 0.2)'};
            color: ${isActive ? '#60a5fa' : 'rgba(255, 255, 255, 0.8)'};
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
            font-family: inherit;
            font-weight: 500;
            transition: all 0.2s ease;
            white-space: nowrap;
        `;
    }

    private isPanelVisible(selector: string): boolean {
        const element = document.querySelector(selector) as HTMLElement;
        if (!element) return false;

        // Check both display style and computed style
        const style = window.getComputedStyle(element);
        const inlineDisplay = element.style.display;

        // Special case for morph box panel
        if (selector === '#morph-box-panel') {
            return element.classList.contains('active');
        }

        // Special case for cymatic patterns panel
        if (selector === '.cymatic-patterns-panel') {
            // Check if panel has its own visibility state
            const panelInstance = (window as any).cymaticPatternsPanel;
            if (panelInstance && panelInstance.isPanelVisible) {
                return panelInstance.isPanelVisible();
            }
        }

        return inlineDisplay !== 'none' && style.display !== 'none';
    }

    private togglePanel(selector: string): void {
        console.log(`🔄 togglePanel called for: ${selector}`);

        const element = document.querySelector(selector) as HTMLElement;
        if (!element) {
            console.error(`❌ Element not found: ${selector}`);
            return;
        }

        const isVisible = this.isPanelVisible(selector);
        console.log(`👁️ isVisible result: ${isVisible}`);

        // Special handling for morph box panel
        if (selector === '#morph-box-panel') {
            if (isVisible) {
                element.classList.remove('active');
                element.style.display = 'none';
            } else {
                element.classList.add('active');
                element.style.display = 'block';
            }
        }
        // Special handling for cymatic patterns panel
        else if (selector === '.cymatic-patterns-panel') {
            console.log(`🌀 Cymatic patterns panel toggle`);
            const panelInstance = (window as any).cymaticPatternsPanel;
            console.log(`📦 Panel instance:`, panelInstance);

            if (panelInstance && panelInstance.setVisibility) {
                console.log(`✨ Calling setVisibility(${!isVisible})`);
                panelInstance.setVisibility(!isVisible);
            } else {
                console.log(`🔄 Fallback DOM manipulation`);
                element.style.display = isVisible ? 'none' : 'block';
            }
        }
        else {
            // Standard show/hide
            element.style.display = isVisible ? 'none' : 'block';
        }
    }

    private updateButtonState(button: HTMLButtonElement, selector: string): void {
        const isVisible = this.isPanelVisible(selector);
        button.style.cssText = this.getButtonStyle(isVisible);
    }

    private updateAllButtonStates(): void {
        this.panels.forEach(panel => {
            const button = document.getElementById(`toggle-${panel.id}`) as HTMLButtonElement;
            if (button) {
                this.updateButtonState(button, panel.selector);
            }
        });
    }

    public showPanel(selector: string): void {
        const element = document.querySelector(selector) as HTMLElement;
        if (!element) return;

        if (selector === '#morph-box-panel') {
            element.classList.add('active');
            element.style.display = 'block';
        } else {
            element.style.display = 'block';
        }

        this.updateAllButtonStates();
    }

    public hidePanel(selector: string): void {
        const element = document.querySelector(selector) as HTMLElement;
        if (!element) return;

        if (selector === '#morph-box-panel') {
            element.classList.remove('active');
            element.style.display = 'none';
        } else {
            element.style.display = 'none';
        }

        this.updateAllButtonStates();
    }

    public hideAllPanels(): void {
        this.panels.forEach(panel => {
            this.hidePanel(panel.selector);
        });
    }

    public showAllPanels(): void {
        this.panels.forEach(panel => {
            this.showPanel(panel.selector);
        });
    }

    // Method to be called when panels are toggled externally
    public refreshButtonStates(): void {
        this.updateAllButtonStates();
    }

    public setToolbarVisibility(visible: boolean): void {
        if (this.toolbarElement) {
            this.toolbarElement.style.display = visible ? 'flex' : 'none';
        }
    }
}
