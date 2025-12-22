import socket
import json
import time
from wyoming.audio import AudioStart, AudioChunk, AudioStop

HOST = 'localhost'
PORT = 10300

try:
    print(f"Connecting to {HOST}:{PORT}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print("✅ Connected!")

    # 1. Send AudioStart
    print("Sending AudioStart...")
    event = AudioStart(rate=16000, width=2, channels=1).event()
    line = (json.dumps(event.to_dict(), ensure_ascii=False) + "\n").encode("utf-8")
    s.sendall(line)
    if event.payload: s.sendall(event.payload)

    # 2. Send Silence (1 second)
    print("Sending 1s Silence...")
    data = b'\x00' * 32000
    event = AudioChunk(rate=16000, width=2, channels=1, audio=data).event()
    line = (json.dumps(event.to_dict(), ensure_ascii=False) + "\n").encode("utf-8")
    s.sendall(line)
    if event.payload: s.sendall(event.payload)

    # 3. Read loop (simple)
    s.settimeout(2.0)
    try:
        f = s.makefile('r', encoding='utf-8')
        while True:
            line = f.readline()
            if not line: break
            print(f"Server says: {line.strip()}")
            # Break if transcript
    except socket.timeout:
        print("Timeout waiting for response.")

    s.close()

except Exception as e:
    print(f"❌ Test Failed: {e}")
