#!/usr/bin/env python3
"""
Console version of Musico - displays track information in terminal instead of GUI
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
import threading

# Import pyaudioop compatibility module for Python 3.13+
try:
    import pyaudioop
except ImportError:
    # Create a compatibility module for Python 3.13+
    import pyaudioop_compat as pyaudioop
    sys.modules['pyaudioop'] = pyaudioop

from shazamio import Shazam
from config import SILENCE_THRESHOLD, SAMPLE_RATE, CHUNK_SIZE, RECORD_DURATION, LOG_LEVEL

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

class MusicIdentifierConsole:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.chunk_size = CHUNK_SIZE
        self.record_duration = RECORD_DURATION
        self.silence_threshold = SILENCE_THRESHOLD
        self.audio = pyaudio.PyAudio()
        self.shazam = Shazam()
        self.current_state = "silence"
        
    def print_status(self, message, color="white"):
        """Print status message with color coding"""
        colors = {
            "red": "\033[91m",      # Red for silence
            "green": "\033[92m",    # Green for music detected
            "yellow": "\033[93m",   # Yellow for music identified
            "blue": "\033[94m",     # Blue for info
            "white": "\033[97m",    # White for normal
            "reset": "\033[0m"      # Reset
        }
        
        print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}")
    
    def print_track_info(self, track_info):
        """Print track information in a nice format"""
        if not track_info:
            return
            
        print("\n" + "="*60)
        self.print_status("🎵 MUSIC IDENTIFIED!", "yellow")
        print("="*60)
        self.print_status(f"🎤 Artist: {track_info['artist']}", "green")
        self.print_status(f"🎵 Title:  {track_info['title']}", "green")
        if track_info['album'] != 'Unknown Album':
            self.print_status(f"💿 Album:  {track_info['album']}", "blue")
        if track_info['cover_url']:
            self.print_status(f"🖼️  Cover:  {track_info['cover_url']}", "blue")
        if track_info['shazam_url']:
            self.print_status(f"🔗 Shazam: {track_info['shazam_url']}", "blue")
        print("="*60)
    
    def print_state_change(self, state):
        """Print state change with appropriate color"""
        if state == "silence":
            self.print_status("🔇 SILENCE DETECTED", "red")
        elif state == "music_detected":
            self.print_status("🎵 MUSIC DETECTED - Identifying...", "green")
        elif state == "music_identified":
            self.print_status("✅ MUSIC IDENTIFIED!", "yellow")
        else:
            self.print_status(f"❓ UNKNOWN STATE: {state}", "white")
    
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
                input_device_index=1,  # default device
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
            if self.current_state != "silence":
                self.current_state = "silence"
                self.print_state_change("silence")
            return
        
        # Music detected
        if self.current_state != "music_detected":
            self.current_state = "music_detected"
            self.print_state_change("music_detected")
        
        logger.info("Music detected! Processing with Shazam...")
        
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
            
            if track_info:
                self.current_state = "music_identified"
                self.print_state_change("music_identified")
                self.print_track_info(track_info)
                logger.info(f"Identified: {track_info['artist']} - {track_info['title']}")
            else:
                self.current_state = "music_detected"
                self.print_state_change("music_detected")
                logger.info("Could not identify the music")
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    async def main_loop(self):
        """Main loop that runs every 60 seconds"""
        logger.info("Starting Musico Console...")
        self.print_status("🎵 Musico Console Started", "blue")
        self.print_status("Listening for music...", "white")
        
        try:
            while True:
                logger.info("Starting new audio sample...")
                await self.process_audio_sample()
                
                # Wait 60 seconds before next sample
                logger.info("Waiting 60 seconds before next sample...")
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.print_status("👋 Musico Console Stopped", "blue")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.audio.terminate()

def main():
    """Main entry point"""
    identifier = MusicIdentifierConsole()
    
    try:
        # Run the async main loop
        asyncio.run(identifier.main_loop())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
