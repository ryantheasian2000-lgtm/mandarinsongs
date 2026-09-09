/**
 * Global Keyboard Handler for HuayuKaraoke
 * Supports Arrow Keys, Spacebar, Replay (R), Loop (L), and Speed adjustments.
 */

document.addEventListener("keydown", (e) => {
  // If user is currently typing in an input, textarea, or select, do not intercept
  const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
  if (activeTag === "input" || activeTag === "textarea" || activeTag === "select") {
    if (e.key === "Escape") {
      document.activeElement.blur();
    }
    return;
  }

  const player = window.karaokePlayer;
  if (!player) return;

  switch (e.code) {
    case "Space":
      e.preventDefault();
      player.togglePlayPause();
      break;

    case "ArrowLeft":
      e.preventDefault();
      player.prevLine();
      break;

    case "ArrowRight":
      e.preventDefault();
      player.nextLine();
      break;

    case "ArrowUp":
      e.preventDefault();
      player.replayLine();
      break;

    case "ArrowDown":
      e.preventDefault();
      player.toggleLoop();
      break;

    case "KeyR":
      e.preventDefault();
      player.replayLine();
      break;

    case "KeyL":
      e.preventDefault();
      player.toggleLoop();
      break;

    case "BracketLeft": // [ slow down
      e.preventDefault();
      const currentRate = player.audio.playbackRate;
      if (currentRate > 0.75) {
        const newRate = Math.max(0.75, currentRate - 0.1);
        player.setSpeed(newRate);
      }
      break;

    case "BracketRight": // ] speed up
      e.preventDefault();
      const currRate = player.audio.playbackRate;
      if (currRate < 1.5) {
        const newRate = Math.min(1.5, currRate + 0.1);
        player.setSpeed(newRate);
      }
      break;

    case "Escape":
      // Close all modals and dictionary popups
      document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.add("hidden"));
      if (window.dictionaryManager) {
        window.dictionaryManager.hide();
      }
      break;

    default:
      break;
  }
});
