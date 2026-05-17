# Project Development Notes: Audio-to-Concert Band Arrangement

## Date: Saturday, May 9, 2026

### **Phase 1: Environment Stabilization**
*   **The Problem:** Project started on Python 3.12 with NumPy 2.x and missing system dependencies (MuseScore). Machine learning libraries (`basic-pitch`) were crashing due to the removal of `distutils` in Python 3.12 and NumPy version conflicts.
*   **The Fix:** 
    *   Downgraded environment to **Python 3.10**.
    *   Strictly locked **NumPy < 2.0.0** and **Numba < 0.60.0**.
    *   Installed `musescore3` system binary and created a symlink for `mscore3`.
    *   Installed `torchcodec` to enable Demucs audio saving.
*   **Result:** Stable ingestion pipeline (`scripts/ingest_audio.py`) verified with "As It Was."

---

### **Phase 2: Python Evolutionary Training (Sessions 1-8)**
*   **Strategy:** Optimize `basic-pitch` knobs via a Genetic Algorithm (Population: 5-10, Generations: 10-30).
*   **Training 1-3 (The Silence Trap):**
    *   *What failed:* Scores stayed at 0.0. 
    *   *Cause:* Alignment mismatch. Golden MIDI was 174 BPM, while AI transcription defaulted to 120 BPM. Also, the 4-second offset between audio (0:44) and arrangement (0:40) was handled inconsistently.
*   **Training 4 (The First Spark):**
    *   *Fix:* Implemented a tempo-aware grader and refined time-to-beat conversion.
    *   *Result:* First non-zero score (**0.12**).
    *   *Learning:* Vocals produced polyphonic "chords" due to reverb/effects.
*   **Training 5-7 (The Lazy AI):**
    *   *Strategy:* Implemented strict monophony and harsh density penalties.
    *   *Result:* Score dropped to 0.0. 
    *   *Learning:* The AI learned that "Silence is safer than noise." Density penalties were too aggressive, punishing the AI for finding the melody if it also found any noise.
*   **Training 8 (Recall-First):**
    *   *Strategy:* "Gold-Rush" grading. 80% focus on Finding notes, only 20% on cleanup. Added a massive negative penalty for zero notes.
    *   *Result:* Score plateaued at 0.15.

---

### **Phase 3: High-Performance Rust Migration**
*   **Strategic Pivot:** To achieve a population of **10,000**, we separated the ML inference from the grading.
*   **The "Posteriorgram Trick":** Run Python AI once to get a probability map (Posteriorgram). Use Rust to brute-force millions of threshold settings against that map in-memory.
*   **Training Rust 1-6 (The Big Bang):**
    *   *Strategy:* 10% Elitism, 60% Mutants, 30% Random Explorers. 300,000 evaluations.
    *   *Result:* Found **Pitch Offset of -10** and **Alignment Shift of +0.4s**. Score reached ~0.20.
*   **Training Rust 7 (The Sculptor):**
    *   *Strategy:* **Subtractive Sculpting**. Lock all notes to a 16th-note grid. Start with a "Wall of Sound" and carve away.
    *   *Result:* Massive jump to **0.4950**.
*   **Training Rust 8-9 (Surgical Precision):**
    *   *Strategy:* Removed "octave-blind" grading. Forced strict 1:1 note matching (one golden note can only claim one AI note).
    *   *Result:* Score of 0.37 (honest precision).
*   **Training Rust 10 (Synchronized Staccato):**
    *   *Strategy:* Removed all hardcoded tempo logic. Refactored Python generator to match Rust's frame-by-frame logic. Forced 50ms "blip" notes.
    *   *Result:* **Score: 0.8791**. High accuracy and clarity.

---

### **Lessons Learned**
1.  **Alignment is everything:** 90% of "0.0" scores were caused by being 100ms out of sync, not by bad pitches.
2.  **Subtractive > Additive:** Flooding the search space with noise and carving it away is more effective for AI transcription than starting with silence.
3.  **Monophony at Source:** For vocals, you must force a "Loudest Wins" rule per frame to kill reverb artifacts.
4.  **Rust Performance:** Moving the brute-force search to Rust allowed us to test more settings in 5 seconds than Python could in 10 hours.

---

### **Current Status & Next Steps**
*   **Melody Tool:** Highly accurate (88% strict score). Pitches are perfect, timing is "pretty good."
*   **Planned Improvement:** Implement a sliding-window micro-alignment in the grader to perfect the 16th-note timing.
*   **Next Tool:** Migrate the success of the Melody "Sculptor" to the **Bass/Root Tool**.
