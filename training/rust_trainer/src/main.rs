use anyhow::Result;
use rand::Rng;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

#[derive(Debug, Deserialize, Serialize, Clone)]
struct MatrixData {
    onsets: Vec<Vec<f32>>,
    notes: Vec<Vec<f32>>,
    fps: f32,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
struct GoldenNote {
    pitch: u8,
    offset: f32,
    duration: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Settings {
    onset_threshold: f32,
    frame_threshold: f32,
    min_midi: u8,
    max_midi: u8,
    alignment_offset: f32,
    pitch_offset: i8,
    minimum_note_length: f32,
}

#[derive(Debug, Clone)]
struct NoteEvent {
    pitch: u8,
    start_time: f32,
    duration: f32,
}

fn pick_notes_crystal(data: &MatrixData, settings: &Settings, tempo: f32) -> Vec<NoteEvent> {
    let mut detected_notes = Vec::new();
    let num_frames = data.notes.len();
    let mut current_note: Option<NoteEvent> = None;
    
    let bps = tempo / 60.0;
    let max_whole_note = 4.0 / bps;
    let min_gap = 2.0 / data.fps;

    // 8-frame Stability window
    let mut best_pitch_history: Vec<u8> = vec![0; 8];

    for f in 0..num_frames {
        let time = f as f32 / data.fps;
        
        // HARD STOP: Don't pick any notes past 8.0 seconds
        if time > 8.0 { break; }
        
        let mut max_v = 0.0;
        for p_idx in 0..88 {
            if data.notes[f][p_idx] > max_v { max_v = data.notes[f][p_idx]; }
        }

        let mut crystal_pitch = 0;
        if max_v > settings.frame_threshold {
            for p_idx in (0..88).rev() {
                let pitch = (p_idx + 21) as u8;
                if pitch < settings.min_midi || pitch > settings.max_midi { continue; }
                if data.notes[f][p_idx] > (max_v * 0.9) {
                    crystal_pitch = pitch;
                    break;
                }
            }
        }
        
        best_pitch_history.remove(0);
        best_pitch_history.push(crystal_pitch);
        let stable_pitch = if best_pitch_history.iter().all(|&p| p == crystal_pitch) { crystal_pitch } else { 0 };

        if stable_pitch > 0 {
            let onset_val = data.onsets[f][stable_pitch as usize - 21];
            if let Some(mut note) = current_note.take() {
                if note.pitch == stable_pitch && onset_val < settings.onset_threshold * 1.5 && note.duration < max_whole_note {
                    note.duration += 1.0 / data.fps;
                    current_note = Some(note);
                } else {
                    detected_notes.push(note);
                    if onset_val > settings.onset_threshold {
                        current_note = Some(NoteEvent {
                            pitch: stable_pitch,
                            start_time: time + min_gap,
                            duration: 1.0 / data.fps,
                        });
                    }
                }
            } else if onset_val > settings.onset_threshold {
                current_note = Some(NoteEvent {
                    pitch: stable_pitch,
                    start_time: time,
                    duration: 1.0 / data.fps,
                });
            }
        } else if let Some(note) = current_note.take() {
            detected_notes.push(note);
        }
    }
    if let Some(note) = current_note { detected_notes.push(note); }
    detected_notes.into_iter().filter(|n| n.duration >= (settings.minimum_note_length / 1000.0)).collect()
}

fn grade_precision(detected: &[NoteEvent], golden: &[GoldenNote], tempo: f32, settings: &Settings) -> f32 {
    if detected.is_empty() { return -1.0; }
    let bps = tempo / 60.0;
    
    // First note alignment
    let d_start = detected[0].start_time;
    let g_start = golden[0].offset / bps;
    
    let mut total_score = 0.0;
    let tolerance = 0.08; 
    let mut used_detected = vec![false; detected.len()];

    for g_note in golden {
        let g_start_time = (g_note.offset / bps) - g_start + d_start + settings.alignment_offset;
        let g_end_time = g_start_time + (g_note.duration / bps);
        
        // Target is already Clarinet Written pitch from extraction script.
        // We only use settings.pitch_offset for fine-tuning.
        let target_pitch = (g_note.pitch as i16 + settings.pitch_offset as i16) as u8;

        let mut best_note_score: f32 = 0.0;
        let mut best_idx: Option<usize> = None;

        for (i, d_note) in detected.iter().enumerate() {
            if used_detected[i] { continue; }
            let d_end_time = d_note.start_time + d_note.duration;
            let overlap_start = g_start_time.max(d_note.start_time);
            let overlap_end = g_end_time.min(d_end_time);
            
            if overlap_start < overlap_end {
                let start_err = (d_note.start_time - g_start_time).abs();
                let start_score = (1.0 - (start_err / tolerance)).max(0.0);
                let end_err = (d_end_time - g_end_time).abs();
                let end_score = (1.0 - (end_err / tolerance)).max(0.0);
                
                let mut hold_score = 0.0;
                if d_note.pitch == target_pitch {
                    hold_score = (overlap_end - overlap_start) / (g_note.duration / bps);
                }
                let note_score = (start_score * 0.2) + (end_score * 0.2) + (hold_score * 0.6);
                if note_score > best_note_score {
                    best_note_score = note_score;
                    best_idx = Some(i);
                }
            }
        }
        if let Some(idx) = best_idx {
            used_detected[idx] = true;
            total_score += best_note_score;
        }
    }
    let recall = total_score / golden.len() as f32;
    
    // DENSITY BONUS: Reward matching the note count
    let count_ratio = detected.len() as f32 / golden.len() as f32;
    // Gaussian-like curve: peaks at 1.0, drops off as ratio moves away from 1
    let density_bonus = (-(count_ratio - 1.0).powi(2) / 0.5).exp();

    let mut penalty = 0.0;
    if detected.len() > (golden.len() * 3) {
        penalty = ((detected.len() as f32 - (golden.len() as f32 * 3.0)) / 50.0).min(1.0);
    }
    
    // 70% Recall, 20% Density Match, 10% Noise Penalty
    (recall * 0.70) + (density_bonus * 0.20) - (penalty * 0.10)
}

fn main() -> Result<()> {
    let song = "shake";
    let tempo = 160.0;

    println!("--- Crystal Vocal Trainer [{}] (1,000 Generations) ---", song);
    let mut session_idx = 1;
    while Path::new(&format!("../../output/Training_Rust_{}", session_idx)).exists() { session_idx += 1; }
    let session_dir = format!("../../output/Training_Rust_{}", session_idx);
    std::fs::create_dir_all(&session_dir)?;

    let file = File::open(format!("../../data/matrices_{}.json", song))?;
    let data: MatrixData = serde_json::from_reader(BufReader::new(file))?;
    let file = File::open(format!("../../data/target_{}.json", song))?;
    let golden: Vec<GoldenNote> = serde_json::from_reader(BufReader::new(file))?;

    let mut best_settings = Settings {
        onset_threshold: 0.24,
        frame_threshold: 0.09,
        min_midi: 21,
        max_midi: 108,
        alignment_offset: -0.141,
        pitch_offset: 0,
        minimum_note_length: 50.0,
    };
    let mut best_score = -100.0;
    let population_size = 10_000;
    let generations = 1000;

    for gen in 1..=generations {
        let mut population = Vec::with_capacity(population_size);
        population.push(best_settings.clone()); 
        let mut rng = rand::thread_rng();
        while population.len() < population_size {
            let mut m = best_settings.clone();
            match rng.gen_range(0..6) {
                0 => m.onset_threshold = (m.onset_threshold + rng.gen_range(-0.05..0.05)).clamp(0.01, 0.99),
                1 => m.frame_threshold = (m.frame_threshold + rng.gen_range(-0.05..0.05)).clamp(0.01, 0.99),
                2 => m.alignment_offset = (m.alignment_offset + rng.gen_range(-0.01..0.01)).clamp(-1.0, 1.0),
                3 => m.minimum_note_length = (m.minimum_note_length + rng.gen_range(-20.0..20.0)).clamp(10.0, 500.0),
                4 => m.min_midi = (m.min_midi as i16 + rng.gen_range(-1..1)).clamp(21, 108) as u8,
                _ => m.pitch_offset = (m.pitch_offset as i16 + rng.gen_range(-1..1)).clamp(-24, 24) as i8,
            }
            population.push(m);
        }
        let results: Vec<(f32, Settings)> = population.into_par_iter().map(|s| {
            let notes = pick_notes_crystal(&data, &s, tempo);
            (grade_precision(&notes, &golden, tempo, &s), s)
        }).collect();
        let mut gen_best_score = -100.0;
        let mut gen_best_settings = best_settings.clone();
        for (sc, s) in results {
            if sc > gen_best_score { gen_best_score = sc; gen_best_settings = s; }
        }
        if gen_best_score > best_score { best_score = gen_best_score; best_settings = gen_best_settings; }
        if gen % 100 == 0 || gen == 1 {
            println!("Gen {}: Best Score = {:.4} (On:{:.2}, Fr:{:.2}, Off:{:.3}, Key:{})", gen, best_score, best_settings.onset_threshold, best_settings.frame_threshold, best_settings.alignment_offset, best_settings.pitch_offset);
        }
    }
    println!("\n--- Training Complete ---");
    let out_file_path = format!("{}/best_settings.json", session_dir);
    let out_file = File::create(&out_file_path)?;
    serde_json::to_writer_pretty(out_file, &best_settings)?;
    
    let audio_src = format!("../../data/temp_gated_{}.wav", song);
    let _ = std::process::Command::new("python3").env("PYTHONPATH", "../../").arg("-c")
        .arg(format!("import json; from tools.melody_tool import process_melody; s = json.load(open('{}')); process_melody('{}', '{}/winner.mid', s)", 
            out_file_path, audio_src, session_dir)).status()?;
    println!("Winner MIDI generated at: {}/winner.mid", session_dir);
    Ok(())
}
