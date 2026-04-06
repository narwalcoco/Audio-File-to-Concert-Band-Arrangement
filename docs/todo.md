# To-Do List

## 🎯 Immediate Priority: Phase 2 Calibration (IN PROGRESS)
- [x] **Design "AI Critic" Scoring Logic:**
    - [x] Integrate Groq API (Llama 3.3 70B).
    - [x] Extract MIDI stats and compare to Ground Truth audio.
- [x] **Implement Surgical De-Jittering:**
    - [x] Create vibrato-merging logic in `processor.py`.
    - [x] Enforce strict monophony and range limits.
- [ ] **Advanced Notation Upgrades (processor.py):**
    - [ ] Update `.quantize()` to permanently allow Triplet grids.
    - [ ] Add a "Condensation Pass" for Trills (rapid alternating pitches).
    - [ ] Add an "Articulation Pass" for Slurs (small gaps) and Staccato (short duration + rest).
    - [ ] Add a "Dynamics Pass" to map MIDI velocity to *p*, *mf*, *f*.
- [ ] **AI Critic Upgrade:**
    - [ ] Inject Python source code for `grid_size`, `min_note_duration`, `merge_proximity` into the prompt.
    - [ ] Add `music21` measure-by-measure "Rhythm Map" to the prompt so the AI can "read" the score.
- [ ] **Genre Model Training:**
    - [ ] Set up `pop_training/`, `classical_training/`, `jazz_training/` with 25-second audio clips.
    - [ ] Run the `evolver.py` to generate and save winning parameters to `models/<genre>_profile.json`.

## 🎻 MuseScore Optimization
- [x] Suppress "random symbols" via `Expression` stripping in processor.
- [x] Automatically set the correct instrument part in the MIDI.
- [ ] Implement auto-layout for a cleaner conductor view.

## 🎻 Phase 3: Orchestration Engine (NEXT)
- [ ] Define the instrument mappings (Melody/Bass/Harmony).
- [ ] Create the Transposition Engine for B♭, E♭, and F instruments.
- [ ] Implement "Phrase-shifting" (Octave adjustments).
