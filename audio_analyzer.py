#!/usr/bin/env python3
"""
Advanced Audio Analyzer module for the morphing visualizer.
Full-featured audio analysis with spectral features, onset detection, and more.
"""

import numpy as np
import threading
import time
import queue
from collections import deque
from PySide6.QtCore import QObject, Signal, QThread
import logging

logger = logging.getLogger(__name__)

# Try to import audio libraries
AUDIO_AVAILABLE = False
SOUNDDEVICE_AVAILABLE = False
PYAUDIO_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
    AUDIO_AVAILABLE = True
except ImportError:
    pass

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
    AUDIO_AVAILABLE = True
except ImportError:
    pass

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

if not AUDIO_AVAILABLE:
    print("Warning: No audio libraries available (install sounddevice or pyaudio)")


class AudioAnalyzer(QObject):
    """Advanced audio analyzer with full spectral analysis and onset detection."""
    
    # Signals for different audio features
    amplitude_changed = Signal(float)
    onset_detected = Signal(float)
    frequency_peak = Signal(float)
    spectral_centroid_signal = Signal(float)
    spectral_rolloff_signal = Signal(float)
    beat_detected = Signal(float)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.stream = None
        self.running = False
        self.thread = None
        
        # Audio parameters
        self.sample_rate = getattr(config, 'AUDIO_SAMPLE_RATE', 44100)
        self.buffer_size = getattr(config, 'AUDIO_BUFFER_SIZE', 2048)
        self.hop_length = getattr(config, 'AUDIO_HOP_LENGTH', 512)
        
        # Audio buffer
        self.audio_buffer = np.zeros(self.buffer_size * 2)
        self.audio_queue = queue.Queue(maxsize=10)
        
        # Analysis parameters
        self.onset_threshold = getattr(config, 'AUDIO_ONSET_THRESHOLD', 2.0)
        self.spectral_rolloff = getattr(config, 'AUDIO_SPECTRAL_ROLLOFF', 0.85)
        self.frequency_range = getattr(config, 'AUDIO_FREQUENCY_RANGE', [20, 20000])
        
        # Feature history for smoothing and detection
        self.amplitude_history = deque(maxlen=100)
        self.spectral_flux_history = deque(maxlen=43)
        self.onset_history = deque(maxlen=20)
        self.beat_history = deque(maxlen=8)
        
        # Current features
        self.current_features = {
            'amplitude': 0.0,
            'rms': 0.0,
            'peak_frequency': 0.0,
            'spectral_centroid': 0.0,
            'spectral_rolloff': 0.0,
            'spectral_bandwidth': 0.0,
            'zero_crossing_rate': 0.0,
            'onset_strength': 0.0,
            'tempo': 0.0,
            'beat_strength': 0.0
        }
        
        # Previous values for delta calculations
        self.previous_spectrum = None
        self.previous_energy = 0.0
        self.previous_onset_strength = 0.0
        
        # Windowing function for FFT
        self.windowing_function = np.hanning(self.buffer_size)
        
        # Audio backend selection
        self.audio_backend = None
        self.audio_device = None
        
    def start(self, device_name=None):
        """Start audio analysis with automatic backend selection."""
        if not AUDIO_AVAILABLE:
            logger.warning("No audio libraries available")
            return False
        
        try:
            # Try sounddevice first
            if SOUNDDEVICE_AVAILABLE:
                return self._start_sounddevice(device_name)
            
            # Fall back to pyaudio
            elif PYAUDIO_AVAILABLE:
                return self._start_pyaudio(device_name)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to start audio analyzer: {e}")
            return False
    
    def _start_sounddevice(self, device_name=None):
        """Start audio using sounddevice backend."""
        try:
            # Find device
            device_id = None
            if device_name:
                devices = sd.query_devices()
                for i, device in enumerate(devices):
                    if device_name.lower() in device['name'].lower() and device['max_input_channels'] > 0:
                        device_id = i
                        break
            
            # Create input stream
            self.stream = sd.InputStream(
                device=device_id,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                callback=self._sounddevice_callback
            )
            
            self.running = True
            self.stream.start()
            
            # Start analysis thread
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            self.audio_backend = "sounddevice"
            logger.info(f"✓ Audio analyzer started with sounddevice (device: {device_id})")
            return True
            
        except Exception as e:
            logger.error(f"Sounddevice initialization failed: {e}")
            return False
    
    def _start_pyaudio(self, device_name=None):
        """Start audio using PyAudio backend."""
        try:
            self.audio_device = pyaudio.PyAudio()
            
            # Find device
            device_id = None
            if device_name:
                for i in range(self.audio_device.get_device_count()):
                    info = self.audio_device.get_device_info_by_index(i)
                    if device_name.lower() in info['name'].lower() and info['maxInputChannels'] > 0:
                        device_id = i
                        break
            
            # Create stream
            self.stream = self.audio_device.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_id,
                frames_per_buffer=self.buffer_size,
                stream_callback=self._pyaudio_callback
            )
            
            self.running = True
            
            # Start analysis thread
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            self.audio_backend = "pyaudio"
            logger.info(f"✓ Audio analyzer started with PyAudio (device: {device_id})")
            return True
            
        except Exception as e:
            logger.error(f"PyAudio initialization failed: {e}")
            return False
    
    def _sounddevice_callback(self, indata, frames, time_info, status):
        """Sounddevice audio callback."""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        audio_data = indata[:, 0].copy()  # Convert to mono
        
        if not self.audio_queue.full():
            self.audio_queue.put(audio_data)
    
    def _pyaudio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback."""
        try:
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            if not self.audio_queue.full():
                self.audio_queue.put(audio_data.copy())
            
            return (None, pyaudio.paContinue)
            
        except Exception as e:
            logger.error(f"PyAudio callback error: {e}")
            return (None, pyaudio.paAbort)
    
    def _analysis_loop(self):
        """Main analysis thread loop."""
        while self.running:
            try:
                # Get audio from queue
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Update buffer
                self._update_buffer(audio_chunk)
                
                # Perform analysis
                features = self._extract_features()
                if features:
                    self._update_current_features(features)
                    self._emit_signals(features)
                
                time.sleep(1.0 / 60)  # 60 Hz analysis rate
                
            except Exception as e:
                logger.error(f"Analysis loop error: {e}")
    
    def _update_buffer(self, new_chunk):
        """Update the audio buffer with new data."""
        try:
            # Apply windowing
            windowed_chunk = new_chunk * self.windowing_function[:len(new_chunk)]
            
            # Shift buffer and add new data
            shift_amount = len(windowed_chunk)
            self.audio_buffer[:-shift_amount] = self.audio_buffer[shift_amount:]
            self.audio_buffer[-shift_amount:] = windowed_chunk
            
        except Exception as e:
            logger.error(f"Buffer update error: {e}")
    
    def _extract_features(self):
        """Extract comprehensive audio features."""
        try:
            features = {}
            
            # Skip if buffer is silent
            if np.max(np.abs(self.audio_buffer)) < 1e-6:
                return None
            
            # Time-domain features
            features['rms'] = np.sqrt(np.mean(self.audio_buffer ** 2))
            features['peak_amplitude'] = np.max(np.abs(self.audio_buffer))
            features['zero_crossing_rate'] = np.sum(np.diff(np.sign(self.audio_buffer)) != 0) / len(self.audio_buffer)
            
            # Frequency-domain features
            fft = np.fft.rfft(self.audio_buffer)
            magnitude_spectrum = np.abs(fft)
            power_spectrum = magnitude_spectrum ** 2
            freqs = np.fft.rfftfreq(len(self.audio_buffer), 1/self.sample_rate)
            
            # Filter to frequency range
            freq_mask = (freqs >= self.frequency_range[0]) & (freqs <= self.frequency_range[1])
            
            if np.any(freq_mask):
                filtered_power = power_spectrum[freq_mask]
                filtered_freqs = freqs[freq_mask]
                
                # Spectral centroid
                if np.sum(filtered_power) > 0:
                    features['spectral_centroid'] = np.sum(filtered_freqs * filtered_power) / np.sum(filtered_power)
                else:
                    features['spectral_centroid'] = 0.0
                
                # Spectral rolloff
                cumsum = np.cumsum(filtered_power)
                total_energy = cumsum[-1]
                if total_energy > 0:
                    rolloff_idx = np.where(cumsum >= self.spectral_rolloff * total_energy)[0]
                    if len(rolloff_idx) > 0:
                        features['spectral_rolloff'] = filtered_freqs[rolloff_idx[0]]
                    else:
                        features['spectral_rolloff'] = filtered_freqs[-1]
                else:
                    features['spectral_rolloff'] = 0.0
                
                # Spectral bandwidth
                if features['spectral_centroid'] > 0:
                    features['spectral_bandwidth'] = np.sqrt(
                        np.sum(((filtered_freqs - features['spectral_centroid']) ** 2) * filtered_power) / 
                        np.sum(filtered_power)
                    )
                else:
                    features['spectral_bandwidth'] = 0.0
                
                # Peak frequency
                peak_idx = np.argmax(filtered_power)
                features['peak_frequency'] = filtered_freqs[peak_idx]
            
            # Onset detection using spectral flux
            if self.previous_spectrum is not None:
                spectral_flux = np.sum(np.maximum(0, magnitude_spectrum - self.previous_spectrum))
                self.spectral_flux_history.append(spectral_flux)
                
                # Calculate adaptive threshold
                if len(self.spectral_flux_history) > 3:
                    mean_flux = np.mean(self.spectral_flux_history)
                    std_flux = np.std(self.spectral_flux_history)
                    threshold = mean_flux + self.onset_threshold * std_flux
                    
                    if spectral_flux > threshold:
                        onset_strength = (spectral_flux - threshold) / std_flux
                        features['onset_detected'] = True
                        features['onset_strength'] = onset_strength
                    else:
                        features['onset_detected'] = False
                        features['onset_strength'] = 0.0
            
            self.previous_spectrum = magnitude_spectrum
            
            # Beat detection (simplified)
            energy = np.sum(power_spectrum)
            if self.previous_energy > 0:
                energy_ratio = energy / self.previous_energy
                if energy_ratio > 1.5:  # Energy jump
                    self.beat_history.append(time.time())
                    features['beat_detected'] = True
                    features['beat_strength'] = energy_ratio
                else:
                    features['beat_detected'] = False
                    features['beat_strength'] = 0.0
            
            self.previous_energy = energy * 0.9 + self.previous_energy * 0.1  # Smooth energy
            
            # Normalize features
            features['normalized_rms'] = np.clip(features['rms'] * 10, 0, 1)
            features['normalized_centroid'] = np.clip(
                (features.get('spectral_centroid', 0) - self.frequency_range[0]) / 
                (self.frequency_range[1] - self.frequency_range[0]), 
                0, 1
            )
            
            features['timestamp'] = time.time()
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return None
    
    def _update_current_features(self, features):
        """Update current features with smoothing."""
        smoothing = 0.7
        
        for key, value in features.items():
            if key in self.current_features and isinstance(value, (int, float)):
                # Smooth numerical values
                self.current_features[key] = (
                    smoothing * self.current_features[key] + 
                    (1 - smoothing) * value
                )
            else:
                self.current_features[key] = value
    
    def _emit_signals(self, features):
        """Emit signals for various audio features."""
        try:
            # Amplitude
            if 'normalized_rms' in features:
                self.amplitude_changed.emit(features['normalized_rms'])
            
            # Onset
            if features.get('onset_detected', False):
                self.onset_detected.emit(features['onset_strength'])
            
            # Frequency
            if 'peak_frequency' in features:
                self.frequency_peak.emit(features['peak_frequency'])
            
            # Spectral features
            if 'spectral_centroid' in features:
                self.spectral_centroid_signal.emit(features['spectral_centroid'])
            
            if 'spectral_rolloff' in features:
                self.spectral_rolloff_signal.emit(features['spectral_rolloff'])
            
            # Beat
            if features.get('beat_detected', False):
                self.beat_detected.emit(features['beat_strength'])
                
        except Exception as e:
            logger.error(f"Signal emission error: {e}")
    
    def stop(self):
        """Stop audio analysis."""
        logger.info("Stopping audio analyzer...")
        self.running = False
        
        # Stop stream
        if self.stream:
            if self.audio_backend == "sounddevice":
                self.stream.stop()
                self.stream.close()
            elif self.audio_backend == "pyaudio":
                self.stream.stop_stream()
                self.stream.close()
                if self.audio_device:
                    self.audio_device.terminate()
        
        # Wait for thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        logger.info("✓ Audio analyzer stopped")
    
    def get_features(self):
        """Get current audio features."""
        return self.current_features.copy()
    
    def get_amplitude(self):
        """Get current amplitude (0-1 range)."""
        return self.current_features.get('normalized_rms', 0.0)
    
    def get_frequency(self):
        """Get current dominant frequency."""
        return self.current_features.get('peak_frequency', 0.0)
    
    def get_spectral_centroid(self):
        """Get spectral centroid (brightness)."""
        return self.current_features.get('spectral_centroid', 0.0)
    
    def is_active(self):
        """Check if analyzer is running."""
        return self.running


class AdvancedAudioAnalyzer(AudioAnalyzer):
    """Extended audio analyzer with additional features for full application."""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Additional features
        self.mel_bands = 128
        self.mfcc_coefficients = 13
        
        # Tempo tracking
        self.tempo_tracker = None
        self.beat_tracker = None
        
        # Advanced onset detection
        self.onset_detector = None
        
        # Initialize librosa components if available
        if LIBROSA_AVAILABLE:
            self._init_librosa_components()
    
    def _init_librosa_components(self):
        """Initialize librosa-based components."""
        try:
            import librosa
            
            # Create onset detector
            self.onset_detector = lambda y: librosa.onset.onset_detect(
                y=y, 
                sr=self.sample_rate, 
                hop_length=self.hop_length
            )
            
            logger.info("✓ Advanced audio features initialized with librosa")
            
        except Exception as e:
            logger.error(f"Failed to initialize librosa components: {e}")
    
    def get_mel_spectrogram(self):
        """Get mel-scale spectrogram."""
        if not LIBROSA_AVAILABLE:
            return None
        
        try:
            import librosa
            mel_spec = librosa.feature.melspectrogram(
                y=self.audio_buffer, 
                sr=self.sample_rate, 
                n_mels=self.mel_bands
            )
            return librosa.power_to_db(mel_spec, ref=np.max)
        except Exception as e:
            logger.error(f"Mel spectrogram calculation failed: {e}")
            return None
    
    def get_mfcc(self):
        """Get MFCC features."""
        if not LIBROSA_AVAILABLE:
            return None
        
        try:
            import librosa
            mfcc = librosa.feature.mfcc(
                y=self.audio_buffer, 
                sr=self.sample_rate, 
                n_mfcc=self.mfcc_coefficients
            )
            return mfcc
        except Exception as e:
            logger.error(f"MFCC calculation failed: {e}")
            return None
    
    def estimate_tempo(self):
        """Estimate tempo using librosa."""
        if not LIBROSA_AVAILABLE:
            return None
        
        try:
            import librosa
            tempo, beats = librosa.beat.beat_track(
                y=self.audio_buffer, 
                sr=self.sample_rate
            )
            return tempo
        except Exception as e:
            logger.error(f"Tempo estimation failed: {e}")
            return None


# Test function
def test_audio_analyzer():
    """Test audio analyzer functionality."""
    from PySide6.QtWidgets import QApplication
    from config import Config
    import sys
    
    app = QApplication(sys.argv)
    config = Config()
    
    # Test advanced analyzer
    analyzer = AdvancedAudioAnalyzer(config) if LIBROSA_AVAILABLE else AudioAnalyzer(config)
    
    # Connect signals for testing
    analyzer.amplitude_changed.connect(lambda a: print(f"📊 Amplitude: {a:.3f}"))
    analyzer.onset_detected.connect(lambda s: print(f"💥 ONSET! Strength: {s:.2f}"))
    analyzer.frequency_peak.connect(lambda f: print(f"🎵 Peak frequency: {f:.1f} Hz"))
    analyzer.spectral_centroid_signal.connect(lambda c: print(f"✨ Spectral centroid: {c:.1f} Hz"))
    analyzer.beat_detected.connect(lambda b: print(f"🥁 BEAT! Strength: {b:.2f}"))
    
    print("\n🎧 Advanced Audio Analyzer Test")
    print("=" * 50)
    print(f"Audio backend available: {AUDIO_AVAILABLE}")
    print(f"Sounddevice: {SOUNDDEVICE_AVAILABLE}")
    print(f"PyAudio: {PYAUDIO_AVAILABLE}")
    print(f"Librosa: {LIBROSA_AVAILABLE}")
    print()
    
    if analyzer.start():
        print("✓ Audio analyzer running. Make some noise!")
        print("Features being tracked:")
        print("  • RMS amplitude")
        print("  • Onset detection")
        print("  • Peak frequency")
        print("  • Spectral centroid (brightness)")
        print("  • Beat detection")
        if LIBROSA_AVAILABLE:
            print("  • MFCC coefficients")
            print("  • Mel spectrogram")
            print("  • Tempo estimation")
        print("\nPress Ctrl+C to stop...")
        
        try:
            app.exec()
        except KeyboardInterrupt:
            pass
    else:
        print("✗ Failed to start audio analyzer")
        print("Make sure you have sounddevice or pyaudio installed:")
        print("  pip install sounddevice")
        print("  pip install pyaudio")
        print("\nFor advanced features, also install:")
        print("  pip install librosa")
    
    analyzer.stop()


if __name__ == "__main__":
    test_audio_analyzer()
