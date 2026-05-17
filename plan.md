# Audio to Concert Band Arrangement: Project Roadmap

## Phase 1: Foundation & Pipeline Infrastructure
*   **Step 1.1:** Environment Setup (Demucs, Basic-Pitch, Music21).
*   **Step 1.2:** **Ingestion Script**: 
    *   Input: `.mp3` or `.wav`.
    *   Process: Run Demucs (4 stems) -> Run Transcription (Basic-Pitch + Librosa/Crepe).
    *   Output: 4 Raw MIDI files.
*   **Step 1.3:** **MIDI Utility Wrapper**: Helper functions for `music21` (transpose, range-check, quantization).

## Phase 2: Core Tool Development ("Good Music" Scripts)
*   **Step 2.1: Melody Tool**: Rhythmic cleanup, noise/ghost note removal.
*   **Step 2.2: Bass & Root Tool**: Harmonic root identification from bass stem.
*   **Step 2.3: Harmony Tool**: Chordal accompaniment generation using roots and "Other" stem.
*   **Step 2.4: Fluency Tool**: Orchestration brain. Handles instrument hand-offs and range enforcement via `config/instruments.json`.

## Phase 3: Evolutionary Tuning Framework ("The Trainer")
*   **Step 3.1: The Grader**: Scoring script comparing Processed MIDI vs. Golden MIDI.
    *   Metrics: Pitch accuracy, Rhythmic alignment, Note density.
*   **Step 3.2: The Iteration Loop**: Manages 10 generations of parameter mutation.
    *   Finds "Golden Settings" for the pop genre.

## Phase 4: Scoring & Arrangement
*   **Step 4.1: Sheet Music Templates**: MuseScore templates for concert band.
*   **Step 4.2: Automated Engraving**: Pouring processed MIDI into templates via `music21`.
*   **Step 4.3: Part Extraction**: Export Conductor Score and individual instrument PDFs.

## Phase 5: Packaging & Web Preparation
*   **Step 5.1: Zip & Export**: Organizational script for `Song_Name_Arrangement` folder structure.
*   **Step 5.2: WASM/PyScript Conversion**: Porting Python logic to run locally in-browser.

---
*Last Updated: 2026-05-01*
