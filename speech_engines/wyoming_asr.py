import asyncio
import threading
import queue
import time
import struct
from .base import ASRBase
import logging
from . import wyoming_server_manager

# AGGRESSIVE SILENCING of Wyoming library
for logger_name in ["wyoming", "wyoming.event", "wyoming.client", "wyoming.server", "wyoming.audio"]:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).disabled = True

from wyoming.client import AsyncTcpClient
from wyoming.info import Describe
from wyoming.audio import AudioStart, AudioChunk, AudioStop
from wyoming.asr import Transcript

class WyomingASR(ASRBase):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.host = config.get("WYOMING_HOST", "127.0.0.1")
        if self.host == "localhost": self.host = "127.0.0.1"
        self.port = config.get("WYOMING_PORT", 10301)
        self.sample_rate = 16000
        self.chunk_size = 1024 # 64ms at 16k
        
        # VAD State
        self.is_speaking = False
        self.silence_timer = 0
        self.chunks_sent = 0
        self.chunk_duration_ms = (self.chunk_size / self.sample_rate) * 1000.0
        
        self.running = False
        self.paused = False
        self.text_queue = queue.Queue()
        
        # Wyoming Client
        self.client = None
        self.client_lock = threading.Lock()
        
        # Wyoming Server Management
        self.server_process = None
        self.server_started_by_us = False
        
        # Async Event Loop
        self.loop = None
        self.loop_thread = None
        
        # Threads
        self.mic_thread = None
        self.read_thread = None
        
        # PyAudio
        self.audio = None
        self.stream = None

    def start(self, input_device_index=None):
        # Auto-start Wyoming server if enabled and not running
        if self.config.get("WYOMING_AUTO_START", True):
            if not wyoming_server_manager.is_server_running(self.host, self.port):
                print("log: Wyoming server not detected, attempting auto-start...")
                self.server_process = wyoming_server_manager.start_wyoming_whisper(self.config)
                if self.server_process:
                    self.server_started_by_us = True
                else:
                    print("warn: Failed to auto-start Wyoming server")
                    print("      You may need to start it manually: ./start_whisper.sh")
            else:
                print("log: Wyoming server already running (not started by us)")
        
        import pyaudio
        self.audio = pyaudio.PyAudio()
        try:
            # DIAGNOSTIC: List all devices
            print("\n--- Audio Devices ---")
            try:
                default_idx = self.audio.get_default_input_device_info()['index']
            except: default_idx = -1
            
            for i in range(self.audio.get_device_count()):
                try:
                    info = self.audio.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        mark = "*" if i == default_idx else " "
                        print(f"{mark} [{i}] {info['name']}")
                except: pass
            print("---------------------\n", flush=True)

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=input_device_index
            )
        except Exception as e:
            print(f"err: Mic Error: {e}")
            return

        self.running = True
        
        # Start Async Event Loop Thread
        self.loop_thread = threading.Thread(target=self._async_loop_worker, daemon=True)
        self.loop_thread.start()
        
        # Wait for loop to be ready
        while self.loop is None:
            time.sleep(0.01)
        
        # Start Mic Worker
        self.mic_thread = threading.Thread(target=self._mic_worker, daemon=True)
        self.mic_thread.start()
        
        print(f"log: Wyoming ASR Client Started ({self.host}:{self.port})")

    def stop(self):
        self.running = False
        
        # Join threads to ensure they stop accessing the stream
        if self.mic_thread and self.mic_thread.is_alive():
            try: self.mic_thread.join(timeout=1.0)
            except: pass
        if self.read_thread and self.read_thread.is_alive():
            try: self.read_thread.join(timeout=1.0)
            except: pass

        # Disconnect client
        if self.loop and self.client:
            try:
                future = asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)
                future.result(timeout=2.0)
            except: pass

        # Stop async loop
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.loop_thread and self.loop_thread.is_alive():
            try: self.loop_thread.join(timeout=1.0)
            except: pass

        try:
            if self.stream: 
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
        except: pass
        
        # Stop Wyoming server if we started it
        if self.server_started_by_us and self.server_process:
            wyoming_server_manager.stop_server(self.server_process)
            self.server_process = None
            self.server_started_by_us = False

    def pause(self):
        self.paused = True
    
    def resume(self):
        self.paused = False
        with self.text_queue.mutex:
             self.text_queue.queue.clear()

    def get_next_text(self):
        return self.text_queue.get()

    def _async_loop_worker(self):
        """Run asyncio event loop in dedicated thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        self.loop.close()

    async def _connect(self):
        """Connect to Wyoming server using AsyncTcpClient."""
        with self.client_lock:
            if self.client:
                return True
                
        print(f"debug: Connecting to {self.host}:{self.port}...")
        try:
            client = AsyncTcpClient(self.host, self.port)
            await client.connect()
            
            # Send Describe (handshake)
            await client.write_event(Describe().event())
            
            # Read Info response
            event = await client.read_event()
            if event:
                print(f"[Handshake]: Server {event.type}", flush=True)
            
            with self.client_lock:
                self.client = client
            
            # Start reader thread
            if not self.read_thread or not self.read_thread.is_alive():
                self.read_thread = threading.Thread(target=self._read_worker, daemon=True)
                self.read_thread.start()
            
            return True
            
        except Exception as e:
            print(f"err: Wyoming Connection Failed: {e}")
            return False

    async def _disconnect(self):
        """Disconnect from Wyoming server."""
        with self.client_lock:
            if self.client:
                try:
                    await self.client.disconnect()
                except: pass
                self.client = None

    def _read_worker(self):
        """Worker thread to read events from Wyoming server."""
        print("debug: Read worker started.")
        
        async def read_events():
            while self.running:
                with self.client_lock:
                    client = self.client
                    
                if not client:
                    await asyncio.sleep(0.1)
                    continue
                
                try:
                    event = await client.read_event()
                    if not event:
                        print("debug: Server closed connection.")
                        with self.client_lock:
                            self.client = None
                        break
                    
                    # Handle transcript events
                    if Transcript.is_type(event.type):
                        transcript = Transcript.from_event(event)
                        print(f"[RX]: Transcript: '{transcript.text}' (Final: True)", flush=True)
                        if transcript.text.strip():
                            self.text_queue.put(transcript.text.strip())
                    
                except Exception as e:
                    print(f"debug: Read Error: {e}")
                    with self.client_lock:
                        self.client = None
                    await asyncio.sleep(1)
        
        # Run async read loop
        asyncio.run_coroutine_threadsafe(read_events(), self.loop).result()

    async def _send_audio_start(self):
        """Send AudioStart event."""
        with self.client_lock:
            client = self.client
        if not client:
            return False
            
        try:
            audio_start = AudioStart(
                rate=self.sample_rate,
                width=2,
                channels=1
            )
            await client.write_event(audio_start.event())
            return True
        except Exception as e:
            print(f"debug: Send AudioStart failed: {e}")
            return False

    async def _send_audio_chunk(self, audio_data, timestamp):
        """Send AudioChunk event."""
        with self.client_lock:
            client = self.client
        if not client:
            return False
            
        try:
            chunk = AudioChunk(
                rate=self.sample_rate,
                width=2,
                channels=1,
                audio=audio_data,
                timestamp=timestamp
            )
            await client.write_event(chunk.event())
            return True
        except Exception as e:
            return False

    async def _send_audio_stop(self):
        """Send AudioStop event."""
        with self.client_lock:
            client = self.client
        if not client:
            return False
            
        try:
            audio_stop = AudioStop()
            await client.write_event(audio_stop.event())
            return True
        except Exception as e:
            return False

    def _mic_worker(self):
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            except: continue

            # Energy Calc
            try:
                count = len(data) // 2
                shorts = struct.unpack(f"{count}h", data)
                max_raw = max(abs(s) for s in shorts) if shorts else 0
            except: continue

            # --- VAD LOGIC ---
            SPEECH_THRESHOLD = 500  
            SILENCE_THRESHOLD = 500 
            SILENCE_LIMIT_MS = 1500 
            MAX_DURATION_MS = 10000 
            
            is_speech = max_raw > SPEECH_THRESHOLD
            
            # Start Speaking?
            if not self.is_speaking and is_speech:
                print("[VAD: Speech Started]", flush=True)
                self.is_speaking = True
                self.silence_timer = 0
                self.chunks_sent = 0
                
                # Connect if needed
                with self.client_lock:
                    client = self.client
                
                if not client:
                    future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
                    try:
                        if not future.result(timeout=5.0):
                            self.is_speaking = False
                            continue
                    except:
                        self.is_speaking = False
                        continue

                # Send AudioStart
                future = asyncio.run_coroutine_threadsafe(self._send_audio_start(), self.loop)
                try:
                    future.result(timeout=1.0)
                    print("debug: AudioStart sent.")
                except:
                    pass

            # Continue Speaking?
            if self.is_speaking:
                if max_raw < SILENCE_THRESHOLD:
                    self.silence_timer += self.chunk_duration_ms
                else:
                    self.silence_timer = 0
                
                # Send Chunk
                timestamp = int(self.chunks_sent * self.chunk_duration_ms)
                future = asyncio.run_coroutine_threadsafe(
                    self._send_audio_chunk(data, timestamp), 
                    self.loop
                )
                try:
                    if future.result(timeout=0.5):
                        self.chunks_sent += 1
                except:
                    with self.client_lock:
                        self.client = None

                # Check Stop Conditions
                current_duration = self.chunks_sent * self.chunk_duration_ms
                if self.silence_timer > SILENCE_LIMIT_MS or current_duration > MAX_DURATION_MS:
                     reason = "Silence" if self.silence_timer > SILENCE_LIMIT_MS else "Max Duration"
                     print(f"[VAD: Speech Stopped ({reason})]", flush=True)
                     self.is_speaking = False
                     
                     # Send AudioStop
                     future = asyncio.run_coroutine_threadsafe(self._send_audio_stop(), self.loop)
                     try:
                         future.result(timeout=1.0)
                     except:
                         pass

