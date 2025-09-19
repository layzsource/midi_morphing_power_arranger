import * as THREE from 'three';
import { Engine } from './engine';

const container = document.getElementById('canvas-container')!;
const engine = new Engine(container);

// Mode switching
const clubBtn = document.getElementById('club-mode')!;
const installationBtn = document.getElementById('installation-mode')!;
const instrumentBtn = document.getElementById('instrument-mode')!;

const buttons = [clubBtn, installationBtn, instrumentBtn];
const modes = ['club', 'installation', 'instrument'] as const;

buttons.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        engine.setMode(modes[index]);
    });
});

// Start the engine
engine.start();

// Handle window resize
window.addEventListener('resize', () => {
    engine.resize();
});

// Keyboard controls for live performance
document.addEventListener('keydown', async (event) => {
    await engine.handleKeyPress(event.key);
});

// Request MIDI access for performance control
if (navigator.requestMIDIAccess) {
    navigator.requestMIDIAccess().then((midiAccess) => {
        engine.connectMIDI(midiAccess);
    }).catch((error) => {
        console.log('MIDI access denied:', error);
    });
}