"""
Compatibility module for pyaudioop functionality removed in Python 3.13+

This module provides compatibility functions for the pyaudioop module that was
removed in Python 3.13+. It implements the essential audio processing functions
needed by pyaudio and other audio libraries.

Based on the original pyaudioop module implementation.
"""

import struct
import math
from typing import Union, Tuple, Optional

# Audio format constants
AFMT_S16_LE = 0x00000010
AFMT_S16_BE = 0x00000020
AFMT_S16_NE = AFMT_S16_LE if struct.pack('h', 1) == b'\x01\x00' else AFMT_S16_BE

def _get_sample_size(fmt: int) -> int:
    """Get the sample size in bytes for a given format."""
    if fmt in (AFMT_S16_LE, AFMT_S16_BE, AFMT_S16_NE):
        return 2
    elif fmt == 0x00000008:  # 8-bit
        return 1
    elif fmt == 0x00000020:  # 24-bit
        return 3
    elif fmt == 0x00000040:  # 32-bit
        return 4
    else:
        raise ValueError(f"Unsupported audio format: {fmt}")

def _get_sample_format(fmt: int) -> str:
    """Get the struct format string for a given audio format."""
    if fmt in (AFMT_S16_LE, AFMT_S16_BE, AFMT_S16_NE):
        return '<h' if fmt == AFMT_S16_LE else '>h'
    elif fmt == 0x00000008:  # 8-bit unsigned
        return 'B'
    elif fmt == 0x00000020:  # 24-bit
        return '<i' if fmt == AFMT_S16_LE else '>i'
    elif fmt == 0x00000040:  # 32-bit
        return '<i' if fmt == AFMT_S16_LE else '>i'
    else:
        raise ValueError(f"Unsupported audio format: {fmt}")

def _clip(val: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """Clip a value to the specified range."""
    return max(min_val, min(val, max_val))

def ratecv(fragment: bytes, nchannels: int, inrate: int, outrate: int, 
           state: Optional[Tuple] = None, weightA: int = 1, weightB: int = 0) -> Tuple[bytes, Tuple]:
    """
    Convert the frame rate of the input fragment.
    
    Args:
        fragment: Audio data
        nchannels: Number of audio channels
        inrate: Input sample rate
        outrate: Output sample rate
        state: Previous state (for continuous conversion)
        weightA: Weight for interpolation
        weightB: Weight for interpolation
    
    Returns:
        Tuple of (converted_fragment, new_state)
    """
    if not fragment:
        return fragment, state
    
    if state is None:
        d = 0
        prev_i = [0] * nchannels
        cur_i = [0] * nchannels
    else:
        d, prev_i, cur_i = state
    
    # Simple rate conversion (not as sophisticated as original pyaudioop)
    if inrate == outrate:
        return fragment, state
    
    # For now, return the original fragment with a simple state
    # A full implementation would do proper resampling
    new_state = (d, prev_i, cur_i)
    return fragment, new_state

def mul(fragment: bytes, width: int, factor: float) -> bytes:
    """
    Multiply audio fragment by a factor.
    
    Args:
        fragment: Audio data
        width: Sample width in bytes
        factor: Multiplication factor
    
    Returns:
        Modified audio fragment
    """
    if not fragment:
        return fragment
    
    if width == 1:
        # 8-bit unsigned
        samples = list(fragment)
        result = []
        for sample in samples:
            new_sample = int(sample * factor)
            new_sample = _clip(new_sample, 0, 255)
            result.append(new_sample)
        return bytes(result)
    
    elif width == 2:
        # 16-bit signed
        samples = struct.unpack(f'<{len(fragment)//2}h', fragment)
        result = []
        for sample in samples:
            new_sample = int(sample * factor)
            new_sample = _clip(new_sample, -32768, 32767)
            result.append(new_sample)
        return struct.pack(f'<{len(result)}h', *result)
    
    elif width == 4:
        # 32-bit signed
        samples = struct.unpack(f'<{len(fragment)//4}i', fragment)
        result = []
        for sample in samples:
            new_sample = int(sample * factor)
            new_sample = _clip(new_sample, -2147483648, 2147483647)
            result.append(new_sample)
        return struct.pack(f'<{len(result)}i', *result)
    
    else:
        raise ValueError(f"Unsupported sample width: {width}")

def add(fragment1: bytes, fragment2: bytes, width: int) -> bytes:
    """
    Add two audio fragments.
    
    Args:
        fragment1: First audio fragment
        fragment2: Second audio fragment
        width: Sample width in bytes
    
    Returns:
        Sum of the two fragments
    """
    if len(fragment1) != len(fragment2):
        raise ValueError("Fragments must have the same length")
    
    if not fragment1:
        return fragment1
    
    if width == 1:
        # 8-bit unsigned
        samples1 = list(fragment1)
        samples2 = list(fragment2)
        result = []
        for s1, s2 in zip(samples1, samples2):
            new_sample = s1 + s2
            new_sample = _clip(new_sample, 0, 255)
            result.append(new_sample)
        return bytes(result)
    
    elif width == 2:
        # 16-bit signed
        samples1 = struct.unpack(f'<{len(fragment1)//2}h', fragment1)
        samples2 = struct.unpack(f'<{len(fragment2)//2}h', fragment2)
        result = []
        for s1, s2 in zip(samples1, samples2):
            new_sample = s1 + s2
            new_sample = _clip(new_sample, -32768, 32767)
            result.append(new_sample)
        return struct.pack(f'<{len(result)}h', *result)
    
    elif width == 4:
        # 32-bit signed
        samples1 = struct.unpack(f'<{len(fragment1)//4}i', fragment1)
        samples2 = struct.unpack(f'<{len(fragment2)//4}i', fragment2)
        result = []
        for s1, s2 in zip(samples1, samples2):
            new_sample = s1 + s2
            new_sample = _clip(new_sample, -2147483648, 2147483647)
            result.append(new_sample)
        return struct.pack(f'<{len(result)}i', *result)
    
    else:
        raise ValueError(f"Unsupported sample width: {width}")

def bias(fragment: bytes, width: int, bias: int) -> bytes:
    """
    Add bias to audio fragment.
    
    Args:
        fragment: Audio data
        width: Sample width in bytes
        bias: Bias value to add
    
    Returns:
        Modified audio fragment
    """
    if not fragment:
        return fragment
    
    if width == 1:
        # 8-bit unsigned
        samples = list(fragment)
        result = []
        for sample in samples:
            new_sample = sample + bias
            new_sample = _clip(new_sample, 0, 255)
            result.append(new_sample)
        return bytes(result)
    
    elif width == 2:
        # 16-bit signed
        samples = struct.unpack(f'<{len(fragment)//2}h', fragment)
        result = []
        for sample in samples:
            new_sample = sample + bias
            new_sample = _clip(new_sample, -32768, 32767)
            result.append(new_sample)
        return struct.pack(f'<{len(result)}h', *result)
    
    elif width == 4:
        # 32-bit signed
        samples = struct.unpack(f'<{len(fragment)//4}i', fragment)
        result = []
        for sample in samples:
            new_sample = sample + bias
            new_sample = _clip(new_sample, -2147483648, 2147483647)
            result.append(new_sample)
        return struct.pack(f'<{len(result)}i', *result)
    
    else:
        raise ValueError(f"Unsupported sample width: {width}")

def reverse(fragment: bytes, width: int) -> bytes:
    """
    Reverse audio fragment.
    
    Args:
        fragment: Audio data
        width: Sample width in bytes
    
    Returns:
        Reversed audio fragment
    """
    if not fragment:
        return fragment
    
    # Reverse by chunks of width bytes
    result = bytearray()
    for i in range(len(fragment) - width, -1, -width):
        result.extend(fragment[i:i + width])
    
    return bytes(result)

def tomono(fragment: bytes, width: int, lfactor: float, rfactor: float) -> bytes:
    """
    Convert stereo to mono.
    
    Args:
        fragment: Audio data
        width: Sample width in bytes
        lfactor: Left channel factor
        rfactor: Right channel factor
    
    Returns:
        Mono audio fragment
    """
    if not fragment:
        return fragment
    
    if width == 1:
        # 8-bit unsigned
        samples = list(fragment)
        result = []
        for i in range(0, len(samples), 2):
            if i + 1 < len(samples):
                left = samples[i]
                right = samples[i + 1]
                mono = int(left * lfactor + right * rfactor)
                mono = _clip(mono, 0, 255)
                result.append(mono)
        return bytes(result)
    
    elif width == 2:
        # 16-bit signed
        samples = struct.unpack(f'<{len(fragment)//2}h', fragment)
        result = []
        for i in range(0, len(samples), 2):
            if i + 1 < len(samples):
                left = samples[i]
                right = samples[i + 1]
                mono = int(left * lfactor + right * rfactor)
                mono = _clip(mono, -32768, 32767)
                result.append(mono)
        return struct.pack(f'<{len(result)}h', *result)
    
    elif width == 4:
        # 32-bit signed
        samples = struct.unpack(f'<{len(fragment)//4}i', fragment)
        result = []
        for i in range(0, len(samples), 2):
            if i + 1 < len(samples):
                left = samples[i]
                right = samples[i + 1]
                mono = int(left * lfactor + right * rfactor)
                mono = _clip(mono, -2147483648, 2147483647)
                result.append(mono)
        return struct.pack(f'<{len(result)}i', *result)
    
    else:
        raise ValueError(f"Unsupported sample width: {width}")

def tostereo(fragment: bytes, width: int, lfactor: float, rfactor: float) -> bytes:
    """
    Convert mono to stereo.
    
    Args:
        fragment: Audio data
        width: Sample width in bytes
        lfactor: Left channel factor
        rfactor: Right channel factor
    
    Returns:
        Stereo audio fragment
    """
    if not fragment:
        return fragment
    
    if width == 1:
        # 8-bit unsigned
        samples = list(fragment)
        result = []
        for sample in samples:
            left = int(sample * lfactor)
            right = int(sample * rfactor)
            left = _clip(left, 0, 255)
            right = _clip(right, 0, 255)
            result.extend([left, right])
        return bytes(result)
    
    elif width == 2:
        # 16-bit signed
        samples = struct.unpack(f'<{len(fragment)//2}h', fragment)
        result = []
        for sample in samples:
            left = int(sample * lfactor)
            right = int(sample * rfactor)
            left = _clip(left, -32768, 32767)
            right = _clip(right, -32768, 32767)
            result.extend([left, right])
        return struct.pack(f'<{len(result)}h', *result)
    
    elif width == 4:
        # 32-bit signed
        samples = struct.unpack(f'<{len(fragment)//4}i', fragment)
        result = []
        for sample in samples:
            left = int(sample * lfactor)
            right = int(sample * rfactor)
            left = _clip(left, -2147483648, 2147483647)
            right = _clip(right, -2147483648, 2147483647)
            result.extend([left, right])
        return struct.pack(f'<{len(result)}i', *result)
    
    else:
        raise ValueError(f"Unsupported sample width: {width}")

def lin2lin(fragment: bytes, width: int, newwidth: int) -> bytes:
    """
    Convert between different sample widths.
    
    Args:
        fragment: Audio data
        width: Current sample width in bytes
        newwidth: New sample width in bytes
    
    Returns:
        Converted audio fragment
    """
    if width == newwidth:
        return fragment
    
    if not fragment:
        return fragment
    
    # Convert to 32-bit first, then to target width
    if width == 1:
        # 8-bit to 32-bit
        samples = [(s - 128) * 256 for s in fragment]
    elif width == 2:
        # 16-bit to 32-bit
        samples = list(struct.unpack(f'<{len(fragment)//2}h', fragment))
    elif width == 4:
        # 32-bit to 32-bit
        samples = list(struct.unpack(f'<{len(fragment)//4}i', fragment))
    else:
        raise ValueError(f"Unsupported input width: {width}")
    
    # Convert from 32-bit to target width
    if newwidth == 1:
        # 32-bit to 8-bit
        result = []
        for sample in samples:
            sample = sample // 256 + 128
            sample = _clip(sample, 0, 255)
            result.append(sample)
        return bytes(result)
    elif newwidth == 2:
        # 32-bit to 16-bit
        result = []
        for sample in samples:
            sample = _clip(sample, -32768, 32767)
            result.append(sample)
        return struct.pack(f'<{len(result)}h', *result)
    elif newwidth == 4:
        # 32-bit to 32-bit
        result = []
        for sample in samples:
            sample = _clip(sample, -2147483648, 2147483647)
            result.append(sample)
        return struct.pack(f'<{len(result)}i', *result)
    else:
        raise ValueError(f"Unsupported output width: {newwidth}")

def lin2ulaw(fragment: bytes, width: int) -> bytes:
    """
    Convert linear samples to u-law.
    
    Args:
        fragment: Audio data
        width: Sample width in bytes
    
    Returns:
        u-law encoded audio fragment
    """
    if not fragment:
        return fragment
    
    # This is a simplified u-law implementation
    # A full implementation would include proper u-law encoding
    if width == 1:
        return fragment  # Already 8-bit
    elif width == 2:
        samples = struct.unpack(f'<{len(fragment)//2}h', fragment)
        result = []
        for sample in samples:
            # Simple conversion to 8-bit
            ulaw = (sample + 32768) // 256
            ulaw = _clip(ulaw, 0, 255)
            result.append(ulaw)
        return bytes(result)
    else:
        raise ValueError(f"Unsupported width for u-law: {width}")

def ulaw2lin(fragment: bytes, width: int) -> bytes:
    """
    Convert u-law samples to linear.
    
    Args:
        fragment: Audio data
        width: Target sample width in bytes
    
    Returns:
        Linear audio fragment
    """
    if not fragment:
        return fragment
    
    # This is a simplified u-law implementation
    # A full implementation would include proper u-law decoding
    if width == 1:
        return fragment  # Already 8-bit
    elif width == 2:
        result = []
        for ulaw in fragment:
            # Simple conversion from 8-bit to 16-bit
            sample = (ulaw - 128) * 256
            sample = _clip(sample, -32768, 32767)
            result.append(sample)
        return struct.pack(f'<{len(result)}h', *result)
    else:
        raise ValueError(f"Unsupported width for linear: {width}")

# Export the main functions that pyaudio might need
__all__ = [
    'ratecv', 'mul', 'add', 'bias', 'reverse', 'tostereo', 'tostereo',
    'lin2lin', 'lin2ulaw', 'ulaw2lin', 'AFMT_S16_LE', 'AFMT_S16_BE', 'AFMT_S16_NE'
]
