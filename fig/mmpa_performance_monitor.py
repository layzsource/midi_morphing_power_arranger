#!/usr/bin/env python3
"""
MMPA Performance Monitor
Real-time monitoring tool for MMPA system performance analysis
"""

import sys
import time
import psutil
import subprocess
import json
from dataclasses import dataclass
from typing import List, Dict

def monitor_mmpa_process():
    """Monitor running MMPA process and provide real-time analysis"""

    print("🔍 MMPA Performance Monitor")
    print("=" * 50)

    # Find MMPA process
    mmpa_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any('enhanced_visual_morphing_mmpa.py' in arg for arg in proc.info['cmdline']):
                mmpa_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not mmpa_processes:
        print("❌ No MMPA process found running")
        print("   Start MMPA with: python3 enhanced_visual_morphing_mmpa.py")
        return

    process = mmpa_processes[0]
    print(f"✅ Found MMPA process: PID {process.pid}")

    # Monitor for 60 seconds
    print("\n📊 Monitoring performance for 60 seconds...")
    print("Press Ctrl+C to stop early\n")

    metrics = []
    start_time = time.time()

    try:
        while (time.time() - start_time) < 60:
            try:
                # Get process metrics
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = process.memory_percent()

                # Get system metrics
                system_cpu = psutil.cpu_percent()
                system_memory = psutil.virtual_memory().percent

                # Calculate load on system
                cpu_load = "HIGH" if cpu_percent > 50 else "NORMAL" if cpu_percent > 20 else "LOW"
                memory_load = "HIGH" if memory_mb > 500 else "NORMAL" if memory_mb > 200 else "LOW"

                metrics.append({
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_mb': memory_mb,
                    'memory_percent': memory_percent,
                    'system_cpu': system_cpu,
                    'system_memory': system_memory
                })

                # Real-time output every 5 seconds
                if len(metrics) % 50 == 0:  # Every 5 seconds (50 * 0.1s intervals)
                    elapsed = time.time() - start_time
                    print(f"[{elapsed:5.1f}s] CPU: {cpu_percent:5.1f}% ({cpu_load:6}) | Memory: {memory_mb:6.1f}MB ({memory_load:6}) | System: {system_cpu:4.1f}%")

            except psutil.NoSuchProcess:
                print("❌ MMPA process terminated")
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")

    # Generate report
    if metrics:
        generate_performance_report(metrics, time.time() - start_time)

def generate_performance_report(metrics: List[Dict], duration: float):
    """Generate comprehensive performance report"""

    print(f"\n📈 PERFORMANCE ANALYSIS REPORT")
    print("=" * 50)

    # Calculate statistics
    cpu_values = [m['cpu_percent'] for m in metrics]
    memory_values = [m['memory_mb'] for m in metrics]
    system_cpu_values = [m['system_cpu'] for m in metrics]

    def stats(values):
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'current': values[-1]
        }

    cpu_stats = stats(cpu_values)
    memory_stats = stats(memory_values)
    system_stats = stats(system_cpu_values)

    print(f"\n⏱️ Monitoring Duration: {duration:.1f} seconds")
    print(f"📊 Data Points: {len(metrics)}")

    print(f"\n🔥 MMPA Process CPU Usage:")
    print(f"   Current: {cpu_stats['current']:6.1f}%")
    print(f"   Average: {cpu_stats['avg']:6.1f}%")
    print(f"   Range:   {cpu_stats['min']:6.1f}% - {cpu_stats['max']:6.1f}%")

    print(f"\n💾 MMPA Process Memory Usage:")
    print(f"   Current: {memory_stats['current']:6.1f} MB")
    print(f"   Average: {memory_stats['avg']:6.1f} MB")
    print(f"   Range:   {memory_stats['min']:6.1f} MB - {memory_stats['max']:6.1f} MB")

    print(f"\n🖥️ System CPU Usage:")
    print(f"   Current: {system_stats['current']:6.1f}%")
    print(f"   Average: {system_stats['avg']:6.1f}%")
    print(f"   Range:   {system_stats['min']:6.1f}% - {system_stats['max']:6.1f}%")

    # Performance analysis
    print(f"\n🎯 PERFORMANCE ANALYSIS:")

    # CPU analysis
    if cpu_stats['avg'] > 80:
        print(f"   ❌ HIGH CPU USAGE: {cpu_stats['avg']:.1f}% average")
        print(f"      • System is CPU-bound")
        print(f"      • Consider reducing visual complexity")
    elif cpu_stats['avg'] > 40:
        print(f"   ⚠️ MODERATE CPU USAGE: {cpu_stats['avg']:.1f}% average")
        print(f"      • Acceptable but room for optimization")
    else:
        print(f"   ✅ LOW CPU USAGE: {cpu_stats['avg']:.1f}% average")
        print(f"      • Efficient CPU utilization")

    # Memory analysis
    memory_growth = memory_stats['max'] - memory_stats['min']
    if memory_growth > 100:  # 100MB growth
        print(f"   ❌ MEMORY LEAK DETECTED: {memory_growth:.1f}MB growth")
        print(f"      • Memory usage increased significantly")
        print(f"      • Check for particle/object cleanup")
    elif memory_growth > 50:
        print(f"   ⚠️ MEMORY GROWTH: {memory_growth:.1f}MB increase")
        print(f"      • Monitor for potential memory leaks")
    else:
        print(f"   ✅ STABLE MEMORY: {memory_growth:.1f}MB variation")
        print(f"      • Good memory management")

    # System impact
    system_impact = system_stats['avg'] - cpu_stats['avg']
    if system_impact < 10:
        print(f"   ✅ LOW SYSTEM IMPACT: MMPA using {cpu_stats['avg']:.1f}% of {system_stats['avg']:.1f}% total")
    else:
        print(f"   📊 SYSTEM USAGE: MMPA using {cpu_stats['avg']:.1f}% of {system_stats['avg']:.1f}% total")

    # Recommendations
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")

    if cpu_stats['avg'] > 60:
        print(f"   • Reduce particle count further")
        print(f"   • Lower shape resolution below 100")
        print(f"   • Increase frame time (lower FPS)")
        print(f"   • Disable complex visual effects")

    if memory_growth > 25:
        print(f"   • Check particle cleanup in update loops")
        print(f"   • Verify signal history buffer limits")
        print(f"   • Monitor OpenGL resource cleanup")

    if cpu_stats['max'] > 90:
        print(f"   • CPU spikes detected - check for blocking operations")
        print(f"   • Consider async processing for heavy computations")

    # Save detailed report
    timestamp = int(time.time())
    filename = f"mmpa_performance_report_{timestamp}.json"

    report_data = {
        'timestamp': timestamp,
        'duration': duration,
        'metrics_count': len(metrics),
        'cpu_stats': cpu_stats,
        'memory_stats': memory_stats,
        'system_stats': system_stats,
        'raw_metrics': metrics
    }

    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"\n💾 Detailed report saved: {filename}")
    print(f"\n✅ Performance analysis complete!")

def get_bottleneck_recommendations(cpu_avg: float, memory_mb: float) -> List[str]:
    """Get specific bottleneck recommendations"""
    recommendations = []

    if cpu_avg > 70:
        recommendations.extend([
            "Reduce shape_resolution from 100 to 50",
            "Increase musical_intelligence_frequency from 60 to 120",
            "Lower target_fps from 20 to 15",
            "Reduce particle multipliers by 50%"
        ])

    if memory_mb > 300:
        recommendations.extend([
            "Limit signal_history buffer size",
            "Clean up old particles more aggressively",
            "Check for OpenGL texture leaks"
        ])

    return recommendations

if __name__ == "__main__":
    monitor_mmpa_process()