#!/usr/bin/env python3
"""
MMPA Performance Profiler
Real-time performance monitoring and bottleneck identification for MMPA system
"""

import sys
import time
import psutil
import threading
from typing import Dict, List
from dataclasses import dataclass
from collections import deque
import json

@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    fps: float
    frame_time_ms: float
    particle_count: int
    vertex_count: int
    gl_calls: int = 0
    gpu_usage: float = 0.0

class MMPAPerformanceProfiler:
    """Real-time performance profiler for MMPA system"""

    def __init__(self, max_history=300):  # 5 minutes at 1fps sampling
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.process = psutil.Process()
        self.monitoring = False
        self.monitor_thread = None

        # Performance tracking
        self.frame_times = deque(maxlen=60)  # Last 60 frame times
        self.last_frame_time = time.time()
        self.frame_count = 0

        # System baseline
        self.baseline_cpu = 0.0
        self.baseline_memory = 0.0
        self._measure_baseline()

    def _measure_baseline(self):
        """Measure system baseline performance"""
        print("📊 Measuring system baseline...")
        cpu_samples = []
        memory_samples = []

        for _ in range(10):
            cpu_samples.append(psutil.cpu_percent(interval=0.1))
            memory_samples.append(self.process.memory_info().rss / 1024 / 1024)

        self.baseline_cpu = sum(cpu_samples) / len(cpu_samples)
        self.baseline_memory = sum(memory_samples) / len(memory_samples)

        print(f"   Baseline CPU: {self.baseline_cpu:.1f}%")
        print(f"   Baseline Memory: {self.baseline_memory:.1f} MB")

    def start_monitoring(self):
        """Start background performance monitoring"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔍 Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("⏹️ Performance monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Collect metrics
                current_time = time.time()
                cpu_percent = self.process.cpu_percent()
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = self.process.memory_percent()

                # Calculate FPS from recent frame times
                fps = self._calculate_fps()
                avg_frame_time = self._calculate_avg_frame_time()

                # Create metrics snapshot
                metrics = PerformanceMetrics(
                    timestamp=current_time,
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    memory_percent=memory_percent,
                    fps=fps,
                    frame_time_ms=avg_frame_time,
                    particle_count=getattr(self, '_last_particle_count', 0),
                    vertex_count=getattr(self, '_last_vertex_count', 0)
                )

                self.metrics_history.append(metrics)

                # Sleep for 1 second
                time.sleep(1.0)

            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                time.sleep(1.0)

    def record_frame(self, particle_count: int = 0, vertex_count: int = 0):
        """Record frame performance data"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time

        self.frame_times.append(frame_time)
        self.last_frame_time = current_time
        self.frame_count += 1

        # Cache for monitoring thread
        self._last_particle_count = particle_count
        self._last_vertex_count = vertex_count

    def _calculate_fps(self) -> float:
        """Calculate current FPS from recent frame times"""
        if len(self.frame_times) < 2:
            return 0.0

        # Use average of recent frame times
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        if avg_frame_time > 0:
            return 1.0 / avg_frame_time
        return 0.0

    def _calculate_avg_frame_time(self) -> float:
        """Calculate average frame time in milliseconds"""
        if not self.frame_times:
            return 0.0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000

    def get_current_metrics(self) -> Dict:
        """Get current performance metrics"""
        if not self.metrics_history:
            return {}

        latest = self.metrics_history[-1]

        # Calculate deltas from baseline
        cpu_delta = latest.cpu_percent - self.baseline_cpu
        memory_delta = latest.memory_mb - self.baseline_memory

        return {
            'timestamp': latest.timestamp,
            'cpu_percent': latest.cpu_percent,
            'cpu_delta': cpu_delta,
            'memory_mb': latest.memory_mb,
            'memory_delta': memory_delta,
            'memory_percent': latest.memory_percent,
            'fps': latest.fps,
            'frame_time_ms': latest.frame_time_ms,
            'particle_count': latest.particle_count,
            'vertex_count': latest.vertex_count,
            'frame_count': self.frame_count
        }

    def get_performance_summary(self) -> Dict:
        """Get performance summary over monitoring period"""
        if not self.metrics_history:
            return {}

        # Calculate statistics
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        memory_values = [m.memory_mb for m in self.metrics_history]
        fps_values = [m.fps for m in self.metrics_history if m.fps > 0]
        frame_time_values = [m.frame_time_ms for m in self.metrics_history if m.frame_time_ms > 0]

        def safe_stats(values):
            if not values:
                return {'min': 0, 'max': 0, 'avg': 0}
            return {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values)
            }

        return {
            'monitoring_duration': len(self.metrics_history),
            'total_frames': self.frame_count,
            'cpu': safe_stats(cpu_values),
            'memory_mb': safe_stats(memory_values),
            'fps': safe_stats(fps_values),
            'frame_time_ms': safe_stats(frame_time_values),
            'baseline': {
                'cpu': self.baseline_cpu,
                'memory_mb': self.baseline_memory
            }
        }

    def identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        if not self.metrics_history:
            return bottlenecks

        latest = self.metrics_history[-1]

        # High CPU usage
        if latest.cpu_percent > 80:
            bottlenecks.append(f"High CPU usage: {latest.cpu_percent:.1f}%")

        # High memory usage
        if latest.memory_percent > 80:
            bottlenecks.append(f"High memory usage: {latest.memory_percent:.1f}%")

        # Low FPS
        if latest.fps > 0 and latest.fps < 15:
            bottlenecks.append(f"Low FPS: {latest.fps:.1f}")

        # High frame time
        if latest.frame_time_ms > 50:  # More than 50ms per frame
            bottlenecks.append(f"High frame time: {latest.frame_time_ms:.1f}ms")

        # Too many particles
        if latest.particle_count > 500:
            bottlenecks.append(f"Too many particles: {latest.particle_count}")

        # Too many vertices
        if latest.vertex_count > 10000:
            bottlenecks.append(f"Too many vertices: {latest.vertex_count}")

        # Memory growth detection
        if len(self.metrics_history) > 60:  # At least 1 minute of data
            recent_memory = [m.memory_mb for m in list(self.metrics_history)[-60:]]
            if recent_memory[-1] > recent_memory[0] * 1.2:  # 20% growth
                bottlenecks.append(f"Memory leak detected: {recent_memory[-1] - recent_memory[0]:.1f}MB growth")

        return bottlenecks

    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        summary = self.get_performance_summary()
        bottlenecks = self.identify_bottlenecks()
        current = self.get_current_metrics()

        report = []
        report.append("📊 MMPA PERFORMANCE REPORT")
        report.append("=" * 50)

        if current:
            report.append(f"\n🔄 Current Status:")
            report.append(f"   CPU: {current['cpu_percent']:.1f}% (Δ{current['cpu_delta']:+.1f}%)")
            report.append(f"   Memory: {current['memory_mb']:.1f}MB (Δ{current['memory_delta']:+.1f}MB)")
            report.append(f"   FPS: {current['fps']:.1f}")
            report.append(f"   Frame Time: {current['frame_time_ms']:.1f}ms")
            report.append(f"   Particles: {current['particle_count']}")
            report.append(f"   Vertices: {current['vertex_count']}")

        if summary:
            report.append(f"\n📈 Performance Summary:")
            report.append(f"   Monitoring Duration: {summary['monitoring_duration']} seconds")
            report.append(f"   Total Frames: {summary['total_frames']}")
            report.append(f"   CPU: {summary['cpu']['avg']:.1f}% avg ({summary['cpu']['min']:.1f}-{summary['cpu']['max']:.1f}%)")
            report.append(f"   Memory: {summary['memory_mb']['avg']:.1f}MB avg ({summary['memory_mb']['min']:.1f}-{summary['memory_mb']['max']:.1f}MB)")

            if summary['fps']['avg'] > 0:
                report.append(f"   FPS: {summary['fps']['avg']:.1f} avg ({summary['fps']['min']:.1f}-{summary['fps']['max']:.1f})")
                report.append(f"   Frame Time: {summary['frame_time_ms']['avg']:.1f}ms avg")

        if bottlenecks:
            report.append(f"\n⚠️ Performance Issues:")
            for bottleneck in bottlenecks:
                report.append(f"   • {bottleneck}")
        else:
            report.append(f"\n✅ No performance issues detected")

        return "\n".join(report)

    def save_metrics(self, filename: str):
        """Save metrics history to file"""
        data = {
            'baseline': {
                'cpu': self.baseline_cpu,
                'memory_mb': self.baseline_memory
            },
            'metrics': [
                {
                    'timestamp': m.timestamp,
                    'cpu_percent': m.cpu_percent,
                    'memory_mb': m.memory_mb,
                    'memory_percent': m.memory_percent,
                    'fps': m.fps,
                    'frame_time_ms': m.frame_time_ms,
                    'particle_count': m.particle_count,
                    'vertex_count': m.vertex_count
                }
                for m in self.metrics_history
            ]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Metrics saved to {filename}")

def test_profiler():
    """Test the performance profiler"""
    print("🧪 Testing MMPA Performance Profiler")

    profiler = MMPAPerformanceProfiler()
    profiler.start_monitoring()

    # Simulate some workload
    print("⚡ Simulating workload...")
    for i in range(10):
        # Simulate frame processing
        profiler.record_frame(particle_count=100 + i*10, vertex_count=1000 + i*100)

        # Simulate some work
        time.sleep(0.1)

        if i % 3 == 0:
            print(f"   Frame {i}: {profiler.get_current_metrics()['fps']:.1f} FPS")

    time.sleep(2)  # Let monitoring collect some data

    # Generate report
    report = profiler.generate_performance_report()
    print(f"\n{report}")

    # Save metrics
    profiler.save_metrics("mmpa_performance_test.json")

    profiler.stop_monitoring()
    print("\n✅ Profiler test completed")

if __name__ == "__main__":
    test_profiler()