# Note to Self: Project State & Critical Context

## 🧠 Current Thinking (End of Session)
We are pivoting from **"Melodic Accuracy Training"** to **"Visual Readability Training."** We realized that trying to force the AI to match pitches when the training audio and gold standard don't match is a dead end. The new strategy is to make the sheet music look professional first (for a novice player) and worry about the exact notes later.

## ❌ What Didn't Work (Failures & Lessons)
1.  **Groq Rate Limits:** The 50-generation loop hits daily token limits on the free tier quickly. 
2.  **Llama Vision Limitations:** The smaller vision models on Groq struggle with the high-level reasoning needed to translate a "messy measure" into a specific mathematical dial adjustment.
3.  **Gold Standard Mismatch:** We tried comparing Olivia Rodrigo's "drivers license" MIDI to a different pop song's audio. The AI (correctly) gave it a failing grade for pitch, which stalled the training.
4.  **Auto-Octave Height:** The initial C5 (72) target was too high for some parts; we lowered it to C4 (60) for better melodic placement.

## 🛠️ To Be Added / Improved
1.  **OpenAI Integration:** Migrate to GPT-4o for its superior Vision capabilities and higher throughput.
2.  **Source Injection:** The AI Critic needs the **full code of `processor.py`** in its prompt so it understands exactly how to turn the "dials."
3.  **Novice Persona:** Refine the prompt to focus on a 12-year-old student player (simplicity over complexity).

## ⏭️ Done Next
- Initialize the OpenAI API client in `src/critic.py`.
- Run the first "Visual Polish" loop (Max 20 generations).
- Save the successful visual parameters to `models/pop_profile.json`.
