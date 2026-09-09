/**
 * Karaoke Audio Player & Lyric Synchronization Engine
 * Handles real-time synchronized playback, line jumping, A-B line loop,
 * spotlight display, and scrubber positioning.
 */

class KaraokePlayer {
  constructor() {
    this.audio = document.getElementById("audioPlayer");
    this.progressBar = document.getElementById("progressBar");
    this.currentTimeLabel = document.getElementById("currentTimeLabel");
    this.durationLabel = document.getElementById("durationLabel");
    this.btnPlayPause = document.getElementById("btnPlayPause");
    this.playIcon = document.getElementById("playIcon");
    this.lyricsContainer = document.getElementById("lyricsContainer");
    this.spotlightPinyin = document.getElementById("spotlightPinyin");
    this.spotlightHanzi = document.getElementById("spotlightHanzi");
    this.spotlightEnglish = document.getElementById("spotlightEnglish");
    this.loopIndicator = document.getElementById("loopIndicator");
    this.btnLoopLine = document.getElementById("btnLoopLine");

    this.currentSong = null;
    this.activeLineIndex = -1;
    this.isLoopingLine = false;
    this.loopLineIndex = -1;
    this.isTraditional = false;
    this.isUserSeeking = false;

    this.initEvents();
  }

  initEvents() {
    // Play/Pause button
    this.btnPlayPause.addEventListener("click", () => this.togglePlayPause());

    // Navigation buttons
    document.getElementById("btnPrevLine").addEventListener("click", () => this.prevLine());
    document.getElementById("btnNextLine").addEventListener("click", () => this.nextLine());
    document.getElementById("btnReplayLine").addEventListener("click", () => this.replayLine());
    this.btnLoopLine.addEventListener("click", () => this.toggleLoop());

    // Audio events
    this.audio.addEventListener("timeupdate", () => this.onTimeUpdate());
    this.audio.addEventListener("loadedmetadata", () => this.onLoadedMetadata());
    this.audio.addEventListener("ended", () => this.onEnded());
    this.audio.addEventListener("play", () => this.updatePlayIcon(true));
    this.audio.addEventListener("pause", () => this.updatePlayIcon(false));

    // Scrubber interaction
    this.progressBar.addEventListener("input", () => {
      this.isUserSeeking = true;
      const targetTime = (this.progressBar.value / 100) * this.audio.duration;
      this.currentTimeLabel.textContent = this.formatTime(targetTime);
    });

    this.progressBar.addEventListener("change", () => {
      const targetTime = (this.progressBar.value / 100) * this.audio.duration;
      this.audio.currentTime = targetTime;
      this.isUserSeeking = false;
    });

    // Speed buttons
    document.querySelectorAll(".speed-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        document.querySelectorAll(".speed-btn").forEach(b => {
          b.classList.remove("bg-slate-700", "text-white");
          b.classList.add("text-slate-400");
        });
        btn.classList.add("bg-slate-700", "text-white");
        btn.classList.remove("text-slate-400");
        const speed = parseFloat(btn.dataset.speed);
        this.setSpeed(speed);
      });
    });

    // Volume bar
    const volumeBar = document.getElementById("volumeBar");
    if (volumeBar) {
      volumeBar.addEventListener("input", (e) => {
        this.audio.volume = parseFloat(e.target.value);
      });
    }
  }

  loadSong(songData) {
    this.currentSong = songData;
    this.activeLineIndex = -1;
    this.isLoopingLine = false;
    this.loopLineIndex = -1;
    this.loopIndicator.classList.add("hidden");
    this.btnLoopLine.classList.remove("bg-rose-600/30", "border-rose-500", "text-rose-300");
    this.updatePlayIcon(false);

    // Audio src
    this.audio.src = songData.audioUrl;
    this.audio.load();

    // Render song headers
    document.getElementById("currentSongTitle").textContent = songData.title || "Untitled Song";
    document.getElementById("currentSongArtist").textContent = songData.artist || "Unknown Artist";
    document.getElementById("difficultyBadge").textContent = songData.difficulty || "Mandarin Song";
    
    const tipText = songData.languageTip || "Click on any word to hear pronunciation and explore vocabulary!";
    document.getElementById("languageTipText").textContent = tipText;

    // Render lyrics in stage
    this.renderLyrics();
    this.renderTimelineMarkers();
  }

  renderLyrics() {
    if (!this.currentSong || !this.currentSong.lines) {
      this.lyricsContainer.innerHTML = `<div class="text-center py-16 text-slate-500">No lyrics available</div>`;
      return;
    }

    const lines = this.currentSong.lines;
    let html = "";

    lines.forEach((line, index) => {
      const pinyin = line.pinyin || "";
      const english = line.english || "";
      const timeStr = this.formatTime(line.startTime);

      // Build word chips for Hanzi
      let wordsHtml = "";
      if (line.words && line.words.length > 0) {
        line.words.forEach((w) => {
          if (w.isPunctuation) {
            wordsHtml += `<span class="punctuation text-slate-400 font-normal">${w.hanzi}</span>`;
          } else {
            const displayChar = this.isTraditional ? (w.traditional || w.hanzi) : w.hanzi;
            const toneClass = `tone-${w.tone || 1}`;
            wordsHtml += `
              <span class="word-chip ${toneClass}" 
                    data-line-idx="${index}" 
                    data-word='${JSON.stringify(w).replace(/'/g, "&apos;")}'>
                ${displayChar}
              </span>
            `;
          }
        });
      } else {
        wordsHtml = line.hanzi;
      }

      html += `
        <div id="lyric-line-${index}" class="lyric-line flex items-start gap-3 group" data-line-idx="${index}">
          <!-- Timestamp Pill -->
          <span class="text-[11px] font-mono text-slate-500 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60 mt-1 flex-shrink-0 group-hover:border-rose-500/50 group-hover:text-rose-300 transition">
            ${timeStr}
          </span>

          <!-- Lyric Content Block -->
          <div class="flex-1 space-y-1">
            <!-- Pinyin Layer -->
            <div class="line-pinyin pinyin-display text-xs text-rose-300/70 font-medium tracking-wider">
              ${pinyin}
            </div>
            <!-- Hanzi Layer -->
            <div class="line-hanzi text-lg sm:text-xl font-bold text-slate-200 tracking-wide">
              ${wordsHtml}
            </div>
            <!-- English Translation Layer -->
            <div class="line-english english-display text-xs text-slate-400 font-normal italic">
              ${english}
            </div>
          </div>

          <!-- Quick Action Controls -->
          <div class="opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity pt-1">
            <button class="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-rose-400 transition" title="Play from this line" onclick="window.karaokePlayer.seekToLine(${index})">
              <i data-lucide="play" class="w-3.5 h-3.5"></i>
            </button>
          </div>
        </div>
      `;
    });

    this.lyricsContainer.innerHTML = html;
    if (window.lucide) lucide.createIcons();

    // Attach click listeners to lines and word chips
    this.attachLyricListeners();
  }

  attachLyricListeners() {
    // Line click seeks to line
    this.lyricsContainer.querySelectorAll(".lyric-line").forEach(lineEl => {
      lineEl.addEventListener("click", (e) => {
        // If clicked on word chip, let word chip handler handle popup
        if (e.target.closest(".word-chip")) return;
        const idx = parseInt(lineEl.dataset.lineIdx, 10);
        this.seekToLine(idx);
      });
    });

    // Word chips click launches dictionary popup
    this.lyricsContainer.querySelectorAll(".word-chip").forEach(chip => {
      chip.addEventListener("click", (e) => {
        e.stopPropagation();
        const wordData = JSON.parse(chip.dataset.word);
        const lineIdx = parseInt(chip.dataset.lineIdx, 10);
        const lineContext = this.currentSong.lines[lineIdx] ? this.currentSong.lines[lineIdx].hanzi : "";
        window.dictionaryManager.show(wordData, lineContext, chip);
      });
    });
  }

  renderTimelineMarkers() {
    const container = document.getElementById("timelineMarkers");
    if (!container || !this.currentSong || !this.currentSong.lines || !this.audio.duration) return;

    container.innerHTML = "";
    const dur = this.audio.duration;
    this.currentSong.lines.forEach(line => {
      const pct = (line.startTime / dur) * 100;
      const marker = document.createElement("div");
      marker.className = "timeline-marker";
      marker.style.left = `${pct}%`;
      marker.title = `${this.formatTime(line.startTime)}: ${line.hanzi}`;
      container.appendChild(marker);
    });
  }

  onTimeUpdate() {
    const currentTime = this.audio.currentTime;
    const duration = this.audio.duration || 1;

    // Update scrubber if not being dragged
    if (!this.isUserSeeking) {
      this.progressBar.value = (currentTime / duration) * 100;
      this.currentTimeLabel.textContent = this.formatTime(currentTime);
    }

    if (!this.currentSong || !this.currentSong.lines) return;

    // Check A-B Loop boundary
    if (this.isLoopingLine && this.loopLineIndex !== -1) {
      const loopLine = this.currentSong.lines[this.loopLineIndex];
      if (loopLine && currentTime >= loopLine.endTime) {
        this.audio.currentTime = loopLine.startTime;
        return;
      }
    }

    // Find current active line
    const lines = this.currentSong.lines;
    let newIndex = -1;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const nextLine = lines[i + 1];
      let lineEnd = line.endTime;
      if (!lineEnd || lineEnd <= line.startTime) {
        lineEnd = (nextLine && nextLine.startTime > line.startTime) ? nextLine.startTime : (line.startTime + 4.0);
      }

      if (currentTime >= line.startTime && currentTime < lineEnd) {
        newIndex = i;
        break;
      }
    }

    // Fallback: if past all lines, stay on last line
    if (newIndex === -1 && lines.length > 0 && currentTime >= lines[lines.length - 1].startTime) {
      newIndex = lines.length - 1;
    }

    if (newIndex !== this.activeLineIndex && newIndex !== -1) {
      this.setActiveLine(newIndex);
    }
  }

  setActiveLine(index) {
    this.activeLineIndex = index;
    const line = this.currentSong.lines[index];
    if (!line) return;

    // Update Stage highlighting
    this.lyricsContainer.querySelectorAll(".lyric-line").forEach((el, i) => {
      if (i === index) {
        el.classList.add("active");
        this.scrollToActiveLine(el);
      } else {
        el.classList.remove("active");
      }
    });

    // Update Spotlight Display Card
    this.spotlightPinyin.textContent = line.pinyin || "";
    this.spotlightEnglish.textContent = line.english || "";
    
    // Spotlight Hanzi word chips
    let wordsHtml = "";
    if (line.words && line.words.length > 0) {
      line.words.forEach(w => {
        if (w.isPunctuation) {
          wordsHtml += `<span class="punctuation text-slate-400 font-normal">${w.hanzi}</span>`;
        } else {
          const displayChar = this.isTraditional ? (w.traditional || w.hanzi) : w.hanzi;
          const toneClass = `tone-${w.tone || 1}`;
          wordsHtml += `
            <span class="word-chip ${toneClass}" 
                  data-line-idx="${index}" 
                  data-word='${JSON.stringify(w).replace(/'/g, "&apos;")}'>
              ${displayChar}
            </span>
          `;
        }
      });
    } else {
      wordsHtml = line.hanzi;
    }
    this.spotlightHanzi.innerHTML = wordsHtml;

    // Attach click to spotlight chips
    this.spotlightHanzi.querySelectorAll(".word-chip").forEach(chip => {
      chip.addEventListener("click", (e) => {
        e.stopPropagation();
        const wordData = JSON.parse(chip.dataset.word);
        window.dictionaryManager.show(wordData, line.hanzi, chip);
      });
    });
  }

  scrollToActiveLine(element) {
    const autoScrollPref = localStorage.getItem("huayu_autoscroll") || "center";
    if (autoScrollPref === "none") return;

    element.scrollIntoView({
      behavior: "smooth",
      block: autoScrollPref === "nearest" ? "nearest" : "center"
    });
  }

  onLoadedMetadata() {
    this.durationLabel.textContent = this.formatTime(this.audio.duration);
    this.renderTimelineMarkers();
  }

  onEnded() {
    this.updatePlayIcon(false);
  }

  togglePlayPause() {
    if (this.audio.paused) {
      this.audio.play().catch(e => console.error(e));
    } else {
      this.audio.pause();
    }
  }

  updatePlayIcon(isPlaying) {
    const btn = this.btnPlayPause || document.getElementById("btnPlayPause");
    if (!btn) return;
    if (isPlaying) {
      btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16" rx="1.5"></rect><rect x="14" y="4" width="4" height="16" rx="1.5"></rect></svg>`;
      btn.setAttribute("title", "Pause (Spacebar)");
    } else {
      btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 ml-0.5" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"></polygon></svg>`;
      btn.setAttribute("title", "Play (Spacebar)");
    }
  }

  seekToLine(lineIndex) {
    if (!this.currentSong || !this.currentSong.lines) return;
    if (lineIndex < 0 || lineIndex >= this.currentSong.lines.length) return;
    
    const targetLine = this.currentSong.lines[lineIndex];
    this.audio.currentTime = Math.max(0, targetLine.startTime);
    this.setActiveLine(lineIndex);

    if (this.audio.paused) {
      this.audio.play().catch(e => console.error(e));
    }
  }

  prevLine() {
    if (!this.currentSong || !this.currentSong.lines) return;
    const targetIdx = Math.max(0, this.activeLineIndex - 1);
    this.seekToLine(targetIdx);
  }

  nextLine() {
    if (!this.currentSong || !this.currentSong.lines) return;
    const targetIdx = Math.min(this.currentSong.lines.length - 1, this.activeLineIndex + 1);
    this.seekToLine(targetIdx);
  }

  replayLine() {
    if (this.activeLineIndex >= 0) {
      this.seekToLine(this.activeLineIndex);
    } else {
      this.seekToLine(0);
    }
  }

  toggleLoop() {
    this.isLoopingLine = !this.isLoopingLine;
    if (this.isLoopingLine) {
      this.loopLineIndex = this.activeLineIndex >= 0 ? this.activeLineIndex : 0;
      this.loopIndicator.classList.remove("hidden");
      this.btnLoopLine.classList.add("bg-rose-600/30", "border-rose-500", "text-rose-300");
    } else {
      this.loopLineIndex = -1;
      this.loopIndicator.classList.add("hidden");
      this.btnLoopLine.classList.remove("bg-rose-600/30", "border-rose-500", "text-rose-300");
    }
  }

  setSpeed(speed) {
    this.audio.playbackRate = speed;
  }

  toggleScript(isTrad) {
    this.isTraditional = isTrad;
    if (this.currentSong) {
      this.renderLyrics();
      if (this.activeLineIndex >= 0) {
        this.setActiveLine(this.activeLineIndex);
      }
    }
  }

  formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return "00:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
}

window.karaokePlayer = new KaraokePlayer();
