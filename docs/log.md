# Development Log

## Session: April 1, 2026

### 🛠️ Completed Today
*   **AI Critic Integration:** Successfully connected the **Groq API** (`llama-3.3-70b-versatile`) to evaluate MIDI statistics.
*   **Vibrato De-Jitter Implementation:** Developed a `consolidate_vibrato` algorithm in `src/processor.py` that identifies micro-note clusters and replaces them with clean, sustained notes.
*   **Audio Ground Truth Analysis:** Added a "Musical Fingerprint" extraction step in `src/evolver.py` that provides the AI Critic with the original audio's BPM and onset density.
*   **Clarinet Calibration:** Optimized the entire pipeline for a **B♭ Clarinet**, including range enforcement and automated removal of "notation clutter" (random accents, clef changes, and expressions).
*   **Triple-Version Deployment:** Created a multi-variant output system that generates **Literal**, **Professional**, and **Jazz/Bossa** versions of the transcription for comparison.

### ❌ What Didn't Work (Lessons Learned)
*   **Automated YT Downloads:** `yt-dlp` was consistently blocked by YouTube's "Precondition check failed" security. **Lesson:** Manual download or browser-cookie passing is the only reliable way for now.
*   **Dependency Collisions:** `torchaudio 2.10.0` attempted to use `torchcodec` for basic file saving, which crashed due to missing CUDA libraries (`libnvrtc.so.13`). **Solution:** Downgraded to a stable `torch/torchaudio 2.4.1` suite.
*   **Over-Quantization:** Initial AI feedback favored extreme simplicity (straight 16ths), which destroyed the "swing" feel of Bossa Nova. **Solution:** Added a "Jazz/Bossa" mode and provided the AI with ground truth density to prevent over-simplification.
*   **Mutable Stream Iteration:** Directly modifying `music21` streams while iterating caused skipped notes. **Solution:** Refactored the processor to rebuild the part from scratch in a single pass.

### ⏭️ Next Steps
*   **Phase 2 Calibration:** Continue stress-testing the triple-version output on different genres (Classical vs. Jazz).
*   **MusicXML Analysis:** Explore having the AI Critic "see" the raw MusicXML to identify visual notation errors like overlapping rests or bad beaming.
*   **Phase 3 (Orchestration):** Begin mapping the 1-part melody to a full 15-20 piece Concert Band lineup.

