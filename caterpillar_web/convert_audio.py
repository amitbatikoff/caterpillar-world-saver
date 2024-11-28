import os

def cleanup_wav_files():
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    wav_files = [f for f in os.listdir(assets_dir) if f.endswith('.wav')]
    
    for wav_file in wav_files:
        wav_path = os.path.join(assets_dir, wav_file)
        ogg_path = os.path.join(assets_dir, wav_file.replace('.wav', '.ogg'))
        
        # Only remove WAV if corresponding OGG exists
        if os.path.exists(ogg_path):
            try:
                os.remove(wav_path)
                print(f"Removed {wav_file} since {wav_file.replace('.wav', '.ogg')} exists")
            except Exception as e:
                print(f"Error removing {wav_file}: {str(e)}")
        else:
            print(f"Warning: Keeping {wav_file} since {wav_file.replace('.wav', '.ogg')} does not exist")

if __name__ == "__main__":
    cleanup_wav_files()
