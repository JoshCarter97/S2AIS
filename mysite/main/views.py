from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from .models import ToDoList
from .forms import CreateListForm
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

import sys
sys.path.insert(0, 'C:/Users/jc2369/PycharmProjects/BathHack24/mysite/main')
import Combined_Processing_Pipeline
import Prompt_Generation
import json


# Create your views here.

def index(request, id):
    ls = ToDoList.objects.get(id=id)

    if request.method == "POST":
        if request.POST.get("save"):
            for item in ls.item_set.all():
                p = request.POST

                if "clicked" == p.get("c" + str(item.id)):
                    item.complete = True
                else:
                    item.complete = False

                if "text" + str(item.id) in p:
                    item.text = p.get("text" + str(item.id))

                item.save()

        elif request.POST.get("add"):
            newItem = request.POST.get("new")
            if newItem != "":
                ls.item_set.create(text=newItem, complete=False)
            else:
                print("invalid")

    return render(request, "main/index.html", {"ls": ls})


def get_name(request):
    if request.method == "POST":
        form = CreateListForm(request.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n, date=timezone.now())
            t.save()

            return HttpResponseRedirect("/%i" % t.id)

    else:
        form = CreateListForm()

    return render(request, "main/create.html", {"form": form})


def upload(request):
    return render(request, "main/upload.html", {})

def record(request):
    if request.method == 'POST':
        random_word = request.POST.get('random_word')
        prompt, image_url = Prompt_Generation.Generate_Outputs(random_word)
        return render(request, 'main/record.html', {'prompt': prompt, 'image_url': image_url})
    else:
        return render(request, 'main/record.html')


def save_audio(request):
    if request.method == 'POST':
        file = request.FILES['audio']
        file_name = default_storage.save('media/' + file.name, file)
        return JsonResponse({'file_name': file_name})
    return JsonResponse({'error': 'Invalid request method'})

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES['audio_file']
        # Save the audio file here...
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

def view(request):
    l = ToDoList.objects.all()
    return render(request, "main/view.html", {"lists": l})


def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['audio_file']
        file_name = default_storage.save(file.name, file)

        # Return the file name in the JsonResponse
        return JsonResponse({'status': 'success', 'file_name': file_name})

    elif request.method == 'GET':
        # Return a simple HttpResponse or render a template
        return HttpResponse("This is the upload_file view.")


def SpeechtoText_old(file_name):

    file_path = f"media/{file_name}"

    # Process the audio file and get the transcribed text
    transcribed_text = Combined_Processing_Pipeline.SpeechToText([file_path])

    return transcribed_text


def SpeechtoText(file_name):
        file_path = f"media/{file_name}"
        transcribed_text = Prompt_Generation.speech_to_text(file_path)

        return transcribed_text


def TexttoAI(transcribed_text):

    save_path = "media/ai_audio_output.wav"

    Combined_Processing_Pipeline.TextToAIAudio(transcribed_text, save_path)

    return save_path


def process_audio(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        tts_model = request.POST.get('tts_model')

    # Process the audio file and get the transcribed text
    transcribed_text = SpeechtoText(file_name)

    # Return the transcribed text in the JsonResponse
    response = JsonResponse({'status': 'success', 'transcribed_text': transcribed_text, 'message': 'AI audio generation in progress...',
                             'file_name': file_name, 'tts_model': tts_model})

    return response

def generate_ai_audio(request):
    if request.method == 'POST':
        transcribed_text = request.POST.get('transcribed_text')
        tts_model = request.POST.get('tts_model')

        print(f"--> Transcribed text: {transcribed_text}")
        print(f"--> TTS model: {tts_model}")

        if transcribed_text is None:
            return JsonResponse({'status': 'error', 'message': 'No transcribed text found in the request.'})

        if tts_model == "cpu":
            # Create a generator object
            generator = generate_ai_audio_generator(transcribed_text)

            # Create a StreamingHttpResponse that uses the generator object
            response = StreamingHttpResponse(generator, content_type='application/json')

            return response

        elif tts_model == "gpu":
            # Create a generator object
            generator = generate_ai_audio_generator_GPU(transcribed_text)

            # Create a StreamingHttpResponse that uses the generator object
            response = StreamingHttpResponse(generator, content_type='application/json')

            return response

def generate_ai_audio_generator(transcribed_text):
    print("started generating AI audio")
    # Process the transcribed text and get the AI generated audio file
    output_wav_path = TexttoAI(transcribed_text)
    print(f"AI audio generated successfully. Path: {output_wav_path}")
    yield json.dumps({'status': 'success', 'message': 'AI audio generated successfully.'})

def generate_ai_audio_generator_GPU(transcribed_text):
    print("started generating AI audio")
    # Process the transcribed text and get the AI generated audio file
    save_path = "media/ai_audio_output.wav"
    Prompt_Generation.Generate_Audio_Only(transcribed_text, save_path)
    print(f"AI audio generated successfully. Path: {save_path}")
    yield json.dumps({'status': 'success', 'message': 'AI audio generated successfully.'})


