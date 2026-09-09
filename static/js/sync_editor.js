/**
 * Tap-to-Sync Lyric Timestamp Editor
 * Lets users stamp or fine-tune millisecond timestamps while listening to audio.
 */

class SyncEditor {
  constructor() {
    this.modal = document.getElementById("syncModal");
    this.linesContainer = document.getElementById("syncLinesList");
    this.btnSave = document.getElementById("btnSaveSyncData");
    this.currentLines = [];
    this.selectedLineIndex = 0;

    this.initEvents();
  }

  initEvents() {
    const btnOpen = document.getElementById("btnSyncEditor");
    if (btnOpen) {
      btnOpen.addEventListener("click", () => this.open());
    }

    if (this.btnSave) {
      this.btnSave.addEventListener("click", () => this.save());
    }
  }

  open() {
    const player = window.karaokePlayer;
    if (!player || !player.currentSong) {
      alert("Please select or upload a song first.");
      return;
    }

    // Clone current song lines
    this.currentLines = JSON.parse(JSON.stringify(player.currentSong.lines || []));
    this.selectedLineIndex = player.activeLineIndex >= 0 ? player.activeLineIndex : 0;
    this.render();
    this.modal.classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
  }

  render() {
    if (this.currentLines.length === 0) {
      this.linesContainer.innerHTML = `<div class="text-center py-8 text-slate-500">No lyric lines to sync.</div>`;
      return;
    }

    let html = "";
    this.currentLines.forEach((line, idx) => {
      const isSelected = idx === this.selectedLineIndex;
      html += `
        <div class="sync-row p-2.5 rounded-xl border ${isSelected ? 'border-emerald-500/80 bg-slate-800/90 shadow-md' : 'border-slate-800 bg-slate-800/40'} flex items-center justify-between gap-3" data-sync-idx="${idx}">
          <div class="flex items-center gap-2">
            <span class="w-6 text-[10px] text-slate-500 font-mono text-right">${idx + 1}</span>
            <button class="stamp-btn px-2 py-1 rounded bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/40 text-[11px] font-semibold transition" title="Stamp audio current time to this line">
              Stamp (${this.formatTime(line.startTime)})
            </button>
          </div>

          <div class="flex-1 min-w-0">
            <div class="text-xs font-bold text-white truncate">${line.hanzi}</div>
            <div class="text-[11px] text-rose-300/80 truncate">${line.pinyin || ""}</div>
          </div>

          <div class="flex items-center gap-2">
            <label class="text-[10px] text-slate-400">Start (s):</label>
            <input type="number" step="0.1" value="${line.startTime}" class="start-time-input w-16 bg-slate-900 border border-slate-700 rounded px-1.5 py-0.5 text-xs text-center text-white" />
            <label class="text-[10px] text-slate-400">End (s):</label>
            <input type="number" step="0.1" value="${line.endTime || (line.startTime + 4.0)}" class="end-time-input w-16 bg-slate-900 border border-slate-700 rounded px-1.5 py-0.5 text-xs text-center text-white" />
          </div>
        </div>
      `;
    });

    this.linesContainer.innerHTML = html;
    this.attachRowEvents();
  }

  attachRowEvents() {
    const player = window.karaokePlayer;

    this.linesContainer.querySelectorAll(".sync-row").forEach(row => {
      const idx = parseInt(row.dataset.syncIdx, 10);

      // Stamp button
      const stampBtn = row.querySelector(".stamp-btn");
      stampBtn.addEventListener("click", () => {
        const currentAudioTime = roundToTenth(player.audio.currentTime);
        this.currentLines[idx].startTime = currentAudioTime;
        if (idx > 0) {
          this.currentLines[idx - 1].endTime = currentAudioTime;
        }
        this.currentLines[idx].endTime = roundToTenth(currentAudioTime + 4.0);
        this.selectedLineIndex = Math.min(this.currentLines.length - 1, idx + 1);
        this.render();
      });

      // Inputs
      const startInput = row.querySelector(".start-time-input");
      startInput.addEventListener("change", (e) => {
        this.currentLines[idx].startTime = parseFloat(e.target.value) || 0;
      });

      const endInput = row.querySelector(".end-time-input");
      endInput.addEventListener("change", (e) => {
        this.currentLines[idx].endTime = parseFloat(e.target.value) || 0;
      });
    });
  }

  async save() {
    const player = window.karaokePlayer;
    if (!player.currentSong) return;

    // Guarantee that every line's endTime connects to the next line's startTime
    for (let i = 0; i < this.currentLines.length; i++) {
      if (i + 1 < this.currentLines.length) {
        if (this.currentLines[i + 1].startTime > this.currentLines[i].startTime) {
          this.currentLines[i].endTime = this.currentLines[i + 1].startTime;
        } else if (!this.currentLines[i].endTime || this.currentLines[i].endTime <= this.currentLines[i].startTime) {
          this.currentLines[i].endTime = roundToTenth(this.currentLines[i].startTime + 4.0);
        }
      } else {
        if (!this.currentLines[i].endTime || this.currentLines[i].endTime <= this.currentLines[i].startTime) {
          this.currentLines[i].endTime = roundToTenth(this.currentLines[i].startTime + 5.0);
        }
      }
    }

    this.btnSave.textContent = "Saving...";
    try {
      const res = await fetch("/api/save-sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          songId: player.currentSong.id,
          lines: this.currentLines
        })
      });
      const data = await res.json();
      if (data.song) {
        player.loadSong(data.song);
      }
      this.modal.classList.add("hidden");
    } catch (err) {
      alert("Error saving sync data: " + err.message);
    } finally {
      this.btnSave.textContent = "Save Changes";
    }
  }

  formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return "00:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
}

function roundToTenth(val) {
  return Math.round(val * 10) / 10;
}

window.syncEditor = new SyncEditor();
