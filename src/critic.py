from groq import Groq
from music21 import converter, note, chord, stream
import os
import json
import base64
import subprocess
from dotenv import load_dotenv

load_dotenv()

class AICritic:
    def __init__(self, api_key=None):
        self.client = Groq(api_key=api_key)
        # Using a Vision model to 'see' the sheet music
        self.vision_model = "llama-3.2-11b-vision-preview"
        self.text_model = "llama-3.3-70b-versatile"

    def pdf_to_base64_image(self, pdf_path):
        """Converts the first page of a PDF to a base64 encoded PNG."""
        output_prefix = pdf_path.replace(".pdf", "_page")
        try:
            # Convert PDF to PNG using pdftoppm (first page only)
            subprocess.run(["pdftoppm", "-png", "-f", "1", "-l", "1", pdf_path, output_prefix], check=True)
            png_path = f"{output_prefix}-1.png"
            
            with open(png_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Clean up the temp PNG
            if os.path.exists(png_path):
                os.remove(png_path)
                
            return encoded_string
        except Exception as e:
            print(f"❌ PDF to Image Error: {e}")
            return None

    def get_melody_map(self, file_path):
        """Generates a text-based map of the pitches and rhythms for the AI."""
        try:
            score = converter.parse(file_path)
            melody_map = []
            for i, measure in enumerate(score.flatten().makeMeasures()):
                m_elements = []
                for el in measure.notesAndRests:
                    if el.isRest:
                        m_elements.append(f"Rest({el.duration.type})")
                    else:
                        pitch = el.pitch.nameWithOctave if hasattr(el, 'pitch') else 'Chord'
                        m_elements.append(f"{pitch}({el.duration.type})")
                
                if m_elements:
                    melody_map.append(f"M{i+1}: " + " -> ".join(m_elements))
            
            return "\n".join(melody_map[:30]) 
        except Exception as e:
            return f"Error generating melody map: {e}"

    def get_midi_stats(self, file_path):
        try:
            score = converter.parse(file_path)
            all_notes = list(score.flatten().notes)
            all_rests = list(score.flatten().getElementsByClass('Rest'))
            durations = [float(n.duration.quarterLength) for n in all_notes]
            
            stats = {
                "metrics": {
                    "total_notes": len(all_notes),
                    "total_rests": len(all_rests),
                    "min_duration": min(durations) if durations else 0,
                    "avg_duration": sum(durations)/len(durations) if durations else 0
                }
            }
            return stats
        except Exception as e:
            return {"error": str(e)}

    def evaluate(self, midi_path, pdf_path, current_params, ground_truth=None, genre="Pop", target_midi_path=None):
        stats = self.get_midi_stats(midi_path)
        melody_map = self.get_melody_map(midi_path)
        
        # Convert the generated PDF to an image for visual analysis
        base64_image = self.pdf_to_base64_image(pdf_path)
        
        target_context = ""
        if target_midi_path and os.path.exists(target_midi_path):
            target_melody = self.get_melody_map(target_midi_path)
            target_context = f"GOLD STANDARD MELODY REFERENCE:\n{target_melody}"

        system_prompt = f"""
        You are a world-class Music Producer and Notation Expert specializing in {genre}.
        You are looking at a SCREENSHOT of the sheet music and the MIDI statistics.
        
        GOAL: Make the transcription visually professional and musically accurate for a B♭ Clarinet.
        
        {target_context}
        
        CRITICAL PRIORITIES:
        1. Visual Clarity: Does the sheet music look clean? (Avoid overlapping notes/rests).
        2. Melodic Fidelity: Are the pitches (C4, D4, etc.) correct compared to the original?
        3. Quantization: Is it too robotic or too jittery?
        """

        user_content = [
            {
                "type": "text",
                "text": f"""
                MIDI Statistics: {json.dumps(stats)}
                Current Melody Map: {melody_map}
                Current Parameters: {json.dumps(current_params)}
                
                TASK:
                1. Look at the screenshot of the sheet music.
                2. Identify visual notation errors (e.g., messy beams, overlapping symbols).
                3. Compare the melody to the reference and suggest adjustments to grid_size, min_note_duration, and merge_proximity.
                
                Respond ONLY in JSON format:
                {{
                    "score": (integer 0-100),
                    "feedback": "Visual and melodic critique",
                    "adjustments": {{
                        "grid_size": (float),
                        "min_note_duration": (float),
                        "merge_proximity": (float)
                    }},
                    "should_stop": (boolean)
                }}
                """
            }
        ]

        if base64_image:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })

        try:
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ Groq Vision Error: {e}")
            return {"score": 0, "feedback": f"Vision API Fail: {e}", "adjustments": {}, "should_stop": False}
