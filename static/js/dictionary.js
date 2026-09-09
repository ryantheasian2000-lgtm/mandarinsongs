/**
 * Dictionary & Word Inspection Module
 * Manages the floating pop-up card, pronunciation audio, vocab saving, and Gemini AI deep dive.
 */

class DictionaryManager {
  constructor() {
    this.popup = document.getElementById("dictPopup");
    this.hanziEl = document.getElementById("dictHanzi");
    this.tradEl = document.getElementById("dictTraditional");
    this.pinyinEl = document.getElementById("dictPinyin");
    this.hskBadge = document.getElementById("dictHskBadge");
    this.translationEl = document.getElementById("dictTranslation");
    this.audioBtn = document.getElementById("dictAudioBtn");
    this.saveBtn = document.getElementById("btnSaveToVocab");
    this.saveBtnText = document.getElementById("saveVocabBtnText");
    this.explainBtn = document.getElementById("btnGeminiExplain");
    this.closeBtn = document.getElementById("closeDictBtn");

    this.currentWordData = null;
    this.currentLineContext = "";

    this.initEvents();
  }

  initEvents() {
    if (this.closeBtn) {
      this.closeBtn.addEventListener("click", () => this.hide());
    }

    if (this.audioBtn) {
      this.audioBtn.addEventListener("click", () => {
        if (this.currentWordData && this.currentWordData.hanzi) {
          this.speakMandarin(this.currentWordData.hanzi);
        }
      });
    }

    if (this.saveBtn) {
      this.saveBtn.addEventListener("click", () => this.saveCurrentWord());
    }

    if (this.explainBtn) {
      this.explainBtn.addEventListener("click", () => this.openAiDeepDive());
    }

    // Close popup on clicking outside
    document.addEventListener("click", (e) => {
      if (
        this.popup &&
        !this.popup.classList.contains("hidden") &&
        !this.popup.contains(e.target) &&
        !e.target.closest(".word-chip")
      ) {
        this.hide();
      }
    });
  }

  show(wordData, lineContext, triggerElement) {
    this.currentWordData = wordData;
    this.currentLineContext = lineContext;

    this.hanziEl.textContent = wordData.hanzi;
    this.tradEl.textContent = wordData.traditional ? `繁: ${wordData.traditional}` : "";
    this.pinyinEl.textContent = wordData.pinyin || "";
    
    // Tone class
    const tone = wordData.tone || 1;
    this.pinyinEl.className = `text-base font-semibold tone-${tone}`;
    if (wordData.pos === "english" || wordData.pos === "number") {
      this.tradEl.textContent = "";
      this.pinyinEl.textContent = wordData.hanzi || "";
      this.pinyinEl.className = "text-base font-semibold text-slate-300";
      this.hskBadge.textContent = wordData.pos === "english" ? "English" : "Number";
      this.hskBadge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-700 text-slate-300";
      this.translationEl.textContent = wordData.pos === "english" ? "English word in lyrics" : "Numeral";
    } else {
      this.tradEl.textContent = wordData.traditional ? `繁: ${wordData.traditional}` : "";
      this.pinyinEl.textContent = wordData.pinyin || "";
      const tone = wordData.tone || 1;
      this.pinyinEl.className = `text-base font-semibold tone-${tone}`;
      const hsk = wordData.hsk || 1;
      this.hskBadge.textContent = `HSK ${hsk}`;
      this.hskBadge.className = `text-[10px] font-semibold px-2 py-0.5 rounded-full tone-bg-${tone}`;
      this.translationEl.textContent = wordData.translation || "Meaning unavailable";
    }

    // HSK Badge
    const hsk = wordData.hsk || 1;
    this.hskBadge.textContent = `HSK ${hsk}`;
    this.hskBadge.className = `text-[10px] font-semibold px-2 py-0.5 rounded-full tone-bg-${tone}`;

    // Translation
    this.translationEl.textContent = wordData.translation || "Meaning unavailable";

    this.saveBtnText.textContent = "Save to Vocab";

    // Position popup next to trigger element
    this.positionPopup(triggerElement);
    this.popup.classList.remove("hidden");
    
    if (window.lucide) {
      lucide.createIcons();
    }
  }

  positionPopup(triggerElement) {
    if (!triggerElement) return;
    const rect = triggerElement.getBoundingClientRect();
    const popupWidth = 320;
    const popupHeight = 220;

    let left = rect.left + window.scrollX;
    let top = rect.bottom + window.scrollY + 8;

    // Boundary checks
    if (left + popupWidth > window.innerWidth - 16) {
      left = window.innerWidth - popupWidth - 16;
    }
    if (left < 16) left = 16;

    if (top + popupHeight > window.innerHeight - 16) {
      top = rect.top + window.scrollY - popupHeight - 8;
    }

    this.popup.style.left = `${left}px`;
    this.popup.style.top = `${top}px`;
  }

  hide() {
    if (this.popup) {
      this.popup.classList.add("hidden");
    }
  }

  speakMandarin(text) {
    if (!("speechSynthesis" in window)) {
      alert("Speech synthesis not supported in this browser.");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "zh-CN";
    utterance.rate = 0.85; // Slightly slower for language learners

    // Try finding standard Chinese voice
    const voices = window.speechSynthesis.getVoices();
    const zhVoice = voices.find(v => v.lang.startsWith("zh") || v.lang.includes("cmn"));
    if (zhVoice) {
      utterance.voice = zhVoice;
    }

    window.speechSynthesis.speak(utterance);
  }

  async saveCurrentWord() {
    if (!this.currentWordData) return;
    try {
      this.saveBtnText.textContent = "Saving...";
      const currentSong = window.karaokePlayer ? window.karaokePlayer.currentSong : null;
      const res = await fetch("/api/vocab", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hanzi: this.currentWordData.hanzi,
          traditional: this.currentWordData.traditional || this.currentWordData.hanzi,
          pinyin: this.currentWordData.pinyin,
          tone: this.currentWordData.tone || 1,
          translation: this.currentWordData.translation,
          hsk: this.currentWordData.hsk || 1,
          songTitle: currentSong ? currentSong.title : "",
          lineContext: this.currentLineContext
        })
      });
      const data = await res.json();
      this.saveBtnText.textContent = "Saved!";
      if (window.app) {
        window.app.updateVocabBadge();
      }
    } catch (e) {
      console.error(e);
      this.saveBtnText.textContent = "Error saving";
    }
  }

  async openAiDeepDive() {
    if (!this.currentWordData) return;
    const aiModal = document.getElementById("aiModal");
    const aiBody = document.getElementById("aiModalBody");
    const aiSubtitle = document.getElementById("aiModalSubtitle");

    aiSubtitle.textContent = `Analyzing "${this.currentWordData.hanzi}" in song context...`;
    aiBody.innerHTML = `
      <div class="text-center py-10 text-slate-400">
        <i data-lucide="loader-2" class="w-8 h-8 mx-auto animate-spin text-rose-500 mb-2"></i>
        <p>Consulting Gemini AI Tutor for phrase nuance & grammar breakdown...</p>
      </div>
    `;
    aiModal.classList.remove("hidden");
    if (window.lucide) lucide.createIcons();

    const apiKey = localStorage.getItem("huayu_gemini_api_key") || "";
    const currentSong = window.karaokePlayer ? window.karaokePlayer.currentSong : null;

    try {
      const res = await fetch("/api/explain-phrase", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phrase: this.currentWordData.hanzi,
          lineContext: this.currentLineContext,
          songTitle: currentSong ? currentSong.title : "",
          apiKey: apiKey
        })
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      aiBody.innerHTML = `
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 rounded-xl bg-slate-800/80 border border-slate-700">
            <div>
              <span class="text-2xl font-bold text-white">${data.phrase}</span>
              <span class="ml-2 text-base font-semibold text-amber-300">${data.pinyin || ""}</span>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-300 font-semibold border border-rose-500/30">${data.hskLevel || "HSK Vocab"}</span>
          </div>

          <div class="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-1">
            <h4 class="text-slate-400 uppercase tracking-wider font-semibold text-[11px]">Literal vs Song Meaning</h4>
            <p class="text-slate-200"><b class="text-slate-400">Literal:</b> ${data.literalMeaning || "N/A"}</p>
            <p class="text-slate-100 font-medium"><b class="text-slate-400">Song Context:</b> ${data.contextualMeaning || "N/A"}</p>
          </div>

          ${data.grammarNote ? `
          <div class="p-3 rounded-xl bg-indigo-950/30 border border-indigo-500/30 space-y-1">
            <h4 class="text-indigo-400 uppercase tracking-wider font-semibold text-[11px]">Grammar & Usage Pattern</h4>
            <p class="text-indigo-200">${data.grammarNote}</p>
          </div>` : ""}

          ${data.culturalNote ? `
          <div class="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-1">
            <h4 class="text-amber-400 uppercase tracking-wider font-semibold text-[11px]">Cultural & Poetic Background</h4>
            <p class="text-amber-200/90">${data.culturalNote}</p>
          </div>` : ""}

          ${data.exampleSentence ? `
          <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700 space-y-1.5">
            <h4 class="text-slate-400 uppercase tracking-wider font-semibold text-[11px]">Practice Example Sentence</h4>
            <p class="text-white font-medium text-sm">${data.exampleSentence.hanzi}</p>
            <p class="text-amber-300 font-mono text-xs">${data.exampleSentence.pinyin}</p>
            <p class="text-slate-300 italic text-xs">${data.exampleSentence.english}</p>
          </div>` : ""}
        </div>
      `;
    } catch (err) {
      aiBody.innerHTML = `
        <div class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-center space-y-2">
          <p class="font-bold">Could not fetch AI explanation</p>
          <p class="text-xs text-rose-400">${err.message}</p>
          <p class="text-xs text-slate-400">Ensure your Gemini API Key is configured in Settings.</p>
        </div>
      `;
    }
  }
}

window.dictionaryManager = new DictionaryManager();
