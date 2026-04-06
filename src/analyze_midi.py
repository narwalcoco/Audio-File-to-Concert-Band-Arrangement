from music21 import converter, note
import os

def analyze_midi(file_path):
    print(f"Analyzing MIDI: {file_path}")
    score = converter.parse(file_path)
    durations = []
    
    for p in score.parts:
        for n in p.recurse().getElementsByClass(['Note']):
            durations.append(n.duration.quarterLength)
    
    if durations:
        print(f"Total Notes: {len(durations)}")
        print(f"Min Duration (Quarter Length): {min(durations)}")
        print(f"Max Duration (Quarter Length): {max(durations)}")
        # Count notes shorter than a 16th note (0.25)
        very_short = [d for d in durations if d < 0.25]
        print(f"Notes < 16th note (0.25): {len(very_short)}")
        
        # Count notes shorter than an 8th note (0.5)
        short_8th = [d for d in durations if d < 0.5]
        print(f"Notes < 8th note (0.5): {len(short_8th)}")
    else:
        print("No notes found.")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "test_output/vocals_transcription.mid"
    if os.path.exists(target):
        analyze_midi(target)
    else:
        print(f"Error: {target} not found.")
