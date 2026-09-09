/**
 * Vocabulary Flashcard Review & Lyric Fill-in-the-Blank Quiz Mode
 */

class QuizManager {
  constructor() {
    this.vocabModal = document.getElementById("vocabModal");
    this.vocabListContainer = document.getElementById("vocabListView");
    this.flashcardView = document.getElementById("flashcardView");
    this.flashcardCard = document.getElementById("flashcardCard");
    this.flashcardHanzi = document.getElementById("flashcardHanzi");
    this.flashcardPinyin = document.getElementById("flashcardPinyin");
    this.flashcardTranslation = document.getElementById("flashcardTranslation");
    this.flashcardCounter = document.getElementById("flashcardCounter");
    this.btnPrevCard = document.getElementById("btnPrevCard");
    this.btnNextCard = document.getElementById("btnNextCard");
    this.btnStartFlashcards = document.getElementById("btnStartFlashcards");
    this.btnExitFlashcards = document.getElementById("btnExitFlashcards");

    this.quizModal = document.getElementById("quizModal");
    this.quizContainer = document.getElementById("quizContainer");

    this.savedVocab = [];
    this.currentCardIndex = 0;
    this.cardFlipped = false;

    this.quizQuestions = [];
    this.currentQuizIdx = 0;
    this.quizScore = 0;

    this.initEvents();
  }

  initEvents() {
    // Open Vocab Modal
    const btnVocab = document.getElementById("btnVocabModal");
    if (btnVocab) {
      btnVocab.addEventListener("click", () => this.openVocabModal());
    }

    // Open Quiz Modal
    const btnQuiz = document.getElementById("btnQuizModal");
    if (btnQuiz) {
      btnQuiz.addEventListener("click", () => this.openQuizModal());
    }

    // Flashcard interactions
    if (this.btnStartFlashcards) {
      this.btnStartFlashcards.addEventListener("click", () => this.startFlashcards());
    }
    if (this.btnExitFlashcards) {
      this.btnExitFlashcards.addEventListener("click", () => this.exitFlashcards());
    }
    if (this.flashcardCard) {
      this.flashcardCard.addEventListener("click", () => this.flipFlashcard());
    }
    if (this.btnPrevCard) {
      this.btnPrevCard.addEventListener("click", () => this.prevCard());
    }
    if (this.btnNextCard) {
      this.btnNextCard.addEventListener("click", () => this.nextCard());
    }
  }

  async openVocabModal() {
    await this.fetchVocab();
    this.exitFlashcards();
    this.vocabModal.classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
  }

  async fetchVocab() {
    try {
      const res = await fetch("/api/vocab");
      const data = await res.json();
      this.savedVocab = data.vocab || [];
      this.renderVocabList();
    } catch (e) {
      console.error(e);
    }
  }

  renderVocabList() {
    if (this.savedVocab.length === 0) {
      this.vocabListContainer.innerHTML = `
        <div class="text-center py-12 text-slate-500">
          <i data-lucide="bookmark" class="w-10 h-10 mx-auto mb-2 opacity-30"></i>
          <p class="font-medium">No saved words yet.</p>
          <p class="text-xs text-slate-600 mt-1">Click any word chip in song lyrics and select "Save to Vocab"!</p>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    let html = "";
    this.savedVocab.forEach((item) => {
      const tone = item.tone || 1;
      html += `
        <div class="p-3 rounded-xl bg-slate-800/70 border border-slate-700/80 flex items-center justify-between gap-3 hover:border-slate-600 transition">
          <div class="flex items-center gap-3">
            <button class="vocab-audio-btn p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-400 transition" title="Pronounce" onclick="window.dictionaryManager.speakMandarin('${item.hanzi}')">
              <i data-lucide="volume-2" class="w-4 h-4"></i>
            </button>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xl font-bold text-white">${item.hanzi}</span>
                <span class="text-xs font-semibold tone-${tone}">${item.pinyin || ""}</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded tone-bg-${tone}">HSK ${item.hsk || 1}</span>
              </div>
              <div class="text-xs text-slate-300 font-medium mt-0.5">${item.translation || ""}</div>
              ${item.lineContext ? `<div class="text-[11px] text-slate-500 italic mt-0.5 truncate max-w-sm">"${item.lineContext}"</div>` : ""}
            </div>
          </div>

          <button class="p-2 text-slate-500 hover:text-rose-400 transition" title="Remove" onclick="window.quizManager.deleteVocab('${item.id}')">
            <i data-lucide="trash-2" class="w-4 h-4"></i>
          </button>
        </div>
      `;
    });

    this.vocabListContainer.innerHTML = html;
    if (window.lucide) lucide.createIcons();
  }

  async deleteVocab(wordId) {
    try {
      const res = await fetch(`/api/vocab/${wordId}`, { method: "DELETE" });
      const data = await res.json();
      this.savedVocab = data.vocab || [];
      this.renderVocabList();
      if (window.app) window.app.updateVocabBadge();
    } catch (e) {
      console.error(e);
    }
  }

  startFlashcards() {
    if (this.savedVocab.length === 0) {
      alert("Save at least 1 word to start flashcard review.");
      return;
    }
    this.currentCardIndex = 0;
    this.cardFlipped = false;
    this.vocabListContainer.classList.add("hidden");
    this.flashcardView.classList.remove("hidden");
    this.showCurrentCard();
  }

  exitFlashcards() {
    this.flashcardView.classList.add("hidden");
    this.vocabListContainer.classList.remove("hidden");
  }

  showCurrentCard() {
    const item = this.savedVocab[this.currentCardIndex];
    if (!item) return;

    this.cardFlipped = false;
    this.flashcardHanzi.textContent = item.hanzi;
    this.flashcardPinyin.textContent = item.pinyin || "";
    this.flashcardTranslation.textContent = item.translation || "";
    this.flashcardTranslation.classList.add("hidden");
    this.flashcardCounter.textContent = `${this.currentCardIndex + 1} / ${this.savedVocab.length}`;
    
    // Auto speak
    window.dictionaryManager.speakMandarin(item.hanzi);
  }

  flipFlashcard() {
    this.cardFlipped = !this.cardFlipped;
    if (this.cardFlipped) {
      this.flashcardTranslation.classList.remove("hidden");
    } else {
      this.flashcardTranslation.classList.add("hidden");
    }
  }

  prevCard() {
    if (this.currentCardIndex > 0) {
      this.currentCardIndex--;
      this.showCurrentCard();
    }
  }

  nextCard() {
    if (this.currentCardIndex < this.savedVocab.length - 1) {
      this.currentCardIndex++;
      this.showCurrentCard();
    }
  }

  // LYRIC FILL-IN-THE-BLANK QUIZ
  openQuizModal() {
    const player = window.karaokePlayer;
    if (!player || !player.currentSong || !player.currentSong.lines || player.currentSong.lines.length < 2) {
      alert("Please load a song with at least 2 lyric lines to play the quiz.");
      return;
    }

    this.generateQuizQuestions(player.currentSong);
    this.currentQuizIdx = 0;
    this.quizScore = 0;
    this.renderCurrentQuestion();
    this.quizModal.classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
  }

  generateQuizQuestions(song) {
    const questions = [];
    const lines = song.lines;

    lines.forEach((line) => {
      if (line.words && line.words.length >= 2) {
        // Pick a non-punctuation word to blank out
        const candidates = line.words.filter(w => !w.isPunctuation && w.hanzi.length >= 1);
        if (candidates.length > 0) {
          const targetWord = candidates[Math.floor(Math.random() * candidates.length)];
          
          // Generate 3 distractors
          const distractors = ["爱", "看", "想", "月亮", "我们", "吻", "打动", "心", "精彩", "幸福", "女孩", "等待"]
            .filter(d => d !== targetWord.hanzi)
            .sort(() => 0.5 - Math.random())
            .slice(0, 3);
          
          const options = [targetWord.hanzi, ...distractors].sort(() => 0.5 - Math.random());

          questions.push({
            lineId: line.id,
            startTime: line.startTime,
            endTime: line.endTime,
            fullHanzi: line.hanzi,
            english: line.english,
            targetWord: targetWord.hanzi,
            blankedHanzi: line.hanzi.replace(targetWord.hanzi, " [ ___ ] "),
            options: options
          });
        }
      }
    });

    this.quizQuestions = questions.sort(() => 0.5 - Math.random()).slice(0, 5); // 5 questions
  }

  renderCurrentQuestion() {
    if (this.currentQuizIdx >= this.quizQuestions.length) {
      this.renderQuizResults();
      return;
    }

    const q = this.quizQuestions[this.currentQuizIdx];
    this.quizContainer.innerHTML = `
      <div class="space-y-4">
        <div class="flex items-center justify-between text-xs text-slate-400">
          <span>Question ${this.currentQuizIdx + 1} of ${this.quizQuestions.length}</span>
          <span class="font-bold text-amber-400">Score: ${this.quizScore}</span>
        </div>

        <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 text-center space-y-3">
          <div class="text-xs text-slate-400 italic">"${q.english}"</div>
          <div class="text-2xl font-bold text-white tracking-widest">${q.blankedHanzi}</div>
          <button id="btnPlaySnippet" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 rounded-lg text-xs font-semibold transition">
            <i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i>
            <span>Play Audio Snippet</span>
          </button>
        </div>

        <div class="grid grid-cols-2 gap-2.5">
          ${q.options.map(opt => `
            <button class="quiz-opt-btn p-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-rose-500 font-bold text-lg text-white transition" data-val="${opt}">
              ${opt}
            </button>
          `).join("")}
        </div>

        <div id="quizFeedback" class="hidden text-xs p-3 rounded-xl font-medium text-center"></div>
      </div>
    `;

    if (window.lucide) lucide.createIcons();

    // Snippet button
    document.getElementById("btnPlaySnippet").addEventListener("click", () => {
      const audio = window.karaokePlayer.audio;
      audio.currentTime = q.startTime;
      audio.play();
      setTimeout(() => {
        audio.pause();
      }, Math.max(1500, (q.endTime - q.startTime) * 1000));
    });

    // Option buttons
    this.quizContainer.querySelectorAll(".quiz-opt-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const chosen = btn.dataset.val;
        this.checkAnswer(chosen, q.targetWord, btn);
      });
    });
  }

  checkAnswer(chosen, correct, targetBtn) {
    const feedback = document.getElementById("quizFeedback");
    const buttons = this.quizContainer.querySelectorAll(".quiz-opt-btn");
    buttons.forEach(b => b.disabled = true);

    if (chosen === correct) {
      this.quizScore++;
      targetBtn.classList.add("bg-emerald-600/40", "border-emerald-500", "text-emerald-200");
      feedback.className = "text-xs p-3 rounded-xl font-semibold text-center bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
      feedback.textContent = `Correct! "${correct}" is the missing word!`;
    } else {
      targetBtn.classList.add("bg-rose-600/40", "border-rose-500", "text-rose-200");
      buttons.forEach(b => {
        if (b.dataset.val === correct) {
          b.classList.add("bg-emerald-600/30", "border-emerald-500", "text-emerald-200");
        }
      });
      feedback.className = "text-xs p-3 rounded-xl font-semibold text-center bg-rose-500/20 text-rose-300 border border-rose-500/30";
      feedback.textContent = `Incorrect. The correct answer was "${correct}".`;
    }
    feedback.classList.remove("hidden");

    setTimeout(() => {
      this.currentQuizIdx++;
      this.renderCurrentQuestion();
    }, 1800);
  }

  renderQuizResults() {
    this.quizContainer.innerHTML = `
      <div class="text-center py-6 space-y-4">
        <div class="w-16 h-16 rounded-full bg-gradient-to-tr from-indigo-500 to-rose-500 mx-auto flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-indigo-500/30">
          ${this.quizScore}/${this.quizQuestions.length}
        </div>
        <h4 class="text-xl font-bold text-white">Quiz Completed!</h4>
        <p class="text-xs text-slate-400">Great practice! Keep listening and singing along to improve your Mandarin recall.</p>
        <button onclick="window.quizManager.openQuizModal()" class="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-xs transition">
          Play Again
        </button>
      </div>
    `;
  }
}

window.quizManager = new QuizManager();
