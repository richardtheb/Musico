#!/usr/bin/env python3
"""
Audio Input Device Selector for Musico
"""

import pyaudio
import sys

def list_audio_devices():
    """List available audio input devices"""
    audio = pyaudio.PyAudio()
    
    print("Available audio input devices:")
    input_devices = []
    
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            input_devices.append((i, info))
            print(f"  {i}: {info['name']} (Channels: {info['maxInputChannels']})")
    
    audio.terminate()
    return input_devices

def select_device():
    """Let user select audio input device"""
    input_devices = list_audio_devices()
    
    if not input_devices:
        print("No input devices found!")
        return None
        
    if len(input_devices) == 1:
        device_id = input_devices[0][0]
        print(f"\nOnly one device found. Using: {input_devices[0][1]['name']}")
        return device_id
        
    print(f"\nSelect your preferred audio input device:")
    
    while True:
        try:
            choice = input(f"Enter device number (0-{len(input_devices)-1}): ").strip()
            device_id = int(choice)
            
            if 0 <= device_id < len(input_devices):
                selected_device = input_devices[device_id]
                print(f"\n✅ Selected: {selected_device[1]['name']}")
                return device_id
            else:
                print("Invalid choice. Please try again.")
                
        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            return None

def update_musico_config(device_id):
    """Update Musico.py to use the selected device"""
    try:
        with open('Musico.py', 'r') as f:
            content = f.read()
        
        # Find the record_audio_sample method and update the stream creation
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if 'stream = self.audio.open(' in line:
                # Look for the stream creation block
                for j in range(i, min(i+15, len(lines))):
                    if 'input_device_index=None' in lines[j]:
                        lines[j] = f"                input_device_index={device_id},  # Selected audio device"
                        updated = True
                        break
                    elif 'input_device_index' not in lines[j] and 'stream_callback=None' in lines[j]:
                        # Insert the parameter before stream_callback
                        lines[j] = f"                input_device_index={device_id},  # Selected audio device"
                        lines.insert(j+1, f"                stream_callback=None")
                        updated = True
                        break
                    elif ')' in lines[j] and 'input_device_index' not in content:
                        # Insert the parameter before the closing parenthesis
                        lines[j] = f"                input_device_index={device_id},  # Selected audio device\n{lines[j]}"
                        updated = True
                        break
        
        if updated:
            with open('Musico.py', 'w') as f:
                f.write('\n'.join(lines))
            print(f"✅ Updated Musico.py to use device {device_id}")
            return True
        else:
            print("⚠️  Could not automatically update Musico.py")
            print(f"   Please manually set input_device_index={device_id} in the record_audio_sample method")
            return False
            
    except Exception as e:
        print(f"❌ Error updating Musico.py: {e}")
        return False

def main():
    """Main function"""
    print("Musico Audio Input Selector")
    print("=" * 40)
    
    # List available devices
    input_devices = list_audio_devices()
    
    if not input_devices:
        print("No audio input devices found!")
        return
    
    # Let user select device
    device_id = select_device()
    
    if device_id is not None:
        # Update Musico configuration
        if update_musico_config(device_id):
            print(f"\n🎉 Configuration updated!")
            print("You can now run Musico with: python Musico.py")
        else:
            print(f"\n⚠️  Manual configuration required")
            print(f"Set input_device_index={device_id} in Musico.py")

if __name__ == "__main__":
    main()
