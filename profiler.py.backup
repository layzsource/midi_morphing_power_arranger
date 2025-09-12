"""
Fixed profiler.py - Performance profiling and monitoring system.
"""

import time
import logging
import psutil
import numpy as np
from collections import deque, defaultdict
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """Comprehensive performance monitoring and profiling system."""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics = defaultdict(lambda: deque(maxlen=max_samples))
        self.counters = defaultdict(int)
        self.timers = {}
        self.start_time = time.time()
        
        # System monitoring
        self.process = psutil.Process()
        self.system_metrics = deque(maxlen=max_samples)
        
        # Performance thresholds
        self.thresholds = {
            'render_time': 0.033,  # 30fps = 33ms
            'memory_mb': 500,      # 500MB memory warning
            'cpu_percent': 80,     # 80% CPU warning
            'fps': 30,             # Minimum FPS target
            'light_update_time': 0.010,  # 10ms for light operations
            'mesh_update_time': 0.020,   # 20ms for mesh updates
        }
        
    def start_timer(self, name: str) -> float:
        """Start a performance timer."""
        start_time = time.perf_counter()
        self.timers[name] = start_time
        return start_time
        
    def end_timer(self, name: str) -> Optional[float]:
        """End a performance timer and record the duration."""
        if name not in self.timers:
            return None
            
        duration = time.perf_counter() - self.timers[name]
        self.metrics[f'{name}_time'].append(duration)
        del self.timers[name]
        return duration
        
    def record_metric(self, name: str, value: float):
        """Record a performance metric."""
        self.metrics[name].append(value)
        
    def increment_counter(self, name: str, amount: int = 1):
        """Increment a performance counter."""
        self.counters[name] += amount
        
    def record_system_metrics(self):
        """Record current system resource usage."""
        try:
            # Get CPU percent with a small interval for accuracy
            cpu_percent = self.process.cpu_percent(interval=0.1)
            
            # Get memory info
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Create system metrics record
            system_data = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'memory_vms_mb': memory_info.vms / 1024 / 1024,
                'threads': self.process.num_threads(),
            }
            
            # Store in collections
            self.system_metrics.append(system_data)
            self.record_metric('cpu_percent', cpu_percent)
            self.record_metric('memory_mb', memory_mb)
            
            return system_data
            
        except Exception as e:
            logger.error(f"Failed to record system metrics: {e}")
            return None
    
    def get_stats(self, name: str) -> Dict:
        """Get statistics for a specific metric."""
        if name not in self.metrics or not self.metrics[name]:
            return {}
            
        values = list(self.metrics[name])
        if not values:
            return {}
            
        return {
            'count': len(values),
            'mean': np.mean(values),
            'min': np.min(values),
            'max': np.max(values),
            'std': np.std(values),
            'p50': np.percentile(values, 50),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99),
            'latest': values[-1] if values else 0,
        }
    
    def get_fps(self) -> float:
        """Calculate current FPS based on render times."""
        render_times = list(self.metrics.get('render_time', []))
        if len(render_times) < 2:
            return 0.0
            
        # Use recent render times for FPS calculation
        recent_times = render_times[-10:]  # Last 10 renders
        if not recent_times:
            return 0.0
            
        avg_time = np.mean(recent_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0
    
    def check_performance_warnings(self) -> List[str]:
        """Check for performance issues and return warnings."""
        warnings = []
        
        try:
            # Check FPS
            current_fps = self.get_fps()
            if current_fps > 0 and current_fps < self.thresholds['fps']:
                warnings.append(f"Low FPS: {current_fps:.1f} (target: {self.thresholds['fps']})")
            
            # Check render time
            render_stats = self.get_stats('render_time')
            if render_stats and 'p95' in render_stats and render_stats['p95'] > self.thresholds['render_time']:
                warnings.append(f"High render time: {render_stats['p95']*1000:.1f}ms (95th percentile)")
            
            # Check memory usage
            memory_stats = self.get_stats('memory_mb')
            if memory_stats and 'latest' in memory_stats and memory_stats['latest'] > self.thresholds['memory_mb']:
                warnings.append(f"High memory usage: {memory_stats['latest']:.1f}MB")
            
            # Check CPU usage
            cpu_stats = self.get_stats('cpu_percent')
            if cpu_stats and 'p95' in cpu_stats and cpu_stats['p95'] > self.thresholds['cpu_percent']:
                warnings.append(f"High CPU usage: {cpu_stats['p95']:.1f}% (95th percentile)")
            
            # Check light update performance
            light_stats = self.get_stats('light_update_time')
            if light_stats and 'p95' in light_stats and light_stats['p95'] > self.thresholds['light_update_time']:
                warnings.append(f"Slow light updates: {light_stats['p95']*1000:.1f}ms")
                
            # Check mesh update performance
            mesh_stats = self.get_stats('mesh_update_time')
            if mesh_stats and 'p95' in mesh_stats and mesh_stats['p95'] > self.thresholds['mesh_update_time']:
                warnings.append(f"Slow mesh updates: {mesh_stats['p95']*1000:.1f}ms")
                
        except Exception as e:
            logger.error(f"Error checking performance warnings: {e}")
            
        return warnings
    
    def generate_report(self) -> str:
        """Generate a comprehensive performance report."""
        try:
            report_lines = [
                "=== PERFORMANCE REPORT ===",
                f"Session Duration: {time.time() - self.start_time:.1f} seconds",
                f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "=== SYSTEM METRICS ===",
            ]
            
            # System metrics
            if self.system_metrics:
                latest_system = self.system_metrics[-1]
                report_lines.extend([
                    f"CPU Usage: {latest_system['cpu_percent']:.1f}%",
                    f"Memory Usage: {latest_system['memory_mb']:.1f} MB (RSS)",
                    f"Virtual Memory: {latest_system['memory_vms_mb']:.1f} MB",
                    f"Thread Count: {latest_system['threads']}",
                    "",
                ])
            
            # Performance metrics
            report_lines.append("=== PERFORMANCE METRICS ===")
            
            key_metrics = [
                'render_time', 'light_update_time', 'mesh_update_time', 
                'osc_message_time', 'midi_callback_time'
            ]
            
            for metric in key_metrics:
                stats = self.get_stats(metric)
                if stats and stats.get('count', 0) > 0:
                    report_lines.extend([
                        f"{metric.replace('_', ' ').title()}:",
                        f"  Count: {stats['count']}",
                        f"  Mean: {stats['mean']*1000:.2f}ms",
                        f"  Min/Max: {stats['min']*1000:.2f}ms / {stats['max']*1000:.2f}ms",
                        f"  95th percentile: {stats['p95']*1000:.2f}ms",
                        f"  99th percentile: {stats['p99']*1000:.2f}ms",
                        "",
                    ])
            
            # FPS calculation
            current_fps = self.get_fps()
            if current_fps > 0:
                report_lines.extend([
                    f"Current FPS: {current_fps:.1f}",
                    "",
                ])
            
            # Counters
            if self.counters:
                report_lines.append("=== COUNTERS ===")
                for name, count in sorted(self.counters.items()):
                    rate = count / (time.time() - self.start_time) if time.time() - self.start_time > 0 else 0
                    report_lines.append(f"{name}: {count} (rate: {rate:.2f}/sec)")
                report_lines.append("")
            
            # Performance warnings
            warnings = self.check_performance_warnings()
            if warnings:
                report_lines.append("=== PERFORMANCE WARNINGS ===")
                report_lines.extend(f"⚠ {warning}" for warning in warnings)
                report_lines.append("")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return f"Performance report generation failed: {e}"
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.system_metrics.clear()
        self.timers.clear()
        self.start_time = time.time()

# Global profiler instance
profiler = PerformanceProfiler()

def profile_function(func_name: str = None):
    """Decorator to automatically profile function execution time."""
    def decorator(func):
        name = func_name or f"{func.__module__}.{func.__name__}"
        
        def wrapper(*args, **kwargs):
            profiler.start_timer(name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profiler.end_timer(name)
                profiler.increment_counter(f"{name}_calls")
        
        return wrapper
    return decorator
