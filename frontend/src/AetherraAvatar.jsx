/**
 * AetherraAvatar.jsx
 * ──────────────────────────────────────────────────────────────────────────
 * 3-D representation of Aetherra — a circuit-patterned neural presence.
 * Aesthetic: dark humanoid with glowing green circuit traces, flowing hair,
 * solid green eyes, and a cyberpunk circuit-board corridor backdrop.
 *
 * Stack: React Three Fiber v9 · Three.js 0.183 · @react-three/drei v10
 */

import { useFrame } from '@react-three/fiber'
import { useEffect, useMemo } from 'react'
import * as THREE from 'three'

// ─── GLSL: Circuit body (head / torso / arms) ────────────────────────────────

const BODY_VERT = /* glsl */`
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vViewPos;
void main() {
  vUv        = uv;
  vNormal    = normalize(normalMatrix * normal);
  vec4 mv    = modelViewMatrix * vec4(position, 1.0);
  vViewPos   = -mv.xyz;
  gl_Position = projectionMatrix * mv;
}`

const BODY_FRAG = /* glsl */`
precision highp float;
uniform float uTime;
uniform vec3  uBase;
uniform vec3  uCircuit;
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vViewPos;

float h2(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }

float circuit(vec2 uv, float s) {
  vec2 p = uv * s;
  vec2 c = floor(p);
  vec2 f = fract(p);
  float h = h2(c);
  float w = 0.036;
  float t = 0.0;
  if      (h < 0.38) t = smoothstep(w, w*0.25, abs(f.y-0.5));
  else if (h < 0.76) t = smoothstep(w, w*0.25, abs(f.x-0.5));
  else               t = max(smoothstep(w,w*0.25,abs(f.y-0.5)),
                             smoothstep(w,w*0.25,abs(f.x-0.5)));
  if (h2(c+vec2(0.5,7.3)) > 0.70)
    t = max(t, smoothstep(0.12, 0.04, length(f-0.5)));
  return clamp(t, 0.0, 1.0);
}

void main() {
  vec3 vd = normalize(vViewPos);
  float fr  = pow(1.0 - abs(dot(vNormal, vd)), 2.8);
  float c1  = circuit(vUv, 7.0);
  float c2  = circuit(vUv * vec2(1.5,0.7)  + vec2(0.40,0.00), 13.0) * 0.50;
  float c3  = circuit(vUv * vec2(0.6,1.25) + vec2(0.11,0.53), 22.0) * 0.28;
  float ci  = clamp(c1+c2+c3, 0.0, 1.0);
  float pulse = pow(sin(vUv.y*14.0 - uTime*2.8)*0.5+0.5, 7.0) * ci;
  float scan  = step(0.996, fract(vUv.y*55.0 - uTime*0.35));
  vec3 col = uBase;
  col += uCircuit * ci    * 0.84;
  col += uCircuit * pulse * 2.0;
  col += uCircuit * scan  * 0.22;
  col += uCircuit * fr    * 1.15;
  gl_FragColor = vec4(col, 0.93 + fr*0.07);
}`

// ─── GLSL: Hair strands ──────────────────────────────────────────────────────

const HAIR_VERT = /* glsl */`
uniform float uTime;
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vViewPos;
void main() {
  vUv     = uv;
  vNormal = normalize(normalMatrix * normal);
  vec3 pos = position;
  float phase = position.x*1.9 + position.z*1.3;
  pos.x += sin(uTime*1.1  + phase)       * 0.042 * uv.y;
  pos.z += cos(uTime*0.83 + phase*0.65)  * 0.028 * uv.y;
  vec4 mv = modelViewMatrix * vec4(pos, 1.0);
  vViewPos    = -mv.xyz;
  gl_Position = projectionMatrix * mv;
}`

const HAIR_FRAG = /* glsl */`
precision mediump float;
uniform float uTime;
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vViewPos;
void main() {
  vec3 vd   = normalize(vViewPos);
  float fr  = pow(1.0 - abs(dot(vNormal, vd)), 3.0);
  float flow = pow(sin(vUv.y*9.0 - uTime*1.75 + vUv.x*2.8)*0.5+0.5, 6.0);
  float alpha = (1.0 - pow(vUv.y, 1.1)*0.62) * 0.90;
  vec3 col = vec3(0.01, 0.042, 0.018);
  col += vec3(0.0, 0.78, 0.30) * fr   * 0.58;
  col += vec3(0.0, 0.72, 0.28) * flow * 0.42;
  gl_FragColor = vec4(col, alpha);
}`

// ─── GLSL: GPU-animated particles ───────────────────────────────────────────

const PARTICLE_VERT = /* glsl */`
attribute float aOffset;
attribute float aSpeed;
uniform float uTime;
void main() {
  vec3 pos = position;
  float drift = mod(uTime*aSpeed*0.18 + aOffset*4.2, 4.2) - 2.1;
  pos.y += drift;
  float ang = aOffset*6.2832 + uTime*aSpeed*0.12;
  float r   = length(position.xz);
  pos.x = cos(ang)*r;
  pos.z = sin(ang)*r;
  vec4 mv = modelViewMatrix * vec4(pos, 1.0);
  gl_PointSize = (1.8 + aOffset*2.8) * (4.5 / -mv.z);
  gl_Position  = projectionMatrix * mv;
}`

const PARTICLE_FRAG = /* glsl */`
precision lowp float;
void main() {
  float d = length(gl_PointCoord - 0.5);
  if (d > 0.5) discard;
  float a = 1.0 - smoothstep(0.28, 0.5, d);
  gl_FragColor = vec4(0.0, 0.88, 0.36, a*0.65);
}`

// ─── GLSL: Background circuit panels ────────────────────────────────────────

const PANEL_VERT = /* glsl */`
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`

const PANEL_FRAG = /* glsl */`
precision mediump float;
uniform float uTime;
varying vec2 vUv;
float h2(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
void main() {
  vec2 g    = fract(vUv * 10.0);
  float ln  = clamp(step(0.935, g.x) + step(0.935, g.y), 0.0, 1.0);
  float nd  = h2(floor(vUv*10.0)) > 0.82
                ? smoothstep(0.45, 0.0, length(fract(vUv*10.0)-0.5)) : 0.0;
  float sc  = step(0.972, sin(vUv.y*6.5 - uTime*0.5)*0.5+0.5);
  float b   = ln*0.18 + nd*0.45 + sc*0.10;
  vec3 col  = vec3(0.0, b, b*0.44);
  float edge = smoothstep(0.0,0.06,vUv.x)*smoothstep(1.0,0.94,vUv.x)
             * smoothstep(0.0,0.06,vUv.y)*smoothstep(1.0,0.94,vUv.y);
  gl_FragColor = vec4(col, (0.42 + b*0.5)*edge);
}`

// ─── Custom hook: circuit shader material ───────────────────────────────────

function useBodyMaterial(baseHex, circuitHex) {
    const mat = useMemo(() => new THREE.ShaderMaterial({
        vertexShader: BODY_VERT,
        fragmentShader: BODY_FRAG,
        uniforms: {
            uTime: { value: 0 },
            uBase: { value: new THREE.Color(baseHex) },
            uCircuit: { value: new THREE.Color(circuitHex) },
        },
        transparent: true,
    }), [baseHex, circuitHex])

    useFrame(({ clock }) => {
        mat.uniforms.uTime.value = clock.getElapsedTime()
    })

    return mat
}

// ─── HEAD ────────────────────────────────────────────────────────────────────

function Head() {
    const mat = useBodyMaterial('#050f06', '#00e855')
    return (
        <mesh position={[0, 1.45, 0]} scale={[0.38, 0.44, 0.37]}>
            <sphereGeometry args={[1, 64, 64]} />
            <primitive object={mat} attach="material" />
        </mesh>
    )
}

// ─── TORSO ───────────────────────────────────────────────────────────────────

function Torso() {
    const mat = useBodyMaterial('#030b04', '#00dd4a')
    return (
        <mesh position={[0, 0.35, 0]}>
            <capsuleGeometry args={[0.33, 0.88, 8, 64]} />
            <primitive object={mat} attach="material" />
        </mesh>
    )
}

// ─── ARMS ────────────────────────────────────────────────────────────────────

function Arms() {
    const mat = useBodyMaterial('#030b04', '#00dd4a')
    return (
        <>
            {/* Left */}
            <mesh position={[-0.52, 0.88, 0]}>
                <sphereGeometry args={[0.19, 32, 32]} />
                <primitive object={mat} attach="material" />
            </mesh>
            <mesh position={[-0.53, 0.46, 0]} rotation={[0, 0, 0.2]}>
                <capsuleGeometry args={[0.115, 0.50, 6, 24]} />
                <primitive object={mat} attach="material" />
            </mesh>
            {/* Right */}
            <mesh position={[0.52, 0.88, 0]}>
                <sphereGeometry args={[0.19, 32, 32]} />
                <primitive object={mat} attach="material" />
            </mesh>
            <mesh position={[0.53, 0.46, 0]} rotation={[0, 0, -0.2]}>
                <capsuleGeometry args={[0.115, 0.50, 6, 24]} />
                <primitive object={mat} attach="material" />
            </mesh>
        </>
    )
}

// ─── EYES ────────────────────────────────────────────────────────────────────

function Eyes() {
    const eyeMat = useMemo(() => new THREE.MeshStandardMaterial({
        color: '#00ff66',
        emissive: '#00ff66',
        emissiveIntensity: 4,
        toneMapped: false,
    }), [])

    return (
        <>
            <mesh position={[-0.115, 1.505, 0.33]}>
                <sphereGeometry args={[0.042, 16, 16]} />
                <primitive object={eyeMat} attach="material" />
            </mesh>
            <pointLight position={[-0.115, 1.505, 0.55]} color="#00ff55" intensity={1.4} distance={2.2} decay={2} />

            <mesh position={[0.115, 1.505, 0.33]}>
                <sphereGeometry args={[0.042, 16, 16]} />
                <primitive object={eyeMat} attach="material" />
            </mesh>
            <pointLight position={[0.115, 1.505, 0.55]} color="#00ff55" intensity={1.4} distance={2.2} decay={2} />
        </>
    )
}

// ─── HAIR STRANDS ────────────────────────────────────────────────────────────

function HairStrands() {
    const STRAND_COUNT = 28

    const hairGeos = useMemo(() => {
        const geos = []
        for (let i = 0; i < STRAND_COUNT; i++) {
            const t = i / (STRAND_COUNT - 1)
            const angle = (t - 0.5) * Math.PI * 0.90
            const root = 0.31 + (Math.random() - 0.5) * 0.05
            const sx = Math.sin(angle) * root
            const sy = 1.74 + (Math.random() - 0.5) * 0.08
            const sz = -Math.cos(angle) * root * 0.55 - 0.08
            const len = 1.3 + Math.random() * 0.85
            const swX = (Math.random() - 0.5) * 0.28
            const swZ = Math.random() * 0.12

            const pts = [
                new THREE.Vector3(sx, sy, sz),
                new THREE.Vector3(sx + swX * 0.2, sy - len * 0.18, sz - 0.06 + swZ),
                new THREE.Vector3(sx + swX * 0.55, sy - len * 0.45, sz + 0.04 + swZ),
                new THREE.Vector3(sx + swX * 0.82, sy - len * 0.72, sz + 0.12 + swZ),
                new THREE.Vector3(sx + swX, sy - len, sz + 0.18 + swZ),
            ]
            const curve = new THREE.CatmullRomCurve3(pts)
            const radius = 0.011 + Math.random() * 0.009
            geos.push(new THREE.TubeGeometry(curve, 14, radius, 6, false))
        }
        return geos
    }, [])

    useEffect(() => () => hairGeos.forEach(g => g.dispose()), [hairGeos])

    const hairMat = useMemo(() => new THREE.ShaderMaterial({
        vertexShader: HAIR_VERT,
        fragmentShader: HAIR_FRAG,
        uniforms: { uTime: { value: 0 } },
        transparent: true,
        side: THREE.DoubleSide,
    }), [])

    useFrame(({ clock }) => { hairMat.uniforms.uTime.value = clock.getElapsedTime() })

    return (
        <>
            {hairGeos.map((geo, i) => (
                <mesh key={i} geometry={geo}>
                    <primitive object={hairMat} attach="material" />
                </mesh>
            ))}
        </>
    )
}

// ─── BACKGROUND CIRCUIT PANELS ───────────────────────────────────────────────
//  [x,  y,    z,   rotY,   w,   h]
const PANELS = [
    [0.0, 0.5, -3.5, 0.00, 6.0, 5.5],   // center back
    [-2.3, 0.5, -2.6, 0.68, 4.2, 5.5],   // left-center
    [2.3, 0.5, -2.6, -0.68, 4.2, 5.5],   // right-center
    [-4.2, 0.5, -0.9, 1.25, 3.2, 5.5],   // far left
    [4.2, 0.5, -0.9, -1.25, 3.2, 5.5],   // far right
]

function CircuitPanels() {
    const mat = useMemo(() => new THREE.ShaderMaterial({
        vertexShader: PANEL_VERT,
        fragmentShader: PANEL_FRAG,
        uniforms: { uTime: { value: 0 } },
        transparent: true,
        side: THREE.FrontSide,
        depthWrite: false,
    }), [])

    useFrame(({ clock }) => { mat.uniforms.uTime.value = clock.getElapsedTime() })

    return (
        <>
            {PANELS.map(([x, y, z, ry, w, h], i) => (
                <mesh key={i} position={[x, y, z]} rotation={[0, ry, 0]}>
                    <planeGeometry args={[w, h]} />
                    <primitive object={mat} attach="material" />
                </mesh>
            ))}
        </>
    )
}

// ─── AMBIENT PARTICLES ───────────────────────────────────────────────────────

const PARTICLE_COUNT = 440

function AmbientParticles() {
    const { pos, off, spd } = useMemo(() => {
        const pos = new Float32Array(PARTICLE_COUNT * 3)
        const off = new Float32Array(PARTICLE_COUNT)
        const spd = new Float32Array(PARTICLE_COUNT)
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            const ang = Math.random() * Math.PI * 2
            const r = 0.7 + Math.random() * 2.3
            pos[i * 3] = Math.cos(ang) * r
            pos[i * 3 + 1] = -2.2 + Math.random() * 4.5
            pos[i * 3 + 2] = Math.sin(ang) * r - 0.5
            off[i] = Math.random()
            spd[i] = 0.4 + Math.random() * 0.9
        }
        return { pos, off, spd }
    }, [])

    const mat = useMemo(() => new THREE.ShaderMaterial({
        vertexShader: PARTICLE_VERT,
        fragmentShader: PARTICLE_FRAG,
        uniforms: { uTime: { value: 0 } },
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
    }), [])

    useFrame(({ clock }) => { mat.uniforms.uTime.value = clock.getElapsedTime() })

    return (
        <points>
            <bufferGeometry>
                <bufferAttribute attach="attributes-position" count={PARTICLE_COUNT} array={pos} itemSize={3} />
                <bufferAttribute attach="attributes-aOffset" count={PARTICLE_COUNT} array={off} itemSize={1} />
                <bufferAttribute attach="attributes-aSpeed" count={PARTICLE_COUNT} array={spd} itemSize={1} />
            </bufferGeometry>
            <primitive object={mat} attach="material" />
        </points>
    )
}

// ─── GROUND GLOW ─────────────────────────────────────────────────────────────

function GroundGlow() {
    const mat = useMemo(() => new THREE.MeshStandardMaterial({
        color: '#001a07',
        emissive: '#003d12',
        emissiveIntensity: 1.4,
        transparent: true,
        opacity: 0.55,
        toneMapped: false,
    }), [])

    return (
        <mesh position={[0, -1.02, -0.4]} rotation={[-Math.PI / 2, 0, 0]}>
            <circleGeometry args={[2.4, 64]} />
            <primitive object={mat} attach="material" />
        </mesh>
    )
}

// ─── ASSEMBLED AVATAR ────────────────────────────────────────────────────────

export function AetherraAvatar() {
    return (
        <group>
            {/* Environment lighting — dark green atmosphere */}
            <ambientLight color="#001808" intensity={0.9} />
            <pointLight position={[0, 3.5, 2.0]} color="#00ff44" intensity={0.5} distance={9} decay={2} />
            <pointLight position={[0, -1.0, 1.5]} color="#003d15" intensity={0.4} distance={7} decay={2} />
            <pointLight position={[2, 1.0, -1.0]} color="#004d1a" intensity={0.25} distance={6} decay={2} />
            <pointLight position={[-2, 1.0, -1.0]} color="#004d1a" intensity={0.25} distance={6} decay={2} />

            <CircuitPanels />
            <GroundGlow />
            <AmbientParticles />

            {/* Body — assembled back-to-front for correct depth */}
            <HairStrands />
            <Torso />
            <Arms />
            <Head />
            <Eyes />
        </group>
    )
}
