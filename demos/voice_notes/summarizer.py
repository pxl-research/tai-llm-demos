import os

import gradio as gr
import scipy.io.wavfile as wavfile
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# load model
# https://huggingface.co/openai/whisper-large-v3-turbo

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = 'openai/whisper-large-v3-turbo'

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    'automatic-speech-recognition',
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    return_timestamps=True,
    model_kwargs={'language': 'nl'}
)


def transcribe(audio_data):
    output_file = "./tmp/audio_sample.wav"  # Or generate a unique filename

    if audio_data is not None:
        sample_rate, audio = audio_data
        wavfile.write(output_file, sample_rate, audio)

    result = pipe(output_file)
    print(result['text'])

    return result['text']


demo = gr.Interface(
    transcribe,
    gr.Audio(type="numpy"),
    # gr.Audio(sources='microphone', type="numpy"),
    'text',
)

if not os.path.exists('./tmp'):
    os.makedirs('./tmp')

demo.launch()
