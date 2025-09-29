#!/usr/bin/env python3
"""
Raspberry Pi Music Identifier
Samples audio every 60 seconds, detects music, and identifies tracks using Shazam.
"""

import pyaudio
import wave
import numpy as np
import time
import logging
import os
import sys
from pathlib import Path
import asyncio
from PIL import Image
import requests
from io import BytesIO
import tkinter as tk
from tkinter import ttk
import threading

# Import pyaudioop compatibility module for Python 3.13+
try:
    import pyaudioop
except ImportError:
    # Create a compatibility module for Python 3.13+
    import pyaudioop_compat as pyaudioop
    sys.modules['pyaudioop'] = pyaudioop

from shazamio import Shazam
from config import SILENCE_THRESHOLD, SAMPLE_RATE, CHUNK_SIZE, RECORD_DURATION, WINDOW_WIDTH, WINDOW_HEIGHT, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Musico.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MusicIdentifier:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.chunk_size = CHUNK_SIZE
        self.record_duration = RECORD_DURATION
        self.silence_threshold = SILENCE_THRESHOLD
        self.audio = pyaudio.PyAudio()
        self.shazam = Shazam()
        self.root = None
        self.cover_label = None
        
    def setup_gui(self):
        """Setup the GUI for displaying cover images"""
        try:
            logger.info("Setting up GUI...")
            self.root = tk.Tk()
            self.root.title("Musico")
            
            # Make window full screen
            self.root.attributes('-fullscreen', True)
            self.root.state('zoomed') #Fixes fullscreeen bug, makes it truly fullscreen
            self.root.configure(cursor='none')  # Hide cursor for cleaner look
            
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
            
            # Set initial state to silence
            self.update_gui(None, "silence")
            
            # Bind Escape key to exit full screen
            self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
            self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))
            
            logger.info("GUI setup completed successfully - Full screen mode")
            
        except Exception as e:
            logger.error(f"Error setting up GUI: {e}")
            self.root = None
        
    def record_audio_sample(self):
        """Record a sample of audio from the default input device"""
        try:
            # Open audio stream with better error handling
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,  # Mono
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=1,  # Selected audio device
                stream_callback=None
            )
            
            logger.info("Recording audio sample...")
            frames = []
            
            # Record for the specified duration
            for _ in range(0, int(self.sample_rate / self.chunk_size * self.record_duration)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            
            # Convert to numpy array for analysis
            audio_data = b''.join(frames)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
    def is_silent(self, audio_data):
        """Check if the audio sample is silent or very quiet"""
        if audio_data is None or len(audio_data) == 0:
            return True
            
        # Calculate RMS (Root Mean Square) to determine volume
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Normalize RMS to 0-1 range
        normalized_rms = rms / 32768.0  # 32768 is max value for 16-bit audio
        
        logger.info(f"Audio RMS level: {normalized_rms:.4f} (threshold: {self.silence_threshold:.4f})")
        
        is_silent = normalized_rms < self.silence_threshold
        logger.info(f"Silence detection: {'SILENT' if is_silent else 'MUSIC DETECTED'}")
        
        return is_silent
    
    def save_audio_sample(self, audio_data, filename="temp_audio.wav"):
        """Save audio data to a temporary WAV file for Shazam processing"""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            return filename
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            return None
    
    async def identify_music(self, audio_file):
        """Use Shazam to identify the music in the audio file"""
        try:
            logger.info("Sending audio to Shazam for identification...")
            result = await self.shazam.recognize(audio_file)
            
            if result and 'track' in result:
                track = result['track']
                return {
                    'title': track.get('title', 'Unknown'),
                    'artist': track.get('subtitle', 'Unknown Artist'),
                    'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown Album'),
                    'cover_url': track.get('images', {}).get('coverart', ''),
                    'shazam_url': track.get('url', '')
                }
            else:
                logger.info("No music identified in the sample")
                return None
                
        except Exception as e:
            logger.error(f"Error identifying music: {e}")
            return None
    
    def display_cover_image(self, cover_url):
        """Display the cover image in the GUI"""
        if not cover_url or not self.root:
            logger.warning("No cover URL or GUI not available")
            return
            
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
            from PIL import ImageTk
            photo = ImageTk.PhotoImage(image)
            
            # Update the cover label
            self.cover_label.configure(image=photo)
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
        
        # Check if silent
        if self.is_silent(audio_data):
            logger.info("Audio sample is silent, skipping...")
            if self.root:
                self.root.after(0, lambda: self.update_gui(None, "silence"))
            return
        
        logger.info("Music detected! Processing with Shazam...")
        
        # Update GUI to show music detected state
        if self.root:
            self.root.after(0, lambda: self.update_gui(None, "music_detected"))
        
        # Save audio to temporary file
        temp_file = self.save_audio_sample(audio_data)
        if not temp_file:
            logger.error("Failed to save audio file")
            return
        
        try:
            # Identify music
            logger.info("Calling identify_music...")
            track_info = await self.identify_music(temp_file)
            logger.info(f"identify_music returned: {track_info}")
            
            # Update GUI based on identification result
            if self.root:
                if track_info:
                    logger.info(f"Updating GUI with track info: {track_info['artist']} - {track_info['title']}")
                    self.root.after(0, lambda: self.update_gui(track_info, "music_identified"))
                    logger.info(f"Identified: {track_info['artist']} - {track_info['title']}")
                else:
                    logger.info("No track info, updating GUI with music_detected state")
                    self.root.after(0, lambda: self.update_gui(None, "music_detected"))
                    logger.info("Could not identify the music")
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def run_gui_loop(self):
        """Run the GUI main loop in a separate thread"""
        # Setup GUI first
        self.setup_gui()
        if self.root:
            self.root.mainloop()
    
    async def main_loop(self):
        """Main loop that runs every 60 seconds"""
        logger.info("Starting Musico...")
        
        # Setup GUI in a separate thread
        gui_thread = threading.Thread(target=self.run_gui_loop, daemon=True)
        gui_thread.start()
        
        # Give GUI time to initialize
        await asyncio.sleep(1)
        
        try:
            while True:
                logger.info("Starting new audio sample...")
                await self.process_audio_sample()
                
                # Wait 60 seconds before next sample
                logger.info("Waiting 60 seconds before next sample...")
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.audio.terminate()
            if self.root:
                self.root.quit()

def main():
    """Main entry point"""
    identifier = MusicIdentifier()
    
    try:
        # Run the async main loop
        asyncio.run(identifier.main_loop())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

