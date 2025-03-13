import datetime
import os

import gradio as gr
import scipy.io.wavfile as wavfile
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

TMP_FOLDER = './tmp/'

# create tmp folder
if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)

# load model
# https://huggingface.co/openai/whisper-large-v3-turbo

torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_id = 'openai/whisper-large-v3-turbo'

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True
)

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
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


def get_new_filename(extension='json'):
    time_stamp = f'{datetime.datetime.now():%y%m%d_%H%M_%S}'
    return f'{time_stamp}.{extension}'


def on_click_transcribe_button(audio_data):
    # store audio file in tmp folder
    tmp_audio_fn = f"{TMP_FOLDER}{get_new_filename('wav')}"  # Or generate a unique filename
    if audio_data is not None:
        sample_rate, audio = audio_data
        wavfile.write(tmp_audio_fn, sample_rate, audio)

    # transcribe
    result = pipe(tmp_audio_fn)
    full_text = result['text']

    # store transcript in file
    audio_fn = os.path.basename(tmp_audio_fn)
    (name, ext) = os.path.splitext(audio_fn)
    transcript_fn = f'{TMP_FOLDER}{name}.txt'
    with open(transcript_fn, 'wt') as fp_text:
        fp_text.write(full_text)

    return [f'{full_text}', full_text, transcript_fn]


def on_audio_input_change(audio):
    if audio is not None:
        return [gr.Button(interactive=True), None]
    else:
        return [gr.Button(interactive=False), None]


# GRADUI UI
explainer = ('Upload an audio file to get a summary. \n'
             'Warning: transcription may take a long time depending on the length of the file.')

custom_css = """
    .gray {background: gray;}
"""
with gr.Blocks(fill_height=True, title='Audio summary', css=custom_css) as blocks_ui:
    # state
    full_transcript = gr.State(None)

    # ui
    with gr.Row():
        md_explainer = gr.Markdown(value=explainer)

    with gr.Row():
        with gr.Column():
            aud_in = gr.Audio(type="numpy")
            btn_transcribe = gr.Button(value='Transcribe audio', interactive=False)
            btn_clear = gr.ClearButton()
        with gr.Column():
            file_download = gr.File(label='Transcript file', interactive=False)
            md_output = gr.Markdown(elem_classes='gray')

    # events
    aud_in.input(
        fn=on_audio_input_change,
        inputs=[aud_in],
        outputs=[btn_transcribe, full_transcript]
    )

    btn_transcribe.click(
        fn=on_click_transcribe_button,
        inputs=[aud_in],
        outputs=[md_output, full_transcript, file_download]
    )

    btn_clear.add([aud_in, file_download, md_output])

blocks_ui.queue().launch(server_name='0.0.0.0',
                         server_port=7029)
