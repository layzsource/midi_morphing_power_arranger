/**
 * Main Display Panel - Skybox Cube Controls
 *
 * UI Controls for the SkyboxCubeLayer system with:
 * - Dual-Mode Loading (JSON/Folder)
 * - Geometry Morphing Controls (Cube/Sphere)
 * - 12-Tone Fractal Mode Toggle
 * - Save/Load Configuration System
 * - Smart Filename Recognition
 */

import { SkyboxCubeLayer } from '../layers/SkyboxCubeLayer';

export class MainDisplayPanel {
    private container: HTMLElement;
    private skyboxLayer: SkyboxCubeLayer;
    private panelElement: HTMLElement | null = null;

    constructor(container: HTMLElement, skyboxLayer: SkyboxCubeLayer) {
        this.container = container;
        this.skyboxLayer = skyboxLayer;
        this.createPanel();
    }

    private createPanel(): void {
        const panel = document.createElement('div');
        panel.className = 'main-display-panel';
        panel.id = 'main-display-panel';
        panel.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            width: 300px;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            color: #ffffff;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            z-index: 20;
            display: none;
        `;

        // Panel Header with collapse functionality
        const header = document.createElement('div');
        header.style.cssText = 'cursor: pointer; display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);';
        header.innerHTML = `
            <h3 style="margin: 0; color: #00ffff; font-size: 16px; font-weight: 600;">
                🌀 Skybox Cube Controls
            </h3>
            <span id="skybox-collapse-icon" style="color: rgba(255,255,255,0.6); font-size: 14px;">▼</span>
        `;

        // Add collapse functionality
        let isCollapsed = false;
        header.addEventListener('click', () => {
            isCollapsed = !isCollapsed;
            const icon = header.querySelector('#skybox-collapse-icon');
            const content = panel.querySelector('.skybox-content');
            if (content && icon) {
                if (isCollapsed) {
                    content.style.display = 'none';
                    icon.textContent = '▶';
                } else {
                    content.style.display = 'block';
                    icon.textContent = '▼';
                }
            }
        });
        panel.appendChild(header);

        // Content container for collapsible sections
        const contentContainer = document.createElement('div');
        contentContainer.className = 'skybox-content';
        contentContainer.style.cssText = 'display: block;';

        // HAL Orb Section (Green Bean/Heart)
        const halSection = this.createHALOrbSection();
        contentContainer.appendChild(halSection);

        // Geometry Controls Section
        const geometrySection = this.createGeometrySection();
        contentContainer.appendChild(geometrySection);

        // Mode Controls Section
        const modeSection = this.createModeSection();
        contentContainer.appendChild(modeSection);

        // Load/Save Section
        const loadSaveSection = this.createLoadSaveSection();
        contentContainer.appendChild(loadSaveSection);

        // Wizard Spells Section
        const spellsSection = this.createWizardSpellsSection();
        contentContainer.appendChild(spellsSection);

        panel.appendChild(contentContainer);

        this.container.appendChild(panel);
        this.panelElement = panel;

        console.log('🌀 MainDisplayPanel created for skybox controls');
        console.log('🔍 Panel ID:', panel.id);
        console.log('🔍 Panel in DOM:', document.getElementById('main-display-panel') !== null);
    }

    private createGeometrySection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = 'margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1);';

        section.innerHTML = `
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 6px; font-size: 12px; color: rgba(255,255,255,0.8);">
                    🌀 Geometry Morph (Cube ↔ Sphere)
                </label>
                <input type="range" id="geometry-morph-slider" min="0" max="100" value="0"
                       style="width: 100%; margin-bottom: 6px;">
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: rgba(255,255,255,0.6);">
                    <span>CUBE (0%)</span>
                    <span id="morph-progress">0%</span>
                    <span>SPHERE (100%)</span>
                </div>
            </div>

            <div style="display: flex; gap: 8px; margin-top: 12px;">
                <button id="reset-cube-btn" style="flex: 1; padding: 8px; background: rgba(255,0,0,0.2); border: 1px solid rgba(255,0,0,0.4); border-radius: 6px; color: #ff4444; font-size: 12px; cursor: pointer;">
                    🎯 Reset Cube
                </button>
                <button id="full-sphere-btn" style="flex: 1; padding: 8px; background: rgba(0,255,0,0.2); border: 1px solid rgba(0,255,0,0.4); border-radius: 6px; color: #44ff44; font-size: 12px; cursor: pointer;">
                    🌍 Full Sphere
                </button>
            </div>
        `;

        // Connect geometry controls
        const slider = section.querySelector('#geometry-morph-slider') as HTMLInputElement;
        const progressLabel = section.querySelector('#morph-progress') as HTMLElement;
        const resetBtn = section.querySelector('#reset-cube-btn') as HTMLButtonElement;
        const sphereBtn = section.querySelector('#full-sphere-btn') as HTMLButtonElement;

        slider.addEventListener('input', () => {
            const progress = parseInt(slider.value) / 100;
            this.skyboxLayer.setMorphProgress(progress);
            progressLabel.textContent = `${slider.value}%`;
        });

        resetBtn.addEventListener('click', () => {
            slider.value = '0';
            this.skyboxLayer.setMorphProgress(0);
            progressLabel.textContent = '0%';
        });

        sphereBtn.addEventListener('click', () => {
            slider.value = '100';
            this.skyboxLayer.setMorphProgress(1);
            progressLabel.textContent = '100%';
        });

        return section;
    }

    private createModeSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = 'margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1);';

        section.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <label style="font-size: 12px; color: rgba(255,255,255,0.8);">
                    🎵 12-Tone Fractal Mode
                </label>
                <label style="position: relative; display: inline-block; width: 50px; height: 24px;">
                    <input type="checkbox" id="fractal-mode-toggle" style="opacity: 0; width: 0; height: 0;">
                    <span style="position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.2); border-radius: 24px; transition: 0.3s;">
                        <span style="position: absolute; content: ''; height: 18px; width: 18px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.3s;"></span>
                    </span>
                </label>
            </div>

            <div id="chromatic-grid" style="display: none; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 12px;">
                ${this.skyboxLayer.getChromaticNotes().map(note => `
                    <button class="note-btn" data-note="${note}" style="padding: 6px; background: rgba(${this.getNoteColorRGB(note)}, 0.3); border: 1px solid rgba(${this.getNoteColorRGB(note)}, 0.6); border-radius: 4px; color: white; font-size: 11px; cursor: pointer; transition: all 0.2s;">
                        ${note}
                    </button>
                `).join('')}
            </div>
        `;

        // Connect mode controls
        const toggle = section.querySelector('#fractal-mode-toggle') as HTMLInputElement;
        const grid = section.querySelector('#chromatic-grid') as HTMLElement;
        const noteButtons = section.querySelectorAll('.note-btn') as NodeListOf<HTMLButtonElement>;

        toggle.addEventListener('change', () => {
            this.skyboxLayer.handleMicrotonalMorph(toggle.checked);
            grid.style.display = toggle.checked ? 'grid' : 'none';
        });

        noteButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const note = btn.getAttribute('data-note');
                if (note) {
                    this.skyboxLayer.castWizardSpell('chromatic_resonance', { note });
                }
            });
        });

        return section;
    }

    private createLoadSaveSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = 'margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1);';

        section.innerHTML = `
            <div style="margin-bottom: 12px;">
                <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                    <button id="load-json-btn" style="flex: 1; padding: 10px; background: rgba(0,150,255,0.2); border: 1px solid rgba(0,150,255,0.4); border-radius: 6px; color: #0096ff; font-size: 12px; cursor: pointer;">
                        📁 Load JSON
                    </button>
                    <button id="save-json-btn" style="flex: 1; padding: 10px; background: rgba(255,150,0,0.2); border: 1px solid rgba(255,150,0,0.4); border-radius: 6px; color: #ff9600; font-size: 12px; cursor: pointer;">
                        💾 Save JSON
                    </button>
                </div>

                <button id="load-folder-btn" style="width: 100%; padding: 10px; background: rgba(150,0,255,0.2); border: 1px solid rgba(150,0,255,0.4); border-radius: 6px; color: #9600ff; font-size: 12px; cursor: pointer; margin-bottom: 8px;">
                    📂 Load Image Folder
                </button>

                <div style="font-size: 11px; color: rgba(255,255,255,0.6); line-height: 1.3;">
                    💡 Folder mode: Use filenames like floor.jpg, north.png, east.gif, etc.
                </div>
            </div>

            <input type="file" id="json-file-input" accept=".json" style="display: none;">
            <input type="file" id="folder-file-input" accept="image/*" multiple style="display: none;">
        `;

        // Connect load/save controls
        const loadJsonBtn = section.querySelector('#load-json-btn') as HTMLButtonElement;
        const saveJsonBtn = section.querySelector('#save-json-btn') as HTMLButtonElement;
        const loadFolderBtn = section.querySelector('#load-folder-btn') as HTMLButtonElement;
        const jsonInput = section.querySelector('#json-file-input') as HTMLInputElement;
        const folderInput = section.querySelector('#folder-file-input') as HTMLInputElement;

        loadJsonBtn.addEventListener('click', () => jsonInput.click());
        loadFolderBtn.addEventListener('click', () => folderInput.click());

        jsonInput.addEventListener('change', async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
                try {
                    const text = await file.text();
                    const config = JSON.parse(text);
                    await this.skyboxLayer.importSkyboxConfiguration(config);
                    console.log('✅ JSON configuration loaded');
                } catch (error) {
                    console.error('❌ Failed to load JSON:', error);
                }
            }
        });

        folderInput.addEventListener('change', async (e) => {
            const files = Array.from((e.target as HTMLInputElement).files || []);
            if (files.length > 0) {
                await this.skyboxLayer.loadSkyboxFromImageFiles(files);
            }
        });

        saveJsonBtn.addEventListener('click', () => {
            const config = this.skyboxLayer.exportSkyboxConfiguration();
            const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `skybox-config-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            console.log('💾 Configuration saved');
        });

        return section;
    }

    private createWizardSpellsSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = 'margin-bottom: 16px;';

        section.innerHTML = `
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 8px; font-size: 12px; color: rgba(255,255,255,0.8);">
                    🧙 Wizard Spells
                </label>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px;">
                    <button class="spell-btn" data-spell="fibonacci_recursion" style="padding: 8px; background: rgba(255,0,255,0.2); border: 1px solid rgba(255,0,255,0.4); border-radius: 4px; color: #ff00ff; font-size: 11px; cursor: pointer;">
                        🌀 Fibonacci
                    </button>
                    <button class="spell-btn" data-spell="consciousness_navigation" style="padding: 8px; background: rgba(0,255,255,0.2); border: 1px solid rgba(0,255,255,0.4); border-radius: 4px; color: #00ffff; font-size: 11px; cursor: pointer;">
                        🧠 Navigate
                    </button>
                    <button class="spell-btn" data-spell="emergence_detection" style="padding: 8px; background: rgba(255,255,0,0.2); border: 1px solid rgba(255,255,0,0.4); border-radius: 4px; color: #ffff00; font-size: 11px; cursor: pointer;">
                        🔍 Emergence
                    </button>
                    <button class="spell-btn" data-spell="chromatic_resonance" style="padding: 8px; background: rgba(0,255,0,0.2); border: 1px solid rgba(0,255,0,0.4); border-radius: 4px; color: #00ff00; font-size: 11px; cursor: pointer;">
                        🎵 Resonance
                    </button>
                </div>
            </div>
        `;

        // Connect wizard spell buttons
        const spellButtons = section.querySelectorAll('.spell-btn') as NodeListOf<HTMLButtonElement>;
        spellButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const spell = btn.getAttribute('data-spell');
                if (spell) {
                    this.skyboxLayer.castWizardSpell(spell);
                    console.log(`🧙 Cast spell: ${spell}`);
                }
            });
        });

        return section;
    }

    private createHALOrbSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = 'margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1);';

        section.innerHTML = `
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 8px; font-size: 12px; color: rgba(255,255,255,0.8);">
                    🫘 HAL Orb (Green Bean/Heart)
                </label>
                <div id="hal-orb-container" style="display: flex; align-items: center; justify-content: center; height: 80px; background: rgba(0,255,0,0.1); border: 1px solid rgba(0,255,0,0.3); border-radius: 8px; margin-bottom: 8px; position: relative; overflow: hidden;">
                    <div id="hal-orb" style="width: 40px; height: 40px; background: radial-gradient(circle, #00ff41, #00aa2a); border-radius: 50%; transition: all 0.3s ease; animation: hal-pulse 2s infinite;"></div>
                </div>
                <div style="display: flex; gap: 6px;">
                    <button id="hal-proximity-btn" style="flex: 1; padding: 6px; background: rgba(0,255,0,0.2); border: 1px solid rgba(0,255,0,0.4); border-radius: 4px; color: #00ff41; font-size: 11px; cursor: pointer;">
                        🫶 Proximity Mode
                    </button>
                    <button id="hal-morph-btn" style="flex: 1; padding: 6px; background: rgba(0,255,0,0.2); border: 1px solid rgba(0,255,0,0.4); border-radius: 4px; color: #00ff41; font-size: 11px; cursor: pointer;">
                        🌀 Morph Respond
                    </button>
                </div>
                <style>
                    @keyframes hal-pulse {
                        0%, 100% { transform: scale(1); opacity: 0.8; }
                        50% { transform: scale(1.1); opacity: 1; }
                    }
                </style>
            </div>
        `;

        // Connect HAL orb controls
        const proximityBtn = section.querySelector('#hal-proximity-btn') as HTMLButtonElement;
        const morphBtn = section.querySelector('#hal-morph-btn') as HTMLButtonElement;
        const orb = section.querySelector('#hal-orb') as HTMLElement;

        proximityBtn.addEventListener('click', () => {
            this.skyboxLayer.castWizardSpell('consciousness_navigation', { mode: 'proximity' });
            orb.style.animation = 'hal-pulse 1s infinite';
            console.log('🫘 HAL orb proximity mode activated');
        });

        morphBtn.addEventListener('click', () => {
            this.skyboxLayer.castWizardSpell('emergence_detection', { hal: 'morph_respond' });
            orb.style.animation = 'hal-pulse 0.5s infinite';
            console.log('🫘 HAL orb morph response mode activated');
        });

        return section;
    }

    private getNoteColorRGB(note: string): string {
        const colorMap = new Map([
            ['C', '255,0,0'],     ['C#', '255,64,0'],   ['D', '255,128,0'],   ['D#', '255,191,0'],
            ['E', '255,255,0'],   ['F', '191,255,0'],   ['F#', '128,255,0'],  ['G', '64,255,0'],
            ['G#', '0,255,0'],    ['A', '0,255,128'],   ['A#', '0,255,191'],  ['B', '0,255,255']
        ]);
        return colorMap.get(note) || '255,255,255';
    }

    public show(): void {
        if (this.panelElement) {
            this.panelElement.style.display = 'block';
        }
    }

    public hide(): void {
        if (this.panelElement) {
            this.panelElement.style.display = 'none';
        }
    }

    public toggle(): void {
        if (this.panelElement) {
            const isVisible = this.panelElement.style.display !== 'none';
            this.panelElement.style.display = isVisible ? 'none' : 'block';
        }
    }

    public dispose(): void {
        if (this.panelElement) {
            this.panelElement.remove();
            this.panelElement = null;
        }
    }
}

// Factory function for easy integration
export function createMainDisplayPanel(container: HTMLElement, skyboxLayer: SkyboxCubeLayer): MainDisplayPanel {
    console.log('🌀 Creating MainDisplayPanel for skybox controls...');
    return new MainDisplayPanel(container, skyboxLayer);
}