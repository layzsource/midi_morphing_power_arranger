/**
 * Cymatic Patterns - Ernst Chladni inspired vibrational pattern visualization
 *
 * Real-time audio-reactive cymatic pattern generation:
 * - Chladni patterns (mid-frequencies 200-1000 Hz)
 * - Mandala patterns (high frequencies >1000 Hz)
 * - Wave interference (low frequencies <200 Hz)
 * - Sacred geometry mathematics integrated
 */

import * as THREE from 'three';

export interface CymaticConfig {
    sensitivity: number;
    complexity: number;
    symmetry: number;
    resonance: number;
}

export class CymaticPatternGenerator {
    private scene: THREE.Scene;
    private geometry: THREE.BufferGeometry;
    private material: THREE.ShaderMaterial;
    private mesh: THREE.Mesh;
    private config: CymaticConfig;

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.config = {
            sensitivity: 1.0,
            complexity: 4,
            symmetry: 6,
            resonance: 0.5
        };

        this.initializeGeometry();
        this.createShaderMaterial();
        this.createMesh();
    }

    private initializeGeometry() {
        // Create a plane geometry for the cymatic pattern surface
        this.geometry = new THREE.PlaneGeometry(4, 4, 128, 128);
    }

    private createShaderMaterial() {
        this.material = new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uFrequency: { value: 440 },
                uAmplitude: { value: 0.5 },
                uComplexity: { value: this.config.complexity },
                uSymmetry: { value: this.config.symmetry },
                uResonance: { value: this.config.resonance },
                uLowFreq: { value: 0 },
                uMidFreq: { value: 0 },
                uHighFreq: { value: 0 }
            },
            vertexShader: `
                uniform float uTime;
                uniform float uFrequency;
                uniform float uAmplitude;
                uniform float uComplexity;
                uniform float uSymmetry;
                uniform float uResonance;
                uniform float uLowFreq;
                uniform float uMidFreq;
                uniform float uHighFreq;

                varying vec2 vUv;
                varying float vElevation;

                // Chladni plate equation approximation
                float chladniPattern(vec2 pos, float freq) {
                    float a = freq * 0.01;
                    float m = floor(uComplexity);
                    float n = floor(uSymmetry);

                    return sin(a * m * pos.x) * sin(a * n * pos.y) +
                           cos(a * n * pos.x) * cos(a * m * pos.y);
                }

                // Wave interference patterns
                float waveInterference(vec2 pos, float freq) {
                    float wave1 = sin(length(pos) * freq * 0.1 + uTime * 2.0);
                    float wave2 = sin(length(pos - vec2(0.5, 0.0)) * freq * 0.1 + uTime * 1.5);
                    float wave3 = sin(length(pos + vec2(0.5, 0.0)) * freq * 0.1 + uTime * 1.8);

                    return (wave1 + wave2 + wave3) / 3.0;
                }

                // Sacred geometry mandala patterns
                float mandalaPattern(vec2 pos, float freq) {
                    float angle = atan(pos.y, pos.x);
                    float radius = length(pos);

                    float symmetryAngle = angle * uSymmetry;
                    float radiusWave = sin(radius * freq * 0.05 + uTime) * uResonance;
                    float angleWave = sin(symmetryAngle + uTime * 0.5) * uResonance;

                    return (radiusWave + angleWave) * 0.5;
                }

                void main() {
                    vUv = uv;
                    vec2 centeredPos = uv - 0.5;

                    // Frequency-based pattern selection
                    float elevation = 0.0;

                    // Low frequencies (<200 Hz) -> Wave interference
                    if (uLowFreq > 0.1) {
                        elevation += waveInterference(centeredPos, uFrequency) * uLowFreq * 0.5;
                    }

                    // Mid frequencies (200-1000 Hz) -> Chladni patterns
                    if (uMidFreq > 0.1) {
                        elevation += chladniPattern(centeredPos, uFrequency) * uMidFreq * 0.8;
                    }

                    // High frequencies (>1000 Hz) -> Mandala patterns
                    if (uHighFreq > 0.1) {
                        elevation += mandalaPattern(centeredPos, uFrequency) * uHighFreq * 0.6;
                    }

                    vElevation = elevation * uAmplitude;

                    vec3 newPosition = position;
                    newPosition.z = vElevation;

                    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
                }
            `,
            fragmentShader: `
                uniform float uTime;
                uniform float uLowFreq;
                uniform float uMidFreq;
                uniform float uHighFreq;

                varying vec2 vUv;
                varying float vElevation;

                void main() {
                    // Color based on elevation and frequency content
                    vec3 lowColor = vec3(0.1, 0.3, 0.8);   // Blue for low freq
                    vec3 midColor = vec3(0.0, 1.0, 1.0);   // Cyan for mid freq
                    vec3 highColor = vec3(1.0, 0.5, 0.0);  // Orange for high freq

                    float normalizedElevation = (vElevation + 1.0) * 0.5;

                    vec3 color = lowColor * uLowFreq +
                               midColor * uMidFreq +
                               highColor * uHighFreq;

                    // Add pattern-based brightness
                    float brightness = 0.5 + normalizedElevation * 0.5;
                    color *= brightness;

                    // Add some shimmer
                    color += sin(vUv.x * 20.0 + uTime * 4.0) * 0.1;

                    gl_FragColor = vec4(color, 0.8);
                }
            `,
            transparent: true,
            side: THREE.DoubleSide
        });
    }

    private createMesh() {
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.rotation.x = -Math.PI * 0.3; // Tilt for better viewing
        this.mesh.position.y = -1;
        // Don't add to scene - cymatic patterns should be in their own dedicated visualization
        // this.scene.add(this.mesh);
    }

    public updateAudioAnalysis(analysis: { frequency: Float32Array, rms: number, peak: number, pitch: number }) {
        if (!analysis.frequency || analysis.frequency.length === 0) return;

        const lowFreq = this.getFrequencyBand(analysis.frequency, 0, 0.2);    // <200 Hz
        const midFreq = this.getFrequencyBand(analysis.frequency, 0.2, 0.6);  // 200-1000 Hz
        const highFreq = this.getFrequencyBand(analysis.frequency, 0.6, 1.0); // >1000 Hz

        // Update shader uniforms
        this.material.uniforms.uTime.value += 0.016;
        this.material.uniforms.uFrequency.value = analysis.pitch || 440;
        this.material.uniforms.uAmplitude.value = Math.min(analysis.rms * 3, 1.0);
        this.material.uniforms.uLowFreq.value = lowFreq;
        this.material.uniforms.uMidFreq.value = midFreq;
        this.material.uniforms.uHighFreq.value = highFreq;
    }

    private getFrequencyBand(frequencyData: Float32Array, startPercent: number, endPercent: number): number {
        const startIndex = Math.floor(startPercent * frequencyData.length);
        const endIndex = Math.floor(endPercent * frequencyData.length);

        let sum = 0;
        let count = 0;

        for (let i = startIndex; i < endIndex && i < frequencyData.length; i++) {
            // Convert from dB to linear scale
            const linearValue = Math.pow(10, frequencyData[i] / 20);
            sum += linearValue;
            count++;
        }

        return count > 0 ? Math.min(sum / count, 1.0) : 0;
    }

    public updateConfig(config: Partial<CymaticConfig>) {
        this.config = { ...this.config, ...config };

        this.material.uniforms.uComplexity.value = this.config.complexity;
        this.material.uniforms.uSymmetry.value = this.config.symmetry;
        this.material.uniforms.uResonance.value = this.config.resonance;
    }

    public setVisibility(visible: boolean) {
        this.mesh.visible = visible;
    }

    public dispose() {
        this.scene.remove(this.mesh);
        this.geometry.dispose();
        this.material.dispose();
    }
}