import sys
import os
import io
import wave
import json
import socket
import struct
import time
import math
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event, write_event
from wyoming.info import Describe

# Configuration
HOST = '127.0.0.1'
PORT = 10301
TEST_FILE = "test_audio.wav"
PIPER_BIN = "/home/startux/.local/share/tuxtalks/piper/piper"
VOICE_MODEL = "/home/startux/.local/share/tuxtalks/voices/en_GB-cori-high.onnx"

def generate_speech():
    """Use Piper to generate a clean WAV file."""
    print("Generating speech with Piper...")
    
    if not os.path.exists(PIPER_BIN):
        print(f"❌ Piper binary not found at {PIPER_BIN}")
        sys.exit(1)
        
    piper_cmd = (
        f"echo 'Hello Computer. Initiate Diagnostics.' | "
        f"{PIPER_BIN} --model {VOICE_MODEL} "
        f"--output_file {TEST_FILE}"
    )
    res = os.system(piper_cmd)
    if res != 0:
        print("Error running piper. Ensure it is installed.")
        sys.exit(1)
    print(f"Generated {TEST_FILE}.")

def chunk_generator(wav_file, chunk_ms=64):
    with wave.open(wav_file, 'rb') as wf:
        rate = wf.getframerate()
        width = wf.getsampwidth()
        channels = wf.getnchannels()
        print(f"Audio Format: {rate}Hz, {channels}ch, {width} bytes/sample")
        
        yield (rate, width, channels) # Header
        
        # Chunk size
        bytes_per_sample = width * channels
        samples_per_chunk = int(rate * (chunk_ms / 1000.0))
        
        while True:
            data = wf.readframes(samples_per_chunk)
            if not data:
                break
            yield data

def test_connection():
    if not os.path.exists(TEST_FILE):
        generate_speech()
        
    print(f"Connecting to {HOST}:{PORT}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        sock_file = s.makefile('r', encoding='utf-8')
        sock_out = s.makefile('wb')
        
        # 1. Handshake
        print("Sending Describe...")
        write_event(Describe().event(), sock_out)
        sock_out.flush()
        
        # Read handshake response
        line = sock_file.readline()
        print(f"Handshake RX: {line.strip()}")
        
        # 2. Audio Prep
        gen = chunk_generator(TEST_FILE)
        rate, width, channels = next(gen)
        print(f"Sending AudioStart ({rate}Hz)...")
        write_event(AudioStart(rate=rate, width=width, channels=channels).event(), sock_out)
        sock_out.flush()
        
        # 3. Stream
        chunks_sent = 0
        for data in gen:
            # Monotonic Timestamp (Relative 0 start)
            # chunk duration = len(data) / (width*channels) / rate
            chunk_samples = len(data) // (width * channels)
            chunk_ms = (chunk_samples / rate) * 1000
            
            timestamp = int(chunks_sent * chunk_ms)
            
            chunk = AudioChunk(
                rate=rate, width=width, channels=channels, 
                audio=data, timestamp=timestamp
            ).event()
            write_event(chunk, sock_out)
            chunks_sent += 1
            if chunks_sent % 10 == 0: print(".", end="", flush=True)
            
        sock_out.flush()
        print("\nSending AudioStop...")
        write_event(AudioStop().event(), sock_out)
        sock_out.flush()
        
        # 4. Listen for Transcripts
        print("Listening for response (10s timeout)...")
        s.settimeout(10.0)
        start_time = time.time()
        
        while (time.time() - start_time) < 10.0:
            try:
                line = sock_file.readline()
                if not line: break
                
                # Robust JSON parsing
                try:
                    event = json.loads(line)
                    evt_type = event.get('type')
                    
                    if evt_type == "transcript":
                        print(f"\n✅ SUCCESS! Transcript received at {time.time()-start_time:.2f}s")
                        print(f"Text: {event['data']['text']}")
                        return
                    elif evt_type:
                        print(f"[Event:{evt_type}]", end=" ", flush=True)
                    else:
                        # Log raw if no type (like status updates)
                        # print(f"[RX-Raw]: {line.strip()[:100]}...")
                        pass
                        
                except Exception:
                    pass
                    
            except socket.timeout:
                print("\n❌ Timeout waiting for transcript.")
                break
                
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    generate_speech() # Ensure fresh file
    test_connection()
