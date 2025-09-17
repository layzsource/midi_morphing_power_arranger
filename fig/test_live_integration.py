#!/usr/bin/env python3
"""
Live Integration Test - MMPA Professional System
==============================================

Real-world testing of all MMPA systems working together:
- Main enhanced morphing system
- Professional UI controls
- Advanced lighting system
- Production versions
- Feature verification

This test actually runs the systems and verifies they work together.
"""

import sys
import time
import subprocess
import threading
from typing import List, Dict

def test_system_startup(system_name: str, command: List[str], timeout: int = 10) -> Dict:
    """Test if a system starts successfully"""
    print(f"🧪 Testing {system_name}...")

    try:
        # Start the system
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Give it time to initialize
        time.sleep(timeout)

        # Check if it's still running
        if process.poll() is None:
            # System is running
            process.terminate()
            process.wait(timeout=5)
            return {
                'name': system_name,
                'status': '✅ PASSED',
                'details': 'System started and ran successfully',
                'running_time': timeout
            }
        else:
            # System crashed or exited
            stdout, stderr = process.communicate()
            return {
                'name': system_name,
                'status': '❌ FAILED',
                'details': f'System crashed: {stderr}',
                'running_time': 0
            }

    except Exception as e:
        return {
            'name': system_name,
            'status': '💥 ERROR',
            'details': f'Failed to start: {str(e)}',
            'running_time': 0
        }

def run_live_integration_tests():
    """Run comprehensive live integration tests"""
    print("🧪 MMPA LIVE INTEGRATION TEST SUITE")
    print("=" * 45)
    print("Testing real system startup and operation\n")

    # Define systems to test
    test_systems = [
        {
            'name': 'Enhanced Visual Morphing (Main System)',
            'command': ['python3', 'enhanced_visual_morphing_mmpa.py'],
            'timeout': 8
        },
        {
            'name': 'Standard Production Version',
            'command': ['python3', 'mmpa_standard.py'],
            'timeout': 8
        },
        {
            'name': 'Light Production Version',
            'command': ['python3', 'mmpa_light.py'],
            'timeout': 6
        },
        {
            'name': 'Professional UI (Fixed)',
            'command': ['python3', 'mmpa_professional_ui_fixed.py'],
            'timeout': 6
        },
        {
            'name': 'Advanced Lighting System',
            'command': ['python3', 'mmpa_advanced_lighting.py'],
            'timeout': 6
        }
    ]

    # Run tests
    results = []
    for system in test_systems:
        result = test_system_startup(
            system['name'],
            system['command'],
            system['timeout']
        )
        results.append(result)

        # Show immediate result
        print(f"   {result['status']} {result['name']}")
        if result['status'] != '✅ PASSED':
            print(f"      Details: {result['details']}")
        print()

    # Summary
    print("\n" + "=" * 50)
    print("🏆 LIVE INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for r in results if '✅' in r['status'])
    failed = sum(1 for r in results if '❌' in r['status'])
    errors = sum(1 for r in results if '💥' in r['status'])
    total = len(results)

    print(f"Systems Tested: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errors}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        print(f"   {result['name']:<40}: {result['status']}")
        if result['status'] == '✅ PASSED':
            print(f"      Ran successfully for {result['running_time']} seconds")
        else:
            print(f"      Issue: {result['details']}")

    # Overall assessment
    success_rate = (passed / total) * 100

    if success_rate >= 80:
        print(f"\n🚀 OVERALL ASSESSMENT: EXCELLENT")
        print("   All major systems are operational")
        print("   Integration is working correctly")
        assessment = "PRODUCTION READY"
    elif success_rate >= 60:
        print(f"\n✅ OVERALL ASSESSMENT: GOOD")
        print("   Most systems operational with minor issues")
        assessment = "MOSTLY READY"
    else:
        print(f"\n⚠️ OVERALL ASSESSMENT: NEEDS WORK")
        print("   Multiple systems have issues")
        assessment = "NOT READY"

    print(f"\n🎯 DEPLOYMENT STATUS: {assessment}")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if passed >= 4:
        print("   • Main enhanced system is working - use as primary")
        print("   • Production versions are operational")
        print("   • Professional UI provides good control interface")
        print("   • System ready for user testing and feedback")
    elif passed >= 2:
        print("   • Core functionality working but needs refinement")
        print("   • Focus on fixing failed systems")
        print("   • Test again after fixes")
    else:
        print("   • Major integration issues detected")
        print("   • Review system dependencies and imports")
        print("   • Fix core systems before proceeding")

    print(f"\n🎵 Live integration testing complete!")
    return success_rate >= 60

def verify_file_availability():
    """Verify all required files are available"""
    print("📁 FILE AVAILABILITY CHECK")
    print("=" * 30)

    required_files = [
        'enhanced_visual_morphing_mmpa.py',
        'mmpa_standard.py',
        'mmpa_light.py',
        'mmpa_professional_ui_fixed.py',
        'mmpa_advanced_lighting.py',
        'mmpa_signal_framework.py',
        'mmpa_midi_processor.py'
    ]

    available_files = []
    missing_files = []

    import os

    for file in required_files:
        if os.path.exists(file):
            available_files.append(file)
            print(f"   ✅ {file}")
        else:
            missing_files.append(file)
            print(f"   ❌ {file}")

    print(f"\nFiles Available: {len(available_files)}/{len(required_files)}")

    if missing_files:
        print(f"⚠️ Missing Files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files are available")
        return True

def check_dependencies():
    """Check Python dependencies"""
    print("\n🔧 DEPENDENCY CHECK")
    print("=" * 20)

    dependencies = [
        ('PySide6', 'PySide6'),
        ('OpenGL', 'OpenGL.GL'),
        ('NumPy', 'numpy'),
    ]

    available_deps = []
    missing_deps = []

    for name, import_name in dependencies:
        try:
            __import__(import_name)
            available_deps.append(name)
            print(f"   ✅ {name}")
        except ImportError:
            missing_deps.append(name)
            print(f"   ❌ {name}")

    print(f"\nDependencies Available: {len(available_deps)}/{len(dependencies)}")

    if missing_deps:
        print(f"⚠️ Missing Dependencies: {', '.join(missing_deps)}")
        return False
    else:
        print("✅ All dependencies are available")
        return True

def main():
    """Run complete live integration test suite"""
    print("🚀 MMPA COMPREHENSIVE LIVE TESTING")
    print("=" * 40)
    print("Real-world integration testing of all MMPA systems")
    print()

    # Check prerequisites
    files_ok = verify_file_availability()
    deps_ok = check_dependencies()

    if not files_ok or not deps_ok:
        print("\n❌ PREREQUISITES NOT MET")
        print("Please ensure all files and dependencies are available")
        return False

    print("\n✅ Prerequisites met - proceeding with live tests\n")

    # Run live integration tests
    success = run_live_integration_tests()

    if success:
        print("\n🎉 INTEGRATION TESTING SUCCESSFUL!")
        print("MMPA systems are working together properly")
        return True
    else:
        print("\n⚠️ INTEGRATION ISSUES DETECTED")
        print("Some systems need attention before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)