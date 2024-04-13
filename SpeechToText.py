# this will be the first test to try and take pre-recorded audio and convert it to text files
# step 1 of 2 for the overall project backend plan (Silero Model)

import torch
import zipfile
import torchaudio
from glob import glob
import os


device = torch.device('cpu')  # gpu also works, but our models are fast enough for CPU

model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en', # also available 'de', 'es'
                                       device=device)

(read_batch, split_into_batches,
 read_audio, prepare_model_input) = utils  # see function signature for details

# download a single file, any format compatible with TorchAudio (soundfile backend)
# torch.hub.download_url_to_file('https://opus-codec.org/static/examples/samples/speech_orig.wav',
#                                dst ='speech_orig.wav', progress=True)

test_files = glob('*.wav')
batches = split_into_batches(test_files, batch_size=10)

for batch in batches:
    input = prepare_model_input(read_batch(batch), device=device)
    output = model(input)
    for filepath, example in zip(batch, output):
        print(f"File: {os.path.basename(filepath)}")
        print(f"Transcript: {decoder(example.cpu())}\n")


print()