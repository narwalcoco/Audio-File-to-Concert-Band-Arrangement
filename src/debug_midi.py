from music21 import converter, chord
import os

def check_midi(file_path):
    print(f"Checking {file_path}...")
    score = converter.parse(file_path)
    all_notes = list(score.flatten().notes)
    
    chords = [n for n in all_notes if isinstance(n, chord.Chord)]
    short_notes = [n for n in all_notes if n.duration.quarterLength < 0.25]
    
    print(f"Total Notes: {len(all_notes)}")
    print(f"Chords Found: {len(chords)}")
    print(f"Short Notes (< 0.25): {len(short_notes)}")
    
    if chords:
        print("Example Chord:")
        print(chords[0])

import sys

if __name__ == "__main__":
    file_to_check = sys.argv[1] if len(sys.argv) > 1 else "output/evolution_gen_1.mid"
    check_midi(file_to_check)
