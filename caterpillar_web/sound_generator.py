import wave
import math
import struct
import os

def generate_sine_wave(frequency, duration, amplitude=0.5, sample_rate=22050):  # Lower sample rate for web
    n_samples = int(sample_rate * duration)
    samples = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        sample = amplitude * math.sin(2.0 * math.pi * frequency * t)
        samples.append(sample)
    return samples

def generate_square_wave(frequency, duration, amplitude=0.5, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    samples = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        if math.sin(2.0 * math.pi * frequency * t) >= 0:
            sample = amplitude
        else:
            sample = -amplitude
        samples.append(sample)
    return samples

def save_wave(samples, filename, sample_rate=22050):
    # Convert samples to 16-bit integers
    packed_samples = []
    for sample in samples:
        packed_value = int(sample * 32767.0)
        packed_samples.append(struct.pack('h', packed_value))

    # Create WAV file
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(packed_samples))

def create_collision_sound():
    # Quick descending tone
    samples = generate_sine_wave(440, 0.05, 0.8)  # Shorter duration
    samples.extend(generate_sine_wave(220, 0.05, 0.6))
    save_wave(samples, './assets/collision.wav')

def create_convert_sound():
    # Rising cheerful tone
    samples = generate_sine_wave(440, 0.05, 0.5)  # Shorter duration
    samples.extend(generate_sine_wave(880, 0.1, 0.6))
    save_wave(samples, './assets/convert.wav')

def create_stage_complete_sound():
    # Victory fanfare
    samples = generate_sine_wave(440, 0.05, 0.5)  # Shorter duration
    samples.extend(generate_sine_wave(550, 0.05, 0.5))
    samples.extend(generate_sine_wave(660, 0.1, 0.6))
    save_wave(samples, './assets/stage_complete.wav')

def create_game_over_sound():
    # Sad descending tones
    samples = generate_sine_wave(440, 0.1, 0.6)
    samples.extend(generate_sine_wave(330, 0.1, 0.5))
    samples.extend(generate_sine_wave(220, 0.15, 0.4))
    save_wave(samples, './assets/game_over.wav')

def main():
    # Ensure assets directory exists
    os.makedirs('./assets', exist_ok=True)
    
    # Generate all sound effects
    create_collision_sound()
    create_convert_sound()
    create_stage_complete_sound()
    create_game_over_sound()
    print("Sound files generated successfully in ./assets directory")

if __name__ == '__main__':
    main()
