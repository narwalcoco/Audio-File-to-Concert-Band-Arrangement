import json
from pathlib import Path
from music21 import converter, midi, stream, note, chord, duration, pitch

def load_instruments_config(config_path="config/instruments.json"):
    """Loads instrument definitions from JSON."""
    with open(config_path, "r") as f:
        return json.load(f)

def load_midi(midi_path):
    """Loads a MIDI file into a music21 Stream."""
    return converter.parse(midi_path)

def save_midi(stream_obj, output_path):
    """Saves a music21 Stream to a MIDI file."""
    mf = midi.translate.streamToMidiFile(stream_obj)
    mf.open(output_path, 'wb')
    mf.write()
    mf.close()

def quantize_stream(stream_obj, quarter_length=0.25):
    """
    Quantizes a stream to the nearest grid (default 0.25 = 16th note).
    """
    return stream_obj.quantize((quarter_length,), processOffsets=True, processDurations=True)

def get_instrument_info(instrument_name, instruments_data):
    """Searches for an instrument's details in the config dictionary."""
    for category in instruments_data.values():
        for inst in category:
            if inst['name'].lower() == instrument_name.lower():
                return inst
    return None

def check_range(stream_obj, instrument_info):
    """
    Returns a list of notes that are outside the instrument's defined range.
    Only applicable for pitched instruments.
    """
    if 'range' not in instrument_info:
        return []

    out_of_range = []
    min_midi = instrument_info['range']['min']
    max_midi = instrument_info['range']['max']

    for n in stream_obj.flat.notes:
        if isinstance(n, note.Note):
            if n.pitch.midi < min_midi or n.pitch.midi > max_midi:
                out_of_range.append(n)
        elif isinstance(n, chord.Chord):
            for p in n.pitches:
                if p.midi < min_midi or p.midi > max_midi:
                    out_of_range.append(n)
                    break
    return out_of_range

def transpose_for_instrument(stream_obj, instrument_info, to_written=True):
    """
    Transposes a stream. 
    If to_written=True, moves from Concert Pitch to Written Pitch (e.g., C -> Bb for Trumpet).
    If to_written=False, moves from Written Pitch back to Concert Pitch.
    """
    transposition_interval = instrument_info.get('transposition', 0)
    if transposition_interval == 0:
        return stream_obj

    # music21 transposition uses intervals. 
    # instrument_info['transposition'] is defined as semitones relative to concert.
    # e.g., Trumpet is -2 (Written C sounds Bb). To get Written from Concert, we go UP 2 semitones.
    interval_val = transposition_interval if not to_written else -transposition_interval
    return stream_obj.transpose(interval_val)

if __name__ == "__main__":
    # Quick test
    config = load_instruments_config()
    trumpet = get_instrument_info("Trumpet", config)
    print(f"Loaded Trumpet Info: {trumpet}")
