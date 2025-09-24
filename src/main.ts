import * as THREE from 'three';
import { MMPAEngine } from './mmpa-engine';
import { ShadowMicroficheInterface } from './ui/ShadowMicroficheInterface';
import { AcidReignVJInterface } from './performance/AcidReignVJInterface';
import { SpaceMorphToolbox } from './ui/SpaceMorphToolbox';
import { VirtualMIDIKeyboard } from './ui/VirtualMIDIKeyboard';
import { AudioInputSelector } from './ui/AudioInputSelector';
import { PanelToolbar } from './ui/PanelToolbar';
import { MicrotonalMorphControls } from './ui/MicrotonalMorphControls';
import { GlobalMorphControls } from './ui/GlobalMorphControls';
import { PanelImageControls } from './ui/PanelImageControls';
import { createMainDisplayPanel } from './ui/MainDisplayPanel';
import { GestureChoreographyPanel } from './ui/GestureChoreographyPanel';
import { AdvancedGestureChoreographer } from './input/AdvancedGestureChoreographer';
import { GesturePresetMapper } from './input/GesturePresetMapper';

const container = document.getElementById('canvas-container')!;
const engine = new MMPAEngine(container);

// Initialize Shadow Microfiche Interface
const microficheInterface = new ShadowMicroficheInterface(container, engine);

// Initialize Acid Reign VJ Interface
const acidReignVJ = new AcidReignVJInterface(container, engine, microficheInterface);

// Initialize Virtual MIDI Keyboard
const virtualMIDIKeyboard = new VirtualMIDIKeyboard(container, engine);

// Initialize Audio Input Selector
const audioInputSelector = new AudioInputSelector(container);

// Connect audio analysis to engine
audioInputSelector.getAudioInputManager().onAnalysis((analysis) => {
    engine.processAudioAnalysis(analysis);
});

// Initialize Space Morph Toolbox
const spaceMorphToolbox = new SpaceMorphToolbox(container, engine, microficheInterface, virtualMIDIKeyboard, audioInputSelector);

// Initialize Panel Toolbar
const panelToolbar = new PanelToolbar(container);

// Initialize Microtonal Morph Controls and connect to SkyboxCubeLayer
const skyboxLayer = engine.getSkyboxLayer();
const microtonalMorphControls = new MicrotonalMorphControls(container, skyboxLayer);

// Initialize Main Display Panel (Skybox Controls)
const mainDisplayPanel = createMainDisplayPanel(container, skyboxLayer);

// Initialize Global Morph Controls
const globalMorphControls = new GlobalMorphControls(container, engine);

// Initialize Panel Image Controls
const panelImageControls = new PanelImageControls(container, engine);

// Initialize Gesture Choreography System
const gestureChoreographer = new AdvancedGestureChoreographer();
const gesturePresetMapper = new GesturePresetMapper();
const gestureChoreographyPanel = new GestureChoreographyPanel(gestureChoreographer, gesturePresetMapper);

// Mode switching
const vjBtn = document.getElementById('club-mode')!;
const installationBtn = document.getElementById('installation-mode')!;
const studioBtn = document.getElementById('instrument-mode')!;

const buttons = [vjBtn, installationBtn, studioBtn];
const modes = ['vj', 'installation', 'studio'] as const;

buttons.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        engine.setMode(modes[index]);

        // Show/hide mode-specific UIs
        updateModeSpecificUIs(modes[index]);
    });
});

function updateModeSpecificUIs(mode: string) {
    // Hide all panels first
    panelToolbar.hideAllPanels();

    switch (mode) {
        case 'installation':
            // Space Morph mode - show space tools
            panelToolbar.showPanel('.space-morph-toolbox');
            break;
        case 'vj':
            // VJ mode - show VJ interface and shadow reader
            panelToolbar.showPanel('.acid-reign-vj-interface');
            panelToolbar.showPanel('.shadow-microfiche-interface');
            break;
        case 'studio':
            // Studio mode - show shadow reader and audio tools
            panelToolbar.showPanel('.shadow-microfiche-interface');
            panelToolbar.showPanel('.audio-input-selector');
            break;
    }
}

// Vessel motion toggle
const vesselMotionToggle = document.getElementById('vessel-motion-toggle')!;
let vesselMotionEnabled = false;

// Morph box (always enabled)
const morphBoxPanel = document.getElementById('morph-box-panel')!;
const morphCanvasContainer = document.getElementById('morph-canvas-container')!;
const midiRoutingText = document.getElementById('midi-routing-text')!;
let morphBoxEnabled = true; // Always enabled

vesselMotionToggle.addEventListener('click', () => {
    vesselMotionEnabled = !vesselMotionEnabled;
    engine.setVesselMotion(vesselMotionEnabled);

    vesselMotionToggle.textContent = vesselMotionEnabled ?
        '🎛️ Shadow Morphing: ON' :
        '🎛️ Shadow Morphing: OFF';

    vesselMotionToggle.style.background = vesselMotionEnabled ?
        'linear-gradient(135deg, #2196f3, #9c27b0)' :
        'rgba(255, 255, 255, 0.05)';

    vesselMotionToggle.style.borderColor = vesselMotionEnabled ?
        'transparent' :
        'rgba(255, 255, 255, 0.1)';

    vesselMotionToggle.style.boxShadow = vesselMotionEnabled ?
        '0 4px 16px rgba(33, 150, 243, 0.3)' :
        'none';
});

// Initialize morph box as enabled by default
engine.enableMorphBox(morphCanvasContainer);
midiRoutingText.textContent = 'Morph Box Panel (Always ON)';
midiRoutingText.style.color = '#00ff80';

// Morph box panel now starts hidden like all other panels

// Morph box collapse functionality
const morphBoxCollapse = document.getElementById('morph-box-collapse')!;
const morphBoxHeader = document.getElementById('morph-box-header')!;
let morphBoxCollapsed = false;

morphBoxHeader.addEventListener('click', () => {
    morphBoxCollapsed = !morphBoxCollapsed;

    if (morphBoxCollapsed) {
        morphBoxPanel.classList.add('collapsed');
        morphBoxCollapse.textContent = '▶';
    } else {
        morphBoxPanel.classList.remove('collapsed');
        morphBoxCollapse.textContent = '▼';
    }
});

// Morph box is now always enabled - no toggle needed

// Controls collapse/expand functionality - now completely hides panel
const controlsToggle = document.getElementById('controls-toggle')!;
const controlsPanel = document.getElementById('controls')!;

controlsToggle.addEventListener('click', () => {
    // Hide the entire controls panel
    controlsPanel.style.display = 'none';

    // Update the toolbar button state
    panelToolbar.refreshButtonStates();
});

// Initialize with all panels hidden - clean start
panelToolbar.hideAllPanels();

// Start the engine
engine.start();

// Handle window resize
window.addEventListener('resize', () => {
    engine.resize();
});

// Keyboard controls for live performance
document.addEventListener('keydown', async (event) => {
    const currentMode = engine.getMode();

    // Space Morph toolbox handles keys first (if visible and in installation mode)
    if (currentMode === 'installation' && spaceMorphToolbox.isToolboxVisible()) {
        if (spaceMorphToolbox.handleKeyPress(event.key)) {
            return; // Key was handled by toolbox
        }
    }

    // Handle vessel rotation with arrow keys
    const rotationStep = Math.PI / 24; // 7.5 degrees
    if (event.key === 'ArrowLeft') {
        engine.rotateVessel('y', -rotationStep); // Rotate left around Y axis
        return;
    }
    if (event.key === 'ArrowRight') {
        engine.rotateVessel('y', rotationStep); // Rotate right around Y axis
        return;
    }
    if (event.key === 'ArrowUp') {
        engine.rotateVessel('x', -rotationStep); // Rotate up around X axis
        return;
    }
    if (event.key === 'ArrowDown') {
        engine.rotateVessel('x', rotationStep); // Rotate down around X axis
        return;
    }

    // Handle microfiche interface controls with Shift + Arrow keys
    if (event.shiftKey && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) {
        const controls = microficheInterface.getCurrentControls();
        if (event.key === 'ArrowLeft') {
            microficheInterface.setViewAngle(Math.max(0, (controls.viewAngle * 180 / Math.PI) - 5));
        } else {
            microficheInterface.setViewAngle(Math.min(360, (controls.viewAngle * 180 / Math.PI) + 5));
        }
        return;
    }
    if (event.key >= '0' && event.key <= '5') {
        microficheInterface.setRingIndex(parseInt(event.key));
        return;
    }
    if (event.key === '`' || event.key === '~') {
        microficheInterface.setRingIndex(-1); // All rings
        return;
    }

    // Mode-specific 'v' key handling (fallback if not handled by toolbox)
    if (event.key === 'v' || event.key === 'V') {
        if (currentMode === 'installation') {
            // Space Morph mode - toggle microfiche reader
            const microficheEl = document.querySelector('.shadow-microfiche-interface') as HTMLElement;
            if (microficheEl) {
                const isVisible = microficheEl.style.display !== 'none';
                microficheEl.style.display = isVisible ? 'none' : 'block';
                panelToolbar.refreshButtonStates();
            }
        } else {
            // VJ mode - toggle performance freeze frame
            acidReignVJ.setPerformanceMode(!acidReignVJ.getPerformanceState().freezeFrame);
        }
        return;
    }

    // Hide/show all UIs (H key) - now uses toolbar
    if (event.key === 'h' || event.key === 'H') {
        // Simple toggle - if any panels are visible (except controls), hide all, otherwise show all
        const microfiche = document.querySelector('.shadow-microfiche-interface') as HTMLElement;
        const anyVisible = microfiche && microfiche.style.display !== 'none';

        if (anyVisible) {
            panelToolbar.hideAllPanels();
        } else {
            panelToolbar.showAllPanels();
        }
        return;
    }

    // Regular engine controls
    await engine.handleKeyPress(event.key);
});

// Request MIDI access for performance control
if (navigator.requestMIDIAccess) {
    navigator.requestMIDIAccess().then((midiAccess) => {
        engine.connectMIDI(midiAccess);

        // Connect VJ MIDI controls
        for (const input of midiAccess.inputs.values()) {
            input.addEventListener('midimessage', (event: any) => {
                const [status, ccNumber, value] = event.data;

                // Handle MIDI CC messages (status 176 = CC on channel 1)
                if (status === 176) {
                    acidReignVJ.handleMIDICC(ccNumber, value);
                }
            });
        }

        console.log('🎛️ Acid Reign VJ MIDI interface connected');
    }).catch((error) => {
        console.log('MIDI access denied:', error);
    });
}

