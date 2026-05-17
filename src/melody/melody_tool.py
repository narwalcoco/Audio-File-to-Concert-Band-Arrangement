import sys
import os
from pathlib import Path
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from music21 import note, chord, stream, midi
from scripts.midi_utils import save_midi, quantize_stream

def detect_key(audio_path):
    """
    Analyzes the full audio file and returns the detected key.
    Uses Librosa's chromagram features to find the tonal center.
    """
    import librosa
    import numpy as np
    
    y, sr = librosa.load(audio_path)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_avg = np.mean(chroma, axis=1)
    
    # Standard key profiles (Krumhansl-Schmuckler)
    # 0:C, 1:C#, 2:D, etc.
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    best_key_idx = np.argmax(chroma_avg)
    return keys[best_key_idx]

def process_melody(input_audio_path, output_midi_path, settings):
    """
    Surgical Melody Processor: Matches the Rust Trainer's frame-by-frame logic.
    """
    from basic_pitch.inference import predict
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from music21 import stream, note, midi
    import numpy as np

    # 1. Run AI Inference
    model_output, _, _ = predict(
        input_audio_path,
        model_or_model_path=ICASSP_2022_MODEL_PATH,
    )
    
    onsets = model_output['onset']
    notes = model_output['note']
    fps = 22050 / 256 # basic-pitch standard
    
    # 2. Frame-by-Frame 'Legato' Selection
    s = stream.Part()
    fps = 22050 / 256
    bps = 174 / 60
    max_whole_note = 4.0 / bps # in seconds

    # MIDI limits from settings
    min_p = settings.get('min_midi', 21)
    max_p = settings.get('max_midi', 108)
    
    current_note = None
    
    for f in range(len(notes)):
        time = f / fps
            
        frame_notes = notes[f]
        best_pitch_idx = np.argmax(frame_notes)
        pitch = best_pitch_idx + 21
        
        if pitch < min_p or pitch > max_p:
            if current_note:
                s.insert(current_note['start'] * bps, current_note['obj'])
                current_note = None
            continue
            
        if notes[f][best_pitch_idx] > settings.get('frame_threshold', 0.5):
            onset_val = onsets[f][best_pitch_idx]
            
            if current_note:
                # PITCH LOCK (Hysteresis): Stick to current pitch unless new pitch is significantly stronger
                current_p_val = notes[f][current_note['pitch'] - 21]
                
                if (current_note['pitch'] == pitch or current_p_val > (frame_notes[best_pitch_idx] * 0.7)) and current_note['duration'] < max_whole_note:
                    # Continue existing note (either same pitch or locked)
                    current_note['duration'] += 1.0 / fps
                    current_note['obj'].duration.quarterLength = current_note['duration'] * bps
                else:
                    # End old, maybe start new if clear onset
                    s.insert(current_note['start'] * bps, current_note['obj'])
                    current_note = None
                    if onset_val > settings.get('onset_threshold', 0.5):
                        n = note.Note(pitch)
                        n.duration.quarterLength = (1.0 / fps) * bps
                        current_note = {'pitch': pitch, 'start': time, 'duration': 1.0/fps, 'obj': n}
            elif onset_val > settings.get('onset_threshold', 0.5):
                n = note.Note(pitch)
                n.duration.quarterLength = (1.0 / fps) * bps
                current_note = {'pitch': pitch, 'start': time, 'duration': 1.0/fps, 'obj': n}
        elif current_note:
            s.insert(current_note['start'] * bps, current_note['obj'])
            current_note = None
            
    if current_note:
        s.insert(current_note['start'] * bps, current_note['obj'])

    # 3. Save
    from scripts.midi_utils import save_midi
    save_midi(s, output_midi_path)
    return output_midi_path


if __name__ == "__main__":
    # Test with default settings
    test_settings = {
        'min_velocity': 30,
        'min_duration': 0.1,
        'quantization': 0.25,
        'monophonic': True
    }
    # Usage: python3 melody_tool.py input.mid output.mid
    if len(sys.argv) > 2:
        process_melody(sys.argv[1], sys.argv[2], test_settings)
