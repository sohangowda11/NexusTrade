"use client";
import { useEffect, useRef } from "react";

export default function ParticleField({ className = "" }: { className?: string }) {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;
    let animId: number;

    const init = async () => {
      const THREE = await import("three");
      const el = mountRef.current!;
      const w = el.clientWidth || 800;
      const h = el.clientHeight || 400;

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(w, h);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setClearColor(0x000000, 0);
      el.appendChild(renderer.domElement);

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 1000);
      camera.position.z = 80;

      const COUNT = 400;
      const positions = new Float32Array(COUNT * 3);
      const velocities: number[] = [];

      for (let i = 0; i < COUNT; i++) {
        positions[i * 3]     = (Math.random() - 0.5) * 200;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 80;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 40;
        velocities.push(
          (Math.random() - 0.5) * 0.04,
          (Math.random() - 0.5) * 0.04,
          0
        );
      }

      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      const mat = new THREE.PointsMaterial({
        color: 0x00d4ff,
        size: 0.6,
        transparent: true,
        opacity: 0.6,
      });
      const points = new THREE.Points(geo, mat);
      scene.add(points);

      const animate = () => {
        animId = requestAnimationFrame(animate);
        const pos = geo.attributes.position.array as Float32Array;
        for (let i = 0; i < COUNT; i++) {
          pos[i * 3]     += velocities[i * 3];
          pos[i * 3 + 1] += velocities[i * 3 + 1];
          if (Math.abs(pos[i * 3])     > 100) velocities[i * 3]     *= -1;
          if (Math.abs(pos[i * 3 + 1]) > 40)  velocities[i * 3 + 1] *= -1;
        }
        geo.attributes.position.needsUpdate = true;
        points.rotation.y += 0.0003;
        renderer.render(scene, camera);
      };
      animate();

      const onResize = () => {
        if (!el) return;
        const nw = el.clientWidth, nh = el.clientHeight;
        camera.aspect = nw / nh;
        camera.updateProjectionMatrix();
        renderer.setSize(nw, nh);
      };
      window.addEventListener("resize", onResize);

      return () => {
        cancelAnimationFrame(animId);
        window.removeEventListener("resize", onResize);
        renderer.dispose();
        if (el.contains(renderer.domElement)) el.removeChild(renderer.domElement);
      };
    };

    let cleanup: (() => void) | undefined;
    init().then((fn) => { cleanup = fn; });
    return () => { cleanup?.(); };
  }, []);

  return (
    <div
      ref={mountRef}
      className={className}
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
    />
  );
}
