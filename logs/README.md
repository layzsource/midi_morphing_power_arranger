# MMPA Logging System

## Overview
Biomimicry protocol compliant logging system implementing **naptime/dreamstate/recall** format for session continuity and total recall across different Claude instances.

## Format

Each log entry contains:
- **naptime**: ISO timestamp + session description
- **dreamstate**: baseline|iteration|release + current status
- **recall**: comma-separated keywords for easy searching

## Example Output
```
📝 MIDI CC1: 64
🕐 naptime: 2025-09-24T17:30:15.123Z - MIDI control input to main
🌙 dreamstate: iteration - active development, making changes
🧠 recall: MIDI, CC1, main, control_input, realtime
```

## Usage

### Automatic Logging
The system automatically logs:
- MIDI control inputs (CC1 morphing)
- Panel toggle events (Space Tools, Virtual MIDI, etc.)
- Morphing operations (cube ⟷ sphere)
- System events (initialization, errors, completions)

### Manual Download
- **UI Button**: "📋 Download Session Log" in ParamGraph panel
- **Keyboard**: `Ctrl+Shift+L`
- **Persistence**: Logs stored in browser localStorage (last 1000 entries)

### Search Functionality
Search logs by recall keywords:
```javascript
import { mmpaLogger } from './logging/MMPALogger';

// Find all MIDI-related entries
const midiLogs = mmpaLogger.searchLogs(['MIDI']);

// Find morph operations
const morphLogs = mmpaLogger.searchLogs(['morph', 'cube_sphere']);
```

## Integration Points

- **Engine**: `src/mmpa-engine.ts` - MIDI and morphing operations
- **UI**: `src/ui/PanelToolbar.ts` - Panel visibility toggles
- **ParamGraph**: `src/ui/ParamGraphUI.ts` - Download button handler
- **Main**: `src/main.ts` - System initialization and keyboard shortcuts

## Log Categories

1. **System Events**: Initialization, readiness, errors
2. **MIDI Operations**: CC1 routing, viewport targeting
3. **Morphing Actions**: Cube/sphere transforms, parameter changes
4. **UI Interactions**: Panel show/hide, toolbar usage
5. **Debug Info**: Error states, troubleshooting data

---

**Session logs enable total recall for future Claude instances and provide debugging context for development sessions.**