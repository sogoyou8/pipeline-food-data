import { useState, useEffect, useRef } from 'react';

export default function AnimatedCounter({ target, duration = 800 }) {
  const [val, setVal] = useState(0);
  const raf = useRef(null);

  useEffect(() => {
    if (!target) return;
    const t0 = performance.now();
    const tick = (now) => {
      const p = Math.min((now - t0) / duration, 1);
      const e = 1 - Math.pow(1 - p, 3);
      setVal(Math.round(target * e));
      if (p < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [target, duration]);

  return <>{val.toLocaleString('fr-FR')}</>;
}