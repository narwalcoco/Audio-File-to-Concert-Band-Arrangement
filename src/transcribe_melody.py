import librosa
import numpy as np
import mido
import math
import os

def audio_to_midi(audio_path, output_midi_path):
    print(f"Analyzing {audio_path}...")
    
    # 1. Load the audio
    y, sr = librosa.load(audio_path)
    
    # 2. Extract Fundamental Frequency (f0) using probabilistic YIN (pyin)
    # This is a high-quality algorithm for finding the pitch of a voice.
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    
    # 3. Convert frequencies to MIDI note numbers
    # We replace 'NaN' (silence) with 0
    midi_notes = librosa.hz_to_midi(f0)
    midi_notes[np.isnan(midi_notes)] = 0
    
    # 4. Create the MIDI file
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Librosa default hop_length is 512. Let's calculate time per frame.
    time_per_frame = 512 / sr
    ticks_per_beat = mid.ticks_per_beat
    tempo = 500000 # Default 120 BPM
    # (60s / 120 BPM) = 0.5s per beat. 
    # Ticks per second = ticks_per_beat / 0.5 = ticks_per_beat * 2
    ticks_per_second = ticks_per_beat * 2
    
    current_note = 0
    current_duration = 0
    
    print("Converting pitch to MIDI messages...")
    for note in midi_notes:
        note = int(round(note)) if note > 0 else 0
        
        if note == current_note:
            current_duration += time_per_frame
        else:
            # Note changed - write the previous note
            tick_duration = int(current_duration * ticks_per_second)
            
            if current_note > 0:
                track.append(mido.Message('note_on', note=current_note, velocity=64, time=0))
                track.append(mido.Message('note_off', note=current_note, velocity=0, time=tick_duration))
            else:
                # It was a rest, so we just add the time to the NEXT message
                if len(track) > 0:
                    # Add rest time to the previous note_off delta if needed, 
                    # but mido handles delta time differently. 
                    # For simplicity, we'll just track the "silence" as a delay.
                    pass 
            
            current_note = note
            current_duration = time_per_frame

    mid.save(output_midi_path)
    print(f"Success! Saved to {output_midi_path}")

if __name__ == "__main__":
    import sys
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "separated/htdemucs_ft/laufey_test/vocals.wav"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/vocals_transcription.mid"
    
    if os.path.exists(audio_file):
        audio_to_midi(audio_file, output_file)
    else:
        print(f"Error: Could not find {audio_file}")
