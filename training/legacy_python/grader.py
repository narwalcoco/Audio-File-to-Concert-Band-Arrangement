import os
from music21 import note, chord, converter, tempo

def get_tempo(stream_obj):
    """Returns the tempo of the stream, defaulting to 120."""
    met = stream_obj.flatten().getElementsByClass(tempo.MetronomeMark)
    if met:
        return met[0].number
    return 120

def grade_melody(processed_midi_path, golden_midi_path, start_time=None, end_time=None, golden_offset=0, golden_part_index=None, golden_transposition=0):
    """
    Grades a processed MIDI file against a golden standard.
    - ZERO-START ALIGNMENT: Shifts first note of each to 0.0 before comparing.
    """
    processed_full = converter.parse(processed_midi_path)
    golden_full = converter.parse(golden_midi_path)
    
    p_tempo = get_tempo(processed_full)
    g_tempo = get_tempo(golden_full)
    
    p_notes_all = processed_full.flatten().notes
    if golden_part_index is not None:
        g_notes_all = golden_full.parts[golden_part_index].flatten().notes
    else:
        g_notes_all = golden_full.flatten().notes

    if not p_notes_all:
        return -1.0 # MASSIVE VOID PENALTY to discourage silence

    # 1. FIND FIRST NOTES AND ZERO THEM OUT
    p_start_offset = p_notes_all[0].offset
    g_start_offset = g_notes_all[0].offset

    matches = 0
    p_tolerance = 0.25 * (p_tempo / 60) # 250ms tolerance

    # RECALL (Melody Finding)
    for g_note in g_notes_all:
        g_norm = g_note.offset - g_start_offset
        expected_p_offset = g_norm + p_start_offset
        candidates = p_notes_all.getElementsByOffset(expected_p_offset - p_tolerance, expected_p_offset + p_tolerance)

        g_pitch = (g_note.pitch.midi if hasattr(g_note, 'pitch') else g_note.pitches[-1].midi) + golden_transposition

        best_note_match = 0
        for p_note in candidates:
            p_pitch = p_note.pitch.midi if hasattr(p_note, 'pitch') else p_note.pitches[-1].midi

            pitch_diff = abs(g_pitch - p_pitch)
            is_match = (g_pitch == p_pitch) or (g_pitch % 12 == p_pitch % 12)
            is_fuzzy = (pitch_diff == 1) or (pitch_diff % 12 == 1) or (pitch_diff % 12 == 11)

            if is_match or is_fuzzy:
                g_dur = g_note.duration.quarterLength
                p_dur = p_note.duration.quarterLength
                dur_ratio = min(g_dur, p_dur) / max(g_dur, p_dur)

                match_weight = 1.0 if is_match else 0.25
                # Current best match for this golden note
                current_match_score = match_weight * (0.5 + (0.5 * dur_ratio))
                best_note_match = max(best_note_match, current_match_score)

        matches += best_note_match

    recall_score = matches / len(g_notes_all)

    # PRECISION (Noise Cleanup - Relaxed)
    # We only penalize if they have > 3x the notes of golden
    precision_penalty = 0.0
    if len(p_notes_all) > (len(g_notes_all) * 3):
        # Scale penalty from 0 to 1 based on how much over 3x they are
        precision_penalty = min(1.0, (len(p_notes_all) - (len(g_notes_all) * 3)) / (len(g_notes_all) * 5))

    # 80% focus on Finding notes, 20% focus on not having too much noise
    final_score = (recall_score * 0.8) - (precision_penalty * 0.2)
    return max(0, final_score)

