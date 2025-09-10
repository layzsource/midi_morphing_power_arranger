"""
Fixed performance monitoring module with proper system metrics recording.
"""

import time
import threading
import psutil
import logging
import json
from collections import deque, defaultdict
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QProgressBar, QGroupBox, QGridLayout, QCheckBox,
    QSpinBox, QDoubleSpinBox, QTabWidget, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
)
from PySide6.QtCore import QTimer, Signal, QObject, Qt
from PySide6.QtGui import QFont, QPalette

logger = logging.getLogger(__name__)

def performance_monitor(func):
    """Decorator for monitoring function performance."""
    def wrapper(self, *args, **kwargs):
        if hasattr(self, 'profiler') and self.profiler.enabled:
            start_time = time.perf_counter()
            try:
                result = func(self, *args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000  # Convert to ms
                self.profiler.log_function_call(func.__name__, execution_time)
        else:
            return func(self, *args, **kwargs)
    return wrapper

class PerformanceProfiler(QObject):
    """Comprehensive performance monitoring system."""
    
    # Signals for real-time updates
    fps_updated = Signal(float)
    memory_updated = Signal(float, float)  # used_mb, percent
    cpu_updated = Signal(float)
    performance_warning = Signal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.enabled = True
        
        # Performance metrics storage
        self.fps_history = deque(maxlen=100)
        self.memory_history = deque(maxlen=100)
        self.cpu_history = deque(maxlen=100)
        self.function_timings = defaultdict(list)
        
        # Frame timing
        self.frame_start_time = None
        self.frame_count = 0
        self.last_fps_calculation = time.time()
        
        # Thresholds
        self.fps_warning_threshold = 30.0
        self.memory_warning_threshold = 80.0  # Percentage
        self.cpu_warning_threshold = 85.0     # Percentage
        self.function_time_warning_threshold = 50.0  # ms
        
        # Monitoring thread
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Statistics
        self.session_start_time = time.time()
        self.total_frames_rendered = 0
        self.performance_warnings_count = 0
        
        # Process handle for system metrics
        self.process = psutil.Process()
    
    def start_monitoring(self):
        """Start performance monitoring thread."""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop running in separate thread."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self.record_system_metrics()
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(2.0)
    
    def record_system_metrics(self):
        """Record current system metrics."""
        try:
            # Memory metrics
            memory_info = psutil.virtual_memory()
            memory_mb = memory_info.used / (1024 * 1024)
            memory_percent = memory_info.percent
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Store metrics
            self.memory_history.append(memory_percent)
            self.cpu_history.append(cpu_percent)
            
            # Emit signals for UI updates
            self.memory_updated.emit(memory_mb, memory_percent)
            self.cpu_updated.emit(cpu_percent)
            
            # Check thresholds and emit warnings
            self._check_performance_thresholds(memory_percent, cpu_percent)
            
        except Exception as e:
            logger.error(f"Error recording system metrics: {e}")
    
    def _check_performance_thresholds(self, memory_percent, cpu_percent):
        """Check if performance metrics exceed warning thresholds."""
        warnings = []
        
        if memory_percent > self.memory_warning_threshold:
            warnings.append(f"High memory usage: {memory_percent:.1f}%")
        
        if cpu_percent > self.cpu_warning_threshold:
            warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        if self.fps_history and len(self.fps_history) > 0:
            current_fps = self.fps_history[-1]
            if current_fps < self.fps_warning_threshold:
                warnings.append(f"Low FPS: {current_fps:.1f}")
        
        for warning in warnings:
            self.performance_warning.emit(warning)
            self.performance_warnings_count += 1
    
    def start_frame(self):
        """Mark the start of a frame for FPS calculation."""
        self.frame_start_time = time.perf_counter()
    
    def end_frame(self):
        """Mark the end of a frame and calculate FPS."""
        if self.frame_start_time is None:
            return
        
        frame_time = time.perf_counter() - self.frame_start_time
        self.frame_count += 1
        self.total_frames_rendered += 1
        
        # Calculate FPS every 10 frames or every second
        current_time = time.time()
        if (self.frame_count >= 10 or 
            current_time - self.last_fps_calculation >= 1.0):
            
            if current_time > self.last_fps_calculation:
                fps = self.frame_count / (current_time - self.last_fps_calculation)
                self.fps_history.append(fps)
                self.fps_updated.emit(fps)
                
                self.frame_count = 0
                self.last_fps_calculation = current_time
    
    def log_function_call(self, function_name, execution_time_ms):
        """Log function execution time."""
        if not self.enabled:
            return
        
        self.function_timings[function_name].append(execution_time_ms)
        
        # Keep only recent timings to prevent memory bloat
        if len(self.function_timings[function_name]) > 1000:
            self.function_timings[function_name] = self.function_timings[function_name][-500:]
        
        # Warn about slow functions
        if execution_time_ms > self.function_time_warning_threshold:
            warning = f"Slow function: {function_name} took {execution_time_ms:.1f}ms"
            self.performance_warning.emit(warning)
    
    def get_fps(self):
        """Get current FPS."""
        if self.fps_history:
            return self.fps_history[-1]
        return 0.0
    
    def get_stats(self, metric_name):
        """Get statistics for a specific metric."""
        if metric_name == 'memory_mb':
            if self.memory_history:
                memory_info = psutil.virtual_memory()
                return {
                    'latest': memory_info.used / (1024 * 1024),
                    'count': len(self.memory_history)
                }
        elif metric_name == 'cpu_percent':
            if self.cpu_history:
                return {
                    'latest': self.cpu_history[-1] if self.cpu_history else 0,
                    'count': len(self.cpu_history)
                }
        
        # For timing metrics
        if metric_name in self.function_timings:
            timings = self.function_timings[metric_name]
            if timings:
                import numpy as np
                return {
                    'count': len(timings),
                    'mean': np.mean(timings),
                    'min': np.min(timings),
                    'max': np.max(timings),
                    'latest': timings[-1],
                    'p95': np.percentile(timings, 95) if len(timings) > 1 else timings[0]
                }
        
        return {}
    
    def check_performance_warnings(self):
        """Check for performance issues and return warnings."""
        warnings = []
        
        # Check FPS
        current_fps = self.get_fps()
        if current_fps > 0 and current_fps < self.fps_warning_threshold:
            warnings.append(f"Low FPS: {current_fps:.1f}")
        
        # Check memory
        if self.memory_history:
            current_memory = self.memory_history[-1]
            if current_memory > self.memory_warning_threshold:
                warnings.append(f"High memory usage: {current_memory:.1f}%")
        
        # Check CPU
        if self.cpu_history:
            current_cpu = self.cpu_history[-1]
            if current_cpu > self.cpu_warning_threshold:
                warnings.append(f"High CPU usage: {current_cpu:.1f}%")
        
        return warnings
    
    def generate_report(self):
        """Generate a performance report."""
        lines = []
        lines.append("=== PERFORMANCE REPORT ===")
        lines.append(f"Session Duration: {time.time() - self.session_start_time:.1f} seconds")
        lines.append(f"Total Frames: {self.total_frames_rendered}")
        lines.append(f"Warnings Count: {self.performance_warnings_count}")
        lines.append("")
        
        # FPS stats
        if self.fps_history:
            import numpy as np
            fps_array = np.array(list(self.fps_history))
            lines.append("FPS Statistics:")
            lines.append(f"  Average: {np.mean(fps_array):.1f}")
            lines.append(f"  Min: {np.min(fps_array):.1f}")
            lines.append(f"  Max: {np.max(fps_array):.1f}")
            lines.append("")
        
        # Memory stats
        if self.memory_history:
            import numpy as np
            memory_array = np.array(list(self.memory_history))
            lines.append("Memory Usage (%):")
            lines.append(f"  Average: {np.mean(memory_array):.1f}")
            lines.append(f"  Min: {np.min(memory_array):.1f}")
            lines.append(f"  Max: {np.max(memory_array):.1f}")
            lines.append("")
        
        # CPU stats
        if self.cpu_history:
            import numpy as np
            cpu_array = np.array(list(self.cpu_history))
            lines.append("CPU Usage (%):")
            lines.append(f"  Average: {np.mean(cpu_array):.1f}")
            lines.append(f"  Min: {np.min(cpu_array):.1f}")
            lines.append(f"  Max: {np.max(cpu_array):.1f}")
            lines.append("")
        
        # Function timings
        if self.function_timings:
            lines.append("Function Timings (top 10 by average):")
            sorted_funcs = sorted(
                self.function_timings.items(),
                key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
                reverse=True
            )[:10]
            
            for func_name, timings in sorted_funcs:
                if timings:
                    avg_time = sum(timings) / len(timings)
                    lines.append(f"  {func_name}: {avg_time:.2f}ms (calls: {len(timings)})")
        
        return "\n".join(lines)
    
    def get_performance_summary(self):
        """Get comprehensive performance summary."""
        current_time = time.time()
        session_duration = current_time - self.session_start_time
        
        # Calculate averages
        avg_fps = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
        avg_memory = sum(self.memory_history) / len(self.memory_history) if self.memory_history else 0
        avg_cpu = sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0
        
        # Function timing statistics
        function_stats = {}
        for func_name, timings in self.function_timings.items():
            if timings:
                function_stats[func_name] = {
                    'calls': len(timings),
                    'avg_time': sum(timings) / len(timings),
                    'max_time': max(timings),
                    'min_time': min(timings),
                    'total_time': sum(timings)
                }
        
        return {
            'session_duration': session_duration,
            'total_frames': self.total_frames_rendered,
            'avg_fps': avg_fps,
            'max_fps': max(self.fps_history) if self.fps_history else 0,
            'min_fps': min(self.fps_history) if self.fps_history else 0,
            'avg_memory_percent': avg_memory,
            'avg_cpu_percent': avg_cpu,
            'performance_warnings': self.performance_warnings_count,
            'function_stats': function_stats
        }
    
    def export_performance_data(self, filename):
        """Export performance data to JSON file."""
        try:
            summary = self.get_performance_summary()
            summary['fps_history'] = list(self.fps_history)
            summary['memory_history'] = list(self.memory_history)
            summary['cpu_history'] = list(self.cpu_history)
            summary['export_timestamp'] = time.time()
            
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Performance data exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export performance data: {e}")
            return False


class PerformanceDialog(QDialog):
    """Performance monitoring dialog with real-time display."""
    
    def __init__(self, profiler, parent=None):
        super().__init__(parent)
        self.profiler = profiler
        self.setWindowTitle("Performance Monitor")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
        self._connect_signals()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second
    
    def _setup_ui(self):
        """Setup the performance monitoring UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Real-time metrics tab
        self._create_realtime_tab()
        
        # Function timing tab
        self._create_function_timing_tab()
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export Report...")
        self.export_button.clicked.connect(self._export_report)
        button_layout.addWidget(self.export_button)
        
        self.clear_button = QPushButton("Clear Metrics")
        self.clear_button.clicked.connect(self._clear_metrics)
        button_layout.addWidget(self.clear_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _create_realtime_tab(self):
        """Create real-time metrics display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance metrics display
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setFont(self.font())
        layout.addWidget(QLabel("Real-time Performance Metrics:"))
        layout.addWidget(self.metrics_text)
        
        # Performance bars
        metrics_layout = QGridLayout()
        
        # FPS bar
        metrics_layout.addWidget(QLabel("FPS:"), 0, 0)
        self.fps_bar = QProgressBar()
        self.fps_bar.setRange(0, 60)
        self.fps_label = QLabel("0.0")
        metrics_layout.addWidget(self.fps_bar, 0, 1)
        metrics_layout.addWidget(self.fps_label, 0, 2)
        
        # Memory bar
        metrics_layout.addWidget(QLabel("Memory:"), 1, 0)
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        self.memory_label = QLabel("0%")
        metrics_layout.addWidget(self.memory_bar, 1, 1)
        metrics_layout.addWidget(self.memory_label, 1, 2)
        
        # CPU bar
        metrics_layout.addWidget(QLabel("CPU:"), 2, 0)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_label = QLabel("0%")
        metrics_layout.addWidget(self.cpu_bar, 2, 1)
        metrics_layout.addWidget(self.cpu_label, 2, 2)
        
        layout.addLayout(metrics_layout)
        
        self.tab_widget.addTab(widget, "Real-time")
    
    def _create_function_timing_tab(self):
        """Create function timing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.timing_text = QTextEdit()
        self.timing_text.setReadOnly(True)
        layout.addWidget(QLabel("Function Timing Statistics:"))
        layout.addWidget(self.timing_text)
        
        self.tab_widget.addTab(widget, "Function Timing")
    
    def _connect_signals(self):
        """Connect profiler signals to UI updates."""
        self.profiler.fps_updated.connect(self._update_fps_display)
        self.profiler.memory_updated.connect(self._update_memory_display)
        self.profiler.cpu_updated.connect(self._update_cpu_display)
    
    def _update_display(self):
        """Update the performance display."""
        try:
            # Update system metrics
            self.profiler.record_system_metrics()
            
            # Generate real-time report
            report = self._generate_realtime_report()
            self.metrics_text.setPlainText(report)
            
            # Update function timings
            self._update_function_timings()
            
        except Exception as e:
            logger.error(f"Failed to update performance display: {e}")
    
    def _generate_realtime_report(self):
        """Generate a condensed real-time performance report."""
        try:
            lines = []
            
            # Performance warnings
            warnings = self.profiler.check_performance_warnings()
            if warnings:
                lines.append("⚠ PERFORMANCE WARNINGS:")
                lines.extend(f"  {warning}" for warning in warnings)
                lines.append("")
            
            # Session info
            session_time = time.time() - self.profiler.session_start_time
            lines.append(f"Session Time: {session_time:.0f}s")
            lines.append(f"Total Frames: {self.profiler.total_frames_rendered}")
            lines.append(f"Warning Count: {self.profiler.performance_warnings_count}")
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"Error generating report: {e}"
    
    def _update_function_timings(self):
        """Update function timing display."""
        try:
            lines = []
            
            # Sort functions by average time
            sorted_funcs = sorted(
                self.profiler.function_timings.items(),
                key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
                reverse=True
            )[:20]  # Top 20
            
            for func_name, timings in sorted_funcs:
                if timings:
                    avg_time = sum(timings) / len(timings)
                    max_time = max(timings)
                    calls = len(timings)
                    lines.append(f"{func_name}:")
                    lines.append(f"  Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms, Calls: {calls}")
            
            self.timing_text.setPlainText("\n".join(lines))
            
        except Exception as e:
            self.timing_text.setPlainText(f"Error: {e}")
    
    def _update_fps_display(self, fps):
        """Update FPS display."""
        self.fps_bar.setValue(min(int(fps), 60))
        self.fps_label.setText(f"{fps:.1f}")
        
        # Color coding
        if fps < 30:
            self.fps_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif fps < 45:
            self.fps_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.fps_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
    
    def _update_memory_display(self, memory_mb, memory_percent):
        """Update memory display."""
        self.memory_bar.setValue(min(int(memory_percent), 100))
        self.memory_label.setText(f"{memory_percent:.1f}%")
        
        # Color coding
        if memory_percent > 80:
            self.memory_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif memory_percent > 60:
            self.memory_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.memory_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
    
    def _update_cpu_display(self, cpu_percent):
        """Update CPU display."""
        self.cpu_bar.setValue(min(int(cpu_percent), 100))
        self.cpu_label.setText(f"{cpu_percent:.1f}%")
        
        # Color coding
        if cpu_percent > 80:
            self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif cpu_percent > 60:
            self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
    
    def _export_report(self):
        """Export full performance report to file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Performance Report", 
                f"performance_report_{int(time.time())}.txt", 
                "Text Files (*.txt)"
            )
            if filename:
                report = self.profiler.generate_report()
                with open(filename, 'w') as f:
                    f.write(report)
                QMessageBox.information(self, "Success", "Performance report exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report: {e}")
    
    def _clear_metrics(self):
        """Clear all performance metrics."""
        try:
            self.profiler.fps_history.clear()
            self.profiler.memory_history.clear()
            self.profiler.cpu_history.clear()
            self.profiler.function_timings.clear()
            self.profiler.session_start_time = time.time()
            self.profiler.total_frames_rendered = 0
            self.profiler.performance_warnings_count = 0
            QMessageBox.information(self, "Success", "Performance metrics cleared!")
        except Exception as e:
            QMessageBox.critical(self, "Clear Error", f"Failed to clear metrics: {e}")
    
    def closeEvent(self, event):
        """Clean up when dialog is closed."""
        self.update_timer.stop()
        event.accept()
