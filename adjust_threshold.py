#!/usr/bin/env python3
"""
Quick threshold adjustment tool for Musico
"""

def update_threshold(new_threshold):
    """Update the threshold in config.py"""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Replace the threshold line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('SILENCE_THRESHOLD'):
                lines[i] = f'SILENCE_THRESHOLD = {new_threshold}  # Lower values = more sensitive to quiet sounds'
                break
        
        with open('config.py', 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Updated threshold to {new_threshold}")
        return True
    except Exception as e:
        print(f"❌ Error updating threshold: {e}")
        return False

def main():
    """Test different threshold values"""
    print("Musico Threshold Adjuster")
    print("=" * 40)
    print("Current threshold: 0.0001")
    print("\nSuggested thresholds based on your environment:")
    print("  0.0001 - Very sensitive (detects very quiet sounds)")
    print("  0.0003 - Sensitive (detects quiet music)")
    print("  0.0005 - Current setting")
    print("  0.001  - Less sensitive")
    print("  0.002  - Not very sensitive")
    
    while True:
        try:
            choice = input("\nEnter new threshold (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                break
            
            new_threshold = float(choice)
            if update_threshold(new_threshold):
                print(f"\n🎉 Threshold updated! Now test with: python Musico.py")
                break
        except ValueError:
            print("Please enter a valid number (e.g., 0.0003)")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()

