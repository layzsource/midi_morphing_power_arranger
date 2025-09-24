/**
 * Advanced Gesture Choreographer
 *
 * Multi-hand gesture combinations for professional VJ performance:
 * - Complex gesture sequences and combinations
 * - Gesture-to-preset mapping system
 * - Choreographed gesture recording/playback
 * - Real-time gesture analysis and pattern recognition
 */

import { Landmark } from '@mediapipe/hands';

export type HandLandmark = Landmark;

export interface GestureChoreographyCallbacks {
    onGestureCombination: (combo: GestureCombination) => void;
    onGestureSequence: (sequence: GestureSequence) => void;
    onChoreographyTrigger: (choreography: string, intensity: number) => void;
}

export interface GestureCombination {
    name: string;
    leftHand: string;
    rightHand: string;
    distance: number;
    synchronization: number; // 0-1, how synchronized the gestures are
    intensity: number; // 0-1, overall gesture intensity
    confidence: number; // 0-1, detection confidence
}

export interface GestureSequence {
    name: string;
    gestures: string[];
    timing: number[]; // Milliseconds between gestures
    totalDuration: number;
    repeatCount: number;
}

export interface ChoreographedMove {
    name: string;
    combinations: GestureCombination[];
    sequences: GestureSequence[];
    visualPreset: string;
    audioTrigger?: string;
}

export interface GestureRecording {
    id: string;
    name: string;
    timestamp: number;
    duration: number;
    frames: GestureFrame[];
    metadata: {
        performer: string;
        tempo: number;
        complexity: number;
        tags: string[];
    };
}

export interface GestureFrame {
    time: number; // Relative to recording start
    leftHand?: HandLandmark[];
    rightHand?: HandLandmark[];
    detectedGestures: string[];
    intensity: number;
    confidence: number;
}

export class AdvancedGestureChoreographer {
    private callbacks: GestureChoreographyCallbacks;

    // Gesture tracking
    private leftHandHistory: { gesture: string; landmarks: HandLandmark[]; time: number }[] = [];
    private rightHandHistory: { gesture: string; landmarks: HandLandmark[]; time: number }[] = [];
    private combinationHistory: GestureCombination[] = [];
    private sequenceHistory: GestureSequence[] = [];

    // Choreography system
    private choreographedMoves: Map<string, ChoreographedMove> = new Map();
    private activeChoreography: string | null = null;
    private choreographyStartTime: number = 0;

    // Recording/Playback system
    private isRecording: boolean = false;
    private currentRecording: GestureRecording | null = null;
    private recordingStartTime: number = 0;
    private recordedGestures: Map<string, GestureRecording> = new Map();

    // Playback system
    private isPlaying: boolean = false;
    private playbackRecording: GestureRecording | null = null;
    private playbackStartTime: number = 0;
    private playbackSpeed: number = 1.0;

    // Pattern recognition
    private gesturePatterns: Map<string, string[]> = new Map();

    constructor(callbacks: GestureChoreographyCallbacks) {
        this.callbacks = callbacks;
        this.initializeChoreographedMoves();
        this.initializeGesturePatterns();
    }

    private initializeChoreographedMoves() {
        // Define professional VJ gesture choreographies

        // 🌀 SPIRAL INCEPTION - Complex ring morphing sequence
        this.choreographedMoves.set('spiral_inception', {
            name: 'Spiral Inception',
            combinations: [
                {
                    name: 'dual_spiral',
                    leftHand: 'spiral_clockwise',
                    rightHand: 'spiral_counter',
                    distance: 0.3,
                    synchronization: 0.8,
                    intensity: 0.9,
                    confidence: 0.85
                }
            ],
            sequences: [
                {
                    name: 'inception_build',
                    gestures: ['open_palm', 'fist', 'spiral_clockwise', 'finger_spread', 'snap'],
                    timing: [500, 300, 800, 400, 200],
                    totalDuration: 2200,
                    repeatCount: 3
                }
            ],
            visualPreset: 'ring_morph_spiral',
            audioTrigger: 'deep_bass_drop'
        });

        // 🔥 FIRE STORM - Intense effects cascade
        this.choreographedMoves.set('fire_storm', {
            name: 'Fire Storm',
            combinations: [
                {
                    name: 'dual_clap',
                    leftHand: 'clap_prep',
                    rightHand: 'clap_prep',
                    distance: 0.05,
                    synchronization: 0.95,
                    intensity: 1.0,
                    confidence: 0.9
                }
            ],
            sequences: [
                {
                    name: 'storm_build',
                    gestures: ['point_up', 'wave_horizontal', 'clap', 'finger_spread', 'fist_slam'],
                    timing: [400, 600, 100, 300, 200],
                    totalDuration: 1600,
                    repeatCount: 1
                }
            ],
            visualPreset: 'effects_cascade_fire',
            audioTrigger: 'storm_buildup'
        });

        // 💎 CRYSTAL FORMATION - Precise geometric patterns
        this.choreographedMoves.set('crystal_formation', {
            name: 'Crystal Formation',
            combinations: [
                {
                    name: 'precise_geometry',
                    leftHand: 'triangle_shape',
                    rightHand: 'triangle_shape',
                    distance: 0.25,
                    synchronization: 0.9,
                    intensity: 0.7,
                    confidence: 0.8
                }
            ],
            sequences: [
                {
                    name: 'crystal_growth',
                    gestures: ['point_center', 'triangle_shape', 'diamond_shape', 'finger_spread', 'hold_position'],
                    timing: [300, 500, 500, 400, 1000],
                    totalDuration: 2700,
                    repeatCount: 2
                }
            ],
            visualPreset: 'geometric_crystal',
            audioTrigger: 'crystalline_tones'
        });
    }

    private initializeGesturePatterns() {
        // Define gesture pattern recognition sequences
        this.gesturePatterns.set('power_up', ['fist', 'open_palm', 'finger_spread', 'snap']);
        this.gesturePatterns.set('energy_burst', ['clap', 'wave_horizontal', 'finger_spread']);
        this.gesturePatterns.set('focus_beam', ['point_forward', 'hold_position', 'slow_wave']);
        this.gesturePatterns.set('reality_shift', ['snap', 'spiral_clockwise', 'clap', 'open_palm']);
        this.gesturePatterns.set('dimension_tear', ['finger_spread', 'fist', 'diagonal_swipe', 'snap']);
    }

    public processGestureFrame(leftHandLandmarks: HandLandmark[] | null, rightHandLandmarks: HandLandmark[] | null): void {
        const now = Date.now();

        // Detect individual hand gestures
        const leftGesture = leftHandLandmarks ? this.detectAdvancedGesture(leftHandLandmarks, 'left') : null;
        const rightGesture = rightHandLandmarks ? this.detectAdvancedGesture(rightHandLandmarks, 'right') : null;

        // Update gesture histories
        if (leftGesture && leftHandLandmarks) {
            this.leftHandHistory.push({ gesture: leftGesture, landmarks: leftHandLandmarks, time: now });
        }
        if (rightGesture && rightHandLandmarks) {
            this.rightHandHistory.push({ gesture: rightGesture, landmarks: rightHandLandmarks, time: now });
        }

        // Clean old history (keep last 3 seconds)
        this.cleanGestureHistory(now);

        // Detect combinations if both hands are active
        if (leftGesture && rightGesture && leftHandLandmarks && rightHandLandmarks) {
            this.detectGestureCombinations(leftGesture, rightGesture, leftHandLandmarks, rightHandLandmarks, now);
        }

        // Detect sequences
        this.detectGestureSequences(now);

        // Check for choreographed moves
        this.analyzeChoreography(now);

        // Pattern recognition
        this.analyzeGesturePatterns(now);
    }

    private detectAdvancedGesture(landmarks: HandLandmark[], hand: 'left' | 'right'): string {
        // Enhanced gesture detection with more complex shapes

        // Basic shape detection
        if (this.isGesture_Fist(landmarks)) return 'fist';
        if (this.isGesture_OpenPalm(landmarks)) return 'open_palm';
        if (this.isGesture_FingerSpread(landmarks)) return 'finger_spread';
        if (this.isGesture_Snap(landmarks)) return 'snap';
        if (this.isGesture_Clap(landmarks)) return 'clap_prep';

        // Advanced shape detection
        if (this.isGesture_Triangle(landmarks)) return 'triangle_shape';
        if (this.isGesture_Diamond(landmarks)) return 'diamond_shape';
        if (this.isGesture_Spiral(landmarks, hand)) return 'spiral_clockwise';
        if (this.isGesture_Wave(landmarks)) return 'wave_horizontal';
        if (this.isGesture_Point(landmarks)) return 'point_forward';

        return 'unknown';
    }

    private detectGestureCombinations(leftGesture: string, rightGesture: string,
                                     leftLandmarks: HandLandmark[], rightLandmarks: HandLandmark[],
                                     timestamp: number): void {

        // Calculate inter-hand distance and synchronization
        const distance = this.calculateHandDistance(leftLandmarks, rightLandmarks);
        const synchronization = this.calculateGestureSynchronization(leftGesture, rightGesture, timestamp);
        const intensity = this.calculateGestureIntensity(leftLandmarks, rightLandmarks);

        // Define combination rules
        const combinations = [
            {
                name: 'dual_spiral',
                condition: (l: string, r: string) => l === 'spiral_clockwise' && r === 'spiral_counter',
                minSync: 0.7,
                visualEffect: 'ring_morph_spiral'
            },
            {
                name: 'synchronized_clap',
                condition: (l: string, r: string) => l === 'clap_prep' && r === 'clap_prep',
                minSync: 0.8,
                visualEffect: 'effects_burst'
            },
            {
                name: 'geometry_formation',
                condition: (l: string, r: string) => l === 'triangle_shape' && r === 'triangle_shape',
                minSync: 0.6,
                visualEffect: 'geometric_pattern'
            },
            {
                name: 'energy_focus',
                condition: (l: string, r: string) => l === 'point_forward' && r === 'point_forward',
                minSync: 0.5,
                visualEffect: 'focused_beam'
            }
        ];

        // Check for matching combinations
        for (const combo of combinations) {
            if (combo.condition(leftGesture, rightGesture) && synchronization >= combo.minSync) {
                const combination: GestureCombination = {
                    name: combo.name,
                    leftHand: leftGesture,
                    rightHand: rightGesture,
                    distance,
                    synchronization,
                    intensity,
                    confidence: Math.min(synchronization + 0.1, 1.0)
                };

                this.combinationHistory.push(combination);
                this.callbacks.onGestureCombination(combination);

                console.log(`🙌 GESTURE COMBO: ${combo.name} (sync: ${(synchronization * 100).toFixed(0)}%, intensity: ${(intensity * 100).toFixed(0)}%)`);
            }
        }
    }

    private detectGestureSequences(timestamp: number): void {
        // Analyze recent gesture history for sequence patterns
        const recentGestures = this.getRecentGestureSequence(timestamp, 2000); // Last 2 seconds

        if (recentGestures.length >= 3) {
            const gestureNames = recentGestures.map(g => g.gesture);

            // Check against known patterns
            for (const [patternName, pattern] of this.gesturePatterns.entries()) {
                if (this.matchesPattern(gestureNames, pattern)) {
                    const sequence: GestureSequence = {
                        name: patternName,
                        gestures: gestureNames,
                        timing: recentGestures.map((g, i) => i > 0 ? g.time - recentGestures[i-1].time : 0),
                        totalDuration: recentGestures[recentGestures.length - 1].time - recentGestures[0].time,
                        repeatCount: 1
                    };

                    this.sequenceHistory.push(sequence);
                    this.callbacks.onGestureSequence(sequence);

                    console.log(`🎭 GESTURE SEQUENCE: ${patternName} (${gestureNames.join(' → ')})`);
                }
            }
        }
    }

    private analyzeChoreography(timestamp: number): void {
        // Check if current combinations and sequences match choreographed moves
        for (const [moveName, move] of this.choreographedMoves.entries()) {
            let choreographyScore = 0;

            // Check combination matches
            for (const targetCombo of move.combinations) {
                const recentCombos = this.combinationHistory.slice(-5);
                for (const combo of recentCombos) {
                    if (combo.name === targetCombo.name && combo.confidence >= 0.7) {
                        choreographyScore += 0.5;
                    }
                }
            }

            // Check sequence matches
            for (const targetSequence of move.sequences) {
                const recentSequences = this.sequenceHistory.slice(-3);
                for (const sequence of recentSequences) {
                    if (sequence.name === targetSequence.name) {
                        choreographyScore += 0.5;
                    }
                }
            }

            // Trigger choreography if score is high enough
            if (choreographyScore >= 0.8) {
                this.activeChoreography = moveName;
                this.choreographyStartTime = timestamp;

                this.callbacks.onChoreographyTrigger(moveName, choreographyScore);

                console.log(`🎪 CHOREOGRAPHY TRIGGERED: ${move.name} (score: ${choreographyScore.toFixed(2)})`);
            }
        }
    }

    // Gesture detection helper methods
    private isGesture_Fist(landmarks: HandLandmark[]): boolean {
        const fingertips = [8, 12, 16, 20]; // Index, middle, ring, pinky tips
        const knuckles = [6, 10, 14, 18]; // Corresponding knuckles

        let foldedFingers = 0;
        for (let i = 0; i < fingertips.length; i++) {
            const tip = landmarks[fingertips[i]];
            const knuckle = landmarks[knuckles[i]];
            if (tip && knuckle && tip.y > knuckle.y) { // Tip below knuckle = folded
                foldedFingers++;
            }
        }

        return foldedFingers >= 3; // At least 3 fingers folded
    }

    private isGesture_OpenPalm(landmarks: HandLandmark[]): boolean {
        const fingertips = [8, 12, 16, 20];
        const knuckles = [6, 10, 14, 18];

        let extendedFingers = 0;
        for (let i = 0; i < fingertips.length; i++) {
            const tip = landmarks[fingertips[i]];
            const knuckle = landmarks[knuckles[i]];
            if (tip && knuckle && tip.y < knuckle.y) { // Tip above knuckle = extended
                extendedFingers++;
            }
        }

        return extendedFingers >= 3; // At least 3 fingers extended
    }

    private isGesture_FingerSpread(landmarks: HandLandmark[]): boolean {
        const fingertips = [4, 8, 12, 16, 20]; // All fingertips including thumb
        let totalSpread = 0;
        let pairCount = 0;

        for (let i = 0; i < fingertips.length; i++) {
            for (let j = i + 1; j < fingertips.length; j++) {
                const tip1 = landmarks[fingertips[i]];
                const tip2 = landmarks[fingertips[j]];
                if (tip1 && tip2) {
                    const distance = Math.sqrt((tip1.x - tip2.x) ** 2 + (tip1.y - tip2.y) ** 2);
                    totalSpread += distance;
                    pairCount++;
                }
            }
        }

        const averageSpread = pairCount > 0 ? totalSpread / pairCount : 0;
        return averageSpread > 0.15; // Spread threshold
    }

    private isGesture_Triangle(landmarks: HandLandmark[]): boolean {
        const thumb = landmarks[4];
        const index = landmarks[8];
        const middle = landmarks[12];

        if (!thumb || !index || !middle) return false;

        // Calculate triangle area to detect triangular shape
        const area = Math.abs(
            (thumb.x * (index.y - middle.y) +
             index.x * (middle.y - thumb.y) +
             middle.x * (thumb.y - index.y)) / 2
        );

        return area > 0.01 && area < 0.05; // Triangle size range
    }

    private isGesture_Spiral(landmarks: HandLandmark[], hand: 'left' | 'right'): boolean {
        // Detect spiral motion by analyzing fingertip trajectory
        const indexTip = landmarks[8];
        if (!indexTip) return false;

        // This would need motion history to detect spiral patterns
        // For now, detect pointing gesture with hand orientation
        const wrist = landmarks[0];
        const middleMcp = landmarks[9];

        if (!wrist || !middleMcp) return false;

        const handAngle = Math.atan2(middleMcp.y - wrist.y, middleMcp.x - wrist.x);

        // Detect if hand is in spiral-friendly orientation
        return Math.abs(handAngle) > Math.PI / 6; // 30 degrees from horizontal
    }

    private isGesture_Snap(landmarks: HandLandmark[]): boolean {
        const thumb = landmarks[4];
        const middle = landmarks[12];

        if (!thumb || !middle) return false;

        const distance = Math.sqrt((thumb.x - middle.x) ** 2 + (thumb.y - middle.y) ** 2);
        return distance < 0.05; // Very close proximity for snap
    }

    private isGesture_Clap(landmarks: HandLandmark[]): boolean {
        // Detect hand in clapping position (palm facing inward)
        const wrist = landmarks[0];
        const middleMcp = landmarks[9];
        const indexMcp = landmarks[5];

        if (!wrist || !middleMcp || !indexMcp) return false;

        // Check if palm is relatively vertical (clap prep position)
        const palmAngle = Math.atan2(middleMcp.y - wrist.y, middleMcp.x - wrist.x);
        return Math.abs(palmAngle) > Math.PI / 3; // More than 60 degrees from horizontal
    }

    private isGesture_Diamond(landmarks: HandLandmark[]): boolean {
        const thumb = landmarks[4];
        const index = landmarks[8];
        const middle = landmarks[12];
        const ring = landmarks[16];

        if (!thumb || !index || !middle || !ring) return false;

        // Check if fingertips form diamond-like shape
        const centerX = (thumb.x + index.x + middle.x + ring.x) / 4;
        const centerY = (thumb.y + index.y + middle.y + ring.y) / 4;

        // Calculate variance from center (diamond should have balanced distribution)
        const variance = [thumb, index, middle, ring].reduce((sum, point) => {
            return sum + Math.sqrt((point.x - centerX) ** 2 + (point.y - centerY) ** 2);
        }, 0) / 4;

        return variance > 0.08 && variance < 0.15; // Diamond size range
    }

    private isGesture_Wave(landmarks: HandLandmark[]): boolean {
        // Detect horizontal waving motion
        const fingertips = [8, 12, 16, 20];
        const wrist = landmarks[0];

        if (!wrist) return false;

        // Check if fingers are extended horizontally
        let horizontalFingers = 0;
        for (const tip of fingertips) {
            const point = landmarks[tip];
            if (point && Math.abs(point.y - wrist.y) < 0.05) { // Fingers roughly level with wrist
                horizontalFingers++;
            }
        }

        return horizontalFingers >= 2; // At least 2 fingers extended horizontally
    }

    private isGesture_Point(landmarks: HandLandmark[]): boolean {
        const indexTip = landmarks[8];
        const indexMcp = landmarks[5];
        const middleTip = landmarks[12];
        const ringTip = landmarks[16];

        if (!indexTip || !indexMcp || !middleTip || !ringTip) return false;

        // Index finger extended, others folded
        const indexExtended = indexTip.y < indexMcp.y;
        const middleFolded = middleTip.y > landmarks[10]?.y;
        const ringFolded = ringTip.y > landmarks[14]?.y;

        return indexExtended && middleFolded && ringFolded;
    }

    // Utility methods
    private calculateHandDistance(leftLandmarks: HandLandmark[], rightLandmarks: HandLandmark[]): number {
        const leftPalm = leftLandmarks[9];
        const rightPalm = rightLandmarks[9];

        if (!leftPalm || !rightPalm) return 1.0;

        return Math.sqrt((leftPalm.x - rightPalm.x) ** 2 + (leftPalm.y - rightPalm.y) ** 2);
    }

    private calculateGestureSynchronization(leftGesture: string, rightGesture: string, timestamp: number): number {
        // Calculate how synchronized the gestures are based on timing and similarity
        const recentLeft = this.leftHandHistory.slice(-5);
        const recentRight = this.rightHandHistory.slice(-5);

        let syncScore = 0;
        const timeWindow = 200; // 200ms synchronization window

        for (const leftEntry of recentLeft) {
            for (const rightEntry of recentRight) {
                const timeDiff = Math.abs(leftEntry.time - rightEntry.time);
                if (timeDiff <= timeWindow) {
                    syncScore += 1 - (timeDiff / timeWindow);
                }
            }
        }

        return Math.min(syncScore / Math.max(recentLeft.length, recentRight.length), 1.0);
    }

    private calculateGestureIntensity(leftLandmarks: HandLandmark[], rightLandmarks: HandLandmark[]): number {
        // Calculate overall gesture intensity based on hand openness and motion
        const leftSpread = this.calculateFingerSpread(leftLandmarks);
        const rightSpread = this.calculateFingerSpread(rightLandmarks);

        return Math.min((leftSpread + rightSpread) / 0.3, 1.0); // Normalize to 0-1
    }

    private calculateFingerSpread(landmarks: HandLandmark[]): number {
        const fingertips = [4, 8, 12, 16, 20];
        let totalSpread = 0;
        let pairCount = 0;

        for (let i = 0; i < fingertips.length; i++) {
            for (let j = i + 1; j < fingertips.length; j++) {
                const tip1 = landmarks[fingertips[i]];
                const tip2 = landmarks[fingertips[j]];
                if (tip1 && tip2) {
                    const distance = Math.sqrt((tip1.x - tip2.x) ** 2 + (tip1.y - tip2.y) ** 2);
                    totalSpread += distance;
                    pairCount++;
                }
            }
        }

        return pairCount > 0 ? totalSpread / pairCount : 0;
    }

    private cleanGestureHistory(currentTime: number): void {
        const maxAge = 3000; // 3 seconds

        this.leftHandHistory = this.leftHandHistory.filter(entry => currentTime - entry.time < maxAge);
        this.rightHandHistory = this.rightHandHistory.filter(entry => currentTime - entry.time < maxAge);
        this.combinationHistory = this.combinationHistory.filter(combo => currentTime - combo.confidence < maxAge);
        this.sequenceHistory = this.sequenceHistory.filter(seq => currentTime - seq.totalDuration < maxAge);
    }

    private getRecentGestureSequence(timestamp: number, windowMs: number): { gesture: string; time: number }[] {
        const cutoff = timestamp - windowMs;
        const leftRecent = this.leftHandHistory.filter(h => h.time >= cutoff).map(h => ({ gesture: h.gesture, time: h.time }));
        const rightRecent = this.rightHandHistory.filter(h => h.time >= cutoff).map(h => ({ gesture: h.gesture, time: h.time }));

        return [...leftRecent, ...rightRecent].sort((a, b) => a.time - b.time);
    }

    private matchesPattern(gestures: string[], pattern: string[]): boolean {
        if (gestures.length < pattern.length) return false;

        // Check if the last N gestures match the pattern
        const recentGestures = gestures.slice(-pattern.length);
        return pattern.every((patternGesture, i) => recentGestures[i] === patternGesture);
    }

    private analyzeGesturePatterns(timestamp: number): void {
        // Advanced pattern analysis for complex choreography detection
        const recentSequence = this.getRecentGestureSequence(timestamp, 3000);

        if (recentSequence.length >= 5) {
            // Look for complex patterns like crescendos, diminuendos, etc.
            this.detectGestureCrescendo(recentSequence);
            this.detectGestureRhythm(recentSequence);
            this.detectGestureSymmetry(recentSequence);
        }
    }

    private detectGestureCrescendo(sequence: { gesture: string; time: number }[]): void {
        // Detect increasing intensity patterns
        const intensityMap: { [key: string]: number } = {
            'fist': 0.2,
            'open_palm': 0.4,
            'finger_spread': 0.6,
            'clap_prep': 0.8,
            'snap': 1.0
        };

        let isIncreasing = true;
        for (let i = 1; i < sequence.length; i++) {
            const prev = intensityMap[sequence[i-1].gesture] || 0.5;
            const curr = intensityMap[sequence[i].gesture] || 0.5;
            if (curr <= prev) {
                isIncreasing = false;
                break;
            }
        }

        if (isIncreasing && sequence.length >= 4) {
            console.log('🎵 GESTURE CRESCENDO detected!');
            this.callbacks.onChoreographyTrigger('crescendo', 0.8);
        }
    }

    private detectGestureRhythm(sequence: { gesture: string; time: number }[]): void {
        // Detect rhythmic patterns in gesture timing
        if (sequence.length < 4) return;

        const intervals = [];
        for (let i = 1; i < sequence.length; i++) {
            intervals.push(sequence[i].time - sequence[i-1].time);
        }

        // Check for steady rhythm (similar intervals)
        const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
        const variance = intervals.reduce((sum, interval) => sum + Math.pow(interval - avgInterval, 2), 0) / intervals.length;

        if (variance < avgInterval * 0.2) { // Low variance = steady rhythm
            console.log('🥁 GESTURE RHYTHM detected!');
            this.callbacks.onChoreographyTrigger('rhythmic', 0.7);
        }
    }

    private detectGestureSymmetry(sequence: { gesture: string; time: number }[]): void {
        // Detect symmetrical gesture patterns
        if (sequence.length < 6 || sequence.length % 2 !== 0) return;

        const mid = sequence.length / 2;
        const firstHalf = sequence.slice(0, mid).map(s => s.gesture);
        const secondHalf = sequence.slice(mid).map(s => s.gesture).reverse();

        const matches = firstHalf.filter((gesture, i) => gesture === secondHalf[i]).length;
        const symmetryScore = matches / firstHalf.length;

        if (symmetryScore >= 0.8) {
            console.log('🪞 GESTURE SYMMETRY detected!');
            this.callbacks.onChoreographyTrigger('symmetry', symmetryScore);
        }
    }

    // Recording and playback methods
    // ═══ RECORDING SYSTEM ═══

    public startRecording(name?: string, performer?: string, tags?: string[]): string {
        if (this.isRecording) {
            console.warn('🔴 Recording already in progress');
            return this.currentRecording?.id || '';
        }

        const recordingId = `recording_${Date.now()}`;
        this.currentRecording = {
            id: recordingId,
            name: name || `Gesture Recording ${new Date().toLocaleTimeString()}`,
            timestamp: Date.now(),
            duration: 0,
            frames: [],
            metadata: {
                performer: performer || 'Unknown',
                tempo: 120, // Will be calculated
                complexity: 0, // Will be calculated
                tags: tags || []
            }
        };

        this.isRecording = true;
        this.recordingStartTime = Date.now();
        this.combinationHistory = [];
        this.sequenceHistory = [];

        console.log(`🔴 GESTURE RECORDING STARTED: ${this.currentRecording.name} (${recordingId})`);
        return recordingId;
    }

    public stopRecording(): GestureRecording | null {
        if (!this.isRecording || !this.currentRecording) {
            console.warn('⏹️ No recording in progress');
            return null;
        }

        this.isRecording = false;
        const recordingDuration = Date.now() - this.recordingStartTime;

        // Finalize recording
        this.currentRecording.duration = recordingDuration;
        this.currentRecording.metadata.tempo = this.calculateTempo();
        this.currentRecording.metadata.complexity = this.calculateComplexity();

        // Store recording
        this.recordedGestures.set(this.currentRecording.id, this.currentRecording);

        console.log(`⏹️ GESTURE RECORDING STOPPED: ${this.currentRecording.name} (${recordingDuration}ms)`);
        console.log(`   📊 Frames: ${this.currentRecording.frames.length}, Tempo: ${this.currentRecording.metadata.tempo} BPM`);

        const finalRecording = this.currentRecording;
        this.currentRecording = null;
        return finalRecording;
    }

    public addFrameToRecording(leftHand?: HandLandmark[], rightHand?: HandLandmark[], detectedGestures: string[] = []): void {
        if (!this.isRecording || !this.currentRecording) return;

        const currentTime = Date.now() - this.recordingStartTime;
        const intensity = this.calculateFrameIntensity(leftHand, rightHand);
        const confidence = this.calculateFrameConfidence(detectedGestures);

        const frame: GestureFrame = {
            time: currentTime,
            leftHand: leftHand ? [...leftHand] : undefined,
            rightHand: rightHand ? [...rightHand] : undefined,
            detectedGestures: [...detectedGestures],
            intensity,
            confidence
        };

        this.currentRecording.frames.push(frame);
    }

    private calculateFrameIntensity(leftHand?: HandLandmark[], rightHand?: HandLandmark[]): number {
        let totalMovement = 0;
        let handCount = 0;

        if (leftHand && this.leftHandHistory.length > 0) {
            const lastLeft = this.leftHandHistory[this.leftHandHistory.length - 1];
            totalMovement += this.calculateHandMovement(leftHand, lastLeft.landmarks);
            handCount++;
        }

        if (rightHand && this.rightHandHistory.length > 0) {
            const lastRight = this.rightHandHistory[this.rightHandHistory.length - 1];
            totalMovement += this.calculateHandMovement(rightHand, lastRight.landmarks);
            handCount++;
        }

        return handCount > 0 ? Math.min(1.0, totalMovement / handCount * 10) : 0;
    }

    private calculateHandMovement(current: HandLandmark[], previous: HandLandmark[]): number {
        if (current.length !== previous.length) return 0;

        let totalDistance = 0;
        for (let i = 0; i < current.length; i++) {
            const dx = current[i].x - previous[i].x;
            const dy = current[i].y - previous[i].y;
            const dz = current[i].z - previous[i].z;
            totalDistance += Math.sqrt(dx * dx + dy * dy + dz * dz);
        }

        return totalDistance / current.length;
    }

    private calculateFrameConfidence(detectedGestures: string[]): number {
        return Math.min(1.0, detectedGestures.length * 0.3);
    }

    private calculateTempo(): number {
        if (!this.currentRecording || this.currentRecording.frames.length < 10) return 120;

        const gestureChanges = [];
        let lastGestures = new Set<string>();

        for (const frame of this.currentRecording.frames) {
            const currentGestures = new Set(frame.detectedGestures);
            if (!this.setsEqual(currentGestures, lastGestures)) {
                gestureChanges.push(frame.time);
            }
            lastGestures = currentGestures;
        }

        if (gestureChanges.length < 2) return 120;

        const averageInterval = (gestureChanges[gestureChanges.length - 1] - gestureChanges[0]) / (gestureChanges.length - 1);
        const beatsPerMinute = (60000 / averageInterval) * 2;

        return Math.max(60, Math.min(200, Math.round(beatsPerMinute)));
    }

    private calculateComplexity(): number {
        if (!this.currentRecording) return 0;

        const uniqueGestures = new Set<string>();
        let maxSimultaneousGestures = 0;
        let totalIntensity = 0;

        for (const frame of this.currentRecording.frames) {
            frame.detectedGestures.forEach(g => uniqueGestures.add(g));
            maxSimultaneousGestures = Math.max(maxSimultaneousGestures, frame.detectedGestures.length);
            totalIntensity += frame.intensity;
        }

        const averageIntensity = totalIntensity / this.currentRecording.frames.length;
        const complexityScore = (uniqueGestures.size * 0.1) + (maxSimultaneousGestures * 0.2) + (averageIntensity * 0.7);

        return Math.min(1.0, complexityScore);
    }

    private setsEqual<T>(a: Set<T>, b: Set<T>): boolean {
        return a.size === b.size && [...a].every(x => b.has(x));
    }

    // ═══ PLAYBACK SYSTEM ═══

    public startPlayback(recordingId: string, speed: number = 1.0, loop: boolean = false): boolean {
        const recording = this.recordedGestures.get(recordingId);
        if (!recording) {
            console.warn(`❌ Recording not found: ${recordingId}`);
            return false;
        }

        if (this.isPlaying) {
            console.warn('▶️ Playback already in progress');
            return false;
        }

        this.playbackRecording = recording;
        this.playbackStartTime = Date.now();
        this.playbackSpeed = speed;
        this.isPlaying = true;

        console.log(`▶️ PLAYBACK STARTED: ${recording.name} (${speed}x speed)`);
        this.schedulePlaybackFrames(loop);

        return true;
    }

    public stopPlayback(): void {
        if (!this.isPlaying) return;

        this.isPlaying = false;
        this.playbackRecording = null;
        console.log('⏹️ PLAYBACK STOPPED');
    }

    private schedulePlaybackFrames(loop: boolean): void {
        if (!this.playbackRecording || !this.isPlaying) return;

        const frames = this.playbackRecording.frames;
        let frameIndex = 0;

        const playFrame = () => {
            if (!this.isPlaying || frameIndex >= frames.length) {
                if (loop && this.isPlaying) {
                    frameIndex = 0;
                    this.playbackStartTime = Date.now();
                } else {
                    this.stopPlayback();
                    return;
                }
            }

            const frame = frames[frameIndex];
            const scheduledTime = frame.time / this.playbackSpeed;
            const actualDelay = Math.max(0, scheduledTime - (Date.now() - this.playbackStartTime));

            setTimeout(() => {
                if (this.isPlaying) {
                    this.executePlaybackFrame(frame);
                    frameIndex++;
                    playFrame();
                }
            }, actualDelay);
        };

        playFrame();
    }

    private executePlaybackFrame(frame: GestureFrame): void {
        for (const gestureName of frame.detectedGestures) {
            console.log(`🎭 PLAYBACK GESTURE: ${gestureName} (intensity: ${frame.intensity.toFixed(2)})`);
            this.callbacks.onChoreographyTrigger(gestureName, frame.intensity);
        }
    }

    // ═══ RECORDING MANAGEMENT ═══

    public getRecording(id: string): GestureRecording | undefined {
        return this.recordedGestures.get(id);
    }

    public getAllRecordings(): Map<string, GestureRecording> {
        return new Map(this.recordedGestures);
    }

    public deleteRecording(id: string): boolean {
        const success = this.recordedGestures.delete(id);
        if (success) {
            console.log(`🗑️ Recording deleted: ${id}`);
        }
        return success;
    }

    public exportRecording(id: string): string | null {
        const recording = this.recordedGestures.get(id);
        if (!recording) return null;

        try {
            return JSON.stringify(recording, null, 2);
        } catch (error) {
            console.error('❌ Export failed:', error);
            return null;
        }
    }

    public importRecording(jsonData: string): string | null {
        try {
            const recording: GestureRecording = JSON.parse(jsonData);

            if (!recording.id || !recording.name || !recording.frames) {
                throw new Error('Invalid recording format');
            }

            this.recordedGestures.set(recording.id, recording);
            console.log(`📥 Recording imported: ${recording.name} (${recording.id})`);
            return recording.id;
        } catch (error) {
            console.error('❌ Import failed:', error);
            return null;
        }
    }

    public getRecordingStatus(): {
        isRecording: boolean,
        isPlaying: boolean,
        currentRecording?: string,
        playbackRecording?: string,
        recordingDuration?: number
    } {
        return {
            isRecording: this.isRecording,
            isPlaying: this.isPlaying,
            currentRecording: this.currentRecording?.name,
            playbackRecording: this.playbackRecording?.name,
            recordingDuration: this.isRecording && this.currentRecording ?
                Date.now() - this.recordingStartTime : undefined
        };
    }

    public getChoreographyLibrary(): Map<string, ChoreographedMove> {
        return this.choreographedMoves;
    }

    public addCustomChoreography(name: string, move: ChoreographedMove): void {
        this.choreographedMoves.set(name, move);
        console.log(`✅ CUSTOM CHOREOGRAPHY ADDED: ${name}`);
    }
}