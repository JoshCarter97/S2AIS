
# script that uses ChatGPT API to generate single sentence text for users to read out

import openai
from openai import OpenAI
import random
import os

openai_key = "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"
client = OpenAI(api_key=openai_key)

# my_random_word = "Hackathon"
# prompt = f"Give me a random 10 word sentence on the topic of {my_random_word}"

def Generate_Outputs(random_word):

    prompt = f"Give me a random 10 word sentence on the topic of {random_word}"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    # print the response
    response = chat_completion.choices[0].message.content

    image_output = client.images.generate(
      model="dall-e-3",
      prompt=response,
      size="1024x1024",
      quality="standard",
      n=1,
    )

    image_url = image_output.data[0].url

    # pick a random voice from the list
    voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    voice_choice = random.choice(voice_options)

    print(f"Voice choice: {voice_choice}")

    # generate ai audio from the response
    audio_output = client.audio.speech.create(model="tts-1", voice=voice_choice, input=response)

    # Get the current working directory
    current_working_directory = os.getcwd()

    print(f"Current working directory: {current_working_directory}")

    # save the audio file
    file_name = "media/API_ai_audio.mp3"
    audio_output.stream_to_file(file_name)

    return response, image_url


def Generate_Audio_Only(text_string, save_path):

    # pick a random voice from the list
    voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    voice_choice = random.choice(voice_options)

    print(f"Voice choice: {voice_choice}")

    # generate ai audio from the response
    audio_output = client.audio.speech.create(model="tts-1", voice=voice_choice, input=text_string)

    # save the audio file
    audio_output.stream_to_file(save_path)

def speech_to_text(file_name):
    audio_file = open(file_name, "rb")
    transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    return transcription.text

print()
