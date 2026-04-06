# Project: AI-Powered Concert Band Arranger

## 1. Project Overview
This project aims to build an end-to-end pipeline that takes a raw audio file (MP3/WAV) as input and outputs a professional-grade Concert Band arrangement, including a conductor's score, individual instrument parts, and a high-quality audio mockup.

### Goals:
*   **Separation:** Divide audio into Melody, Bass, and Percussion stems.
*   **Accuracy:** Prioritize readable, musicologically correct sheet music (proper keys, time signatures, and rhythms).
*   **Orchestration:** Intelligently map simple audio stems to a full 15-20 piece concert band.
*   **Accessibility:** Provide a web-based interface for uploading and downloading results.
*   **Packaging:** Deliver a final ZIP containing PDFs and HQ audio.

## 2. Technical Stack
*   **Core Language:** Python 3.10 (Essential for `basic-pitch` and library stability)
*   **Separation:** Meta Demucs (Source Separation)
*   **Transcription:** Spotify Basic Pitch (Audio-to-MIDI)
*   **Music Theory Logic:** Music21 (Symbolic Music Processing)
*   **Engraving/Rendering:** MuseScore CLI (PDF & Audio Generation)
*   **Interface:** Flask (Web Framework) + HTML/CSS

## 3. Phase Plan

### Phase 1: The "Digital Ear" (Core Transcription)
**Goal:** Convert raw audio into clean, quantized MIDI data.
1.  [x] **Audio Pre-processing:** Normalize and format audio for AI models.
2.  [x] **Stem Separation:** Use Demucs to isolate Vocals (Melody), Bass, and Drums.
3.  [x] **Transcription:** Pass stems through Basic Pitch to generate raw MIDI.
4.  [ ] **Quantization & Cleaning:** (Moving to Phase 2 AI Logic)

### Phase 2: The "AI Orchestrator" (Genre Calibration & Notation Engine)
**Goal:** Create clean, highly-readable sheet music using an AI feedback loop trained on specific genre profiles (Pop, Jazz, Classical).
1.  [x] **The "AI Critic" Quality Control Loop:** Evaluate MIDI vs. Audio Ground Truth using Groq LLM.
2.  [ ] **Genre-Specific Calibration:** Train specialized profiles on 25-second clips for different genres (Pop, Jazz/Swing, Classical) to build a library of `models/*.json` presets.
3.  [ ] **Advanced Musical Condensation:** 
    *   **Articulations:** Automatically detect and apply Slurs (legato) and Staccato based on post-quantized note gaps.
    *   **Expressions:** Condense rapid alternating pitches into Trills (`tr`), and rapid repetitions into Vibrato markings.
    *   **Dynamics:** Map raw MIDI velocity (volume) to sheet music dynamic markings (*p*, *mf*, *f*).
    *   **Rhythm:** Permanently allow triplet quantization grids for swing/jazz feel.

### Phase 3: The "Full Ensemble" (Orchestration Engine)
**Goal:** Expand the separated audio stems (Melody, Bass, Harmony, Percussion) into a full Concert Band lineup.
1.  **Instrument Mapping & Stem Distribution:**
    *   *Melody Stem (Vocals):* Duplicated and transposed for the "Front Line": Flute (C, +1 8va), Clarinet (Bb), Trumpet (Bb), Alto Sax (Eb).
    *   *Harmony Stem (Other):* Split into chordal voicings and distributed to the "Middle Voices": F Horns, Trombones, Tenor Sax.
    *   *Bass Stem (Bass):* Transposed for the "Foundation": Tuba (C, -1 8va), Bari Sax (Eb), Euphonium (Bb).
    *   *Percussion Stem (Drums):* Split into Snare Drum, Bass Drum, and Cymbals based on onset velocity/density.
2.  **Transposition Engine:** Handle B♭, E♭, and F transpositions for band instruments automatically during MusicXML generation.
3.  **Smart Range Logic:**
    *   Implement "Auto-Octave" shifting (Completed in Phase 2) to move entire sections up/down an octave to fit instrument sweet spots.
    *   Maintain "Foundation Priority" (ensuring the Tuba remains the lowest voice).

### Phase 4: The "Studio & Interface" (Delivery)
**Goal:** Build the user-facing app and high-quality export system.
1.  **Web Interface:** Create a simple HTML upload portal using Flask.
2.  **HQ Rendering:** Integrate Concert Band SoundFonts into MuseScore for "Realistic" audio exports.
3.  **The Ziperator:** Build logic to generate:
    *   Full Conductor Score (PDF).
    *   Individual Part Folders (PDFs).
    *   HQ Audio Recording (MP3/WAV).
4.  **Final Packaging:** Compress all files into a structured ZIP for the user.

## 4. Testing & Validation Strategy
*   **Reference Testing:** Run known songs with existing sheet music through the system and compare results.
*   **Range Validation:** Scripted checks to ensure no instrument is assigned a note outside its physical capabilities.
*   **Rhythm Stress Test:** Feed the system complex rhythms (triplets/syncopation) to verify quantization accuracy.

## 5. Cost Analysis
*   **Software:** $0 (All tools are Open Source).
*   **Infrastructure:** Potential costs for GPU-accelerated cloud hosting (Optional; can run locally for free).
