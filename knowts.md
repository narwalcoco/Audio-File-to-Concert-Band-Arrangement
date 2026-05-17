# The "How-To-Make-A-Music-AI" Guide (High School Edition)

## Date: Saturday, May 9, 2026

### **What are we actually doing?**
Imagine you’re trying to teach a computer to listen to a song (like "As It Was" by Harry Styles) and write down the sheet music for a high school concert band. It sounds simple, but computers are actually pretty bad at listening to vocals because singers slide between notes and use weird effects.

---

### **The Journey So Far**

#### **Step 1: The "Messy Room" Problem (Phase 1)**
When we started, our code was like a messy bedroom. Some tools were too old, some were too new, and they kept fighting each other. We had to downgrade everything to "stable" versions so the computer could finally "listen" to the music without crashing.

#### **Step 2: Training the AI (The "Hot or Cold" Game)**
We used something called a **Genetic Algorithm**.
*   **Analogy:** Imagine you have 10 robots trying to learn to shoot a basketball. You give them all random settings. Nine robots miss, but one hits the rim. You take that "best" robot, make 10 copies of it, but tweak its settings slightly (mutations). 
*   **Result:** Eventually, after 30 or 100 rounds (generations), you have a robot that never misses a shot.

#### **Step 3: The "Rust" Speed Boost**
Python (the language we used first) is like a bicycle. It’s easy to ride but slow. We switched the "Brain" of the project to **Rust**, which is like a Ferrari. 
*   **The Result:** We went from testing 10 robots at a time to testing **10,000 robots at a time.** We ran **1 million tests** in just a few seconds!

#### **Step 4: Subtractive Sculpting (The Block of Marble)**
At first, we tried to find notes starting from silence. It didn't work.
*   **New Plan:** We decided to start with a "Solid Block of Sound" (the AI plays every note possible). Then, we use our Genetic Algorithm to "carve away" the noise until only the melody is left.
*   **Breakthrough:** This took us from a 15% accuracy score to **almost 90%!**

---

### **Big Words We Use (Simplified)**
1.  **Posteriorgram:** A giant "Probability Map." It’s like a weather map that shows where it’s 90% likely to rain. Instead of rain, our map shows where it’s 90% likely a note is playing.
2.  **Monophony:** Only playing one note at a time. No chords allowed!
3.  **Hysteresis (Pitch Lock):** This is like a "Sticky" piano key. Once the AI hits a note, it stays on that note even if the singer's voice wobbles a little bit. It prevents the music from sounding "bumpy."
4.  **16th-Note Grid:** Imagine a piece of graph paper. We force every note to fit perfectly into the little boxes. This makes it way easier for a real human to play on a Trumpet or Flute.

---

### **What’s Next?**
Right now, the AI is a bit "clumsy" when it moves from one note to the next. It "scoops" into the notes like a singer would. We’re currently teaching it to be more like a piano player: hit the note perfectly, let go, and then hit the next one cleanly.
