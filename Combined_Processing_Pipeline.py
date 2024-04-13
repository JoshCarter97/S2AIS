## Going to stitch together the SpeechToText.py with the TextToAISpeech.py scripts so that we take in a .wav file
## and output a .wav file with the AI generated speech

import torch
from glob import glob
import os
from transformers import AutoProcessor, BarkModel
import scipy
import numpy as np

## ---- load the models and functions needed for SpeechToText ---- ##
silero_model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en', # also available 'de', 'es'
                                       device=torch.device('cpu'))

(read_batch, split_into_batches,
 read_audio, prepare_model_input) = utils  # see function signature for details


## ---- load the models and functions needed for TextToAIAudio ---- ##
processor = AutoProcessor.from_pretrained("suno/bark")

SMALL_MODEL = True

if SMALL_MODEL:
    bark_model = BarkModel.from_pretrained("suno/bark-small", torch_dtype=torch.float32).to(torch.device('cpu'))

else:
    bark_model = BarkModel.from_pretrained("suno/bark")


def SpeechToText(file_path):

    """"
    This function takes in a .wav file and converts it to text using the Silero Model
    assuming file_path is a single file_path
    """

    # model expects data in batches so need to split the file into batches even if it is just one file
    batches = split_into_batches(file_path, batch_size=10)

    #
    for batch in batches:
        input = prepare_model_input(read_batch(batch), device=torch.device('cpu'))
        output = silero_model(input)

        return decoder(output[0].cpu())



def TextToAIAudio(text_string, save_path, voice_preset="v2/en_speaker_6"):

    """
    This function takes in a string of text and converts it to an AI generated audio file using the Suna-ai Bark model
    """

    print(f"Text being converted to audio: {text_string}\n Processing...")

    # identify how many words are in the text_string
    num_words = len(text_string.split())

    # if there are less than 20 words then we can probably pass the text_string to the model in one go
    if num_words < 20:

        inputs = processor(text_string, voice_preset=voice_preset)

        audio_array = bark_model.generate(**inputs)
        audio_array = audio_array.cpu().numpy().squeeze()

        sample_rate = bark_model.generation_config.sample_rate

        scipy.io.wavfile.write(save_path, rate=sample_rate, data=audio_array)
        print(f"Audio file saved to: {save_path}")

    # if there are more than 20 words then we need to split the text_string into smaller chunks before passing to model
    else:

        # split the input text into chunks of 10 words and create a list of these chunks
        text_chunks = [text_string.split()[i:i + 10] for i in range(0, len(text_string.split()), 10)]

        # convert the text chunks back into full strings
        text_chunks = [" ".join(chunk) for chunk in text_chunks]

        sample_rate = bark_model.generation_config.sample_rate

        chunk_save_paths = []

        for count, chunk in enumerate(text_chunks):

            print(f"Processing chunk {count + 1} of {len(text_chunks)}", end="\r")

            inputs = processor(chunk, voice_preset=voice_preset)

            audio_array = bark_model.generate(**inputs)
            audio_array = audio_array.cpu().numpy().squeeze()

            chunk_save_path = f"chunk_{count}.wav"
            scipy.io.wavfile.write(chunk_save_path, rate=sample_rate, data=audio_array)
            chunk_save_paths.append(chunk_save_path)

        # Concatenate all the chunks
        concatenated_audio = np.concatenate([scipy.io.wavfile.read(chunk)[1] for chunk in chunk_save_paths])

        # remove the chunk files
        for chunk in chunk_save_paths:
            os.remove(chunk)

        # save the concatenated audio to the save_path
        scipy.io.wavfile.write(save_path, rate=sample_rate, data=concatenated_audio)
        print(f"Audio file saved to: {save_path}")


# test the full pipeline
# output = SpeechToText(["louder_test.wav"])

output = "Hey, have you heard about this new text-to-audio model called Bark? Apparently, it's the most realistic and natural-sounding text-to-audio model out there right now. People are saying it sounds just like a real person speaking. I think it uses advanced machine learning algorithms to analyze and understand the nuances of human speech, and then replicates those nuances in its own speech output."

TextToAIAudio(output, "bark_out_small.wav")


print()




