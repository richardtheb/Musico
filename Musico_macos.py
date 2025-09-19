#!/usr/bin/env python3
"""
Musico - Music Identification Tool (macOS Version)
A tool that listens for music and identifies it using Shazam API
Optimized for macOS with proper thread handling
"""

import asyncio
import logging
import os
import tempfile
import threading
import time
import tkinter as tk
from io import BytesIO

import numpy as np
import pyaudio
import requests
from PIL import Image, ImageTk
from shazamio import Shazam

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('musico.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MusicoMacOS:
    def __init__(self):
        self.audio = None
        self.stream = None
        self.shazam = Shazam()
        self.root = None
        self.cover_label = None
        self.status_label = None
        self.track_label = None
        self.running = False
        
        # Audio configuration for macOS
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        self.silence_threshold = 0.0002
        self.recording_duration = 2.0
        
        # macOS-specific audio device selection
        self.input_device_index = None
        self.setup_audio()
    
    def setup_audio(self):
        """Setup audio for macOS with automatic device detection"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # List available audio devices
            logger.info("Available audio devices:")
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    logger.info(f"  {i}: {info['name']} (inputs: {info['maxInputChannels']})")
                    if any(keyword in info['name'].lower() for keyword in ['microphone', 'mic', 'built-in', 'internal']):
                        self.input_device_index = i
                        logger.info(f"  Selected microphone: {info['name']}")
            
            if self.input_device_index is None:
                # Use default input device
                self.input_device_index = None
                logger.info("Using default input device")
            
        except Exception as e:
            logger.error(f"Error setting up audio: {e}")
            raise
    
    def setup_gui(self):
        """Setup the GUI for macOS (must be called on main thread)"""
        try:
            logger.info("Setting up GUI...")
            
            # Create main window
            self.root = tk.Tk()
            self.root.title("Musico - macOS")
            self.root.attributes('-fullscreen', True)
            self.root.configure(cursor='none')
            
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            logger.info(f"Screen dimensions: {screen_width}x{screen_height}")
            
            # Create main frame with full coverage
            main_frame = tk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Only cover image label - no text labels
            self.cover_label = tk.Label(main_frame, text="", 
                                      anchor="center", fg="white", bg="black")
            self.cover_label.pack(fill=tk.BOTH, expand=True)
            
            # Store references for state management (but don't display)
            self.status_label = None
            self.track_label = None
            
            # Set initial background to black (silence state)
            self.root.configure(bg="black")
            main_frame.configure(bg="black")
            
            # Add keyboard bindings
            self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
            self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))
            self.root.bind('<q>', lambda e: self.quit_app())
            self.root.bind('<Command-q>', lambda e: self.quit_app())
            
            # Set initial state
            self.update_gui(None, "silence")
            
            logger.info("GUI setup completed successfully - Full screen mode")
            
        except Exception as e:
            logger.error(f"Error setting up GUI: {e}")
            raise
    
    def quit_app(self):
        """Quit the application"""
        logger.info("Quitting Musico...")
        self.running = False
        if self.root:
            self.root.quit()
    
    def record_audio_sample(self):
        """Record a sample of audio from the microphone"""
        try:
            logger.info("Recording audio sample...")
            
            # Calculate number of frames needed
            frames_needed = int(self.sample_rate * self.recording_duration)
            
            # Open audio stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk_size
            )
            
            # Record audio
            frames = []
            for _ in range(0, int(frames_needed / self.chunk_size)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            # Stop and close stream
            stream.stop_stream()
            stream.close()
            
            # Convert to numpy array
            audio_data = b''.join(frames)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            logger.info(f"Recorded {len(audio_array)} samples")
            return audio_array
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
    def is_silent(self, audio_data):
        """Check if the audio data represents silence"""
        if audio_data is None or len(audio_data) == 0:
            return True
        
        # Calculate RMS (Root Mean Square) of the audio
        rms = np.sqrt(np.mean(audio_data**2))
        logger.info(f"Audio RMS level: {rms:.4f} (threshold: {self.silence_threshold})")
        
        is_silent = rms < self.silence_threshold
        logger.info(f"Silence detection: {'SILENCE' if is_silent else 'MUSIC DETECTED'}")
        
        return is_silent
    
    async def identify_music(self, audio_file):
        """Identify music using Shazam API"""
        try:
            logger.info("Sending audio to Shazam for identification...")
            result = await self.shazam.recognize_song(audio_file)
            
            if result and 'track' in result:
                track = result['track']
                track_info = {
                    'title': track.get('title', 'Unknown Title'),
                    'artist': track.get('subtitle', 'Unknown Artist'),
                    'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown Album'),
                    'cover_url': track.get('images', {}).get('coverart', ''),
                    'shazam_url': track.get('url', '')
                }
                logger.info(f"Identified: {track_info['artist']} - {track_info['title']}")
                return track_info
            else:
                logger.info("No music identified")
                return None
                
        except Exception as e:
            logger.error(f"Error identifying music: {e}")
            return None
    
    def display_cover_image(self, cover_url):
        """Display the cover image in the GUI"""
        try:
            logger.info(f"Downloading cover image from: {cover_url}")
            
            # Download the cover image
            response = requests.get(cover_url, timeout=10)
            response.raise_for_status()
            
            # Open and resize the image
            image = Image.open(BytesIO(response.content))
            logger.info(f"Original image size: {image.size}")
            
            # Get screen dimensions for full screen cover art
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Resize to fill the entire screen
            image = image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            logger.info(f"Resized image to: {image.size} (full screen)")
            
            # Convert to PhotoImage for tkinter
            photo = ImageTk.PhotoImage(image)
            
            # Update the cover label
            self.cover_label.configure(image=photo, text="")
            self.cover_label.image = photo  # Keep a reference
            
            logger.info("Cover image displayed successfully")
            
        except Exception as e:
            logger.error(f"Error displaying cover image: {e}")
            # Clear the cover label on error
            self.cover_label.configure(image='')
            self.cover_label.image = None
    
    def update_gui(self, track_info, state="silence"):
        """Update the GUI with background color and cover art only"""
        logger.info(f"update_gui called with state: {state}, track_info: {track_info}")
        if not self.root:
            logger.warning("GUI root not available, skipping update")
            return
        
        # Set background color based on state
        if state == "silence":
            bg_color = "black"
        elif state == "music_detected":
            bg_color = "white"
        elif state == "music_identified" and track_info:
            bg_color = "white"
        else:  # music_detected but not identified
            bg_color = "white"
        
        # Update background colors
        self.root.configure(bg=bg_color)
        self.cover_label.configure(bg=bg_color)
        
        # Handle cover image for identified music
        if state == "music_identified" and track_info and track_info.get('cover_url'):
            self.display_cover_image(track_info['cover_url'])
        else:
            # Clear cover image for other states
            self.cover_label.configure(image='', text="")
            self.cover_label.image = None
    
    async def process_audio_sample(self):
        """Main processing function for each audio sample"""
        # Record audio
        audio_data = self.record_audio_sample()
        
        if audio_data is None:
            logger.error("Failed to record audio")
            return
        
        # Check for silence
        if self.is_silent(audio_data):
            if self.root:
                self.root.after(0, lambda: self.update_gui(None, "silence"))
            return
        
        # Music detected - update GUI immediately
        if self.root:
            self.root.after(0, lambda: self.update_gui(None, "music_detected"))
        
        # Save audio to temporary file for Shazam
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            # Convert numpy array to WAV format
            import wave
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            # Identify music
            logger.info("Calling identify_music...")
            track_info = await self.identify_music(temp_file.name)
            logger.info(f"identify_music returned: {track_info}")
            
            # Update GUI with results
            if self.root:
                if track_info:
                    logger.info(f"Updating GUI with track info: {track_info['artist']} - {track_info['title']}")
                    self.root.after(0, lambda: self.update_gui(track_info, "music_identified"))
                else:
                    logger.info("No track info, updating GUI with music_detected state")
                    self.root.after(0, lambda: self.update_gui(None, "music_detected"))
            
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    def start_audio_processing(self):
        """Start audio processing in a background thread"""
        def audio_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def audio_loop():
                while self.running:
                    try:
                        logger.info("Starting new audio sample...")
                        await self.process_audio_sample()
                        logger.info("Waiting 60 seconds before next sample...")
                        await asyncio.sleep(60)
                    except Exception as e:
                        logger.error(f"Error in audio processing: {e}")
                        await asyncio.sleep(10)  # Wait before retrying
            
            try:
                loop.run_until_complete(audio_loop())
            finally:
                loop.close()
        
        self.audio_thread = threading.Thread(target=audio_thread, daemon=True)
        self.audio_thread.start()
    
    def run(self):
        """Main run loop - GUI runs on main thread"""
        logger.info("Starting Musico...")
        self.running = True
        
        # Setup GUI on main thread
        self.setup_gui()
        
        # Start audio processing in background thread
        self.start_audio_processing()
        
        # Run GUI main loop (this blocks on main thread)
        try:
            if self.root:
                self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Musico stopped by user")
        finally:
            self.running = False
            if self.audio:
                self.audio.terminate()

def main():
    """Main entry point"""
    musico = MusicoMacOS()
    musico.run()

if __name__ == "__main__":
    main()
