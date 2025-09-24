import { MMPAEngine } from '../mmpa-engine';

export class PanelImageControls {
    private container: HTMLElement;
    private engine: MMPAEngine;

    // Panel file inputs
    private floorImageInput!: HTMLInputElement;
    private ceilingImageInput!: HTMLInputElement;
    private northImageInput!: HTMLInputElement;
    private southImageInput!: HTMLInputElement;
    private eastImageInput!: HTMLInputElement;
    private westImageInput!: HTMLInputElement;

    // Panel fit selectors
    private floorFitSelect!: HTMLSelectElement;
    private ceilingFitSelect!: HTMLSelectElement;
    private northFitSelect!: HTMLSelectElement;
    private southFitSelect!: HTMLSelectElement;
    private eastFitSelect!: HTMLSelectElement;
    private westFitSelect!: HTMLSelectElement;

    // Control buttons
    private clearAllImagesButton!: HTMLButtonElement;
    private resetToCubeButton!: HTMLButtonElement;

    // Panel mapping
    private panelInputs: { [key: string]: HTMLInputElement } = {};
    private panelFitSelectors: { [key: string]: HTMLSelectElement } = {};

    constructor(container: HTMLElement, engine: MMPAEngine) {
        this.container = container;
        this.engine = engine;
        this.initializeControls();
        this.setupEventListeners();
    }

    private initializeControls(): void {
        // Get panel file inputs
        this.floorImageInput = document.getElementById('floor-image') as HTMLInputElement;
        this.ceilingImageInput = document.getElementById('ceiling-image') as HTMLInputElement;
        this.northImageInput = document.getElementById('north-image') as HTMLInputElement;
        this.southImageInput = document.getElementById('south-image') as HTMLInputElement;
        this.eastImageInput = document.getElementById('east-image') as HTMLInputElement;
        this.westImageInput = document.getElementById('west-image') as HTMLInputElement;

        // Get panel fit selectors
        this.floorFitSelect = document.getElementById('floor-fit') as HTMLSelectElement;
        this.ceilingFitSelect = document.getElementById('ceiling-fit') as HTMLSelectElement;
        this.northFitSelect = document.getElementById('north-fit') as HTMLSelectElement;
        this.southFitSelect = document.getElementById('south-fit') as HTMLSelectElement;
        this.eastFitSelect = document.getElementById('east-fit') as HTMLSelectElement;
        this.westFitSelect = document.getElementById('west-fit') as HTMLSelectElement;

        // Get control buttons
        this.clearAllImagesButton = document.getElementById('clear-all-images') as HTMLButtonElement;
        this.resetToCubeButton = document.getElementById('reset-to-cube') as HTMLButtonElement;

        // Map panel inputs for easier access
        this.panelInputs = {
            'floor': this.floorImageInput,      // Panel 0 - White
            'ceiling': this.ceilingImageInput,  // Panel 1 - Blue
            'north': this.northImageInput,      // Panel 2 - Red
            'south': this.southImageInput,      // Panel 3 - Green
            'east': this.eastImageInput,        // Panel 4 - Yellow
            'west': this.westImageInput         // Panel 5 - Magenta
        };

        // Map panel fit selectors for easier access
        this.panelFitSelectors = {
            'floor': this.floorFitSelect,
            'ceiling': this.ceilingFitSelect,
            'north': this.northFitSelect,
            'south': this.southFitSelect,
            'east': this.eastFitSelect,
            'west': this.westFitSelect
        };
    }

    private setupEventListeners(): void {
        // Set up file input listeners for each panel
        Object.entries(this.panelInputs).forEach(([panelName, input]) => {
            input.addEventListener('change', (e) => {
                this.handlePanelImageChange(panelName, e.target as HTMLInputElement);
            });
        });

        // Set up fit selector listeners for each panel
        Object.entries(this.panelFitSelectors).forEach(([panelName, selector]) => {
            selector.addEventListener('change', (e) => {
                this.handlePanelFitChange(panelName, e.target as HTMLSelectElement);
            });
        });

        // Clear all images button
        this.clearAllImagesButton.addEventListener('click', () => {
            this.clearAllImages();
        });

        // Reset to cube button
        this.resetToCubeButton.addEventListener('click', () => {
            this.resetToCube();
        });
    }

    private async handlePanelImageChange(panelName: string, input: HTMLInputElement): Promise<void> {
        const file = input.files?.[0];
        if (!file) return;

        try {
            console.log(`Loading image for ${panelName} panel:`, file.name);

            // Create object URL for the file
            const imageUrl = URL.createObjectURL(file);

            // Get the skybox layer
            const skyboxLayer = this.engine.getSkyboxLayer();
            if (!skyboxLayer) {
                console.error('Skybox layer not available');
                return;
            }

            // Map panel names to indices (matching PERIAKTOS configuration)
            const panelIndexMap: { [key: string]: number } = {
                'floor': 0,    // White - Floor
                'ceiling': 1,  // Blue - Ceiling
                'north': 2,    // Red - North
                'south': 3,    // Green - South
                'east': 4,     // Yellow - East
                'west': 5      // Magenta - West
            };

            const panelIndex = panelIndexMap[panelName];
            if (panelIndex === undefined) {
                console.error(`Unknown panel: ${panelName}`);
                return;
            }

            // Get the current fit mode
            const fitMode = this.panelFitSelectors[panelName]?.value || 'cover';

            // Apply image to the specific panel with fit mode
            if (skyboxLayer.setPanelTexture) {
                await skyboxLayer.setPanelTexture(panelIndex, imageUrl, fitMode);
                console.log(`✅ Applied image to ${panelName} panel (index ${panelIndex}) with fit: ${fitMode}`);

                // Show feedback
                this.showFeedback(`Image applied to ${panelName.toUpperCase()} panel (${fitMode})`);
            } else {
                console.error('setPanelTexture method not available on skybox layer');
            }

        } catch (error) {
            console.error(`Error loading image for ${panelName}:`, error);
            this.showFeedback(`Error loading ${panelName} image`, true);
        }
    }

    private handlePanelFitChange(panelName: string, selector: HTMLSelectElement): void {
        const fitMode = selector.value;
        console.log(`Fit mode changed for ${panelName}: ${fitMode}`);

        // If panel has an image, reapply it with the new fit mode
        const input = this.panelInputs[panelName];
        if (input?.files && input.files[0]) {
            this.handlePanelImageChange(panelName, input);
        }

        // Show feedback
        this.showFeedback(`${panelName.toUpperCase()} fit mode: ${fitMode}`);
    }

    private clearAllImages(): void {
        console.log('Clearing all panel images...');

        // Clear all file inputs
        Object.values(this.panelInputs).forEach(input => {
            input.value = '';
        });

        // Clear textures from all panels
        const skyboxLayer = this.engine.getSkyboxLayer();
        if (skyboxLayer && skyboxLayer.clearAllPanelTextures) {
            skyboxLayer.clearAllPanelTextures();
            console.log('✅ All panel textures cleared');
            this.showFeedback('All panel images cleared');
        } else if (skyboxLayer && skyboxLayer.setPanelTexture) {
            // Clear each panel individually if no bulk clear method
            for (let i = 0; i < 6; i++) {
                skyboxLayer.setPanelTexture(i, null);
            }
            console.log('✅ All panel textures cleared individually');
            this.showFeedback('All panel images cleared');
        }
    }

    private resetToCube(): void {
        console.log('Resetting to original cube shape...');

        const skyboxLayer = this.engine.getSkyboxLayer();
        if (!skyboxLayer) {
            console.error('Skybox layer not available');
            return;
        }

        try {
            // Reset morphing to 0
            if (skyboxLayer.morphPanelSquareToCircle) {
                skyboxLayer.morphPanelSquareToCircle(0);
            }

            // Reset any rotations
            if (skyboxLayer.resetRotation) {
                skyboxLayer.resetRotation();
            }

            // Reset to original panel positions and shapes
            if (skyboxLayer.resetToOriginalShape) {
                skyboxLayer.resetToOriginalShape();
            } else {
                // Fallback: reinitialize the panel system
                if (skyboxLayer.initPanelSystem) {
                    skyboxLayer.initPanelSystem();
                }
            }

            console.log('✅ Reset to original cube shape');
            this.showFeedback('Reset to original cube shape');

        } catch (error) {
            console.error('Error resetting cube:', error);
            this.showFeedback('Error resetting cube', true);
        }
    }

    private showFeedback(message: string, isError: boolean = false): void {
        // Create temporary feedback element
        const feedback = document.createElement('div');
        feedback.textContent = message;
        feedback.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: ${isError ? 'rgba(255, 64, 64, 0.1)' : 'rgba(0, 255, 255, 0.1)'};
            color: ${isError ? '#ff6b6b' : '#00ffff'};
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid ${isError ? 'rgba(255, 107, 107, 0.3)' : 'rgba(0, 255, 255, 0.3)'};
            font-size: 14px;
            font-weight: 500;
            z-index: 1000;
            backdrop-filter: blur(10px);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        document.body.appendChild(feedback);

        // Animate in
        requestAnimationFrame(() => {
            feedback.style.opacity = '1';
        });

        // Remove after 2 seconds
        setTimeout(() => {
            feedback.style.opacity = '0';
            setTimeout(() => {
                if (feedback.parentNode) {
                    document.body.removeChild(feedback);
                }
            }, 300);
        }, 2000);
    }

    // Public methods for external control
    public clearPanel(panelName: string): void {
        const input = this.panelInputs[panelName];
        if (input) {
            input.value = '';

            const skyboxLayer = this.engine.getSkyboxLayer();
            const panelIndexMap: { [key: string]: number } = {
                'floor': 0, 'ceiling': 1, 'north': 2, 'south': 3, 'east': 4, 'west': 5
            };

            const panelIndex = panelIndexMap[panelName];
            if (panelIndex !== undefined && skyboxLayer && skyboxLayer.setPanelTexture) {
                // Clear texture (null will restore original color)
                skyboxLayer.setPanelTexture(panelIndex, null);
                console.log(`Cleared ${panelName} panel and restored original color`);
            }
        }
    }

    public async setPanelImage(panelName: string, imageUrl: string): Promise<void> {
        const skyboxLayer = this.engine.getSkyboxLayer();
        if (!skyboxLayer || !skyboxLayer.setPanelTexture) return;

        const panelIndexMap: { [key: string]: number } = {
            'floor': 0, 'ceiling': 1, 'north': 2, 'south': 3, 'east': 4, 'west': 5
        };

        const panelIndex = panelIndexMap[panelName];
        if (panelIndex !== undefined) {
            await skyboxLayer.setPanelTexture(panelIndex, imageUrl);
        }
    }
}