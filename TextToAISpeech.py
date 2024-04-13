# The first test of step 2 of 2 for the overall project backend plan
# take a text file and convert it to an AI generated audio file using the Suna-ai Bark model

from transformers import AutoProcessor, BarkModel
from bark import generate_audio
import scipy
import time
import torch

processor_start_time = time.time()
processor = AutoProcessor.from_pretrained("suno/bark")
print(f"Processor load time: {time.time() - processor_start_time:.2f} seconds")

model_start_time = time.time()
# model = BarkModel.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark-small", torch_dtype=torch.float32).to(torch.device('cpu'))
print(f"Model load time: {time.time() - model_start_time:.2f} seconds")

voice_preset = "v2/en_speaker_6"

processor_function_start_time = time.time()
inputs = processor("hello the time is one eleven at the university of bath in the u k", voice_preset=voice_preset)
print(f"Processor function time: {time.time() - processor_function_start_time:.2f} seconds")

audio_generation_start_time = time.time()
audio_array = model.generate(**inputs)
audio_array = audio_array.cpu().numpy().squeeze()
print(f"Audio generation time: {time.time() - audio_generation_start_time:.2f} seconds")


sample_rate = model.generation_config.sample_rate

write_start_time = time.time()
scipy.io.wavfile.write("bark_out.wav", rate=sample_rate, data=audio_array)
print(f"Write time: {time.time() - write_start_time:.2f} seconds")





print()
