/**
 * Audio Input Selector UI
 *
 * Provides interface for selecting and configuring audio input sources
 */

import { AudioInputManager, AudioInputSource, AudioAnalysis } from '../audio/AudioInputManager';

export class AudioInputSelector {
    private container: HTMLElement;
    private audioInputManager: AudioInputManager;
    private selectorElement: HTMLElement | null = null;
    private isVisible: boolean = false;
    private currentAnalysis: AudioAnalysis | null = null;

    constructor(container: HTMLElement) {
        this.container = container;
        this.audioInputManager = new AudioInputManager();
        this.createSelector();
        this.setupAnalysis();

        // Make globally accessible for inline onclick handlers
        (window as any).audioInputSelector = this;
    }

    private createSelector() {
        const selector = document.createElement('div');
        selector.className = 'audio-input-selector';
        selector.style.cssText = `
            position: fixed;
            top: 20px;
            right: 400px;
            width: 320px;
            max-height: 80vh;
            background: rgba(0, 20, 40, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 12px;
            padding: 16px;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            z-index: 150;
            display: none;
            overflow-y: auto;
            overflow-x: hidden;
            box-shadow:
                0 1px 0 0 rgba(0, 255, 255, 0.1) inset,
                0 8px 32px 0 rgba(0, 0, 0, 0.6),
                0 32px 80px 0 rgba(0, 255, 255, 0.15);
        `;

        // Header
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0, 255, 255, 0.2);
        `;

        const title = document.createElement('h3');
        title.textContent = '🎵 AUDIO INPUT SOURCE';
        title.style.cssText = `
            margin: 0;
            color: #00ffff;
            font-size: 12px;
            font-weight: 600;
            text-shadow: 0 0 8px #00ffff;
        `;

        const closeButton = document.createElement('button');
        closeButton.textContent = '✕';
        closeButton.title = 'Hide panel (use toolbar to show again)';
        closeButton.style.cssText = `
            background: rgba(255, 100, 100, 0.2);
            border: 1px solid #ff6464;
            color: #ff6464;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
        `;
        closeButton.onclick = () => {
            this.setVisibility(false);

            // Trigger a global event so the toolbar can update
            window.dispatchEvent(new CustomEvent('panelClosed', {
                detail: { selector: '.audio-input-selector' }
            }));
        };

        header.appendChild(title);
        header.appendChild(closeButton);
        selector.appendChild(header);

        // Source selection
        const sourceSection = this.createSourceSection();
        selector.appendChild(sourceSection);

        // Controls section
        const controlsSection = this.createControlsSection();
        selector.appendChild(controlsSection);

        // Analysis section
        const analysisSection = this.createAnalysisSection();
        selector.appendChild(analysisSection);

        this.container.appendChild(selector);
        this.selectorElement = selector;
    }

    private createSourceSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 16px;
            padding: 12px;
            border: 1px solid rgba(0, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 20, 40, 0.3);
        `;

        const sectionTitle = document.createElement('div');
        sectionTitle.textContent = 'INPUT SOURCE';
        sectionTitle.style.cssText = `
            font-size: 10px;
            font-weight: 600;
            color: #00ffaa;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        section.appendChild(sectionTitle);

        const sources = [
            { id: 'internal', name: 'Internal Synthesis', icon: '🎛️', description: 'Built-in sound engine' },
            { id: 'microphone', name: 'Microphone', icon: '🎤', description: 'Live microphone input' },
            { id: 'line-in', name: 'Line Input', icon: '🔌', description: 'External line input' },
            { id: 'file', name: 'Audio File', icon: '📁', description: 'Upload audio file' },
            { id: 'youtube', name: 'YouTube', icon: '📺', description: 'YouTube video audio' },
            { id: 'spotify', name: 'Spotify', icon: '🎵', description: 'Spotify streaming' },
            { id: 'itunes', name: 'Apple Music', icon: '🍎', description: 'iTunes/Apple Music' },
            { id: 'ableton', name: 'Ableton Live', icon: '🎚️', description: 'DAW integration' },
            { id: 'midi', name: 'MIDI Device', icon: '🎹', description: 'External MIDI controller' }
        ];

        sources.forEach(source => {
            const sourceElement = document.createElement('div');
            sourceElement.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px;
                margin: 4px 0;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s ease;
                border: 1px solid transparent;
            `;

            const sourceInfo = document.createElement('div');
            sourceInfo.style.cssText = `
                display: flex;
                align-items: center;
                gap: 8px;
                flex: 1;
            `;

            const icon = document.createElement('span');
            icon.textContent = source.icon;
            icon.style.fontSize = '14px';

            const nameAndDesc = document.createElement('div');
            nameAndDesc.innerHTML = `
                <div style="font-size: 11px; font-weight: 500; color: #00ffff;">
                    ${source.name}
                </div>
                <div style="font-size: 9px; color: #00aaaa; margin-top: 1px;">
                    ${source.description}
                </div>
            `;

            const status = document.createElement('span');
            status.id = `status-${source.id}`;
            status.textContent = source.id === 'internal' ? '●' : '○';
            status.style.cssText = `
                color: ${source.id === 'internal' ? '#00ff00' : '#666'};
                font-size: 12px;
                font-weight: bold;
            `;

            sourceInfo.appendChild(icon);
            sourceInfo.appendChild(nameAndDesc);
            sourceElement.appendChild(sourceInfo);
            sourceElement.appendChild(status);

            // Hover and click effects
            sourceElement.onmouseenter = () => {
                sourceElement.style.background = 'rgba(0, 255, 255, 0.1)';
                sourceElement.style.borderColor = 'rgba(0, 255, 255, 0.3)';
            };
            sourceElement.onmouseleave = () => {
                sourceElement.style.background = 'transparent';
                sourceElement.style.borderColor = 'transparent';
            };

            sourceElement.onclick = () => {
                this.selectAudioSource(source.id as AudioInputSource);
            };

            section.appendChild(sourceElement);
        });

        return section;
    }

    private createControlsSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 16px;
            padding: 12px;
            border: 1px solid rgba(0, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 20, 40, 0.3);
        `;

        const sectionTitle = document.createElement('div');
        sectionTitle.textContent = 'AUDIO CONTROLS';
        sectionTitle.style.cssText = `
            font-size: 10px;
            font-weight: 600;
            color: #00ffaa;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        section.appendChild(sectionTitle);

        // Master gain
        section.appendChild(this.createSlider('Master Gain', '🔊', 0, 1, 0.8, (value) => {
            this.audioInputManager.setMasterGain(value);
        }));

        // File upload for audio files
        const fileUpload = document.createElement('div');
        fileUpload.style.cssText = `
            margin: 8px 0;
            padding: 8px;
            border: 1px dashed rgba(0, 255, 255, 0.3);
            border-radius: 4px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        `;
        fileUpload.innerHTML = `
            <input type="file" accept="audio/*" style="display: none;" id="audio-file-input">
            <div style="color: #00aaaa; font-size: 10px;">
                📁 Click to select audio file
            </div>
        `;

        fileUpload.onclick = () => {
            const input = document.getElementById('audio-file-input') as HTMLInputElement;
            input?.click();
        };

        const input = fileUpload.querySelector('input') as HTMLInputElement;
        input.onchange = (event) => {
            const file = (event.target as HTMLInputElement).files?.[0];
            if (file) {
                this.audioInputManager.connectAudioFile(file);
                fileUpload.innerHTML = `
                    <div style="color: #00ff00; font-size: 10px;">
                        ✅ ${file.name}
                    </div>
                `;
            }
        };

        section.appendChild(fileUpload);

        // YouTube URL input
        const youtubeInput = document.createElement('div');
        youtubeInput.style.cssText = 'margin: 8px 0;';
        youtubeInput.innerHTML = `
            <input type="text" placeholder="Try: https://www.youtube.com/watch?v=dQw4w9WgXcQ" style="
                width: 100%;
                padding: 6px;
                background: rgba(0, 20, 40, 0.8);
                border: 1px solid rgba(0, 255, 255, 0.3);
                color: #00ffff;
                border-radius: 4px;
                font-size: 10px;
                font-family: inherit;
            ">
            <div style="display: flex; gap: 4px; margin-top: 4px;">
                <button id="youtube-connect-btn" style="
                    flex: 1;
                    padding: 6px;
                    background: rgba(255, 0, 0, 0.2);
                    border: 1px solid #ff4444;
                    color: #ff4444;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 10px;
                    font-family: inherit;
                ">📺 Connect YouTube</button>
                <button id="youtube-disconnect-btn" style="
                    padding: 6px 8px;
                    background: rgba(100, 100, 100, 0.2);
                    border: 1px solid #666;
                    color: #666;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 10px;
                    font-family: inherit;
                    display: none;
                ">🗑️</button>
            </div>
        `;

        const ytButton = youtubeInput.querySelector('#youtube-connect-btn') as HTMLButtonElement;
        const ytDisconnectButton = youtubeInput.querySelector('#youtube-disconnect-btn') as HTMLButtonElement;
        const ytInput = youtubeInput.querySelector('input') as HTMLInputElement;

        // Connect button handler
        ytButton?.addEventListener('click', async () => {
            console.log('🔘 YouTube connect button clicked!');
            const url = ytInput.value;
            console.log('🔗 URL from input:', url);

            if (!url || url.trim() === '') {
                console.warn('⚠️ No YouTube URL provided');
                return;
            }

            if (url) {
                // Update button to show loading state
                if (ytButton) {
                    ytButton.textContent = '⏳ Connecting...';
                    ytButton.style.background = 'rgba(255, 165, 0, 0.2)';
                    ytButton.style.borderColor = '#ffa500';
                    ytButton.style.color = '#ffa500';
                }

                try {
                    console.log('🚀 Starting YouTube connection with timeout...');

                    // Add timeout wrapper
                    const timeoutPromise = new Promise((_, reject) => {
                        setTimeout(() => reject(new Error('Connection timeout')), 5000);
                    });

                    const success = await Promise.race([
                        this.audioInputManager.connectYouTube(url),
                        timeoutPromise
                    ]);

                    if (success && ytButton) {
                        // Update status indicator
                        const statusElement = document.getElementById('status-youtube');
                        if (statusElement) {
                            statusElement.textContent = '●';
                            statusElement.style.color = '#00ff00';
                        }

                        // Show connected state and play/pause button
                        ytButton.textContent = '▶️ Play';
                        ytButton.style.background = 'rgba(0, 255, 0, 0.2)';
                        ytButton.style.borderColor = '#00ff00';
                        ytButton.style.color = '#00ff00';

                        // Show disconnect button
                        if (ytDisconnectButton) {
                            ytDisconnectButton.style.display = 'block';
                        }

                        // Update button functionality to play/pause
                        ytButton.onclick = () => {
                            if (ytButton.textContent.includes('Play')) {
                                this.audioInputManager.playYouTube();
                                ytButton.textContent = '⏸️ Pause';
                            } else {
                                this.audioInputManager.pauseYouTube();
                                ytButton.textContent = '▶️ Play';
                            }
                        };

                    } else if (ytButton) {
                        ytButton.textContent = '❌ Failed';
                        ytButton.style.background = 'rgba(255, 0, 0, 0.2)';
                        ytButton.style.borderColor = '#ff4444';
                        ytButton.style.color = '#ff4444';

                        // Reset button after 3 seconds only for failures
                        setTimeout(() => {
                            if (ytButton && ytButton.textContent === '❌ Failed') {
                                ytButton.textContent = '📺 Connect YouTube';
                                ytButton.style.background = 'rgba(255, 0, 0, 0.2)';
                                ytButton.style.borderColor = '#ff4444';
                                ytButton.style.color = '#ff4444';
                            }
                        }, 3000);
                    }

                } catch (error) {
                    console.error('YouTube connection error:', error);
                    if (ytButton) {
                        ytButton.textContent = '❌ Error';
                        ytButton.style.background = 'rgba(255, 0, 0, 0.2)';
                        ytButton.style.borderColor = '#ff4444';
                        ytButton.style.color = '#ff4444';
                    }
                }
            }
        });

        // Disconnect button handler
        ytDisconnectButton?.addEventListener('click', () => {
            // Disconnect YouTube
            this.audioInputManager.disconnectYouTube();

            // Reset UI
            ytButton.textContent = '📺 Connect YouTube';
            ytButton.style.background = 'rgba(255, 0, 0, 0.2)';
            ytButton.style.borderColor = '#ff4444';
            ytButton.style.color = '#ff4444';

            // Reset button click handler to connect
            ytButton.onclick = null; // Clear existing handler
            // The original handler will be restored by the addEventListener above

            // Hide disconnect button
            ytDisconnectButton.style.display = 'none';

            // Reset status indicator
            const statusElement = document.getElementById('status-youtube');
            if (statusElement) {
                statusElement.textContent = '○';
                statusElement.style.color = '#666';
            }

            // Clear URL input
            ytInput.value = '';
        });

        section.appendChild(youtubeInput);

        // BlackHole Test Button
        const blackHoleTest = document.createElement('div');
        blackHoleTest.style.cssText = 'margin: 8px 0; padding: 8px; border: 1px solid rgba(255, 255, 0, 0.3); border-radius: 4px; background: rgba(255, 255, 0, 0.1);';
        blackHoleTest.innerHTML = `
            <div style="color: #ffff00; font-size: 10px; margin-bottom: 4px; font-weight: bold;">🔊 BlackHole Audio Test</div>
            <button onclick="
                (async () => {
                try {
                    console.log('🧪 Starting comprehensive audio test...');

                    // Start Tone.js first (this handles user gesture requirements)
                    await Tone.start();
                    console.log('✅ Tone.js started!');

                    const ctx = Tone.getContext().rawContext;
                    console.log('🎛️ AudioContext state:', ctx.state);
                    console.log('🔌 Destination:', ctx.destination);
                    console.log('📊 Sample rate:', ctx.sampleRate);

                    // Test microphone access and analysis
                    navigator.mediaDevices.getUserMedia({audio: true})
                        .then(stream => {
                            console.log('✅ Audio access granted');
                            console.log('🎤 Stream tracks:', stream.getTracks());

                            // Create audio analysis chain
                            const source = ctx.createMediaStreamSource(stream);
                            const analyser = ctx.createAnalyser();
                            analyser.fftSize = 2048;
                            source.connect(analyser);

                            // Test analysis data
                            const freqData = new Float32Array(analyser.frequencyBinCount);
                            const timeData = new Float32Array(analyser.fftSize);

                            const testLoop = () => {
                                analyser.getFloatFrequencyData(freqData);
                                analyser.getFloatTimeDomainData(timeData);

                                const rms = Math.sqrt(timeData.reduce((sum, val) => sum + val * val, 0) / timeData.length);
                                const peak = Math.max(...timeData);

                                console.log('📊 RMS:', rms.toFixed(4), 'Peak:', peak.toFixed(4));

                                if (rms > 0.001) {
                                    console.log('🎉 AUDIO DETECTED! Analysis working!');
                                    stream.getTracks().forEach(track => track.stop());
                                    return;
                                }

                                setTimeout(testLoop, 100);
                            };

                            console.log('🎧 Speak into microphone to test analysis...');
                            testLoop();

                            // Cleanup after 10 seconds
                            setTimeout(() => {
                                stream.getTracks().forEach(track => track.stop());
                                console.log('🧪 Audio test completed');
                            }, 10000);
                        })
                        .catch(err => console.error('❌ Audio access denied:', err));
                } catch(e) { console.error('❌ Audio test failed:', e); }
                })();
            " style="
                width: 100%;
                padding: 6px;
                background: rgba(255, 255, 0, 0.2);
                border: 1px solid #ffff00;
                color: #ffff00;
                border-radius: 4px;
                cursor: pointer;
                font-size: 10px;
                font-family: inherit;
            ">🧪 Test Audio Access</button>
            <div style="color: #999; font-size: 9px; margin-top: 4px;">
                Check console for audio system status with BlackHole
            </div>
        `;

        section.appendChild(blackHoleTest);

        // Simple Audio Test
        const simpleAudioTest = document.createElement('div');
        simpleAudioTest.style.cssText = 'margin: 8px 0; padding: 8px; border: 1px solid rgba(0, 255, 0, 0.3); border-radius: 4px; background: rgba(0, 255, 0, 0.1);';
        simpleAudioTest.innerHTML = `
            <div style="color: #00ff00; font-size: 10px; margin-bottom: 4px; font-weight: bold;">🎵 Simple Audio Test</div>
            <input type="file" accept="audio/*" style="
                width: 100%;
                padding: 4px;
                margin-bottom: 4px;
                background: rgba(0, 20, 40, 0.8);
                border: 1px solid rgba(0, 255, 0, 0.3);
                color: #00ff00;
                border-radius: 4px;
                font-size: 10px;
                font-family: inherit;
            ">
            <button onclick="
                const fileInput = this.previousElementSibling;
                if (fileInput.files[0]) {
                    // Connect to our AudioInputManager instead of creating standalone audio
                    const audioInputManager = window.audioInputSelector?.getAudioInputManager();
                    if (audioInputManager) {
                        console.log('🎵 Connecting audio file to analysis system...');
                        audioInputManager.connectAudioFile(fileInput.files[0]).then(() => {
                            console.log('✅ Audio file connected successfully');
                            audioInputManager.playAudioFile();
                            audioInputManager.startAnalysis();
                            console.log('🎵 Audio playing with analysis active');
                        }).catch(err => {
                            console.error('❌ Failed to connect audio file:', err);
                        });
                    } else {
                        // Fallback to simple audio if manager not available
                        const audio = new Audio();
                        audio.src = URL.createObjectURL(fileInput.files[0]);
                        audio.controls = true;
                        audio.style.width = '100%';
                        audio.style.marginTop = '4px';
                        this.parentElement.appendChild(audio);
                        audio.play();
                        console.log('🎵 Simple audio playing (no analysis)');
                    }
                } else {
                    alert('Please select an audio file first');
                }
            " style="
                width: 100%;
                padding: 6px;
                background: rgba(0, 255, 0, 0.2);
                border: 1px solid #00ff00;
                color: #00ff00;
                border-radius: 4px;
                cursor: pointer;
                font-size: 10px;
                font-family: inherit;
            ">🎵 Play Audio File</button>
            <div style="color: #999; font-size: 9px; margin-top: 4px;">
                Upload and play any audio file to test basic audio
            </div>
        `;

        section.appendChild(simpleAudioTest);

        // Spotify authentication
        const spotifyAuth = document.createElement('div');
        spotifyAuth.style.cssText = 'margin: 8px 0; padding: 8px; border: 1px solid rgba(29, 185, 84, 0.3); border-radius: 4px; background: rgba(29, 185, 84, 0.1);';
        spotifyAuth.innerHTML = `
            <div style="color: #1db954; font-size: 10px; margin-bottom: 4px; font-weight: bold;">🎵 Spotify Authentication</div>
            <button style="
                width: 100%;
                padding: 6px;
                background: rgba(29, 185, 84, 0.2);
                border: 1px solid #1db954;
                color: #1db954;
                border-radius: 4px;
                cursor: pointer;
                font-size: 10px;
                font-family: inherit;
            " onclick="window.open('https://accounts.spotify.com/authorize?client_id=YOUR_CLIENT_ID&response_type=token&redirect_uri=' + encodeURIComponent(window.location.origin) + '&scope=streaming%20user-read-email%20user-read-private', '_blank')">
                🔐 Login to Spotify
            </button>
            <div style="color: #999; font-size: 9px; margin-top: 4px;">
                Note: Requires Spotify Premium account
            </div>
        `;

        section.appendChild(spotifyAuth);

        // Apple Music authentication
        const itunesAuth = document.createElement('div');
        itunesAuth.style.cssText = 'margin: 8px 0; padding: 8px; border: 1px solid rgba(252, 61, 57, 0.3); border-radius: 4px; background: rgba(252, 61, 57, 0.1);';
        itunesAuth.innerHTML = `
            <div style="color: #fc3d39; font-size: 10px; margin-bottom: 4px; font-weight: bold;">🍎 Apple Music Authentication</div>
            <button style="
                width: 100%;
                padding: 6px;
                background: rgba(252, 61, 57, 0.2);
                border: 1px solid #fc3d39;
                color: #fc3d39;
                border-radius: 4px;
                cursor: pointer;
                font-size: 10px;
                font-family: inherit;
            " onclick="alert('Apple Music integration requires developer token setup. See documentation.')">
                🔐 Setup Apple Music
            </button>
            <div style="color: #999; font-size: 9px; margin-top: 4px;">
                Note: Requires Apple Developer account
            </div>
        `;

        section.appendChild(itunesAuth);

        // Playback controls
        const playbackControls = document.createElement('div');
        playbackControls.style.cssText = `
            display: flex;
            gap: 8px;
            margin-top: 8px;
        `;

        const playButton = document.createElement('button');
        playButton.textContent = '▶️ Play';
        playButton.style.cssText = this.getControlButtonStyle();
        playButton.onclick = () => {
            this.audioInputManager.playAudioFile();
            this.audioInputManager.playYouTube();
            this.audioInputManager.playSpotify();
            this.audioInputManager.playItunes();
        };

        const pauseButton = document.createElement('button');
        pauseButton.textContent = '⏸️ Pause';
        pauseButton.style.cssText = this.getControlButtonStyle();
        pauseButton.onclick = () => {
            this.audioInputManager.pauseAudioFile();
            this.audioInputManager.pauseYouTube();
            this.audioInputManager.pauseSpotify();
            this.audioInputManager.pauseItunes();
        };

        playbackControls.appendChild(playButton);
        playbackControls.appendChild(pauseButton);
        section.appendChild(playbackControls);

        return section;
    }

    private createAnalysisSection(): HTMLElement {
        const section = document.createElement('div');
        section.style.cssText = `
            padding: 12px;
            border: 1px solid rgba(0, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 20, 40, 0.3);
        `;

        const sectionTitle = document.createElement('div');
        sectionTitle.textContent = 'AUDIO ANALYSIS';
        sectionTitle.style.cssText = `
            font-size: 10px;
            font-weight: 600;
            color: #00ffaa;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        section.appendChild(sectionTitle);

        const analysisDisplay = document.createElement('div');
        analysisDisplay.id = 'audio-analysis-display';
        analysisDisplay.style.cssText = `
            font-size: 9px;
            color: #00aaaa;
            line-height: 1.4;
        `;
        analysisDisplay.innerHTML = `
            <div>🔊 RMS Level: <span id="rms-level">0.00</span></div>
            <div>📊 Peak: <span id="peak-level">0.00</span></div>
            <div>🎵 Pitch: <span id="pitch-detect">--- Hz</span></div>
            <div>📡 Source: <span id="current-source">Internal</span></div>
        `;

        section.appendChild(analysisDisplay);

        return section;
    }

    private createSlider(
        label: string,
        icon: string,
        min: number,
        max: number,
        defaultValue: number,
        onChange: (value: number) => void
    ): HTMLElement {
        const container = document.createElement('div');
        container.style.cssText = 'margin: 8px 0;';

        const labelEl = document.createElement('label');
        labelEl.textContent = `${icon} ${label}:`;
        labelEl.style.cssText = `
            display: block;
            margin-bottom: 4px;
            font-size: 10px;
            color: #00aaaa;
        `;

        const sliderContainer = document.createElement('div');
        sliderContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
        `;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = min.toString();
        slider.max = max.toString();
        slider.value = defaultValue.toString();
        slider.step = '0.01';
        slider.style.cssText = `
            flex: 1;
            height: 4px;
            background: rgba(0, 255, 255, 0.2);
            outline: none;
            border-radius: 2px;
        `;

        const valueDisplay = document.createElement('span');
        valueDisplay.textContent = defaultValue.toFixed(2);
        valueDisplay.style.cssText = `
            color: #00ffff;
            font-size: 9px;
            font-weight: bold;
            min-width: 35px;
            text-align: right;
        `;

        slider.oninput = () => {
            const value = parseFloat(slider.value);
            valueDisplay.textContent = value.toFixed(2);
            onChange(value);
        };

        sliderContainer.appendChild(slider);
        sliderContainer.appendChild(valueDisplay);
        container.appendChild(labelEl);
        container.appendChild(sliderContainer);

        return container;
    }

    private getControlButtonStyle(): string {
        return `
            flex: 1;
            padding: 6px;
            background: rgba(0, 255, 255, 0.2);
            border: 1px solid #00ffff;
            color: #00ffff;
            border-radius: 4px;
            cursor: pointer;
            font-size: 9px;
            font-family: inherit;
            transition: all 0.2s ease;
        `;
    }

    private async selectAudioSource(source: AudioInputSource) {
        const success = await this.audioInputManager.selectAudioSource(source);

        // Update status indicators
        const allStatuses = this.selectorElement?.querySelectorAll('[id^="status-"]');
        allStatuses?.forEach(status => {
            status.textContent = '○';
            (status as HTMLElement).style.color = '#666';
        });

        if (success) {
            const statusElement = document.getElementById(`status-${source}`);
            if (statusElement) {
                statusElement.textContent = '●';
                statusElement.style.color = '#00ff00';
            }

            // Update current source display
            const currentSourceEl = document.getElementById('current-source');
            if (currentSourceEl) {
                currentSourceEl.textContent = source.charAt(0).toUpperCase() + source.slice(1);
            }
        }
    }

    private setupAnalysis() {
        this.audioInputManager.onAnalysis((analysis) => {
            this.currentAnalysis = analysis;
            this.updateAnalysisDisplay();
        });
    }

    private updateAnalysisDisplay() {
        if (!this.currentAnalysis) return;

        const rmsEl = document.getElementById('rms-level');
        const peakEl = document.getElementById('peak-level');
        const pitchEl = document.getElementById('pitch-detect');

        if (rmsEl) rmsEl.textContent = this.currentAnalysis.rms.toFixed(3);
        if (peakEl) peakEl.textContent = this.currentAnalysis.peak.toFixed(3);
        if (pitchEl) {
            const pitch = this.currentAnalysis.pitch;
            pitchEl.textContent = pitch > 0 ? `${pitch.toFixed(1)} Hz` : '--- Hz';
        }
    }

    public setVisibility(visible: boolean) {
        this.isVisible = visible;
        if (this.selectorElement) {
            this.selectorElement.style.display = visible ? 'block' : 'none';
        }
    }

    public toggleVisibility(): boolean {
        this.setVisibility(!this.isVisible);
        return this.isVisible;
    }

    public isInputSelectorVisible(): boolean {
        return this.isVisible;
    }

    public getAudioInputManager(): AudioInputManager {
        return this.audioInputManager;
    }
}