import librosa
import numpy as np
import mido
import os

def transcribe_drums(audio_path, output_midi_path, sensitivity=0.1):
    """
    Transcribes drums by detecting onsets (hits) rather than pitch.
    sensitivity: lower is MORE sensitive (captures quieter hits).
    """
    print(f"🥁 Analyzing Percussion: {audio_path}...")
    
    # 1. Load the audio
    y, sr = librosa.load(audio_path)
    
    # 2. Onset Detection (Finding the 'hits')
    # We use a lower 'wait' to allow for fast drum rolls (e.g. 16th notes)
    # and a custom backtrack to align with the peak.
    onset_frames = librosa.onset.onset_detect(
        y=y, sr=sr, 
        wait=5, # Minimum frames between onsets
        pre_avg=3, 
        post_avg=3, 
        pre_max=3, 
        post_max=3,
        delta=sensitivity # Higher delta = less sensitive, Lower = more hits
    )
    
    # 3. Convert frames to time
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    # 4. Create MIDI file
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # In General MIDI, Channel 10 is reserved for drums.
    # Note 36 is Bass Drum, 38 is Snare, 42 is Closed Hi-Hat.
    # For a generic "percussion" stem, we'll map all hits to a generic note (e.g. 38 for snare).
    
    ticks_per_beat = mid.ticks_per_beat
    tempo = 500000 # 120 BPM
    ticks_per_second = ticks_per_beat * 2
    
    last_tick = 0
    print(f"Found {len(onset_times)} percussion hits. Converting to MIDI...")
    
    for hit_time in onset_times:
        current_tick = int(hit_time * ticks_per_second)
        delta_time = current_tick - last_tick
        
        # Add a short hit (1 tick duration)
        track.append(mido.Message('note_on', note=38, velocity=100, time=delta_time, channel=9))
        track.append(mido.Message('note_off', note=38, velocity=0, time=10, channel=9))
        
        last_tick = current_tick + 10 # Update to the end of the note_off

    mid.save(output_midi_path)
    print(f"✅ Success! Percussion saved to {output_midi_path}")

if __name__ == "__main__":
    import sys
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "separated/htdemucs_ft/laufey_test/drums.wav"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/percussion_transcription.mid"
    
    if os.path.exists(audio_file):
        transcribe_drums(audio_file, output_file, sensitivity=0.05)
    else:
        print(f"Error: Could not find {audio_file}")
