# Project Notes & Observations

## ⚠️ Issues & Known Limitations
*   **Basic Pitch Transcription:** 
    *   Struggles with **long notes and vibrato**. 
    *   Notes tend to trail off, become weak, shaky, or out of tune towards the end of a phrase.
    *   *Correction Strategy:* Need to implement a logic in Phase 2 to merge "shaky" short notes into a single long note if they are within a certain pitch tolerance.
*   **MuseScore Output Quality:**
    *   Initial PDF output is "messy": poor structure, random symbols, and unreadable rhythms.
    *   *Cause:* Likely due to raw MIDI having too much "resolution" (tiny variations in start/end times) which MuseScore tries to notation literally.
    *   *Goal:* Achieve "Conductor-Ready" clean sheet music through aggressive quantization and symbolic cleaning.

## 🛠️ Environment Checklist
- [x] Python 3.10.19 Installed (Required for `basic-pitch` stability)
- [x] `venv` configured with compatible libraries
- [x] NumPy downgraded to 1.26.4 (Fixed TFLite compatibility)
- [x] `basic-pitch` successfully transcribing audio to MIDI
- [x] `musescore-cli` successfully rendering MIDI to PDF

## 📝 Planned Features (To-Do)
- [ ] Implement Phase 1 Quantization (The "32nd Note Filter").
- [ ] Research "AI Feedback Loop" for quality scoring.
- [ ] Build the Music21 bridge for smarter score mapping.
- [ ] Test instrument transposition for Concert Band.
