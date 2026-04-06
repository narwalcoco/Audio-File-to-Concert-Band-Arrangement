from music21 import converter, note, chord, stream
import os

def simple_clean_midi(input_path, output_path):
    print(f"Applying 3-Step Cleanup to: {input_path}")
    
    # Load the original transcription
    score = converter.parse(input_path)
    
    # 1. THE FLOOR FILTER & BUILT-IN QUANTIZE
    # We iterate through each part (usually just one from basic-pitch)
    for p in score.parts:
        # Step A: Snap to 16th note grid using music21's robust built-in tool
        # This handles the complex 'offset' math for us
        p.quantize([0.25], processOffsets=True, processDurations=True, inPlace=True)
        
        # Step B: Filter out the "jitter" (notes shorter than a 16th note)
        # We do this AFTER quantizing so that notes that were meant to be 16ths are safe
        notes_to_remove = []
        for n in p.recurse().notes:
            if n.duration.quarterLength < 0.25:
                notes_to_remove.append(n)
        
        print(f"Filtered out {len(notes_to_remove)} jitter notes.")
        for n in notes_to_remove:
            p.remove(n, recurse=True)

    # 3. CLEAN RECONSTRUCTION
    # We'll write this to a new MIDI file
    score.write('midi', fp=output_path)
    print(f"✅ Success! Cleaned MIDI saved to {output_path}")

if __name__ == "__main__":
    input_file = "output/vocals_transcription.mid"
    output_file = "output/vocals_quantized.mid"
    
    if os.path.exists(input_file):
        simple_clean_midi(input_file, output_file)
    else:
        print(f"Error: {input_file} not found.")
