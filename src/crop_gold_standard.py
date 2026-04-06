from music21 import converter, stream
import os

def crop_and_extract_melody(input_path, output_path, part_name="B♭ Trumpet 1", end_beat=60):
    """Crops a MIDI and extracts a specific instrument's part."""
    print(f"✂️ Extracting {part_name} from {input_path} and cropping to {end_beat} beats...")
    score = converter.parse(input_path)
    new_score = stream.Score()
    
    found = False
    for p in score.parts:
        if p.partName == part_name:
            print(f"✅ Found {part_name}. Cropping...")
            new_part = p.getElementsByOffset(0, end_beat, includeEndBoundary=True, mustBeginInSpan=True).stream()
            new_score.insert(0, new_part)
            found = True
            break
            
    if not found:
        print(f"❌ Could not find part: {part_name}. Using first part instead.")
        new_part = score.parts[0].getElementsByOffset(0, end_beat, includeEndBoundary=True, mustBeginInSpan=True).stream()
        new_score.insert(0, new_part)

    new_score.write('midi', fp=output_path)
    print(f"💾 Saved melodic reference to {output_path}")

if __name__ == "__main__":
    input_file = "pop_training/examples/drivers-licence-olivia-rodrigo-arr-jakub-burda.mid"
    output_file = "pop_training/examples/gold_standard_cropped.mid"
    if os.path.exists(input_file):
        crop_and_extract_melody(input_file, output_file, part_name="B♭ Trumpet 1", end_beat=60)
