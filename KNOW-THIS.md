# HANDOVER DOCUMENT: Chordastrate Project (Presentation Phase)

## **Status Overview**
We have successfully completed **Stage 1: Melodic Extraction** for the "Chordastrate" project. The goal is to turn raw pop audio into professional concert band arrangements.

## **Core Engineering Concepts (Crucial for Accuracy)**
1.  **Surgical Sculpting:** Instead of building a melody from scratch, we start with a "Wall of Sound" (all 16th notes filled) and use a Genetic Algorithm to carve away the noise.
2.  **Rust Evolutionary Engine:** We migrated the training loop from Python to Rust to achieve a **10,000 population size**. We ran over **5 million evaluations** to find the optimal settings.
3.  **The "Magic Numbers":** 
    - **Pitch Shift:** Consistently found to be **-10 semitones** (Concert vs. Written) for vocal-to-brass transcription.
    - **Pitch Lock (Hysteresis):** A 5-to-8 frame stability window used to prevent "scooping" or vocal sliding artifacts.
4.  **Monophony:** The tool is strictly monophonic (one note at a time) to ensure clear, playable melodic lines.

## **Current Task: The Trifold Poster / Website Prototype**
We are creating a **Simulated Prototype** for a science-fair style trifold presentation.

### **The "Simulated Reality" Strategy:**
We are taking the "Big Tech" approach of showing a highly polished, complete vision of the final product, even though some components are still in development. The goal is to present a **perfectly functional user journey** using pre-rendered results.

### **The Presentation Prompt for the next AI:**
> My trifold poster is due soon. I also put a style sheet for our website in the presentation directory. When we make our website, you can use that as reference. But, with that said, I won't be able to finish making this whole project in time. So, we are going to do a fake presentation that shows what it should look like when complete (we will do exactly what big tech companies do all of the time and show what it will be like and not say that it isn't done yet). So, I will define some of the things we will need on the trifold. I want you after to create an html file that creates three sections, each with sections dedicated to specific topics. Sections required: problem being solved, design matrix (I will handle this, just allot a space for this---must be decently big), procedure/materials (let’s also include how we trained/calibrated our tools), data collected, professionals (I will handle this, just allot a decently big space for this), final prototype (summary of final prototype and how it works to solve the problem, explains improvements from previous prototypes, how our thoughts and dreams changed from start to finish, success and challenges, better than Klang.io because it's more focussed towards a target audience leading to better results with more instruments and blending of them, a working vs simulated prototype (explain what my teacher means by this last one)), future work/extension, and large title/logo in the top middle. FYI, try to make the section code easy for me to edit so that I can input my paragraphs for some of them and describe the materials. But, still put down actual stuff before I add my own as I want to see if I forgot to add anything and want to see what you think is most important to have on the trifold. To have a representation of what it looks like (our website), I was thinking that we first use the part from As It Was trimmed-training-audio.wav, but that segment from the actual song. Then, show it in the next step as separated stems and display the separated vocals stem (the trimmed-training-audio.wav). Next, show the “result” of our tools processing it into midi (play our as-it-was-final.midi). Then play all generated parts together (we manually beforehand use the generated midi notes to create four note chords which, each note, gets split into notes for saxophone, flute, trumpet, and clarinet that comprise midi files for each instrument). Lastly, we show the download step where the user can select a generated part (trumpet part, clarinet part, flute part, saxophone part) to view (generated beforehand too using musescore-cli to convert the midi to sheet music with respective transcribed keys and such based on the key of the actual song. These steps will be shown on our example website.

## **Visual Identity (The Style Sheet)**
- **Visual Style:** Futuristic "Neon Dark Mode." 
- **Palette:** Electric Blue (#3AB0FF), Ice Blue, Navy Blue (#101B2F), and Pure Black.
- **Typography:** Orbitron (Titles), Space Grotesk (Headers), Inter (Body).
- **Layout:** Standard Trifold (1.0x Left, 1.6x Center, 1.0x Right).

---
**Permanent Record:** Refer to `notes.md` for the technical history and `knowts.md` for the simplified high-school explanations.
