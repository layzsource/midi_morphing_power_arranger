import * as THREE from 'three';

export class VesselLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private wireframeCube: THREE.LineSegments;
    private rings: THREE.Mesh[] = [];
    private triangleFacets: THREE.Mesh[] = [];
    private intensity = 0.6;
    private pulseRate = 1.0;
    private isInMotion = false;
    private rotationSpeed = 0.2;

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.initGeometry();
    }

    private initGeometry() {
        // Create wireframe cube with rings in each face
        // Each ring's edges touch all four sides of its square face

        const cubeSize = 3.0;
        const halfCube = cubeSize / 2;
        const ringRadius = halfCube; // Ring radius = half cube size so edges touch sides
        const tubeRadius = 0.06;
        const tubularSegments = 32;
        const radialSegments = 8;

        // 1. Wireframe cube removed - now just the 6 rings

        // 2. Ring material
        const ringMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.7,
            roughness: 0.1,
            metalness: 0.8,
            emissive: 0x002244,
            emissiveIntensity: 0.2,
            clearcoat: 1.0,
            clearcoatRoughness: 0.0,
            iridescence: 0.6,
            iridescenceIOR: 1.4,
            iridescenceThicknessRange: [100, 400]
        });

        // 3. Triangle facet material
        const facetMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x004466,
            transparent: true,
            opacity: 0.4,
            roughness: 0.2,
            metalness: 0.5,
            side: THREE.DoubleSide
        });

        // 4. Create rings for all 6 faces of the cube
        const ellipse = new THREE.EllipseCurve(
            0, 0,
            ringRadius, ringRadius,
            0, 2 * Math.PI,
            false,
            0
        );

        const points = ellipse.getPoints(64);
        const points3d = points.map(p => new THREE.Vector3(p.x, p.y, 0));
        const curve3d = new THREE.CatmullRomCurve3(points3d, true);

        const tubeGeometry = new THREE.TubeGeometry(
            curve3d,
            tubularSegments,
            tubeRadius,
            radialSegments,
            true
        );

        // Front face ring (YZ plane)
        const frontRing = new THREE.Mesh(tubeGeometry, ringMaterial);
        frontRing.position.set(0, 0, halfCube);
        frontRing.rotation.set(0, 0, 0);
        this.rings.push(frontRing);
        this.group.add(frontRing);

        // Back face ring (YZ plane)
        const backRing = new THREE.Mesh(tubeGeometry, ringMaterial.clone());
        backRing.position.set(0, 0, -halfCube);
        backRing.rotation.set(0, 0, 0);
        this.rings.push(backRing);
        this.group.add(backRing);

        // Right face ring (XZ plane)
        const rightRing = new THREE.Mesh(tubeGeometry, ringMaterial.clone());
        rightRing.position.set(halfCube, 0, 0);
        rightRing.rotation.set(0, Math.PI/2, 0);
        this.rings.push(rightRing);
        this.group.add(rightRing);

        // Left face ring (XZ plane)
        const leftRing = new THREE.Mesh(tubeGeometry, ringMaterial.clone());
        leftRing.position.set(-halfCube, 0, 0);
        leftRing.rotation.set(0, Math.PI/2, 0);
        this.rings.push(leftRing);
        this.group.add(leftRing);

        // Top face ring (XY plane)
        const topRing = new THREE.Mesh(tubeGeometry, ringMaterial.clone());
        topRing.position.set(0, halfCube, 0);
        topRing.rotation.set(Math.PI/2, 0, 0);
        this.rings.push(topRing);
        this.group.add(topRing);

        // Bottom face ring (XY plane)
        const bottomRing = new THREE.Mesh(tubeGeometry, ringMaterial.clone());
        bottomRing.position.set(0, -halfCube, 0);
        bottomRing.rotation.set(Math.PI/2, 0, 0);
        this.rings.push(bottomRing);
        this.group.add(bottomRing);

        // 5. Create 4 triangle facets connecting ring to front face corners
        const frontFaceCorners = [
            new THREE.Vector3(-halfCube, -halfCube, halfCube), // Bottom left
            new THREE.Vector3(halfCube, -halfCube, halfCube),  // Bottom right
            new THREE.Vector3(halfCube, halfCube, halfCube),   // Top right
            new THREE.Vector3(-halfCube, halfCube, halfCube)   // Top left
        ];

        const ringTouchPoints = [
            new THREE.Vector3(0, -ringRadius, halfCube),      // Bottom touch point
            new THREE.Vector3(ringRadius, 0, halfCube),       // Right touch point
            new THREE.Vector3(0, ringRadius, halfCube),       // Top touch point
            new THREE.Vector3(-ringRadius, 0, halfCube)       // Left touch point
        ];

        for (let i = 0; i < 4; i++) {
            const triangleGeometry = new THREE.BufferGeometry();
            const vertices = new Float32Array([
                // Ring touch point
                ringTouchPoints[i].x, ringTouchPoints[i].y, ringTouchPoints[i].z,
                // Corner
                frontFaceCorners[i].x, frontFaceCorners[i].y, frontFaceCorners[i].z,
                // Next corner
                frontFaceCorners[(i + 1) % 4].x, frontFaceCorners[(i + 1) % 4].y, frontFaceCorners[(i + 1) % 4].z
            ]);

            triangleGeometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
            triangleGeometry.computeVertexNormals();

            const triangle = new THREE.Mesh(triangleGeometry, facetMaterial.clone());
            this.triangleFacets.push(triangle);
            this.group.add(triangle);
        }

        this.group.position.set(0, 0, 0);
    }

    public processFrequency(signal: any) {
        // Empty
    }

    public setIntensity(intensity: number) {
        this.intensity = Math.max(0.3, intensity);
    }

    public update(deltaTime: number, elapsedTime: number) {
        if (this.isInMotion) {
            // Slow rotation on Y axis
            this.group.rotation.y += deltaTime * this.rotationSpeed;

            // Gyration cycle - subtle tilting and oscillation
            const gyrationSpeed = 0.3;
            this.group.rotation.x = Math.sin(elapsedTime * gyrationSpeed) * 0.15;
            this.group.rotation.z = Math.cos(elapsedTime * gyrationSpeed * 0.7) * 0.1;

            // Subtle position oscillation for breathing effect
            const breathingAmplitude = 0.05;
            this.group.position.y = Math.sin(elapsedTime * 0.5) * breathingAmplitude;
        }
    }

    public reset() {
        // Empty
    }

    public getCurrentIntensity(): number {
        return this.intensity;
    }

    public getCurrentPulseRate(): number {
        return this.pulseRate;
    }

    public setPulseRate(rate: number) {
        this.pulseRate = rate;
    }

    public triggerHarmony() {
        // Empty
    }

    public triggerConflict() {
        // Empty
    }

    public getMorphingState() {
        return {
            isMorphing: false,
            morphProgress: 0.0
        };
    }

    public toggleMotion() {
        this.isInMotion = !this.isInMotion;
        if (!this.isInMotion) {
            // Reset to static position
            this.group.rotation.set(0, 0, 0);
            this.group.position.set(0, 0, 0);
        }
    }

    public setMotion(inMotion: boolean) {
        this.isInMotion = inMotion;
        if (!this.isInMotion) {
            // Reset to static position
            this.group.rotation.set(0, 0, 0);
            this.group.position.set(0, 0, 0);
        }
    }

    public getMotionState(): boolean {
        return this.isInMotion;
    }

    public setVisible(visible: boolean) {
        this.group.visible = visible;
    }

    public rotateX(angle: number) {
        this.group.rotation.x += angle;
    }

    public rotateY(angle: number) {
        this.group.rotation.y += angle;
    }

    public rotateZ(angle: number) {
        this.group.rotation.z += angle;
    }

    public setRotation(x: number, y: number, z: number) {
        this.group.rotation.set(x, y, z);
    }

    public getRotation() {
        return {
            x: this.group.rotation.x,
            y: this.group.rotation.y,
            z: this.group.rotation.z
        };
    }
}