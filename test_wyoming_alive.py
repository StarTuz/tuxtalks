import socket
import json
from wyoming.info import Describe, Info
from wyoming.event import write_event, Event

HOST = "127.0.0.1"
PORT = 10301

def test_server():
    print(f"Connecting to {HOST}:{PORT}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((HOST, PORT))
            print("Connected.")
            
            # Use raw file objects for wyoming library
            sock_file = s.makefile('r', encoding='utf-8')
            sock_out = s.makefile('wb')
            
            print("Sending Describe...")
            write_event(Describe().event(), sock_out)
            sock_out.flush()
            
            print("Waiting for response...")
            line = sock_file.readline()
            if line:
                print(f"Received: {line.strip()}")
                event = Event.from_dict(json.loads(line))
                if event.type == "info":
                    print("✅ Server is ALIVE and responding!")
                else:
                    print(f"⚠️ Server returned unexpected event: {event.type}")
            else:
                print("❌ Server closed connection without response.")
                
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_server()
