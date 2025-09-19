import * as THREE from 'three';

interface EasterEggConfig {
    duration: number;
    opacity: number;
    scale: number;
    position: THREE.Vector3;
    animation: 'fade' | 'spiral' | 'pulse' | 'fractal' | 'explode';
}

export class EasterEggRenderer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private activeEggs: Map<string, THREE.Object3D> = new Map();
    private textureLoader: THREE.TextureLoader;
    private fontLoader: any; // THREE.FontLoader
    private loadedFont: any = null;

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.textureLoader = new THREE.TextureLoader();

        // Initialize font loader for text easter eggs
        if (typeof window !== 'undefined') {
            import('three/examples/jsm/loaders/FontLoader.js').then(({ FontLoader }) => {
                this.fontLoader = new FontLoader();
                this.loadFont();
            });
        }

        this.initializeEasterEggSystems();
    }

    private async loadFont() {
        // Load a font for text rendering
        try {
            // Using a simple approach for now - in production would load actual font
            console.log('Font system initialized for easter eggs');
        } catch (error) {
            console.log('Font loading failed, using fallback');
        }
    }

    private initializeEasterEggSystems() {
        // Set up event listeners for easter egg triggers
        document.addEventListener('russell-easter-egg', () => this.triggerRussellEgg());
        document.addEventListener('blake-easter-egg', () => this.triggerBlakeEgg());
        document.addEventListener('tesla-easter-egg', () => this.triggerTeslaEgg());
        document.addEventListener('einstein-easter-egg', () => this.triggerEinsteinEgg());
        document.addEventListener('hawking-easter-egg', () => this.triggerHawkingEgg());
        document.addEventListener('beatles-easter-egg', () => this.triggerBeatlesEgg());
        document.addEventListener('leadbelly-easter-egg', () => this.triggerLeadBellyEgg());
        document.addEventListener('pranksters-easter-egg', () => this.triggerPrankstersEgg());
        document.addEventListener('hoffman-easter-egg', () => this.triggerHoffmanEgg());
        document.addEventListener('waas-easter-egg', () => this.triggerWaasEgg());
        document.addEventListener('greiff-easter-egg', () => this.triggerGreiffEgg());
    }

    private triggerRussellEgg() {
        // Walter Russell - Cube-sphere cosmology with sacred geometry
        this.createSacredGeometryEgg('russell', {
            duration: 5000,
            opacity: 0.8,
            scale: 2,
            position: new THREE.Vector3(0, 3, 0),
            animation: 'spiral'
        });
    }

    private triggerBlakeEgg() {
        // William Blake - Mystical mandala with "Tyger" pattern
        this.createMysticMandalaEgg('blake', {
            duration: 6000,
            opacity: 0.9,
            scale: 1.5,
            position: new THREE.Vector3(-2, 2, 1),
            animation: 'fractal'
        });
    }

    private triggerTeslaEgg() {
        // Nikola Tesla - Patent diagram visualization
        this.createPatentDiagramEgg('tesla', {
            duration: 4000,
            opacity: 0.7,
            scale: 1.8,
            position: new THREE.Vector3(2, 1, -1),
            animation: 'pulse'
        });
    }

    private triggerEinsteinEgg() {
        // Einstein - Relativity equations in curved space
        this.createEquationEgg('einstein', 'E=mc²', {
            duration: 7000,
            opacity: 0.6,
            scale: 1.2,
            position: new THREE.Vector3(0, -1, 2),
            animation: 'spiral'
        });
    }

    private triggerHawkingEgg() {
        // Stephen Hawking - Black hole with Hawking radiation
        this.createBlackHoleEgg('hawking', {
            duration: 8000,
            opacity: 0.9,
            scale: 2.5,
            position: new THREE.Vector3(-3, 0, 0),
            animation: 'spiral'
        });
    }

    private triggerBeatlesEgg() {
        // The Beatles - Psychedelic rainbow with "Here Comes the Sun"
        this.createPsychedelicEgg('beatles', {
            duration: 5000,
            opacity: 0.8,
            scale: 1.6,
            position: new THREE.Vector3(1, 3, 1),
            animation: 'pulse'
        });
    }

    private triggerLeadBellyEgg() {
        // Lead Belly - Guitar strings with blues notes
        this.createBluesStringEgg('leadbelly', {
            duration: 4000,
            opacity: 0.7,
            scale: 1.4,
            position: new THREE.Vector3(-1, -2, 0),
            animation: 'fade'
        });
    }

    private triggerPrankstersEgg() {
        // Merry Pranksters - Kaleidoscope explosion
        this.createKaleidoscopeEgg('pranksters', {
            duration: 3000,
            opacity: 1.0,
            scale: 2.0,
            position: new THREE.Vector3(3, 2, -2),
            animation: 'explode'
        });
    }

    private triggerHoffmanEgg() {
        // Abbie Hoffman - "REVOLUTION" text with protest imagery
        this.createRevolutionEgg('hoffman', {
            duration: 2000,
            opacity: 0.9,
            scale: 1.8,
            position: new THREE.Vector3(-2, -1, 1),
            animation: 'explode'
        });
    }

    private triggerWaasEgg() {
        // Les Waas - Absurd clock showing "Procrastination Time"
        this.createAbsurdClockEgg('waas', {
            duration: 4200, // 42 * 100ms for absurdity
            opacity: 0.6,
            scale: 1.0,
            position: new THREE.Vector3(0, 0, 3),
            animation: 'pulse'
        });
    }

    private triggerGreiffEgg() {
        // Constance Greiff - Architectural memorial structure
        this.createMemorialEgg('greiff', {
            duration: 6000,
            opacity: 0.5,
            scale: 1.3,
            position: new THREE.Vector3(2, -2, 2),
            animation: 'fade'
        });
    }

    private createSacredGeometryEgg(id: string, config: EasterEggConfig) {
        // Sacred geometry with platonic solids
        const group = new THREE.Group();

        // Create nested platonic solids
        const geometries = [
            new THREE.TetrahedronGeometry(0.5),
            new THREE.OctahedronGeometry(0.7),
            new THREE.IcosahedronGeometry(0.9)
        ];

        geometries.forEach((geometry, index) => {
            const material = new THREE.MeshPhongMaterial({
                color: new THREE.Color().setHSL(index * 0.2, 0.8, 0.6),
                transparent: true,
                opacity: config.opacity * (1 - index * 0.2),
                wireframe: true
            });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.rotation.set(
                Math.PI * index * 0.3,
                Math.PI * index * 0.4,
                Math.PI * index * 0.2
            );
            group.add(mesh);
        });

        this.addEasterEgg(id, group, config);
    }

    private createMysticMandalaEgg(id: string, config: EasterEggConfig) {
        // Mystical mandala pattern
        const group = new THREE.Group();

        // Create concentric circles with mystical patterns
        for (let ring = 0; ring < 5; ring++) {
            const radius = 0.3 + ring * 0.2;
            const segments = 8 + ring * 4;

            for (let i = 0; i < segments; i++) {
                const angle = (i / segments) * Math.PI * 2;
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius;

                const geometry = new THREE.SphereGeometry(0.02 + ring * 0.01);
                const material = new THREE.MeshPhongMaterial({
                    color: new THREE.Color().setHSL((ring + i) * 0.1, 0.9, 0.7),
                    transparent: true,
                    opacity: config.opacity
                });

                const sphere = new THREE.Mesh(geometry, material);
                sphere.position.set(x, y, Math.sin(angle * 3) * 0.1);
                group.add(sphere);
            }
        }

        this.addEasterEgg(id, group, config);
    }

    private createPatentDiagramEgg(id: string, config: EasterEggConfig) {
        // Tesla coil patent diagram simulation
        const group = new THREE.Group();

        // Create coil structure
        const curve = new THREE.QuadraticBezierCurve3(
            new THREE.Vector3(-1, -1, 0),
            new THREE.Vector3(0, 1, 0),
            new THREE.Vector3(1, -1, 0)
        );

        const tubeGeometry = new THREE.TubeGeometry(curve, 20, 0.02, 8, false);
        const coilMaterial = new THREE.MeshPhongMaterial({
            color: 0x4169e1,
            transparent: true,
            opacity: config.opacity,
            emissive: 0x001133
        });

        // Create multiple coil layers
        for (let i = 0; i < 8; i++) {
            const coil = new THREE.Mesh(tubeGeometry, coilMaterial);
            coil.rotation.y = (i / 8) * Math.PI * 2;
            coil.scale.setScalar(0.3 + i * 0.1);
            group.add(coil);
        }

        // Add electrical arc effects
        for (let i = 0; i < 5; i++) {
            const arcGeometry = new THREE.CylinderGeometry(0.005, 0.005, 2);
            const arcMaterial = new THREE.MeshBasicMaterial({
                color: 0x00ffff,
                transparent: true,
                opacity: config.opacity * 0.8
            });

            const arc = new THREE.Mesh(arcGeometry, arcMaterial);
            arc.position.set(
                (Math.random() - 0.5) * 2,
                (Math.random() - 0.5) * 2,
                (Math.random() - 0.5) * 2
            );
            arc.rotation.set(
                Math.random() * Math.PI,
                Math.random() * Math.PI,
                Math.random() * Math.PI
            );
            group.add(arc);
        }

        this.addEasterEgg(id, group, config);
    }

    private createEquationEgg(id: string, equation: string, config: EasterEggConfig) {
        // Create floating equation in curved spacetime
        const group = new THREE.Group();

        // Create text plane (simplified - would use actual font in production)
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d')!;
        canvas.width = 256;
        canvas.height = 128;

        context.fillStyle = 'rgba(255, 255, 255, 0.9)';
        context.font = '48px Arial';
        context.textAlign = 'center';
        context.fillText(equation, 128, 64);

        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            opacity: config.opacity
        });

        const geometry = new THREE.PlaneGeometry(2, 1);
        const textMesh = new THREE.Mesh(geometry, material);
        group.add(textMesh);

        // Add spacetime curvature effect
        const gridGeometry = new THREE.PlaneGeometry(4, 4, 20, 20);
        const gridMaterial = new THREE.MeshBasicMaterial({
            color: 0x444444,
            wireframe: true,
            transparent: true,
            opacity: config.opacity * 0.3
        });

        const grid = new THREE.Mesh(gridGeometry, gridMaterial);
        grid.position.z = -0.5;

        // Curve the grid to show spacetime warping
        const positions = grid.geometry.attributes.position;
        for (let i = 0; i < positions.count; i++) {
            const x = positions.getX(i);
            const y = positions.getY(i);
            const distance = Math.sqrt(x * x + y * y);
            const warp = Math.exp(-distance) * 0.3;
            positions.setZ(i, -warp);
        }
        positions.needsUpdate = true;

        group.add(grid);
        this.addEasterEgg(id, group, config);
    }

    private createBlackHoleEgg(id: string, config: EasterEggConfig) {
        // Black hole with accretion disk and Hawking radiation
        const group = new THREE.Group();

        // Event horizon
        const horizonGeometry = new THREE.SphereGeometry(0.3);
        const horizonMaterial = new THREE.MeshBasicMaterial({
            color: 0x000000,
            transparent: true,
            opacity: 0.9
        });
        const horizon = new THREE.Mesh(horizonGeometry, horizonMaterial);
        group.add(horizon);

        // Accretion disk
        const diskGeometry = new THREE.RingGeometry(0.4, 1.2, 32);
        const diskMaterial = new THREE.MeshBasicMaterial({
            color: 0xff6600,
            transparent: true,
            opacity: config.opacity * 0.7,
            side: THREE.DoubleSide
        });
        const disk = new THREE.Mesh(diskGeometry, diskMaterial);
        disk.rotation.x = Math.PI / 2;
        group.add(disk);

        // Hawking radiation particles
        const particleGeometry = new THREE.BufferGeometry();
        const particleCount = 100;
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount; i++) {
            const radius = 1.5 + Math.random() * 2;
            const angle = Math.random() * Math.PI * 2;
            const height = (Math.random() - 0.5) * 0.5;

            positions[i * 3] = Math.cos(angle) * radius;
            positions[i * 3 + 1] = height;
            positions[i * 3 + 2] = Math.sin(angle) * radius;
        }

        particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const particleMaterial = new THREE.PointsMaterial({
            color: 0x88ffff,
            size: 0.02,
            transparent: true,
            opacity: config.opacity
        });

        const particles = new THREE.Points(particleGeometry, particleMaterial);
        group.add(particles);

        this.addEasterEgg(id, group, config);
    }

    private createPsychedelicEgg(id: string, config: EasterEggConfig) {
        // Psychedelic rainbow spiral
        const group = new THREE.Group();

        // Create rainbow spiral
        for (let i = 0; i < 50; i++) {
            const angle = i * 0.3;
            const radius = i * 0.02;
            const height = Math.sin(i * 0.2) * 0.5;

            const geometry = new THREE.SphereGeometry(0.03);
            const material = new THREE.MeshPhongMaterial({
                color: new THREE.Color().setHSL(i * 0.02, 1.0, 0.6),
                transparent: true,
                opacity: config.opacity,
                emissive: new THREE.Color().setHSL(i * 0.02, 0.5, 0.2)
            });

            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(
                Math.cos(angle) * radius,
                height,
                Math.sin(angle) * radius
            );
            group.add(sphere);
        }

        this.addEasterEgg(id, group, config);
    }

    private createBluesStringEgg(id: string, config: EasterEggConfig) {
        // Guitar strings with musical notes
        const group = new THREE.Group();

        // Create 6 guitar strings
        for (let string = 0; string < 6; string++) {
            const stringGeometry = new THREE.CylinderGeometry(0.002, 0.002, 3);
            const stringMaterial = new THREE.MeshBasicMaterial({
                color: 0xc0c0c0,
                transparent: true,
                opacity: config.opacity
            });

            const stringMesh = new THREE.Mesh(stringGeometry, stringMaterial);
            stringMesh.position.x = (string - 2.5) * 0.1;
            stringMesh.rotation.z = Math.PI / 2;
            group.add(stringMesh);

            // Add vibration effect
            const noteGeometry = new THREE.SphereGeometry(0.02);
            const noteMaterial = new THREE.MeshPhongMaterial({
                color: new THREE.Color().setHSL(string * 0.1, 0.8, 0.6),
                transparent: true,
                opacity: config.opacity * 0.8
            });

            for (let note = 0; note < 3; note++) {
                const noteMesh = new THREE.Mesh(noteGeometry, noteMaterial);
                noteMesh.position.set(
                    (string - 2.5) * 0.1,
                    (note - 1) * 0.3,
                    Math.sin(note + string) * 0.1
                );
                group.add(noteMesh);
            }
        }

        this.addEasterEgg(id, group, config);
    }

    private createKaleidoscopeEgg(id: string, config: EasterEggConfig) {
        // Chaotic kaleidoscope explosion
        const group = new THREE.Group();

        // Create random colorful fragments
        for (let i = 0; i < 30; i++) {
            const geometries = [
                new THREE.BoxGeometry(0.1, 0.1, 0.1),
                new THREE.TetrahedronGeometry(0.1),
                new THREE.OctahedronGeometry(0.1)
            ];

            const geometry = geometries[Math.floor(Math.random() * geometries.length)];
            const material = new THREE.MeshPhongMaterial({
                color: new THREE.Color().setHSL(Math.random(), 1.0, 0.6),
                transparent: true,
                opacity: config.opacity
            });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(
                (Math.random() - 0.5) * 2,
                (Math.random() - 0.5) * 2,
                (Math.random() - 0.5) * 2
            );
            mesh.rotation.set(
                Math.random() * Math.PI * 2,
                Math.random() * Math.PI * 2,
                Math.random() * Math.PI * 2
            );
            group.add(mesh);
        }

        this.addEasterEgg(id, group, config);
    }

    private createRevolutionEgg(id: string, config: EasterEggConfig) {
        // "REVOLUTION" text with protest imagery
        const group = new THREE.Group();

        // Create text (simplified approach)
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d')!;
        canvas.width = 512;
        canvas.height = 128;

        context.fillStyle = 'red';
        context.font = 'bold 36px Arial';
        context.textAlign = 'center';
        context.fillText('REVOLUTION!', 256, 64);

        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            opacity: config.opacity
        });

        const geometry = new THREE.PlaneGeometry(3, 0.75);
        const textMesh = new THREE.Mesh(geometry, material);
        group.add(textMesh);

        // Add explosive particles
        for (let i = 0; i < 20; i++) {
            const particleGeometry = new THREE.SphereGeometry(0.02);
            const particleMaterial = new THREE.MeshBasicMaterial({
                color: Math.random() > 0.5 ? 0xff0000 : 0x000000,
                transparent: true,
                opacity: config.opacity
            });

            const particle = new THREE.Mesh(particleGeometry, particleMaterial);
            particle.position.set(
                (Math.random() - 0.5) * 4,
                (Math.random() - 0.5) * 2,
                (Math.random() - 0.5) * 1
            );
            group.add(particle);
        }

        this.addEasterEgg(id, group, config);
    }

    private createAbsurdClockEgg(id: string, config: EasterEggConfig) {
        // Absurd clock with impossible time
        const group = new THREE.Group();

        // Clock face
        const faceGeometry = new THREE.CylinderGeometry(0.5, 0.5, 0.05);
        const faceMaterial = new THREE.MeshPhongMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: config.opacity
        });
        const face = new THREE.Mesh(faceGeometry, faceMaterial);
        group.add(face);

        // Clock hands pointing in impossible directions
        const handMaterial = new THREE.MeshBasicMaterial({
            color: 0x000000,
            transparent: true,
            opacity: config.opacity
        });

        // Hour hand
        const hourGeometry = new THREE.BoxGeometry(0.02, 0.3, 0.01);
        const hourHand = new THREE.Mesh(hourGeometry, handMaterial);
        hourHand.position.y = 0.15;
        hourHand.rotation.z = Math.PI * 0.42; // 42% around for absurdity
        group.add(hourHand);

        // Minute hand
        const minuteGeometry = new THREE.BoxGeometry(0.01, 0.4, 0.01);
        const minuteHand = new THREE.Mesh(minuteGeometry, handMaterial);
        minuteHand.position.y = 0.2;
        minuteHand.rotation.z = Math.PI * 1.42; // Impossible rotation
        group.add(minuteHand);

        // Numbers in wrong positions
        for (let i = 0; i < 12; i++) {
            const angle = (Math.random() * Math.PI * 2); // Random instead of ordered
            const x = Math.cos(angle) * 0.4;
            const y = Math.sin(angle) * 0.4;

            const numberGeometry = new THREE.SphereGeometry(0.03);
            const numberMaterial = new THREE.MeshBasicMaterial({
                color: new THREE.Color().setHSL(i / 12, 1.0, 0.5),
                transparent: true,
                opacity: config.opacity
            });

            const number = new THREE.Mesh(numberGeometry, numberMaterial);
            number.position.set(x, y, 0.05);
            group.add(number);
        }

        this.addEasterEgg(id, group, config);
    }

    private createMemorialEgg(id: string, config: EasterEggConfig) {
        // Architectural memorial structure
        const group = new THREE.Group();

        // Create pillars
        for (let i = 0; i < 4; i++) {
            const pillarGeometry = new THREE.BoxGeometry(0.1, 1.5, 0.1);
            const pillarMaterial = new THREE.MeshPhongMaterial({
                color: 0x8b7355,
                transparent: true,
                opacity: config.opacity * 0.8
            });

            const pillar = new THREE.Mesh(pillarGeometry, pillarMaterial);
            const angle = (i / 4) * Math.PI * 2;
            pillar.position.set(
                Math.cos(angle) * 0.8,
                0.75,
                Math.sin(angle) * 0.8
            );
            group.add(pillar);
        }

        // Central memorial stone
        const stoneGeometry = new THREE.BoxGeometry(0.3, 0.4, 0.1);
        const stoneMaterial = new THREE.MeshPhongMaterial({
            color: 0x555555,
            transparent: true,
            opacity: config.opacity
        });

        const stone = new THREE.Mesh(stoneGeometry, stoneMaterial);
        stone.position.y = 0.2;
        group.add(stone);

        // Memory particles floating upward
        for (let i = 0; i < 15; i++) {
            const particleGeometry = new THREE.SphereGeometry(0.01);
            const particleMaterial = new THREE.MeshBasicMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: config.opacity * 0.6
            });

            const particle = new THREE.Mesh(particleGeometry, particleMaterial);
            particle.position.set(
                (Math.random() - 0.5) * 1.5,
                Math.random() * 2,
                (Math.random() - 0.5) * 1.5
            );
            group.add(particle);
        }

        this.addEasterEgg(id, group, config);
    }

    private addEasterEgg(id: string, object: THREE.Object3D, config: EasterEggConfig) {
        // Remove existing egg with same ID
        this.removeEasterEgg(id);

        // Apply configuration
        object.position.copy(config.position);
        object.scale.setScalar(config.scale);

        // Add to scene
        this.group.add(object);
        this.activeEggs.set(id, object);

        // Apply animation
        this.animateEasterEgg(object, config);

        // Schedule removal
        setTimeout(() => {
            this.removeEasterEgg(id);
        }, config.duration);

        console.log(`🥚 Easter egg triggered: ${id}`);
    }

    private animateEasterEgg(object: THREE.Object3D, config: EasterEggConfig) {
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / config.duration;

            if (progress >= 1) {
                return;
            }

            switch (config.animation) {
                case 'fade':
                    object.traverse((child) => {
                        if (child instanceof THREE.Mesh && child.material) {
                            const material = child.material as THREE.Material & { opacity?: number };
                            if (material.opacity !== undefined) {
                                material.opacity = config.opacity * (1 - progress);
                            }
                        }
                    });
                    break;

                case 'spiral':
                    object.rotation.y += 0.02;
                    object.position.y += Math.sin(elapsed * 0.005) * 0.001;
                    break;

                case 'pulse':
                    const pulse = 1 + Math.sin(elapsed * 0.01) * 0.3;
                    object.scale.setScalar(config.scale * pulse);
                    break;

                case 'fractal':
                    object.rotation.x += 0.01;
                    object.rotation.y += 0.015;
                    object.rotation.z += 0.008;
                    break;

                case 'explode':
                    const explosion = progress * 2;
                    object.scale.setScalar(config.scale * (1 + explosion));
                    object.traverse((child) => {
                        if (child instanceof THREE.Mesh && child.material) {
                            const material = child.material as THREE.Material & { opacity?: number };
                            if (material.opacity !== undefined) {
                                material.opacity = config.opacity * (1 - progress * 0.8);
                            }
                        }
                    });
                    break;
            }

            requestAnimationFrame(animate);
        };

        animate();
    }

    private removeEasterEgg(id: string) {
        const egg = this.activeEggs.get(id);
        if (egg) {
            this.group.remove(egg);
            this.activeEggs.delete(id);

            // Dispose of geometries and materials
            egg.traverse((child) => {
                if (child instanceof THREE.Mesh) {
                    if (child.geometry) child.geometry.dispose();
                    if (child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach(material => material.dispose());
                        } else {
                            child.material.dispose();
                        }
                    }
                }
            });
        }
    }

    public update(deltaTime: number, elapsedTime: number) {
        // Update any ongoing animations
        this.group.rotation.y += deltaTime * 0.01;
    }

    public clearAllEasterEggs() {
        const eggIds = Array.from(this.activeEggs.keys());
        eggIds.forEach(id => this.removeEasterEgg(id));
    }

    public getActiveEasterEggs(): string[] {
        return Array.from(this.activeEggs.keys());
    }
}