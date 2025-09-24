/**
 * 🎩👑 The Mad Hatter's Morph Solution - Integration Example
 *
 * "In the haze of our haberdashery, we found the White Queen's Crown!"
 * This demonstrates how Catmull-Clark subdivision solves the morphing mystery
 */

import * as THREE from 'three';
import { SubdivisionMorph } from './SubdivisionMorph';
import { WizardGestureController } from '../input/WizardGestureController';

export class MorphIntegrationExample {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private subdivisionMorph: SubdivisionMorph;
    private gestureController: WizardGestureController;

    // Unicode visual feedback (inspired by batgrl)
    private readonly symbols = {
        crown: '👑',     // The White Queen's Crown
        hat: '🎩',       // Mad Hatter's hat
        rabbit: '🐰',    // Down the rabbit hole
        tea: '☕',       // Tea party
        morph: '◐◑◒◓',  // Morphing phases
        cube: '■',       // Starting form
        sphere: '●'      // Final form
    };

    constructor(container: HTMLElement) {
        this.initializeThreeJS(container);
        this.initializeSubdivisionMorph();
        this.initializeGestureControl();
        this.startAnimation();
        this.demonstrateMorphSolution();
    }

    private initializeThreeJS(container: HTMLElement): void {
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.z = 5;

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(this.renderer.domElement);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);

        console.log(`${this.symbols.hat} Mad Hatter's Workshop initialized!`);
    }

    private initializeSubdivisionMorph(): void {
        // Create the subdivision morph engine
        this.subdivisionMorph = new SubdivisionMorph(this.scene, 6);

        console.log(`${this.symbols.crown} White Queen's Crown activated!`);
        console.log(`${this.symbols.cube} Starting with 6-faced cube`);
        console.log(`${this.symbols.sphere} Target: Perfect sphere through subdivision`);
    }

    private initializeGestureControl(): void {
        // Mock gesture controller setup (replace with actual implementation)
        this.gestureController = {
            getHandPosition: () => ({ x: 0, y: 0, z: 0 }),
            getProximity: () => Math.sin(Date.now() * 0.001) * 0.5 + 0.5, // Demo oscillation
            isActive: () => true
        } as any;

        console.log(`${this.symbols.rabbit} Gesture control down the rabbit hole!`);
    }

    private startAnimation(): void {
        const animate = () => {
            requestAnimationFrame(animate);

            // Get gesture proximity (0-1)
            const proximity = this.gestureController.getProximity();

            // Control subdivision morph with proximity
            this.subdivisionMorph.controlWithThereminField(proximity);

            // Get morph info for visual feedback
            const morphInfo = this.subdivisionMorph.getMorphInfo();

            // Update visual feedback
            this.updateConsoleOutput(morphInfo, proximity);

            // Render
            this.renderer.render(this.scene, this.camera);
        };

        animate();
    }

    private updateConsoleOutput(morphInfo: any, proximity: number): void {
        // Clear console periodically for live updates
        if (Math.random() < 0.02) { // ~2% chance per frame
            console.clear();
            console.log(`${this.symbols.crown} White Queen's Crown - Live Morph Status`);
            console.log('═'.repeat(50));
            console.log(`${morphInfo.symbol} Level: ${morphInfo.level.toFixed(2)}`);
            console.log(`${this.symbols.tea} Faces: ${morphInfo.faceCount.toLocaleString()}`);
            console.log(`${this.symbols.rabbit} Proximity: ${(proximity * 100).toFixed(1)}%`);
            console.log(`${this.symbols.hat} Sphere Progress: ${(morphInfo.sphereProgress * 100).toFixed(1)}%`);

            // Visual progress bar using Unicode
            const progressChars = '░▒▓█';
            const progressBar = Array(20).fill(0).map((_, i) => {
                const threshold = i / 20;
                if (morphInfo.sphereProgress > threshold + 0.05) return progressChars[3];
                if (morphInfo.sphereProgress > threshold) return progressChars[2];
                if (morphInfo.sphereProgress > threshold - 0.05) return progressChars[1];
                return progressChars[0];
            }).join('');

            console.log(`Progress: [${progressBar}]`);
        }
    }

    /**
     * 🎪 Demonstrate the complete solution to morphing issues
     */
    private async demonstrateMorphSolution(): Promise<void> {
        console.log('\n' + '🎭'.repeat(25));
        console.log(`${this.symbols.hat} MAD HATTER'S MORPH SOLUTION DEMONSTRATION`);
        console.log('🎭'.repeat(25));

        await this.sleep(2000);

        console.log(`\n${this.symbols.cube} PROBLEM SOLVED:`);
        console.log('❌ Old approach: Jarring transitions between cube and sphere');
        console.log('❌ Vertex count mismatches causing visual glitches');
        console.log('❌ No smooth progression between forms');

        await this.sleep(3000);

        console.log(`\n${this.symbols.crown} CATMULL-CLARK SOLUTION:`);
        console.log('✅ Recursive subdivision: 6 → 24 → 96 → 384 → 1,536 → 6,144 faces');
        console.log('✅ Smooth geometric progression preserving topology');
        console.log('✅ Perfect interpolation between subdivision levels');
        console.log('✅ Theremin field controls subdivision depth naturally');

        await this.sleep(4000);

        console.log(`\n${this.symbols.rabbit} DEMONSTRATION SEQUENCE:`);

        // Level 0: Pure cube
        await this.subdivisionMorph.animateToLevel(0, 1500);
        console.log(`${this.symbols.cube} Level 0: Pure cube (6 faces)`);
        await this.sleep(2000);

        // Level 2: Early subdivision
        await this.subdivisionMorph.animateToLevel(2, 1500);
        console.log(`${this.symbols.morph} Level 2: Early morph (96 faces)`);
        await this.sleep(2000);

        // Level 4: Mid subdivision
        await this.subdivisionMorph.animateToLevel(4, 1500);
        console.log(`${this.symbols.morph} Level 4: Advanced morph (1,536 faces)`);
        await this.sleep(2000);

        // Level 6: Near sphere
        await this.subdivisionMorph.animateToLevel(6, 1500);
        console.log(`${this.symbols.sphere} Level 6: Near-perfect sphere (24,576 faces)`);
        await this.sleep(2000);

        console.log(`\n${this.symbols.tea} TEA PARTY CONCLUSION:`);
        console.log(`${this.symbols.crown} The White Queen's Crown provides infinite subdivision!`);
        console.log(`${this.symbols.hat} Mad Hatter approves: "Smooth as butter, precise as clockwork!"`);
        console.log(`${this.symbols.rabbit} Down the rabbit hole: Each level reveals more detail`);

        // Start continuous theremin control
        console.log(`\n${this.symbols.tea} Entering continuous theremin control mode...`);
        console.log('👋 Move your hand closer/further to control subdivision!');
    }

    /**
     * 🎪 Utility for async demonstration
     */
    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 🎨 Get current morph visualization for external use
     */
    public getMorphVisualization() {
        const morphInfo = this.subdivisionMorph.getMorphInfo();
        const proximity = this.gestureController.getProximity();

        return {
            level: morphInfo.level,
            faceCount: morphInfo.faceCount,
            sphereProgress: morphInfo.sphereProgress,
            proximity,
            symbol: morphInfo.symbol,
            isAnimating: morphInfo.isAnimating
        };
    }

    /**
     * 🎭 Manual control for testing
     */
    public setSubdivisionLevel(level: number): void {
        this.subdivisionMorph.setMorphLevel(level);
    }

    /**
     * 🗑️ Cleanup
     */
    public dispose(): void {
        this.subdivisionMorph.dispose();
        this.renderer.dispose();
    }
}

/**
 * 🎪 Usage example for integration into main app
 */
export function integrateSubdivisionMorph(container: HTMLElement): MorphIntegrationExample {
    console.log(`${Array(3).fill('🎩').join('')} Welcome to the Mad Hatter's Morph Workshop!`);
    console.log('Solving the mysteries of smooth geometric transformation...');

    const integration = new MorphIntegrationExample(container);

    // Catalog this achievement
    console.log('\n📝 Achievement Unlocked: Morph Mystery Solved!');
    console.log('🏷️  Tags: subdivision-surfaces, catmull-clark, morphing, white-queens-crown');

    return integration;
}

// Export for main app integration
export { MorphIntegrationExample };