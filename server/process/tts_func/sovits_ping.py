import requests
### MUST START SERVERS FIRST USING START ALL SERVER SCRIPT
import time
import soundfile as sf 
import sounddevice as sd
import yaml

# Load YAML config
with open('../../../character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)


def play_audio(path):
    data, samplerate = sf.read(path)
    sd.play(data, samplerate)
    sd.wait()  # Wait until playback is finished

def sovits_gen(in_text, output_wav_pth = "output.wav"):
    url = "http://127.0.0.1:9880/"

    params = {
        "text": in_text,
        "text_language": char_config['sovits_ping_config']['text_lang'],
        "refer_wav_path": char_config['sovits_ping_config']['ref_audio_path'],  # Make sure this path is valid
        "prompt_text": char_config['sovits_ping_config']['prompt_text'],
        "prompt_language": char_config['sovits_ping_config']['prompt_lang']
    }

    try:
        print(f"🎵 Requesting TTS from GPT-SoVITS...")
        print(f"   Text: {in_text}")
        print(f"   Language: {params['text_language']}")
        print(f"   Reference: {params['refer_wav_path']}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"   Raw response: {response.text[:200]}...")
        
        response.raise_for_status()  # throws if not 200

        print(f"✅ Response status: {response.status_code}")
        print(f"   Content length: {len(response.content)} bytes")

        # Save the response audio if it's binary
        with open(output_wav_pth, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Audio saved as {output_wav_pth}")
        return output_wav_pth

    except Exception as e:
        print(f"❌ Error in sovits_gen: {e}")
        return None



if __name__ == "__main__":

    start_time = time.time()
    output_wav_pth1 = "output.wav"
    path_to_aud = sovits_gen("Hello Tyler", output_wav_pth1)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    print(path_to_aud)
    
    if path_to_aud:
        print("✅ GPT-SoVITS is working! Playing audio...")
        play_audio(path_to_aud)
    else:
        print("❌ GPT-SoVITS failed")


