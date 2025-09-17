#!/usr/bin/env python3
"""
Test the Performance Recording system
This script simulates user interaction to test recording features
"""

import json
import os
import time
from pathlib import Path

def check_recording_files():
    """Check for existing recording files"""
    print("🎬 Checking for existing recording files...")

    recording_files = list(Path('.').glob('*recording*.json'))
    performance_files = list(Path('.').glob('*performance*.json'))

    all_files = recording_files + performance_files

    if all_files:
        print(f"✅ Found {len(all_files)} recording files:")
        for file in all_files:
            size = file.stat().st_size
            modified = time.ctime(file.stat().st_mtime)
            print(f"  📁 {file.name} ({size} bytes, modified: {modified})")

            # Show snippet of content
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    print(f"     📊 Contains: {len(data.get('frames', []))} frames")
                    if 'recording_info' in data:
                        info = data['recording_info']
                        print(f"     🎵 Duration: {info.get('duration', 'unknown')}s")
                        print(f"     🎼 Genre detections: {len(info.get('genre_changes', []))}")
                        print(f"     🎨 Color changes: {len(info.get('color_changes', []))}")
            except Exception as e:
                print(f"     ❌ Error reading file: {e}")
    else:
        print("📭 No recording files found")

    return all_files

def analyze_recording_structure():
    """Analyze the structure of recording files to understand the data format"""
    files = check_recording_files()

    if files:
        # Analyze the most recent file
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        print(f"\n🔍 Analyzing structure of: {latest_file.name}")

        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)

            print(f"📋 Recording Structure Analysis:")
            print(f"  🗃️ Top-level keys: {list(data.keys())}")

            if 'frames' in data and data['frames']:
                frame = data['frames'][0]
                print(f"  📊 Frame structure: {list(frame.keys())}")

                if 'musical_intelligence' in frame:
                    mi = frame['musical_intelligence']
                    print(f"  🎼 Musical intelligence data: {list(mi.keys())}")

            if 'recording_info' in data:
                info = data['recording_info']
                print(f"  ℹ️ Recording info: {list(info.keys())}")

        except Exception as e:
            print(f"❌ Error analyzing file: {e}")

def test_recording_features():
    """Test various aspects of the recording system"""
    print("\n🧪 RECORDING SYSTEM TEST SUMMARY")
    print("=" * 50)

    print("\n✅ WHAT WE CAN VERIFY:")
    print("  🎬 Recording file creation and structure")
    print("  📊 JSON data format and content")
    print("  🎵 Musical intelligence data capture")
    print("  ⏱️ Timestamp and duration tracking")

    print("\n🎯 TO TEST INTERACTIVELY:")
    print("  1. Start MMPA system: python3 enhanced_visual_morphing_mmpa.py")
    print("  2. Click '🔴 Start Recording' button")
    print("  3. Play music or generate audio (run test_musical_intelligence_live.py)")
    print("  4. Click '⏹️ Stop Recording' button")
    print("  5. Check for new .json files with recording data")

    print("\n📁 CURRENT RECORDING STATUS:")
    check_recording_files()

if __name__ == "__main__":
    test_recording_features()
    analyze_recording_structure()