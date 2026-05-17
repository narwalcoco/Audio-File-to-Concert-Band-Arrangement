import os
import subprocess
import argparse
from pathlib import Path
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

def run_demucs(input_audio, output_dir):
    """
    Runs Demucs to separate audio into 4 stems: vocals, bass, drums, other.
    """
    print(f"--- Running Demucs on {input_audio} ---")
    command = [
        "python3", "-m", "demucs.separate",
        "-o", str(output_dir),
        str(input_audio)
    ]
    subprocess.run(command, check=True)
    
    # Demucs creates a subfolder named after the model (usually 'htdemucs') 
    # and then another named after the file. We'll need to locate them.
    # For now, we assume standard htdemucs output.
    song_name = Path(input_audio).stem
    stem_path = Path(output_dir) / "htdemucs" / song_name
    return stem_path

def transcribe_stems(stem_dir, midi_output_dir):
    """
    Uses basic-pitch to transcribe separated audio stems into MIDI files.
    """
    print(f"--- Transcribing stems in {stem_dir} ---")
    midi_output_dir.mkdir(parents=True, exist_ok=True)
    
    stems = ["vocals.wav", "bass.wav", "drums.wav", "other.wav"]
    
    for stem in stems:
        audio_path = stem_dir / stem
        if audio_path.exists():
            print(f"Transcribing {stem}...")
            # predict_and_save handles the transcription and file writing
            predict_and_save(
                audio_path_list=[str(audio_path)],
                output_directory=str(midi_output_dir),
                save_midi=True,
                sonify_midi=False,
                save_model_outputs=False,
                save_notes=False,
                model_or_model_path=ICASSP_2022_MODEL_PATH
            )
        else:
            print(f"Warning: {stem} not found in {stem_dir}")

def main():
    parser = argparse.ArgumentParser(description="Ingest audio, separate stems, and transcribe to MIDI.")
    parser.add_argument("input", help="Path to input audio file (mp3/wav)")
    args = parser.parse_args()
    
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: File {input_file} not found.")
        return

    # Define paths
    stems_base_dir = Path("data/stems")
    raw_midi_dir = Path("data/raw_midi") / input_file.stem
    
    # 1. Separate Stems
    stem_path = run_demucs(input_file, stems_base_dir)
    
    # 2. Transcribe to MIDI
    transcribe_stems(stem_path, raw_midi_dir)
    
    print(f"\n--- Ingestion Complete ---")
    print(f"Stems located in: {stem_path}")
    print(f"Raw MIDI files located in: {raw_midi_dir}")

if __name__ == "__main__":
    main()
