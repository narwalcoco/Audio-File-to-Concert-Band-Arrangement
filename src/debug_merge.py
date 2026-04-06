from music21 import converter, note
import os

def debug_merge_logic(input_path):
    print(f"Debugging Merge Logic on: {input_path}")
    score = converter.parse(input_path)
    for p in score.parts:
        all_notes = list(p.recurse().getElementsByClass(note.Note))
        print(f"Total notes in part: {len(all_notes)}")
        
        for i in range(len(all_notes) - 1):
            n1 = all_notes[i]
            n2 = all_notes[i+1]
            gap = n2.offset - (n1.offset + n1.duration.quarterLength)
            is_same_pitch = n1.pitch == n2.pitch
            is_touching = gap < 0.05
            is_jitter = n1.duration.quarterLength < 0.2
            
            if i < 10: # Just look at first 10
                print(f"Note {i} vs {i+1}: SamePitch={is_same_pitch}, Gap={gap:.4f}, Touching={is_touching}, Jitter={is_jitter}")

if __name__ == "__main__":
    debug_merge_logic("output/vocals_transcription.mid")
