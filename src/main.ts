import * as THREE from 'three';
import { MMPAEngine } from './mmpa-engine';
import { ShadowMicroficheInterface } from './ui/ShadowMicroficheInterface';
import { AcidReignVJInterface } from './performance/AcidReignVJInterface';

const container = document.getElementById('canvas-container')!;
const engine = new MMPAEngine(container);

// Initialize Shadow Microfiche Interface
const microficheInterface = new ShadowMicroficheInterface(container, engine);

// Initialize Acid Reign VJ Interface
const acidReignVJ = new AcidReignVJInterface(container, engine, microficheInterface);

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
    });
});

// Vessel motion toggle
const vesselMotionToggle = document.getElementById('vessel-motion-toggle')!;
let vesselMotionEnabled = false;

// Morph box toggle
const morphBoxToggle = document.getElementById('morph-box-toggle')!;
const morphBoxPanel = document.getElementById('morph-box-panel')!;
const morphCanvasContainer = document.getElementById('morph-canvas-container')!;
const midiRoutingText = document.getElementById('midi-routing-text')!;
let morphBoxEnabled = false;

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

// Morph box toggle functionality
morphBoxToggle.addEventListener('click', () => {
    morphBoxEnabled = !morphBoxEnabled;

    if (morphBoxEnabled) {
        morphBoxPanel.classList.add('active');
        engine.enableMorphBox(morphCanvasContainer);
        midiRoutingText.textContent = 'Morph Box Panel (Box ON)';
        midiRoutingText.style.color = '#00ff80';
    } else {
        morphBoxPanel.classList.remove('active');
        engine.disableMorphBox();
        midiRoutingText.textContent = 'Main Scene (Box OFF)';
        midiRoutingText.style.color = 'rgba(255,255,255,0.6)';
    }

    morphBoxToggle.textContent = morphBoxEnabled ?
        '📦 Morph Box: ON' :
        '📦 Morph Box: OFF';

    morphBoxToggle.style.background = morphBoxEnabled ?
        'linear-gradient(135deg, #2196f3, #9c27b0)' :
        'rgba(255, 255, 255, 0.05)';

    morphBoxToggle.style.borderColor = morphBoxEnabled ?
        'transparent' :
        'rgba(255, 255, 255, 0.1)';

    morphBoxToggle.style.boxShadow = morphBoxEnabled ?
        '0 4px 16px rgba(33, 150, 243, 0.3)' :
        'none';
});

// Controls collapse/expand functionality
const controlsToggle = document.getElementById('controls-toggle')!;
const controlsContent = document.getElementById('controls-content')!;
let controlsCollapsed = false;

controlsToggle.addEventListener('click', () => {
    controlsCollapsed = !controlsCollapsed;

    if (controlsCollapsed) {
        controlsContent.style.display = 'none';
        controlsToggle.textContent = '⬆️';
        controlsToggle.title = 'Expand controls';
    } else {
        controlsContent.style.display = 'block';
        controlsToggle.textContent = '⬇️';
        controlsToggle.title = 'Collapse controls';
    }
});

// Start the engine
engine.start();

// Handle window resize
window.addEventListener('resize', () => {
    engine.resize();
});

// Keyboard controls for live performance
document.addEventListener('keydown', async (event) => {
    // Handle microfiche interface controls first
    if (event.key === 'ArrowLeft') {
        const controls = microficheInterface.getCurrentControls();
        microficheInterface.setViewAngle(Math.max(0, (controls.viewAngle * 180 / Math.PI) - 5));
        return;
    }
    if (event.key === 'ArrowRight') {
        const controls = microficheInterface.getCurrentControls();
        microficheInterface.setViewAngle(Math.min(360, (controls.viewAngle * 180 / Math.PI) + 5));
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

    // VJ Interface controls
    if (event.key === 'v' || event.key === 'V') {
        acidReignVJ.setPerformanceMode(!acidReignVJ.getPerformanceState().freezeFrame);
        return;
    }

    // Hide/show all UIs (H key)
    if (event.key === 'h' || event.key === 'H') {
        const allUIs = [
            document.getElementById('controls'),
            document.querySelector('.shadow-microfiche-interface'),
            document.querySelector('.acid-reign-vj-interface')
        ];

        allUIs.forEach(ui => {
            if (ui) {
                const isHidden = (ui as HTMLElement).style.display === 'none';
                (ui as HTMLElement).style.display = isHidden ? 'block' : 'none';
            }
        });
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