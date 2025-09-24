# MMPA Session Briefing Document
**Category:** 000_System
**naptime:** 2025-09-24T16:30:15Z
**dreamstate:** baseline - session recall document
**recall:** MMPA, repair_tracker, priorities, PERIAKTOS, biomimicry_protocol

---

## Project Overview
**MMPA Universal Signal Engine** - MIDI Morphing Power Arranger
**Core Identity:** 6-panel PERIAKTOS cube with transparent colored panels, morphing capabilities, image/video mapping

---

## Key File Locations

### Repair Tracker (Always Check First)
- `/Users/ticegunther/Downloads/MMPA_Repair_Tracker_Status (1).csv`
- Contains priority order: High → Medium → Low
- Current Priority #1: Cube & Morph System (colored + transparent panels)

### MMPA Baseline Specifications
- `/Users/ticegunther/Downloads/MMPA_Baseline/`
  - `docs/dewey_system.md` - File organization (000-900 categories)
  - `docs/vessel_controls.md` - Keyboard + control mappings
  - `midi/mappings.json` - CC1 deadband system (0-52, 53-73, 74-127)

### Biomimicry Protocol
- `/Users/ticegunther/Downloads/biomimicry_starter_bundle 4/docs/collaboration_protocol.md`
- Contains logging format: naptime, dreamstate, recall tags
- Kill scripts and workflow rules

### Working Python Scripts
- `/Users/ticegunther/morphing_interface/working_full_app_backup.py` - Functional MIDI morphing
- `/Users/ticegunther/morphing_interface/working_full_app.py` - Alternative version

---

## Current System State

### Web Interface
- **Location:** `/Users/ticegunther/universal-signal-engine/`
- **Dev Server:** http://localhost:3000/
- **Core File:** `src/layers/SkyboxCubeLayer_v2_subdivision.ts`
- **Status:** Fixed to show colored panels instead of red cube (line 115)

### PERIAKTOS Panel System
- **FLOOR:** White (0xffffff)
- **CEILING:** Blue (0x0000ff)
- **NORTH:** Red (0xff0000)
- **SOUTH:** Green (0x00ff00)
- **EAST:** Yellow (0xffff00)
- **WEST:** Magenta (0xff00ff)
- **Transparency:** 0.9 opacity
- **Ready for:** Image/video mapping

---

## Recent Fixes Applied

### 2025-09-24 Session
1. **Fixed Priority #1:** Changed `showSolidCube()` to `showColoredPanels()` in constructor
2. **File:** `SkyboxCubeLayer_v2_subdivision.ts:115`
3. **Result:** PERIAKTOS colored panels now display instead of red solid cube
4. **Backup:** Created `SkyboxCubeLayer_v3_backwards_e.ts` (broken state)

---

## Next Priorities (From Repair Tracker)

### High Priority
1. ✅ **Core Engine - Cube & Morph System** - COMPLETED
2. **Controls - Mod Wheels:** Isolate across windows, stop cross-talk, keep deadband logic
3. **Controls - On-Screen Layer:** Touch/mouse + MIDI coexistence
4. **Controls - Toolbars & Panels:** Make all visible, inside viewport, scrollable

### Medium Priority
- **Docs - Logging & Tags:** naptime/dreamstate timestamps
- **Docs - Dewey System:** File organization documentation

### Low Priority
- **Features - Theremin/Webcam:** Toolbar button + UI placeholder
- **Expansion - Voice Control:** Spell-casting layer

---

## MIDI Specifications (MMPA Baseline)

### CC1 Modwheel (Primary Control)
- **Target:** morph_axis_blend
- **Deadband System:**
  - 0-52: Left action (continuous motion)
  - 53-73: Hold/neutral zone (stop motion)
  - 74-127: Right action (continuous motion)

### Other Controls
- **CC7:** Volume → global_intensity
- **CC11:** Expression → color_saturation
- **Sustain:** hold_state (gate mode)
- **Pads 1-8:** Various preset/control functions

---

## Development Notes

### Server Issues
- Frequent reload problems - use cache clearing: `rm -rf node_modules/.vite && npm run dev`
- Multiple background processes cause conflicts
- Use `lsof -ti:3000 | xargs kill -9` to clear ports

### Code Organization
- Follow Dewey system: 000-System, 100-Theory, 200-Geometry, 300-Audio, 400-Visual, 500-WebUI, etc.
- Use proper TypeScript compilation - avoid breaking changes
- Test each modification before proceeding

---

## Logging Format (For All Future Sessions)

```
naptime: 2025-MM-DDTHH:MM:SSZ - session description
dreamstate: baseline|iteration|release - current status
recall: keyword1, keyword2, priority_item, file_location
```

**Example:**
```
naptime: 2025-09-24T16:30:00Z - MMPA cube morph repair
dreamstate: iteration - fixing PERIAKTOS panels
recall: showColoredPanels, transparent, FLOOR_WHITE_CEILING_BLUE, line_115
```

---

## Quick Start for New Sessions

1. **Read repair tracker first:** Check current priorities
2. **Review this briefing:** Understand system state
3. **Check dev server:** Ensure http://localhost:3000/ loads
4. **Apply logging format:** Use naptime/dreamstate/recall tags
5. **Follow Dewey organization:** Categorize all work properly
6. **Test incrementally:** Don't break working functionality

---

**End of Briefing**
**naptime:** 2025-09-24T16:32:00Z
**dreamstate:** baseline - ready for handoff
**recall:** session_continuity, future_claude_instances, MMPA_complete_context