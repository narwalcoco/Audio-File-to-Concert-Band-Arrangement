import os
import time
import json
import subprocess
import librosa
from dotenv import load_dotenv
from processor import process_midi
from critic import AICritic

load_dotenv()

def get_audio_ground_truth(audio_path, duration=25):
    """Analyzes the first 25s of the original audio for ground truth."""
    print(f"👂 Analyzing Audio Ground Truth (First {duration}s): {audio_path}")
    y, sr = librosa.load(audio_path, duration=duration)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    
    return {
        "bpm": float(tempo),
        "total_onsets": len(onsets),
        "average_density": len(onsets) / duration
    }

def training_loop(genre, input_midi, audio_path, target_midi=None, max_iters=50):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("Error: GROQ_API_KEY not set.")
        return

    ground_truth = get_audio_ground_truth(audio_path)
    critic = AICritic(key)
    
    # Starting parameters for training
    params = {'grid_size': 0.125, 'min_note_duration': 0.125, 'merge_proximity': 0.05}
    
    best_score = -1
    best_params = params.copy()
    
    training_dir = f"{genre.lower()}_training"
    os.makedirs(training_dir, exist_ok=True)
    
    print(f"\n🚀 Starting {genre} Model Training with Vision (Full {max_iters} gens)...")
    
    mscore_path = "tools/musescore-cli/AppRun"

    for i in range(1, max_iters + 1):
        gen_dir = f"{training_dir}/gen_{i}"
        os.makedirs(gen_dir, exist_ok=True)
        
        output_midi = f"{gen_dir}/attempt_{i}.mid"
        output_pdf = f"{gen_dir}/attempt_{i}.pdf"
        
        # 1. Process MIDI
        process_midi(input_midi, output_midi, params)
        
        # 2. Generate PDF for Vision Analysis
        subprocess.run([mscore_path, "-o", output_pdf, output_midi], check=False)
        
        # 3. Evaluate with Vision + Stats
        result = critic.evaluate(
            midi_path=output_midi, 
            pdf_path=output_pdf, 
            current_params=params, 
            ground_truth=ground_truth, 
            genre=genre, 
            target_midi_path=target_midi
        )
        
        score = result.get('score', 0)
        print(f"  [Gen {i}] Score: {score}/100 | {result.get('feedback')[:100]}...")
        
        with open(f"{gen_dir}/critic_feedback.json", "w") as f:
            json.dump(result, f, indent=2)

        if score > best_score:
            best_score = score
            best_params = params.copy()
            subprocess.run(["cp", output_midi, f"{training_dir}/best_training_result.mid"])

        if score >= 98:
            print(f"✅ Training Target Reached! Score: {score}")
            break
            
        if result.get('adjustments'):
            params.update(result.get('adjustments'))
            
        #vision model has different rate limits, be careful
        time.sleep(2)

    # SAVE THE WINNING MODEL
    model_path = f"models/{genre.lower()}_profile.json"
    with open(model_path, "w") as f:
        json.dump(best_params, f, indent=2)
    
    print(f"\n🏆 Training Complete! Best Score: {best_score}")
    print(f"📂 Model saved to: {model_path}")

if __name__ == "__main__":
    import sys
    genre = sys.argv[1] if len(sys.argv) > 1 else "Pop"
    
    if genre == "Pop":
        target = "pop_training/examples/gold_standard_cropped.mid"
        vocal_path = "pop_training/separated/htdemucs/pop-song/vocals.wav"
        input_midi = "pop_training/pop_vocals_raw.mid"
        training_loop("Pop", input_midi, vocal_path, target_midi=target)
    elif genre == "Classical":
        training_loop("Classical", "classical_training/classical_raw.mid", "classical_training/classical.mp3")
    elif genre == "Jazz":
        training_loop("Jazz", "jazz_training/jazz_raw.mid", "jazz_training/jazz.mp3")
    else:
        print(f"Unknown genre: {genre}")
