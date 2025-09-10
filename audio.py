"""
Real-time audio analysis and processing.
"""

import time
import logging
import numpy as np
import pyaudio
import queue
from typing import Dict, Optional
from PySide6.QtCore import QThread, Signal

from config import Config
from exceptions import AudioAnalysisError
from profiler import profiler, profile_function

logger = logging.getLogger(__name__)

class AudioAnalysisThread(QThread):
    """Real-time audio analysis thread using PyAudio and librosa."""
    
    audio_feature_signal = Signal(dict)  # Emits audio features
    error_signal = Signal(str)
    status_signal = Signal(str)
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.running = True
        
        # Audio setup
        self.audio = None
        self.stream = None
        self.audio_queue = queue.Queue()
        
        # Analysis parameters
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.chunk_size = config.AUDIO_CHUNK_SIZE
        self.fft_size = config.AUDIO_FFT_SIZE
        self.hop_length = config.AUDIO_HOP_LENGTH
        
        # Audio buffer for analysis
        self.audio_buffer = np.zeros(self.fft_size)
        self.windowing_function = np.hanning(self.chunk_size)
        
        # Feature tracking
        self.onset_detector = None
        self.tempo_tracker = None
        self.previous_onset_strength = 0.0
        
    def run(self):
        """Main audio analysis loop."""
        try:
            if not self.config.AUDIO_ENABLED:
                self.status_signal.emit("Audio disabled")
                return
                
            self._setup_audio()
            self._start_audio_stream()
            self._analysis_loop()
            
        except Exception as e:
            logger.error(f"Audio analysis thread failed: {e}")
            self.error_signal.emit(f"Audio error: {e}")
        finally:
            self._cleanup_audio()
    
    def _setup_audio(self):
        """Initialize PyAudio and find audio devices."""
        try:
            self.audio = pyaudio.PyAudio()
            
            # List available audio devices
            device_count = self.audio.get_device_count()
            logger.info(f"Found {device_count} audio devices")
            
            # Find appropriate input device
            device_index = self.config.AUDIO_DEVICE_INDEX
            if device_index is None:
                device_index = self._find_best_input_device()
            
            device_info = self.audio.get_device_info_by_index(device_index)
            logger.info(f"Using audio device: {device_info['name']}")
            self.status_signal.emit(f"Audio: {device_info['name']}")
            
        except Exception as e:
            raise AudioAnalysisError(f"Audio setup failed: {e}")
    
    def _find_best_input_device(self) -> int:
        """Find the best available input device."""
        try:
            default_device = self.audio.get_default_input_device_info()
            return default_device['index']
        except Exception:
            # Fallback: find any input device
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    return i
            raise AudioAnalysisError("No input devices found")
    
    def _start_audio_stream(self):
        """Start the audio input stream."""
        try:
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.config.AUDIO_CHANNELS,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.config.AUDIO_DEVICE_INDEX,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            logger.info("Audio stream started")
            
        except Exception as e:
            raise AudioAnalysisError(f"Failed to start audio stream: {e}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for incoming audio data."""
        try:
            if status:
                logger.warning(f"Audio stream status: {status}")
            
            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            # Add to queue for processing
            if not self.audio_queue.full():
                self.audio_queue.put(audio_data.copy())
            
            return (None, pyaudio.paContinue)
            
        except Exception as e:
            logger.error(f"Audio callback error: {e}")
            return (None, pyaudio.paAbort)
    
    @profile_function("audio_analysis")
    def _analysis_loop(self):
        """Main analysis loop processing audio data."""
        while self.running:
            try:
                # Get audio data from queue (blocking with timeout)
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Update audio buffer
                self._update_audio_buffer(audio_chunk)
                
                # Perform audio analysis
                features = self._analyze_audio()
                
                # Emit features
                if features:
                    self.audio_feature_signal.emit(features)
                    profiler.increment_counter('audio_features_processed')
                
            except Exception as e:
                logger.error(f"Audio analysis error: {e}")
                profiler.increment_counter('audio_analysis_errors')
    
    def _update_audio_buffer(self, new_chunk: np.ndarray):
        """Update the rolling audio buffer with new data."""
        try:
            # Apply windowing
            windowed_chunk = new_chunk * self.windowing_function
            
            # Shift buffer and add new data
            shift_amount = len(windowed_chunk)
            self.audio_buffer[:-shift_amount] = self.audio_buffer[shift_amount:]
            self.audio_buffer[-shift_amount:] = windowed_chunk
            
        except Exception as e:
            logger.error(f"Buffer update error: {e}")
    
    def _analyze_audio(self) -> Optional[Dict]:
        """Analyze current audio buffer and extract features."""
        try:
            if np.max(np.abs(self.audio_buffer)) < 1e-6:
                return None  # Silence
            
            features = {}
            
            # Basic amplitude features
            features['rms'] = np.sqrt(np.mean(self.audio_buffer ** 2))
            features['peak_amplitude'] = np.max(np.abs(self.audio_buffer))
            
            # Spectral analysis
            fft = np.fft.rfft(self.audio_buffer)
            magnitude_spectrum = np.abs(fft)
            power_spectrum = magnitude_spectrum ** 2
            
            # Frequency analysis
            freqs = np.fft.rfftfreq(len(self.audio_buffer), 1/self.sample_rate)
            
            # Filter to frequency range of interest
            freq_mask = (freqs >= self.config.AUDIO_FREQUENCY_RANGE[0]) & \
                       (freqs <= self.config.AUDIO_FREQUENCY_RANGE[1])
            
            if np.any(freq_mask):
                filtered_power = power_spectrum[freq_mask]
                filtered_freqs = freqs[freq_mask]
                
                # Spectral centroid (brightness/pitch estimate)
                if np.sum(filtered_power) > 0:
                    features['spectral_centroid'] = np.sum(filtered_freqs * filtered_power) / np.sum(filtered_power)
                else:
                    features['spectral_centroid'] = 0.0
                
                # Spectral rolloff
                cumsum = np.cumsum(filtered_power)
                total_energy = cumsum[-1]
                if total_energy > 0:
                    rolloff_idx = np.where(cumsum >= self.config.AUDIO_SPECTRAL_ROLLOFF * total_energy)[0]
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
            else:
                features['spectral_centroid'] = 0.0
                features['spectral_rolloff'] = 0.0
                features['spectral_bandwidth'] = 0.0
            
            # Onset detection (simplified)
            onset_strength = np.sum(np.diff(magnitude_spectrum, axis=0) ** 2)
            onset_detected = onset_strength > self.previous_onset_strength * (1 + self.config.AUDIO_ONSET_THRESHOLD)
            features['onset_detected'] = onset_detected
            features['onset_strength'] = onset_strength
            self.previous_onset_strength = onset_strength * 0.9 + onset_strength * 0.1  # Simple smoothing
            
            # Normalize features for visualization
            features['normalized_rms'] = np.clip(features['rms'] * 10, 0, 1)
            features['normalized_centroid'] = np.clip(
                (features['spectral_centroid'] - self.config.AUDIO_FREQUENCY_RANGE[0]) / 
                (self.config.AUDIO_FREQUENCY_RANGE[1] - self.config.AUDIO_FREQUENCY_RANGE[0]), 
                0, 1
            )
            
            features['timestamp'] = time.time()
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return None
    
    def stop(self):
        """Stop the audio analysis thread."""
        self.running = False
        self.quit()
    
    def _cleanup_audio(self):
        """Clean up audio resources."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                logger.info("Audio stream closed")
            
            if self.audio:
                self.audio.terminate()
                logger.info("PyAudio terminated")
                
        except Exception as e:
            logger.error(f"Audio cleanup error: {e}")