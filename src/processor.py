from music21 import converter, note, stream, chord, instrument, expressions, dynamics, spanner, articulations
import os
from collections import Counter

def consolidate_vibrato(notes, jitter_threshold=0.25):
    """
    Identifies clusters of short notes (vibrato/trill jitter) and merges them.
    """
    if not notes:
        return []
    
    final_notes = []
    buffer = []
    
    for n in notes:
        if n.duration.quarterLength <= jitter_threshold:
            if not buffer:
                buffer.append(n)
            else:
                last_in_buffer = buffer[-1]
                gap = n.offset - (last_in_buffer.offset + last_in_buffer.duration.quarterLength)
                if gap <= 0.1:
                    buffer.append(n)
                else:
                    final_notes.append(merge_cluster(buffer))
                    buffer = [n]
        else:
            if buffer:
                final_notes.append(merge_cluster(buffer))
                buffer = []
            final_notes.append(n)
            
    if buffer:
        final_notes.append(merge_cluster(buffer))
        
    return final_notes

def merge_cluster(cluster):
    if len(cluster) == 1:
        return cluster[0]
    
    pitches = [n.pitch.ps for n in cluster if hasattr(n, 'pitch')]
    if not pitches:
        return cluster[0]
        
    unique_pitches = list(set(pitches))
    most_common_pitch_ps = Counter(pitches).most_common(1)[0][0]
    
    start_offset = cluster[0].offset
    end_offset = cluster[-1].offset + cluster[-1].duration.quarterLength
    
    merged_note = note.Note()
    merged_note.pitch.ps = most_common_pitch_ps
    merged_note.offset = start_offset
    merged_note.duration.quarterLength = end_offset - start_offset
    
    # Dynamics (Take max velocity of the cluster)
    velocities = [n.volume.velocity for n in cluster if n.volume.velocity is not None]
    if velocities:
        merged_note.volume.velocity = max(velocities)
    
    # Detect Trill (Alternating between 2 pitches rapidly)
    if len(unique_pitches) == 2 and len(cluster) >= 4:
        diff = abs(unique_pitches[0] - unique_pitches[1])
        if diff <= 2: # Whole step or half step
            merged_note.expressions.append(expressions.Trill())
    
    return merged_note

def process_midi(input_path, output_path, params):
    grid_size = params.get('grid_size', 0.25)
    min_dur = params.get('min_note_duration', 0.25)
    merge_prox = params.get('merge_proximity', 0.05)
    
    score = converter.parse(input_path)
    new_score = stream.Score()

    # Divisors for quantization (Straight + Triplets)
    base_div = max(1, int(1 / grid_size))
    triplet_div = max(1, int(1.5 / grid_size))
    divisors = (base_div, triplet_div)

    for p in score.parts:
        try:
            # Safe clear of expressions
            for expr in p.recurse().getElementsByClass('Expression'):
                p.remove(expr, recurse=True)
        except:
            pass
        
        # 1. Quantize FIRST with Triplets Allowed
        p.quantize(quarterLengthDivisors=divisors, processOffsets=True, processDurations=True, inPlace=True)
        
        final_part = stream.Part()
        final_part.insert(0, instrument.Clarinet())
        final_part.id = "Clarinet"
        
        raw_elements = sorted(list(p.flatten().notes), key=lambda x: x.offset)
        monophonic_list = []
        for el in raw_elements:
            if isinstance(el, chord.Chord):
                n = sorted(el.notes, key=lambda x: x.pitch.ps, reverse=True)[0]
                n.duration = el.duration
                n.offset = el.offset
                if el.volume.velocity is not None:
                    n.volume.velocity = el.volume.velocity
                monophonic_list.append(n)
            else:
                monophonic_list.append(el)

        # 3. Vibrato & Trill De-Jitter
        de_jittered = consolidate_vibrato(monophonic_list, jitter_threshold=grid_size)
        
        # 4. Cleanup & Short Note Filter
        cleaned_notes = []
        last_note = None
        for n in de_jittered:
            if n.duration.quarterLength < min_dur:
                continue
                
            n.articulations = []
            
            if last_note and last_note.pitch == n.pitch:
                gap = n.offset - (last_note.offset + last_note.duration.quarterLength)
                if 0 <= gap <= merge_prox:
                    last_note.duration.quarterLength += (gap + n.duration.quarterLength)
                    continue
            
            # Prevent overlap
            if last_note and n.offset < (last_note.offset + last_note.duration.quarterLength):
                last_note.duration.quarterLength = n.offset - last_note.offset
            
            if n.duration.quarterLength > 0:
                cleaned_notes.append(n)
                last_note = n

        # 4.5 Auto-Octave Alignment
        all_pitches = [n.pitch.ps for n in cleaned_notes if hasattr(n, 'pitch')]
        if all_pitches:
            avg_pitch = sum(all_pitches) / len(all_pitches)
            target_pitch = 60 # C4 is MIDI 60 (Lowered from C5 based on feedback)
            octave_shift = round((target_pitch - avg_pitch) / 12)
            if octave_shift != 0:
                for n in cleaned_notes:
                    if hasattr(n, 'pitch'):
                        n.transpose(octave_shift * 12, inPlace=True)

        # 5. Articulations, Dynamics, & Phrasing Pass
        current_phrase = []
        for i, n in enumerate(cleaned_notes):
            # Dynamics Mapping (New phrase if gap > 1.0 beat)
            if i == 0 or (cleaned_notes[i-1] and n.offset - (cleaned_notes[i-1].offset + cleaned_notes[i-1].duration.quarterLength) > 1.0):
                vel = n.volume.velocity if n.volume.velocity else 64
                if vel < 45:
                    dyn = dynamics.Dynamic('p')
                elif vel > 85:
                    dyn = dynamics.Dynamic('f')
                else:
                    dyn = dynamics.Dynamic('mf')
                final_part.insert(n.offset, dyn)

            # Insert note
            final_part.insert(n.offset, n)
            
            # Staccato & Slur Detection
            gap_to_next = float('inf')
            if i < len(cleaned_notes) - 1:
                next_n = cleaned_notes[i+1]
                gap_to_next = next_n.offset - (n.offset + n.duration.quarterLength)

            if gap_to_next <= 0.05:
                current_phrase.append(n)
            else:
                current_phrase.append(n)
                if len(current_phrase) > 1:
                    # Add Slur over the phrase
                    slur = spanner.Slur(current_phrase)
                    final_part.insert(0, slur)
                elif n.duration.quarterLength < 0.5 and gap_to_next > 0.25:
                    # Short isolated note -> Staccato
                    n.articulations.append(articulations.Staccato())
                current_phrase = []
            
        new_score.insert(0, final_part)

    new_score.write('midi', fp=output_path)
    return output_path

if __name__ == "__main__":
    test_params = {'grid_size': 0.25, 'min_note_duration': 0.25, 'merge_proximity': 0.1}
    process_midi("Field_Test/vocals_raw.mid", "output/evolution_test.mid", test_params)