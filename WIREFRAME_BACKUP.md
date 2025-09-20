# Sacred Geometry Wireframe System - BACKUP

This is a backup of the current sacred geometry morphing wireframe system before implementing the 6-circle cube alternative.

## Current Sacred Geometry Implementation

The current system morphs between 5 sacred geometric shapes:
1. **Sphere** - Unity, Wholeness
2. **Icosahedron** - Sacred 20-sided form, Golden Ratio
3. **Dodecahedron** - Pentagon-based, Universal harmony
4. **Octahedron** - 8-sided, Balance of air element
5. **Tetrahedron** - Fire element, Foundation of 3D

**Note:** Torus was removed per user request.

## Key Features Implemented

### Smooth Vertex Interpolation
- Uses smoothstep easing function: `t * t * (3.0 - 2.0 * t)`
- 3-second morph duration between shapes
- Geometry normalization ensures consistent vertex counts
- Morphs trigger every 12 seconds automatically

### Particle Breathing Synchronization
- Particles expand/contract during wireframe morphing
- Particles are contained within wireframe boundary when NOT morphing
- During morphing, particles can breathe beyond boundary
- Breathing scale: 0.6 to 1.4x during morphs

### State Management
- `isMorphing: boolean` - tracks if currently morphing
- `morphProgress: number` - 0.0 to 1.0 interpolation progress
- `getMorphingState()` method exposes state to other layers

## Files Modified for Sacred Geometry System

### VesselLayer.ts
- `initSacredGeometries()` - creates 5 geometric shapes
- `normalizeGeometriesForMorphing()` - ensures consistent vertex counts
- `startMorphToNextGeometry()` - initiates smooth morphing
- `updateMorphing()` - handles vertex interpolation
- `completeMorph()` - finalizes morph transition

### ParticleLayer.ts
- `synchronizeWithMorphing()` - syncs breathing with wireframe
- `breathingScale` and `breathingSpeed` properties
- Conditional boundary containment based on morphing state

### Engine.ts
- Connects particle breathing to wireframe morphing state
- `morphState = this.vesselLayer.getMorphingState()`
- `this.particleLayer.synchronizeWithMorphing(morphState.isMorphing, morphState.morphProgress)`

## Restoration Instructions

To restore this system after testing alternatives:
1. Use the sacred geometry initialization in `initSacredGeometries()`
2. Enable the morphing system in `update()` method
3. Restore vertex interpolation logic in `updateMorphing()`
4. Re-enable particle breathing synchronization

This system provides smooth, meditative morphing between sacred geometric forms with synchronized particle breathing effects.