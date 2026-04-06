from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import os

audio_path = "separated/htdemucs_ft/laufey_test/vocals.wav"
output_dir = "test_output"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Running inference on {audio_path}...")
try:
    # basic-pitch predict handles the whole pipeline
    model_output, midi_data, note_events = predict(audio_path)
    
    # Save the MIDI file
    midi_path = os.path.join(output_dir, "vocals_transcription.mid")
    midi_data.write(midi_path)
    print(f"✅ Success! MIDI saved to {midi_path}")
    print(f"Number of notes detected: {len(note_events)}")
except Exception as e:
    print(f"❌ Error during inference: {e}")
