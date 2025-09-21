import * as THREE from 'three';
import { FluidDynamics, CavitationBubble } from '../physics/FluidDynamics';
import { ParticlePhysicsEncoder, PhysicsProperties } from '../physics/ParticlePhysicsEncoder';
import { ShadowCastingSystem } from '../shadow/ShadowCastingSystem';

export class EmergentFormLayer {
    private scene: THREE.Scene;
    private group: THREE.Group;
    private morphTargets: THREE.Mesh[] = [];
    private currentForm = 0;
    private speed = 0.8;
    private intensity = 0.7;
    private morphingSpeed = 1.0;

    // Core archetypal forms - clean, distinct, professional
    private blakeForm: THREE.Mesh;
    private teslaForm: THREE.Mesh;
    private beatlesForm: THREE.Mesh;
    private greenBeanForm: THREE.Mesh; // The beloved morphing green bean returns!

    private emittedSprites: THREE.Mesh[] = [];
    private spriteEmissionRate = 0.1;
    private fluidDynamics: FluidDynamics;
    private physicsEncoder: ParticlePhysicsEncoder;
    private shadowCasting: ShadowCastingSystem;
    private currentSignal: any = null;

    // Tim Cook-level state management
    private morphState = {
        isActive: false,
        targetForm: 0,
        progress: 0,
        elegantTiming: 0
    };

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.group = new THREE.Group();
        this.scene.add(this.group);
        this.fluidDynamics = new FluidDynamics();
        this.physicsEncoder = new ParticlePhysicsEncoder();
        this.shadowCasting = new ShadowCastingSystem(scene);
        this.initProfessionalForms();
    }

    private initProfessionalForms() {
        // Create the beloved morphing green bean - organic, flowing, alive
        this.createGreenBean();

        // Blake: Ethereal spiritual presence - completely distinct from particles
        this.createBlakeApparition();

        // Tesla: Electromagnetic field visualization - structured energy
        this.createTeslaField();

        // Beatles: Harmonic resonance forms - collective energy
        this.createBeatlesHarmony();

        // Start with the green bean as default
        this.setActiveForm(3); // Green bean
    }

    private createGreenBean() {
        // The beloved organic morphing shape - like a living green bean
        const beanGeometry = new THREE.CapsuleGeometry(0.3, 1.2, 8, 16);

        // Organic, flowing material - distinctly different from particles
        const beanMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x4ade80,           // Beautiful green
            transparent: true,
            opacity: 0.8,
            roughness: 0.3,
            metalness: 0.1,
            emissive: 0x166534,        // Subtle green glow
            emissiveIntensity: 0.2,
            clearcoat: 0.8,
            clearcoatRoughness: 0.1,
            transmission: 0.1,         // Slightly translucent
            thickness: 0.5
        });

        this.greenBeanForm = new THREE.Mesh(beanGeometry, beanMaterial);
        this.greenBeanForm.visible = true; // Start visible as default
        this.group.add(this.greenBeanForm);
    }

    private createBlakeApparition() {
        // William Blake: Spiritual flame-like form - ethereal and wispy
        const blakeGeometry = new THREE.ConeGeometry(0.4, 2.0, 8, 1, true);

        // Spiritual apparition material - completely distinct from particles
        const blakeMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xff6b6b,           // Warm spiritual red
            transparent: true,
            opacity: 0.4,
            roughness: 0.0,
            metalness: 0.0,
            emissive: 0x662222,
            emissiveIntensity: 0.3,
            side: THREE.DoubleSide,
            blending: THREE.NormalBlending // NO additive blending to differentiate
        });

        this.blakeForm = new THREE.Mesh(blakeGeometry, blakeMaterial);
        this.blakeForm.visible = false;
        this.group.add(this.blakeForm);
    }

    private createTeslaField() {
        // Tesla: Electromagnetic coil structure
        const teslaGeometry = new THREE.TorusGeometry(0.8, 0.15, 8, 24);

        // Electric blue energy field - solid, not particle-like
        const teslaMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x3b82f6,           // Electric blue
            transparent: true,
            opacity: 0.7,
            roughness: 0.1,
            metalness: 0.9,
            emissive: 0x1e3a8a,
            emissiveIntensity: 0.4,
            clearcoat: 1.0,
            clearcoatRoughness: 0.0
        });

        this.teslaForm = new THREE.Mesh(teslaGeometry, teslaMaterial);
        this.teslaForm.visible = false;
        this.group.add(this.teslaForm);
    }

    private createBeatlesHarmony() {
        // Beatles: Four-part harmony - four spheres in formation
        const beatlesGroup = new THREE.Group();

        const sphereGeometry = new THREE.SphereGeometry(0.25, 16, 12);
        const harmonicColors = [0xff9500, 0x8b5cf6, 0xf59e0b, 0xec4899]; // Psychedelic colors

        for (let i = 0; i < 4; i++) {
            const sphereMaterial = new THREE.MeshPhysicalMaterial({
                color: harmonicColors[i],
                transparent: true,
                opacity: 0.6,
                roughness: 0.2,
                metalness: 0.3,
                emissive: harmonicColors[i],
                emissiveIntensity: 0.1,
                iridescence: 0.5
            });

            const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            const angle = (i / 4) * Math.PI * 2;
            sphere.position.set(Math.cos(angle) * 0.8, 0, Math.sin(angle) * 0.8);
            beatlesGroup.add(sphere);
        }

        this.beatlesForm = beatlesGroup;
        this.beatlesForm.visible = false;
        this.group.add(this.beatlesForm);
    }

    private setActiveForm(formIndex: number) {
        // Hide all forms first
        [this.blakeForm, this.teslaForm, this.beatlesForm, this.greenBeanForm].forEach(form => {
            if (form) form.visible = false;
        });

        // Show the selected form
        switch (formIndex) {
            case 0:
                if (this.blakeForm) this.blakeForm.visible = true;
                break;
            case 1:
                if (this.teslaForm) this.teslaForm.visible = true;
                break;
            case 2:
                if (this.beatlesForm) this.beatlesForm.visible = true;
                break;
            case 3:
                if (this.greenBeanForm) this.greenBeanForm.visible = true;
                break;
        }

        this.currentForm = formIndex;
    }

    public processMIDI(signal: any) {
        this.currentSignal = signal;

        // MIDI controls form selection and morphing
        if (signal.type === 'note_on') {
            const noteMap = { 60: 0, 62: 1, 64: 2, 65: 3 }; // C, D, E, F
            if (noteMap[signal.note] !== undefined) {
                this.triggerMorph(noteMap[signal.note]);
            }
        }

        // CC controls morphing parameters
        if (signal.type === 'control_change') {
            const ccValue = signal.value / 127;
            switch (signal.cc) {
                case 1: // Modulation wheel - morphing intensity
                    this.morphingSpeed = 0.5 + ccValue * 2;
                    break;
                case 7: // Volume - form opacity
                    this.setFormOpacity(ccValue);
                    break;
            }
        }
    }

    public processBeat(signal: any) {
        const intensity = signal.intensity || 0.5;

        // Beat triggers elegant pulsing, not random flashes
        this.createElegantPulse(intensity);

        // Emit physics-encoded sprites from the heart of the form
        if (this.currentForm >= 0 && intensity > 0.6) {
            this.emitEncodedSprite(intensity);
        }
    }

    private createElegantPulse(intensity: number) {
        const currentMesh = this.getCurrentFormMesh();
        if (!currentMesh) return;

        // Elegant scaling pulse - no random flashing
        const pulseScale = 1 + intensity * 0.2;
        currentMesh.scale.setScalar(pulseScale);

        // Return to normal scale gracefully
        setTimeout(() => {
            if (currentMesh.scale) {
                currentMesh.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1);
            }
        }, 100);
    }

    private getCurrentFormMesh(): THREE.Mesh | THREE.Group | null {
        switch (this.currentForm) {
            case 0: return this.blakeForm;
            case 1: return this.teslaForm;
            case 2: return this.beatlesForm;
            case 3: return this.greenBeanForm;
            default: return null;
        }
    }

    private setFormOpacity(opacity: number) {
        const currentMesh = this.getCurrentFormMesh();
        if (!currentMesh) return;

        if (currentMesh instanceof THREE.Mesh) {
            (currentMesh.material as THREE.MeshPhysicalMaterial).opacity = opacity;
        } else if (currentMesh instanceof THREE.Group) {
            currentMesh.children.forEach(child => {
                if (child instanceof THREE.Mesh) {
                    (child.material as THREE.MeshPhysicalMaterial).opacity = opacity;
                }
            });
        }
    }

    private emitEncodedSprite(intensity: number) {
        // Create cavitation bubble with physics encoding
        const bubble: CavitationBubble = {
            position: new THREE.Vector3(0, 0, 0),
            pressure: intensity * 100,
            temperature: 300 + intensity * 200,
            collapsing: false,
            emissionTime: Date.now()
        };

        // Encode with physics properties
        const physicsProps: PhysicsProperties = {
            chirality: Math.random() > 0.5 ? 'left' : 'right',
            helicity: Math.random() > 0.5 ? 'parallel' : 'antiparallel',
            charge: (Math.random() - 0.5) * 2,
            quarkFlavor: ['up', 'down', 'charm', 'strange'][Math.floor(Math.random() * 4)] as any,
            polarization: Math.random() * Math.PI * 2,
            decayPattern: 'stable'
        };

        const encodedData = this.physicsEncoder.encodeSprite(bubble, physicsProps, this.currentSignal);

        // Create elegant sprite - not random flash
        const spriteGeometry = new THREE.SphereGeometry(0.05, 8, 6);
        const spriteMaterial = new THREE.MeshBasicMaterial({
            color: this.getFormColor(),
            transparent: true,
            opacity: 0.8
        });

        const sprite = new THREE.Mesh(spriteGeometry, spriteMaterial);
        sprite.position.copy(this.group.position);

        // Elegant outward movement
        const direction = new THREE.Vector3(
            (Math.random() - 0.5) * 2,
            (Math.random() - 0.5) * 2,
            (Math.random() - 0.5) * 2
        ).normalize();

        sprite.userData = {
            velocity: direction.multiplyScalar(0.02),
            lifetime: 3.0,
            encoded: encodedData
        };

        this.emittedSprites.push(sprite);
        this.scene.add(sprite);

        // Cast shadow for microfiche system
        this.shadowCasting.castSpriteShadow(sprite, encodedData);
    }

    private getFormColor(): number {
        switch (this.currentForm) {
            case 0: return 0xff6b6b; // Blake red
            case 1: return 0x3b82f6; // Tesla blue
            case 2: return 0xff9500; // Beatles orange
            case 3: return 0x4ade80; // Green bean green
            default: return 0xffffff;
        }
    }

    public update(deltaTime: number, elapsedTime: number) {
        this.morphState.elegantTiming += deltaTime;

        // Update current form with elegant organic motion
        const currentMesh = this.getCurrentFormMesh();
        if (currentMesh) {
            // Gentle organic breathing and movement
            if (this.currentForm === 3) { // Green bean gets special organic motion
                currentMesh.rotation.y += deltaTime * 0.3;
                currentMesh.rotation.x = Math.sin(elapsedTime * 0.8) * 0.1;
                currentMesh.scale.y = 1 + Math.sin(elapsedTime * 1.2) * 0.1; // Breathing
            } else {
                // Other forms get subtle movement
                currentMesh.rotation.y += deltaTime * 0.2;
                const breathe = 1 + Math.sin(elapsedTime * 0.6) * 0.05;
                currentMesh.scale.setScalar(breathe);
            }
        }

        // Update sprites elegantly
        this.updateSprites(deltaTime);

        // Fluid dynamics update
        this.fluidDynamics.update(deltaTime);
    }

    private updateSprites(deltaTime: number) {
        for (let i = this.emittedSprites.length - 1; i >= 0; i--) {
            const sprite = this.emittedSprites[i];

            // Elegant movement
            sprite.position.add(sprite.userData.velocity);
            sprite.userData.lifetime -= deltaTime;

            // Graceful fade
            const material = sprite.material as THREE.MeshBasicMaterial;
            material.opacity = sprite.userData.lifetime / 3.0;

            // Remove when done
            if (sprite.userData.lifetime <= 0) {
                this.scene.remove(sprite);
                this.emittedSprites.splice(i, 1);
            }
        }
    }

    public triggerMorph(targetForm: number) {
        this.setActiveForm(targetForm);
        this.morphState.isActive = true;
        this.morphState.targetForm = targetForm;
    }

    // Legacy API compatibility
    public setIntensity(intensity: number) { this.intensity = intensity; }
    public setSpeed(speed: number) { this.speed = speed; }
    public getCurrentIntensity(): number { return this.intensity; }
    public getCurrentSpeed(): number { return this.speed; }
    public triggerBlakeForm() { this.triggerMorph(0); }
    public triggerTeslaForm() { this.triggerMorph(1); }
    public triggerBeatlesForm() { this.triggerMorph(2); }
    public triggerGreenBean() { this.triggerMorph(3); }
    public reset() { this.triggerMorph(3); } // Default to beloved green bean
    public getMorphingState() { return this.morphState; }

    // VJ Interface compatibility method
    public getShadowStatistics() {
        return {
            activeSprites: this.emittedSprites.length,
            shadowsCast: this.emittedSprites.length,
            totalEncoded: this.emittedSprites.length * 8, // Estimated
            compressionRatio: 0.85
        };
    }

    public setVisible(visible: boolean) {
        this.group.visible = visible;
    }
}