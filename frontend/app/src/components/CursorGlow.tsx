import { useEffect } from "react";
import "../styles/App.css";

const CursorGlow = () => {
  useEffect(() => {
    let lastX = 0,
      lastY = 0;
    let currentSize = 700; // initial size
    let targetSize = 700;

    // Get the glow element once; it will be available after the component mounts.
    const glow = document.querySelector(".glow") as HTMLDivElement | null;

    // Animation loop: updates the size smoothly.
    const updateGlowSize = () => {
      if (glow) {
        // Use a damping factor to interpolate the size smoothly.
        const damping = 0.1; // Adjust for smoother or snappier transitions.
        currentSize += (targetSize - currentSize) * damping;

        glow.style.width = `${currentSize}px`;
        glow.style.height = `${currentSize}px`;
      }
      requestAnimationFrame(updateGlowSize);
    };

    // Start the size animation loop.
    requestAnimationFrame(updateGlowSize);

    // Handle mouse movement.
    const handleMouseMove = (e: MouseEvent) => {
      // Immediately update the glow's position so it stays on top of the cursor.
      if (glow) {
        glow.style.left = `${e.clientX}px`;
        glow.style.top = `${e.clientY}px`;
      }

      // Calculate movement speed based on how far the cursor moved.
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      const velocity = Math.sqrt(dx * dx + dy * dy);

      // Update target size based on velocity.
      // (Adjust the formula to control the range of sizes.)
      targetSize = Math.min(800 - velocity * 25, 700);

      lastX = e.clientX;
      lastY = e.clientY;
    };

    document.addEventListener("mousemove", handleMouseMove);
    return () => document.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return <div className="glow"></div>;
};

export default CursorGlow;
