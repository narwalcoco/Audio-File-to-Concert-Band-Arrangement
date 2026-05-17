import os
import json
import numpy as np
import librosa
import soundfile as sf
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from music21 import converter, tempo, stream

def extract_for_song(audio_path, golden_midi_path, golden_part_idx, g_start_s, g_end_s, a_start_s, a_end_s, output_suffix):
    print(f"--- Exporting Data for {output_suffix} ---")
    
    # 1. Load Audio and Apply Simple Noise Gate
    y, sr = librosa.load(audio_path, sr=22050, offset=a_start_s, duration=(a_end_s - a_start_s))
    
    # Simple Noise Gate: kill everything below 15% of peak volume
    peak = np.max(np.abs(y))
    y_gated = np.where(np.abs(y) > (peak * 0.15), y, 0)
    
    temp_gated = f"data/temp_gated_{output_suffix}.wav"
    sf.write(temp_gated, y_gated, sr)

    # 2. AI Inference on standard vocals
    model_output, _, _ = predict(temp_gated, model_or_model_path=ICASSP_2022_MODEL_PATH)
    FPS = 22050 / 256
    
    data_to_export = {
        "onsets": model_output['onset'].tolist(),
        "notes": model_output['note'].tolist(),
        "fps": FPS
    }
    with open(f"data/matrices_{output_suffix}.json", "w") as f:
        json.dump(data_to_export, f)

    # 3. Golden Target Extraction
    s = converter.parse(golden_midi_path)
    met = s.flatten().getElementsByClass(tempo.MetronomeMark)
    bpm = met[0].number if met else 120
    bps = bpm / 60.0
    
    target_part = s.parts[golden_part_idx]
    g_start_beat = g_start_s * bps
    g_end_beat = g_end_s * bps
    
    segment = target_part.flatten().notes.getElementsByOffset(g_start_beat, g_end_beat, includeEndBoundary=True)
    
    target_notes = []
    # Use the first note's actual offset for relative alignment normalization
    if len(segment) > 0:
        first_offset = segment[0].offset
        for n in segment:
            # Transpose Alto Sax (Eb) to Clarinet (Bb) (+5 semitones)
            pitch = (n.pitch.midi if hasattr(n, 'pitch') else n.pitches[-1].midi) + 5
            target_notes.append({
                "pitch": pitch,
                "offset": float(n.offset - first_offset), # Start at 0 relative to first note
                "duration": float(n.duration.quarterLength)
            })
    
    with open(f"data/target_{output_suffix}.json", "w") as f:
        json.dump(target_notes, f)
        
    # Also save a target midi for listening
    new_s = stream.Stream()
    new_s.insert(0, tempo.MetronomeMark(number=bpm))
    for n in segment:
        new_s.insert(n.offset - g_start_beat, n)
    new_s.write('midi', fp=f'data/golden/target_{output_suffix}.mid')
    
    print(f"Export Complete: data/matrices_{output_suffix}.json, data/target_{output_suffix}.json")
    print(f"Listen to target at: data/golden/target_{output_suffix}.mid")
    return bpm

if __name__ == "__main__":
    # Taylor Swift - Shake It Off
    extract_for_song(
        audio_path="data/stems/htdemucs/Taylor Swift - Shake It Off/vocals.wav",
        golden_midi_path="data/golden/shake-it-off.mid",
        golden_part_idx=3, # Alto Saxophone
        g_start_s=63,
        g_end_s=71,
        a_start_s=28,
        a_end_s=36,
        output_suffix="shake"
    )
