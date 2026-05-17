import random
import os
import json
import librosa
import soundfile as sf
from pathlib import Path
from tools.melody_tool import process_melody
from scripts.grader import grade_melody

# Parameters search space
PARAM_SPACE = {
    'onset_threshold': (0.01, 0.6), 
    'frame_threshold': (0.01, 0.6), 
    'minimum_note_length': (5, 250), 
    'min_duration': (0.01, 0.4),
    'quantization': [0.125, 0.25, 0.5]
}

def get_next_session_dir(base_dir="output"):
    i = 1
    while os.path.exists(os.path.join(base_dir, f"Training_{i}")):
        i += 1
    session_dir = Path(base_dir) / f"Training_{i}"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir

def generate_random_settings():
    return {
        'onset_threshold': random.uniform(*PARAM_SPACE['onset_threshold']),
        'frame_threshold': random.uniform(*PARAM_SPACE['frame_threshold']),
        'minimum_note_length': random.uniform(*PARAM_SPACE['minimum_note_length']),
        'min_duration': random.uniform(*PARAM_SPACE['min_duration']),
        'quantization': random.choice(PARAM_SPACE['quantization'])
    }

def mutate_settings(best_settings):
    new_settings = best_settings.copy()
    param_to_tweak = random.choice(list(PARAM_SPACE.keys()))
    if param_to_tweak in ['onset_threshold', 'frame_threshold']:
        new_settings[param_to_tweak] = max(0.001, min(0.99, best_settings[param_to_tweak] + random.uniform(-0.05, 0.05)))
    elif param_to_tweak == 'minimum_note_length':
        new_settings[param_to_tweak] = max(5, best_settings[param_to_tweak] + random.uniform(-20, 20))
    elif param_to_tweak == 'min_duration':
        new_settings[param_to_tweak] = max(0.005, best_settings[param_to_tweak] + random.uniform(-0.03, 0.03))
    elif param_to_tweak == 'quantization':
        new_settings[param_to_tweak] = random.choice(PARAM_SPACE['quantization'])
    return new_settings

def run_training(tool_name, input_audio_path, golden_midi_path, generations=30, population_size=10, 
                 start_time=44, end_time=52, golden_offset=40.0, golden_part_index=None):
    
    session_dir = get_next_session_dir()
    print(f"--- Starting {tool_name} Training Session: {session_dir.name} ---")
    
    # 1. Trim Audio
    print(f"Trimming audio to segment {start_time}s - {end_time}s...")
    y, sr = librosa.load(input_audio_path, sr=None, offset=start_time, duration=(end_time - start_time))
    trimmed_audio_path = session_dir / "trimmed_input.wav"
    sf.write(trimmed_audio_path, y, sr)

    best_overall_settings = None
    best_overall_score = -1.0
    
    # HYBRID SEEDING with Training 4, Gen 22, Pop 5 settings
    current_population = [
        # Seeding with the settings you liked!
        {'onset_threshold': 0.18, 'frame_threshold': 0.44, 'minimum_note_length': 100, 'min_duration': 0.1, 'quantization': 0.25},
        # Ultra-Broad
        {'onset_threshold': 0.01, 'frame_threshold': 0.01, 'minimum_note_length': 10, 'min_duration': 0.01, 'quantization': 0.125},
    ]
    while len(current_population) < population_size:
        current_population.append(generate_random_settings())

    for gen in range(1, generations + 1):
        gen_dir = session_dir / f"Gen_{gen}"
        gen_dir.mkdir(exist_ok=True)
        print(f"\nGeneration {gen}")
        scores = []
        
        for i, settings in enumerate(current_population):
            temp_output = gen_dir / f"pop_{i}.mid"
            process_melody(str(trimmed_audio_path), temp_output, settings)
            
            score = grade_melody(
                temp_output, 
                golden_midi_path, 
                golden_transposition=-2
            )
            
            scores.append((score, settings))
            print(f"  Pop {i}: Score = {score:.4f} (On:{settings['onset_threshold']:.2f}, Fr:{settings['frame_threshold']:.2f}, Dur:{settings['min_duration']:.2f})")
        
        scores.sort(key=lambda x: x[0], reverse=True)
        best_gen_score, best_gen_settings = scores[0]
        
        if best_gen_score > best_overall_score:
            best_overall_score = best_gen_score
            best_overall_settings = best_gen_settings
        
        print(f"Generation {gen} Best: {best_gen_score:.4f}")
        current_population = [best_gen_settings] + [mutate_settings(best_gen_settings) for _ in range(population_size - 1)]

    print(f"\n--- Training Complete ---")
    print(f"Best Score: {best_overall_score:.4f}")
    
    best_config_path = session_dir / f"best_settings_{tool_name}.json"
    with open(best_config_path, "w") as f:
        json.dump(best_overall_settings, f, indent=2)
    print(f"Golden Settings saved to: {best_config_path}")

if __name__ == "__main__":
    vocal_stem = "data/stems/htdemucs/Harry Styles - As It Was (Audio)/vocals.wav"
    golden = "data/golden/as_it_was_vocal_target.mid"
    if os.path.exists(vocal_stem) and os.path.exists(golden):
        run_training("melody", vocal_stem, golden)
    else:
        print("Error: Input files not found.")
