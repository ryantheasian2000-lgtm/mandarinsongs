/**
 * Main Application Orchestrator for HuayuKaraoke
 */

class App {
  constructor() {
    this.songSelect = document.getElementById("songSelect");
    this.uploadModal = document.getElementById("uploadModal");
    this.uploadForm = document.getElementById("uploadForm");
    this.btnUploadModal = document.getElementById("btnUploadModal");
    this.btnYoutubeModal = document.getElementById("btnYoutubeModal");
    this.youtubeModal = document.getElementById("youtubeModal");
    this.youtubeForm = document.getElementById("youtubeForm");
    this.settingsModal = document.getElementById("settingsModal");
    this.btnSettingsModal = document.getElementById("btnSettingsModal");
    this.btnSaveSettings = document.getElementById("btnSaveSettings");
    this.vocabCountBadge = document.getElementById("vocabCountBadge");

    this.btnDeleteSong = document.getElementById("btnDeleteSong");
    this.btnTranslateLyrics = document.getElementById("btnTranslateLyrics");
    this.allSongsList = [];

    this.init();
  }

  async init() {
    this.initToggles();
    this.initModals();
    this.initSettings();
    if (this.btnDeleteSong) {
      this.btnDeleteSong.addEventListener("click", () => this.handleDeleteSong());
    }
    if (this.btnTranslateLyrics) {
      this.btnTranslateLyrics.addEventListener("click", () => this.handleTranslateLyrics());
    }
    await this.loadSongList();
    await this.updateVocabBadge();
  }

  initToggles() {
    // Tone colors active by default
    document.body.classList.add("tone-colors-active");
    const toggleToneBtn = document.getElementById("toggleToneColorsBtn");
    const toneText = document.getElementById("toneColorsToggleText");
    if (toggleToneBtn) {
      toggleToneBtn.addEventListener("click", () => {
        const active = document.body.classList.toggle("tone-colors-active");
        if (toneText) toneText.textContent = active ? "Active" : "Disabled";
        toggleToneBtn.classList.toggle("active", active);
      });
    }

    // Pinyin Full vs Hidden (Blinder Mode)
    const pinyinFullBtn = document.getElementById("pinyinFullBtn");
    const pinyinHideBtn = document.getElementById("pinyinHideBtn");
    if (pinyinFullBtn && pinyinHideBtn) {
      pinyinFullBtn.addEventListener("click", () => {
        document.body.classList.remove("pinyin-hidden");
        pinyinFullBtn.classList.add("active");
        pinyinHideBtn.classList.remove("active");
      });
      pinyinHideBtn.addEventListener("click", () => {
        document.body.classList.add("pinyin-hidden");
        pinyinHideBtn.classList.add("active");
        pinyinFullBtn.classList.remove("active");
      });
    }

    // English Toggle
    const toggleEnglishBtn = document.getElementById("toggleEnglishBtn");
    const englishText = document.getElementById("englishToggleText");
    if (toggleEnglishBtn) {
      toggleEnglishBtn.addEventListener("click", () => {
        const hidden = document.body.classList.toggle("english-hidden");
        if (englishText) englishText.textContent = hidden ? "Hidden" : "Shown";
        toggleEnglishBtn.classList.toggle("active", !hidden);
      });
    }

    // Script Mode (Simplified / Traditional)
    const scriptSimpBtn = document.getElementById("scriptSimpBtn");
    const scriptTradBtn = document.getElementById("scriptTradBtn");
    if (scriptSimpBtn && scriptTradBtn) {
      scriptSimpBtn.addEventListener("click", () => {
        scriptSimpBtn.classList.add("active");
        scriptTradBtn.classList.remove("active");
        window.karaokePlayer.toggleScript(false);
      });
      scriptTradBtn.addEventListener("click", () => {
        scriptTradBtn.classList.add("active");
        scriptSimpBtn.classList.remove("active");
        window.karaokePlayer.toggleScript(true);
      });
    }
  }

  initModals() {
    // Upload Modal trigger
    this.btnUploadModal.addEventListener("click", () => {
      this.uploadModal.classList.remove("hidden");
      if (window.lucide) lucide.createIcons();
    });

    // YouTube Import Modal trigger
    if (this.btnYoutubeModal && this.youtubeModal) {
      this.btnYoutubeModal.addEventListener("click", () => {
        const savedKey = localStorage.getItem("huayu_gemini_api_key") || "";
        const keyInput = document.getElementById("youtubeApiKeyInput");
        const keyStatus = document.getElementById("ytApiKeyStatus");
        if (keyInput) keyInput.value = savedKey;
        if (keyStatus) {
          if (savedKey) {
            keyStatus.className = "text-[10px] text-emerald-400 font-medium";
            keyStatus.textContent = "✓ Key loaded from Settings";
          } else {
            keyStatus.className = "text-[10px] text-amber-400 font-medium";
            keyStatus.textContent = "⚠️ Key missing (add key for translations)";
          }
        }
        this.youtubeModal.classList.remove("hidden");
        if (window.lucide) lucide.createIcons();
      });
    }

    // Close buttons on all modals
    document.querySelectorAll(".closeModalBtn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.add("hidden"));
      });
    });

    // Upload Form Submit
    this.uploadForm.addEventListener("submit", (e) => this.handleSongUpload(e));

    // YouTube Form Submit
    if (this.youtubeForm) {
      this.youtubeForm.addEventListener("submit", (e) => this.handleYoutubeImport(e));
    }
  }

  initSettings() {
    const keyInput = document.getElementById("geminiApiKeyInput");
    const scrollSelect = document.getElementById("autoScrollSelect");

    // Load saved settings
    keyInput.value = localStorage.getItem("huayu_gemini_api_key") || "";
    scrollSelect.value = localStorage.getItem("huayu_autoscroll") || "center";

    this.btnSettingsModal.addEventListener("click", () => {
      this.settingsModal.classList.remove("hidden");
      if (window.lucide) lucide.createIcons();
    });

    this.btnSaveSettings.addEventListener("click", () => {
      localStorage.setItem("huayu_gemini_api_key", keyInput.value.trim());
      localStorage.setItem("huayu_autoscroll", scrollSelect.value);
      this.settingsModal.classList.add("hidden");
      alert("Settings saved successfully!");
    });
  }

  async loadSongList() {
    try {
      const res = await fetch("/api/songs");
      const data = await res.json();
      this.allSongsList = data.songs || [];

      this.songSelect.innerHTML = "";
      this.allSongsList.forEach(song => {
        const opt = document.createElement("option");
        opt.value = song.id;
        opt.textContent = `${song.title} - ${song.artist}${song.isCustom ? " (Custom)" : ""}`;
        this.songSelect.appendChild(opt);
      });

      this.songSelect.onchange = (e) => {
        if (e.target.value) {
          this.loadSongDetail(e.target.value);
        }
      };

      // Load first song by default
      if (this.allSongsList.length > 0) {
        await this.loadSongDetail(this.allSongsList[0].id);
      }
    } catch (err) {
      console.error("Error loading songs:", err);
    }
  }

  async loadSongDetail(songId) {
    try {
      const res = await fetch(`/api/songs/${songId}`);
      const songData = await res.json();
      if (songData.error) throw new Error(songData.error);
      
      window.karaokePlayer.loadSong(songData);
      this.songSelect.value = songId;

      // Update Delete Song Button visibility
      if (this.btnDeleteSong) {
        if (songData.isCustom) {
          this.btnDeleteSong.classList.remove("hidden");
        } else {
          this.btnDeleteSong.classList.add("hidden");
        }
      }
    } catch (err) {
      alert("Could not load song: " + err.message);
    }
  }

  async handleDeleteSong() {
    const currentSong = window.karaokePlayer ? window.karaokePlayer.currentSong : null;
    if (!currentSong || !currentSong.isCustom) {
      alert("Built-in demo songs cannot be deleted.");
      return;
    }

    if (!confirm(`Are you sure you want to delete "${currentSong.title}"?`)) {
      return;
    }

    try {
      const res = await fetch(`/api/songs/${currentSong.id}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      alert("Song deleted successfully.");
      await this.loadSongList();
    } catch (err) {
      alert("Error deleting song: " + err.message);
    }
  }

  async handleTranslateLyrics() {
    const player = window.karaokePlayer;
    if (!player || !player.currentSong) {
      alert("Please select a song first.");
      return;
    }

    const currentSong = player.currentSong;
    if (!currentSong.lines || currentSong.lines.length === 0) {
      alert("This song has no lyric lines to translate.");
      return;
    }

    const apiKey = localStorage.getItem("huayu_gemini_api_key") || "";
    if (!apiKey) {
      alert("Please configure your Gemini API Key in Settings first.");
      this.settingsModal.classList.remove("hidden");
      return;
    }

    const btn = this.btnTranslateLyrics;
    const btnText = document.getElementById("translateBtnText");
    const originalText = btnText ? btnText.textContent : "Translate with Gemini";

    try {
      if (btn) btn.disabled = true;
      if (btnText) btnText.innerHTML = `<span class="inline-block animate-pulse">Translating ${currentSong.lines.length} lines with Gemini...</span>`;

      const res = await fetch(`/api/songs/${currentSong.id}/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ apiKey: apiKey })
      });

      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || "Failed to translate lyrics");
      }

      if (data.song) {
        player.loadSong(data.song);
        const songIdx = this.allSongsList.findIndex(s => s.id === data.song.id);
        if (songIdx !== -1) {
          this.allSongsList[songIdx] = data.song;
        }
      }

      alert(data.message || "Lyrics translated successfully!");
    } catch (err) {
      console.error(err);
      alert(`Translation Error: ${err.message}`);
    } finally {
      if (btn) btn.disabled = false;
      if (btnText) btnText.textContent = originalText;
      if (window.lucide) lucide.createIcons();
    }
  }

  async handleSongUpload(e) {
    e.preventDefault();
    const fileInput = document.getElementById("audioFileInput");
    const titleInput = document.getElementById("songTitleInput");
    const artistInput = document.getElementById("artistInput");
    const statusMsg = document.getElementById("uploadStatusMessage");
    const submitBtn = document.getElementById("btnSubmitUpload");
    const lrcText = document.getElementById("lrcTextInput").value;

    if (!fileInput.files || fileInput.files.length === 0) {
      alert("Please choose an audio file.");
      return;
    }

    if (!lrcText.trim()) {
      alert("Please paste LRC or Chinese lyrics.");
      return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("audio", file);
    formData.append("title", titleInput.value.trim() || file.name.replace(/\.[^/.]+$/, ""));
    formData.append("artist", artistInput.value.trim() || "Mandarin Artist");

    statusMsg.className = "text-xs p-2.5 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30";
    statusMsg.textContent = "Uploading audio file to server...";
    statusMsg.classList.remove("hidden");
    submitBtn.disabled = true;

    try {
      // Step 1: Upload audio file
      const uploadRes = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });
      const uploadedSong = await uploadRes.json();
      if (uploadedSong.error) throw new Error(uploadedSong.error);

      // Step 2: Parse lyrics & generate Pinyin
      statusMsg.textContent = "Parsing lyrics, generating Pinyin, and building vocabulary tokens...";
      const lrcRes = await fetch("/api/parse-lrc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          songId: uploadedSong.id,
          lrcText: lrcText,
          apiKey: localStorage.getItem("huayu_gemini_api_key") || ""
        })
      });

      const contentType = lrcRes.headers.get("content-type") || "";
      if (!lrcRes.ok || !contentType.includes("application/json")) {
        const errText = await lrcRes.text();
        throw new Error(`Server returned HTTP ${lrcRes.status}: ${errText.substring(0, 150)}`);
      }
      const lrcData = await lrcRes.json();
      if (lrcData.error) throw new Error(lrcData.error);

      statusMsg.className = "text-xs p-2.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
      statusMsg.textContent = "Song processed and saved successfully!";

      // Reload song list and select the new custom song
      await this.loadSongList();
      await this.loadSongDetail(uploadedSong.id);

      setTimeout(() => {
        this.uploadModal.classList.add("hidden");
        this.uploadForm.reset();
        statusMsg.classList.add("hidden");
        submitBtn.disabled = false;
      }, 1000);

    } catch (err) {
      statusMsg.className = "text-xs p-3 rounded-xl bg-rose-500/20 text-rose-200 border border-rose-500/40 space-y-1";
      statusMsg.innerHTML = `
        <div class="font-bold text-rose-300">Upload Error</div>
        <div>${err.message}</div>
      `;
      submitBtn.disabled = false;
    }
  }

  async handleYoutubeImport(e) {
    e.preventDefault();
    const urlInput = document.getElementById("youtubeUrlInput");
    const statusBox = document.getElementById("youtubeStatusBox");
    const submitBtn = document.getElementById("btnSubmitYoutube");
    const btnText = document.getElementById("youtubeBtnText");

    const url = (urlInput ? urlInput.value : "").trim();
    if (!url) {
      alert("Please enter a YouTube URL.");
      return;
    }

    const keyInput = document.getElementById("youtubeApiKeyInput");
    let apiKey = (keyInput && keyInput.value ? keyInput.value.trim() : "") || localStorage.getItem("huayu_gemini_api_key") || "";
    if (keyInput && keyInput.value.trim()) {
      localStorage.setItem("huayu_gemini_api_key", keyInput.value.trim());
    }

    if (statusBox) {
      statusBox.className = "text-xs p-3 rounded-xl bg-blue-500/20 text-blue-200 border border-blue-500/30 space-y-1.5";
      statusBox.innerHTML = `
        <div class="flex items-center gap-2 font-medium text-blue-300">
          <svg class="animate-spin h-4 w-4 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span>Processing YouTube song...</span>
        </div>
        <div class="text-[11px] text-slate-300 leading-relaxed">
          1. Gemini 3.5 Flash-Lite extracting title & artist<br/>
          2. LRCLIB querying synced lyrics<br/>
          3. yt-dlp downloading audio<br/>
          4. Generating Pinyin & English translations<br/>
          <i>Please wait a few moments...</i>
        </div>
      `;
      statusBox.classList.remove("hidden");
    }

    if (submitBtn) submitBtn.disabled = true;
    if (btnText) btnText.textContent = "Processing...";

    try {
      const res = await fetch("/api/import-youtube", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          youtubeUrl: url,
          apiKey: apiKey
        })
      });

      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const text = await res.text();
        throw new Error(`Server returned HTTP ${res.status}: ${text.substring(0, 150)}`);
      }

      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || "Failed to import YouTube song");
      }

      const song = data.song;
      if (statusBox) {
        statusBox.className = "text-xs p-3 rounded-xl bg-emerald-500/20 text-emerald-200 border border-emerald-500/30 space-y-1";
        statusBox.innerHTML = `
          <div class="font-bold text-emerald-300">Import Successful!</div>
          <div class="text-[11px]">Added "${song.title}" with ${song.lines ? song.lines.length : 0} synced lines.</div>
        `;
      }

      // Reload song list and switch to the newly created song
      await this.loadSongList();
      await this.loadSongDetail(song.id);

      setTimeout(() => {
        if (this.youtubeModal) this.youtubeModal.classList.add("hidden");
        if (this.youtubeForm) this.youtubeForm.reset();
        if (statusBox) statusBox.classList.add("hidden");
        if (submitBtn) submitBtn.disabled = false;
        if (btnText) btnText.textContent = "Import & Process";
      }, 1500);

    } catch (err) {
      if (statusBox) {
        statusBox.className = "text-xs p-3 rounded-xl bg-rose-500/20 text-rose-200 border border-rose-500/40 space-y-1";
        statusBox.innerHTML = `
          <div class="font-bold text-rose-300">Import Failed</div>
          <div class="text-[11px]">${err.message}</div>
        `;
      }
      if (submitBtn) submitBtn.disabled = false;
      if (btnText) btnText.textContent = "Import & Process";
    }
  }

  async updateVocabBadge() {
    try {
      const res = await fetch("/api/vocab");
      const data = await res.json();
      const count = data.vocab ? data.vocab.length : 0;
      this.vocabCountBadge.textContent = count;
    } catch (e) {
      console.error(e);
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.app = new App();
});
