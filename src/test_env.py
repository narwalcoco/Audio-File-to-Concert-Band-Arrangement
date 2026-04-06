import os
import sys

def test_imports():
    print(f"Python version: {sys.version}")
    try:
        import basic_pitch
        print("✅ basic-pitch imported")
    except ImportError as e:
        print(f"❌ basic-pitch failed: {e}")

    try:
        import demucs
        print("✅ demucs imported")
    except ImportError as e:
        print(f"❌ demucs failed: {e}")

    try:
        import music21
        print("✅ music21 imported")
    except ImportError as e:
        print(f"❌ music21 failed: {e}")

    try:
        import librosa
        print("✅ librosa imported")
    except ImportError as e:
        print(f"❌ librosa failed: {e}")

    try:
        import flask
        print("✅ flask imported")
    except ImportError as e:
        print(f"❌ flask failed: {e}")

    try:
        import torch
        print(f"✅ torch imported (version: {torch.__version__})")
        print(f"   CUDA available: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"❌ torch failed: {e}")

if __name__ == "__main__":
    test_imports()
