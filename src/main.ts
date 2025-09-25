import * as THREE from 'three';
import { MMPAEngine } from './mmpa-engine';
import { paramGraphUI } from './ui/ParamGraphUI';
import { ShadowMicroficheInterface } from './ui/ShadowMicroficheInterface';
import { AcidReignVJInterface } from './performance/AcidReignVJInterface';
import { SpaceMorphToolbox } from './ui/SpaceMorphToolbox';
import { VirtualMIDIKeyboard } from './ui/VirtualMIDIKeyboard';
import { AudioInputSelector } from './ui/AudioInputSelector';
import { PanelToolbar } from './ui/PanelToolbar';
import { MicrotonalMorphControls } from './ui/MicrotonalMorphControls';
import { GlobalMorphControls } from './ui/GlobalMorphControls';
import { PanelImageControls } from './ui/PanelImageControls';
import { ThereminControlPanel } from './ui/ThereminControlPanel';
import { createMainDisplayPanel } from './ui/MainDisplayPanel';
import { GestureChoreographyPanel } from './ui/GestureChoreographyPanel';
import { AdvancedGestureChoreographer } from './input/AdvancedGestureChoreographer';
import { GesturePresetMapper } from './input/GesturePresetMapper';
import { CymaticPatternsPanel } from './ui/CymaticPatternsPanel';
import { mmpaLogger } from './logging/MMPALogger';

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

/**
 * AUDIO ANALYSIS PIPELINE
 *
 * Flow: BlackHole Audio → AudioInputManager → Analysis Loop → Callbacks
 *
 * 1. Audio comes from BlackHole (Ableton output)
 * 2. AudioInputManager analyzes audio in real-time
 * 3. This callback distributes analysis data to:
 *    - AudioInputSelector (for display)
 *    - MMPA Engine (for visualization)
 *    - Cymatic Panel (for frequency bars)
 */
audioInputSelector.getAudioInputManager().onAnalysis((analysis) => {
    console.log('AUDIO ANALYSIS WORKING:', analysis.rms, analysis.peak);

    // Update everything with audio
    audioInputSelector.updateCurrentAnalysis(analysis);
    engine.processAudioAnalysis(analysis);

    if (analysis.frequency && analysis.frequency.length > 0) {
        const lowFreq = getFrequencyBand(analysis.frequency, 0, 0.2);
        const midFreq = getFrequencyBand(analysis.frequency, 0.2, 0.6);
        const highFreq = getFrequencyBand(analysis.frequency, 0.6, 1.0);
        console.log('FREQ BANDS:', lowFreq, midFreq, highFreq);
        cymaticPatternsPanel.updateFrequencyBars(lowFreq, midFreq, highFreq);
    }
});

// Helper function for frequency band analysis
function getFrequencyBand(frequencyData: Float32Array, startPercent: number, endPercent: number): number {
    const startIndex = Math.floor(startPercent * frequencyData.length);
    const endIndex = Math.floor(endPercent * frequencyData.length);

    let sum = 0;
    let count = 0;

    for (let i = startIndex; i < endIndex && i < frequencyData.length; i++) {
        // Convert from dB to linear scale
        const linearValue = Math.pow(10, frequencyData[i] / 20);
        sum += linearValue;
        count++;
    }

    return count > 0 ? Math.min(sum / count, 1.0) : 0;
}

let audioUnlocked = false;
const unlockAudioContext = async () => {
    if (audioUnlocked) return;
    audioUnlocked = true;
    try {
        await engine.initializeAudio();
        await audioInputSelector.getAudioInputManager().selectAudioSource('internal');
        console.log('🔊 Audio systems unlocked');
        mmpaLogger.logSystemEvent('audio_unlocked', 'Audio context resumed and analyzer started');
    } catch (error) {
        audioUnlocked = false;
        console.error('❌ Audio unlock failed:', error);
        mmpaLogger.logError('Audio unlock failed', 'audio_init');
    }
};

['pointerdown', 'touchstart', 'keydown'].forEach((evt) => {
    window.addEventListener(evt, () => {
        unlockAudioContext();
    }, { once: true, passive: true });
});

// Initialize Space Morph Toolbox
const spaceMorphToolbox = new SpaceMorphToolbox(container, engine, microficheInterface, virtualMIDIKeyboard, audioInputSelector);

// Initialize Cymatic Patterns Panel (MUST be before PanelToolbar)
const cymaticPatternsPanel = new CymaticPatternsPanel();

// Make cymatic panel available to toolbar
(window as any).cymaticPatternsPanel = cymaticPatternsPanel;

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

// Initialize Theremin/Webcam placeholder panel
const thereminControlPanel = new ThereminControlPanel(container, skyboxLayer);

// Initialize ParamGraph UI
paramGraphUI.initialize();

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
    const currentMode = engine.getCurrentMode();

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

/**
 * MIDI PIPELINE
 *
 * Two MIDI systems running in parallel:
 *
 * 1. Web MIDI API (this code):
 *    - Direct hardware MIDI controllers
 *    - Handles CC messages for real-time control
 *
 * 2. WebSocket MIDI (via WebSocketMIDIClient):
 *    - MIDI from Ableton via WebSocket bridge
 *    - Handles both CC and Note messages
 *    - Window focus isolation prevents cross-talk
 *
 * Both systems feed into the same engine.handleMIDIMessage()
 */
if (navigator.requestMIDIAccess) {
    navigator.requestMIDIAccess().then((midiAccess) => {
        engine.connectMIDI(midiAccess);
    }).catch((error) => {
        console.log('MIDI access denied:', error);
        mmpaLogger.logError('MIDI access denied', 'MIDI_initialization');
    });
}

// Complete system initialization
mmpaLogger.completeIteration('MMPA Engine initialization');
mmpaLogger.logSystemEvent('system_ready', 'All components initialized and running');

// Add keyboard shortcut to download session logs (Ctrl+Shift+L)
document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.shiftKey && event.key === 'L') {
        event.preventDefault();
        mmpaLogger.downloadSessionLog();
        mmpaLogger.logSystemEvent('log_download', 'Session log downloaded by user');
    }
});
