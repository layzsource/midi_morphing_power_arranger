#!/usr/bin/env python3
"""
MMPA Quick Start Script
Launches the recommended stable advanced version with proper setup.
"""

import sys
import os
from pathlib import Path

def main():
    """Quick start for MMPA with guidance."""

    print("🎵" + "="*60 + "🎵")
    print("    MMPA - The Language of Signals Becoming Form")
    print("         Professional Audio Visual Synthesis")
    print("🎵" + "="*60 + "🎵")
    print()

    print("🚀 QUICK START OPTIONS:")
    print()
    print("1️⃣  Advanced Version (Recommended)")
    print("    ✅ Professional spectral analysis")
    print("    ✅ Real-time frequency displays")
    print("    ✅ Manual audio toggle")
    print("    ✅ Stable & reliable")
    print()
    print("2️⃣  Minimal Version (Ultra-Safe)")
    print("    ✅ 100% freeze-proof")
    print("    ✅ Basic functionality")
    print("    ✅ System diagnostics")
    print("    ✅ Minimal resources")
    print()

    try:
        choice = input("Choose version (1 for Advanced, 2 for Minimal, Enter for Advanced): ").strip()

        if choice == "2":
            print("\n🔧 Launching Minimal MMPA...")
            os.system("python3 run_minimal_mmpa.py")
        else:
            print("\n🔧 Launching Advanced MMPA...")
            print("📖 Note: Audio starts OFF - click 'START Audio' button when ready")
            os.system("python3 run_stable_advanced_mmpa.py")

    except KeyboardInterrupt:
        print("\n\n👋 MMPA startup cancelled")
        sys.exit(0)

if __name__ == "__main__":
    main()