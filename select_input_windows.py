#!/usr/bin/env python3
"""
Windows Audio Device Selector for Musico
Lists available audio input devices and allows selection
"""

import pyaudio
import sys

def list_audio_devices():
    """List all available audio input devices"""
    print("Musico Windows - Audio Device Selector")
    print("=" * 40)
    
    try:
        audio = pyaudio.PyAudio()
        
        print("\nAvailable audio input devices:")
        print("-" * 40)
        
        input_devices = []
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append((i, info))
                print(f"  {i}: {info['name']}")
                print(f"      Channels: {info['maxInputChannels']}")
                print(f"      Sample Rate: {info['defaultSampleRate']}")
                print()
        
        if not input_devices:
            print("No input devices found!")
            return None
        
        # Try to find a microphone device
        microphone_device = None
        for device_id, info in input_devices:
            if any(keyword in info['name'].lower() for keyword in ['microphone', 'mic', 'audio', 'input']):
                microphone_device = device_id
                print(f"Auto-selected microphone: {info['name']} (Device {device_id})")
                break
        
        if microphone_device is None:
            # Use the first available input device
            microphone_device = input_devices[0][0]
            print(f"Using first available device: {input_devices[0][1]['name']} (Device {microphone_device})")
        
        audio.terminate()
        return microphone_device
        
    except Exception as e:
        print(f"Error listing audio devices: {e}")
        return None

def test_audio_device(device_id):
    """Test recording from a specific audio device"""
    print(f"\nTesting audio device {device_id}...")
    
    try:
        audio = pyaudio.PyAudio()
        
        # Test recording
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            input_device_index=device_id,
            frames_per_buffer=1024
        )
        
        print("Recording 2 seconds of audio...")
        frames = []
        for _ in range(0, int(44100 / 1024 * 2)):
            data = stream.read(1024)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        print("Audio recording test successful!")
        return True
        
    except Exception as e:
        print(f"Error testing audio device: {e}")
        return False

def main():
    """Main function"""
    print("Musico Windows Audio Setup")
    print("=" * 30)
    
    # List devices
    device_id = list_audio_devices()
    
    if device_id is None:
        print("No suitable audio device found!")
        input("Press Enter to exit...")
        return
    
    # Test the device
    if test_audio_device(device_id):
        print(f"\n✅ Audio device {device_id} is working correctly!")
        print("You can now run Musico with: run_windows.bat")
    else:
        print(f"\n❌ Audio device {device_id} failed the test!")
        print("Please check your microphone settings and try again.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
