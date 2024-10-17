
import sounddevice as sd
import numpy as np
import subprocess
import threading
import math, time
import os, json
from openai import OpenAI
from scipy.io.wavfile import read, write
from adafruit_servokit import ServoKit

FREQUENCY = 44100
DURATIION = 5
RECORDED_FILE = "recording.wav"
RESPONSE_FILE = "response.wav"
CONVERSATION_HISTORY_FILE = "conversations.txt"
PIPER_MODEL_PATH = "<insert path to piper binary>"
RESPONSE_TO_SERVO_PAUSE = 0.5
ITERATIONS_TO_FORGET = 10
OPEN_ANGLE, CLOSED_ANGLE = 100, 150 # Servo angles at which jaw is open/closed
client = OpenAI(api_key="<YOUR OPENAI API KEY HERE>")
kit = ServoKit(channels=16)


def get_prompt(conversation_history = ""):
    print(conversation_history)
    return f"""
    You are an animatronic talking skull in a person's front yard. It is Halloween time and people will want to talk with you. 
    You need to be dark and somewhat ominous. If you have an opportunity to be witty or sarcastic, then take it, but don't be corny. 
    One-sentence answers are often the most appropriate but you can be slightly longer if it's necessary.
    corny. No emojis. In triple backticks is the previous conversation you have had so far. The most recent messages are at the bottom.

    ```
    {conversation_history}
    ```
    """


def send_to_gpt(text, prompt, temperature = 0.5):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
    )
    return response.choices[0].message.content


def get_text_from_audio():
    recording = sd.rec(int(DURATIION * FREQUENCY), samplerate=FREQUENCY, channels=1)

    # Record audio for the given number of seconds
    sd.wait()
    print("done recording...")
    write(RECORDED_FILE, FREQUENCY, recording)
    audio_file= open(RECORDED_FILE, "rb")
    transcription = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file
    )
    return transcription.text


def respond_to_audio(prompt):
    text = get_text_from_audio()
    response = send_to_gpt(text, prompt)
    return response
    

def record_until_silence(duration=0.75, threshold=0.1, samplerate=44100):
    """Records audio until a period of silence is detected."""
    print("Recording...")
    audio_data = []
    silent_time = 0

    while True:
        print(".", end="")
        chunk = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1)
        sd.wait()  # Wait for recording to finish
        # Check if the audio is below the threshold (silence)
        if np.abs(chunk).max() < threshold:
            silent_time += duration
        else:
            audio_data.append(chunk)
            silent_time = 0

        # Stop recording if silent for a certain period
        if silent_time > 1.5:  # Adjust this value as needed
            break

    print("Recording finished.")
    print(len(audio_data))
    if audio_data:
        return np.concatenate(audio_data)
        
 
def run_speech():
    subprocess.call(f"aplay {RESPONSE_FILE}", 
                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        

def run_servo():
    sample_rate, myrecording = read(RESPONSE_FILE)

    len(myrecording), sample_rate
    WINDOW_SIZE = 500
    recording_len = len(myrecording)
    myrecording = myrecording/np.max(np.abs(myrecording))

    for i in range(0, math.ceil(recording_len/WINDOW_SIZE)):
        window = myrecording[i*WINDOW_SIZE:(i+1)*WINDOW_SIZE]
        # volume = np.sqrt(np.mean(window**2))
        volume = max(window)
        angle = int(np.interp(volume, [0, 1.0], [CLOSED_ANGLE, OPEN_ANGLE]))
        print(volume, angle)
        kit.servo[0].angle = angle
        time.sleep(WINDOW_SIZE/sample_rate)


def main():
    new_session = True
    while True:
        if new_session:
            history = []
            cnt = 0
            new_session = False
        audio_data = record_until_silence()
        if audio_data is not None:
            print("writing file")
            write(RECORDED_FILE, FREQUENCY, audio_data)
            audio_data = open(RECORDED_FILE, "rb")
            print("getting transcription")
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data
            )
            text = transcription.text
            print("Speech to text:", text)
            history_str = "\n".join(history)
            prompt = get_prompt(history_str)
            response = send_to_gpt(text, prompt)
            print("GPT response: ", response)

            subprocess.call(f"echo '{response}' | piper --model {PIPER_MODEL_PATH} --output_file {RESPONSE_FILE}",
                      shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            tts_thread = threading.Thread(target=run_speech)
            tts_thread.start()
            time.sleep(RESPONSE_TO_SERVO_PAUSE)
            run_servo()
            tts_thread.join()  # Ensure TTS completes before returning

            convo = json.dumps({"user_message":text, "skeleton_response":response})
            history.append(convo)

            with open(CONVERSATION_HISTORY_FILE, "a") as myfile:
                myfile.write(convo)
            os.remove(RECORDED_FILE)
            os.remove(RESPONSE_FILE)
        else:
            cnt += 1
            if cnt == ITERATIONS_TO_FORGET:
              new_session = True


if __name__ == "__main__":
    main()
