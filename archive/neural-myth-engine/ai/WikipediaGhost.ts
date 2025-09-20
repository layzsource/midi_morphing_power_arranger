import * as THREE from 'three';

interface HistoricalFigureData {
    name: string;
    imageUrl?: string;
    summary: string;
    birthYear?: number;
    deathYear?: number;
    categories: string[];
}

export class WikipediaGhost {
    private scene: THREE.Scene;
    private ghostMeshes: Map<string, THREE.Mesh> = new Map();
    private figureData: Map<string, HistoricalFigureData> = new Map();

    // Archetype to historical figure mapping
    private archetypeMapping = {
        'russell': 'Walter Russell',
        'blake': 'William Blake',
        'tesla': 'Nikola Tesla',
        'beatles': 'The Beatles',
        'leadbelly': 'Lead Belly',
        'hawking': 'Stephen Hawking',
        'pranksters': 'Ken Kesey', // Leader of Merry Pranksters
        'hoffman': 'Abbie Hoffman',
        'waas': 'Les Waas',
        'greiff': 'Constance Greiff'
    };

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.initializeFigureData();
    }

    private initializeFigureData() {
        // Pre-populate with known data to avoid API calls for now
        // In a real implementation, this would fetch from Wikipedia API
        this.figureData.set('russell', {
            name: 'Walter Russell',
            summary: 'American polymath, artist, scientist, and philosopher. Known for his theory of the universe based on wave phenomena.',
            birthYear: 1871,
            deathYear: 1963,
            categories: ['cosmology', 'sacred geometry', 'consciousness'],
            imageUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iIzAwZDRmZiIgb3BhY2l0eT0iMC4zIi8+PHRleHQgeD0iNTAiIHk9IjU1IiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+V1I8L3RleHQ+PC9zdmc+'
        });

        this.figureData.set('blake', {
            name: 'William Blake',
            summary: 'English poet, painter, and printmaker. A seminal figure in the history of poetry and visual arts of the Romantic Age.',
            birthYear: 1757,
            deathYear: 1827,
            categories: ['mysticism', 'poetry', 'art'],
            imageUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iIzUwYzg3OCIgb3BhY2l0eT0iMC4zIi8+PHRleHQgeD0iNTAiIHk9IjU1IiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+V0I8L3RleHQ+PC9zdmc+'
        });

        this.figureData.set('tesla', {
            name: 'Nikola Tesla',
            summary: 'Serbian-American inventor, electrical engineer, mechanical engineer, and futurist best known for his contributions to the design of alternating current.',
            birthYear: 1856,
            deathYear: 1943,
            categories: ['electricity', 'invention', 'physics'],
            imageUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iIzQxNjllMSIgb3BhY2l0eT0iMC4zIi8+PHRleHQgeD0iNTAiIHk9IjU1IiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+TlQ8L3RleHQ+PC9zdmc+'
        });
    }

    public async summonGhost(archetype: string): Promise<void> {
        const figureName = this.archetypeMapping[archetype as keyof typeof this.archetypeMapping];
        if (!figureName) return;

        console.log(`👻 Summoning ghost of ${figureName}...`);

        // Get or create ghost mesh
        let ghostMesh = this.ghostMeshes.get(archetype);

        if (!ghostMesh) {
            ghostMesh = await this.createGhostMesh(archetype);
            this.ghostMeshes.set(archetype, ghostMesh);
            this.scene.add(ghostMesh);
        }

        // Animate ghost appearance
        this.animateGhostAppearance(ghostMesh);

        // Display information
        this.displayFigureInfo(archetype);
    }

    private async createGhostMesh(archetype: string): Promise<THREE.Mesh> {
        const figureData = this.figureData.get(archetype);

        // Create ghostly plane for image display
        const geometry = new THREE.PlaneGeometry(1.5, 1.5);

        // Load image texture (fallback to generated avatar)
        const texture = await this.loadGhostTexture(figureData?.imageUrl);

        const material = new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            opacity: 0.6,
            side: THREE.DoubleSide,
            blending: THREE.NormalBlending, // Less intense blending
            alphaTest: 0.1, // Remove noise pixels
            depthWrite: false, // Prevent z-fighting
            color: 0xffffff
        });

        const mesh = new THREE.Mesh(geometry, material);

        // Position ghost in a clean circular formation around the center
        const angle = this.getArchetypeAngle(archetype);
        const radius = 4; // Further from center for cleaner look
        mesh.position.set(
            Math.cos(angle) * radius,
            2.0, // Higher floating position
            Math.sin(angle) * radius
        );

        // Always face camera
        mesh.lookAt(0, 1.5, 0);

        return mesh;
    }

    private async loadGhostTexture(imageUrl?: string): Promise<THREE.Texture> {
        if (imageUrl && imageUrl.startsWith('data:')) {
            // Load from data URL
            const loader = new THREE.TextureLoader();
            return new Promise((resolve, reject) => {
                loader.load(
                    imageUrl,
                    resolve,
                    undefined,
                    (error) => {
                        console.warn('Failed to load ghost image, using procedural texture', error);
                        resolve(this.createProceduralGhostTexture());
                    }
                );
            });
        }

        return this.createProceduralGhostTexture();
    }

    private createProceduralGhostTexture(): THREE.Texture {
        // Create higher resolution ghost texture
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d')!;

        // Clear background
        ctx.clearRect(0, 0, 256, 256);

        // Create multiple layered ethereal effects
        for (let i = 0; i < 3; i++) {
            const size = 128 - (i * 30);
            const alpha = 0.8 - (i * 0.2);

            // Create ghostly orb with multiple gradients
            const gradient = ctx.createRadialGradient(128, 128, 0, 128, 128, size);
            gradient.addColorStop(0, `rgba(255, 255, 255, ${alpha})`);
            gradient.addColorStop(0.3, `rgba(200, 220, 255, ${alpha * 0.7})`);
            gradient.addColorStop(0.6, `rgba(150, 180, 255, ${alpha * 0.4})`);
            gradient.addColorStop(0.8, `rgba(100, 150, 255, ${alpha * 0.2})`);
            gradient.addColorStop(1, 'rgba(80, 120, 200, 0)');

            ctx.fillStyle = gradient;
            ctx.globalCompositeOperation = 'screen'; // Additive blending
            ctx.beginPath();
            ctx.arc(128, 128, size, 0, Math.PI * 2);
            ctx.fill();
        }

        // Add wispy texture
        ctx.globalCompositeOperation = 'overlay';
        for (let i = 0; i < 20; i++) {
            const x = Math.random() * 256;
            const y = Math.random() * 256;
            const radius = Math.random() * 30 + 10;

            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, 'rgba(255, 255, 255, 0.1)');
            gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        }

        const texture = new THREE.CanvasTexture(canvas);
        texture.generateMipmaps = false;
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;

        return texture;
    }

    private getArchetypeAngle(archetype: string): number {
        const archetypes = Object.keys(this.archetypeMapping);
        const index = archetypes.indexOf(archetype);
        return (index / archetypes.length) * Math.PI * 2;
    }

    private animateGhostAppearance(mesh: THREE.Mesh): void {
        // Start invisible and fade in
        const material = mesh.material as THREE.MeshBasicMaterial;
        material.opacity = 0;

        const startTime = Date.now();
        const duration = 2000; // 2 seconds

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Fade in with gentle floating
            material.opacity = progress * 0.7;
            mesh.position.y = 1.5 + Math.sin(progress * Math.PI) * 0.3;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    private displayFigureInfo(archetype: string): void {
        const figureData = this.figureData.get(archetype);
        if (!figureData) return;

        console.log(`📚 ${figureData.name} (${figureData.birthYear}-${figureData.deathYear})`);
        console.log(`📖 ${figureData.summary}`);
        console.log(`🏷️ Categories: ${figureData.categories.join(', ')}`);
    }

    public dismissGhost(archetype: string): void {
        const mesh = this.ghostMeshes.get(archetype);
        if (!mesh) return;

        // Animate ghost disappearance
        const material = mesh.material as THREE.MeshBasicMaterial;
        const startOpacity = material.opacity;
        const startTime = Date.now();
        const duration = 1000; // 1 second

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            material.opacity = startOpacity * (1 - progress);
            mesh.position.y += 0.01; // Float upward as it fades

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.scene.remove(mesh);
                this.ghostMeshes.delete(archetype);
            }
        };

        animate();
    }

    public dismissAllGhosts(): void {
        for (const archetype of this.ghostMeshes.keys()) {
            this.dismissGhost(archetype);
        }
    }

    public update(deltaTime: number): void {
        // Update ghost animations with very subtle movement
        for (const mesh of this.ghostMeshes.values()) {
            // Very gentle floating animation - much subtler
            const baseY = 2.0;
            const floatOffset = Math.sin(Date.now() * 0.0005) * 0.1;
            mesh.position.y = baseY + floatOffset;

            // Keep ghosts facing camera (billboard effect)
            mesh.lookAt(0, mesh.position.y, 0);
        }
    }
}