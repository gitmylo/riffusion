import io
import typing as T

import numpy as np
import pydub
import streamlit as st
import torch
from PIL import Image

from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.spectrogram_params import SpectrogramParams
from riffusion.streamlit import util as streamlit_util


@st.experimental_memo
def load_audio_file(audio_file: io.BytesIO) -> pydub.AudioSegment:
    return pydub.AudioSegment.from_file(audio_file)


def render_audio_to_audio() -> None:
    st.set_page_config(layout="wide", page_icon="🎸")

    st.subheader(":wave: Audio to Audio")
    st.write(
        """
    Modify existing audio from a text prompt.
    """
    )

    device = streamlit_util.select_device(st.sidebar)

    audio_file = st.file_uploader(
        "Upload audio",
        type=["mp3", "ogg", "wav", "flac"],
        label_visibility="collapsed",
    )

    if not audio_file:
        st.info("Upload audio to get started")
        return

    st.write("#### Original Audio")
    st.audio(audio_file)

    segment = load_audio_file(audio_file)

    if "counter" not in st.session_state:
        st.session_state.counter = 0

    def increment_counter():
        st.session_state.counter += 1

    cols = st.columns(4)
    start_time_s = cols[0].number_input(
        "Start Time [s]",
        min_value=0.0,
        value=0.0,
    )
    duration_s = cols[1].number_input(
        "Duration [s]",
        min_value=0.0,
        max_value=segment.duration_seconds,
        value=15.0,
    )
    clip_duration_s = cols[2].number_input(
        "Clip Duration [s]",
        min_value=3.0,
        max_value=10.0,
        value=5.0,
    )
    overlap_duration_s = cols[3].number_input(
        "Overlap Duration [s]",
        min_value=0.0,
        max_value=10.0,
        value=0.2,
    )

    increment_s = clip_duration_s - overlap_duration_s
    clip_start_times = start_time_s + np.arange(0, duration_s - clip_duration_s, increment_s)
    st.write(
        f"Slicing {len(clip_start_times)} clips of duration {clip_duration_s}s "
        f"with overlap {overlap_duration_s}s."
    )

    with st.form("Conversion Params"):

        prompt = st.text_input("Text Prompt")
        negative_prompt = st.text_input("Negative Prompt")

        cols = st.columns(4)
        denoising_strength = cols[0].number_input(
            "Denoising Strength",
            min_value=0.0,
            max_value=1.0,
            value=0.65,
        )
        guidance_scale = cols[1].number_input(
            "Guidance Scale",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
        )
        num_inference_steps = int(
            cols[2].number_input(
                "Num Inference Steps",
                min_value=1,
                max_value=150,
                value=50,
            )
        )
        seed = int(
            cols[3].number_input(
                "Seed",
                min_value=-1,
                value=-1,
            )
        )
        # TODO replace seed -1 with random

        submit_button = st.form_submit_button("Convert", on_click=increment_counter)

    # TODO fix


    show_clip_details = st.sidebar.checkbox("Show Clip Details", True)

    clip_segments: T.List[pydub.AudioSegment] = []
    for clip_start_time_s in clip_start_times:
        clip_start_time_ms = int(clip_start_time_s * 1000)
        clip_duration_ms = int(clip_duration_s * 1000)
        clip_segment = segment[clip_start_time_ms : clip_start_time_ms + clip_duration_ms]
        clip_segments.append(clip_segment)

    if not prompt:
        st.info("Enter a prompt")
        return

    if not submit_button:
        return

    params = SpectrogramParams()

    result_images: T.List[Image.Image] = []
    result_segments: T.List[pydub.AudioSegment] = []
    for i, clip_segment in enumerate(clip_segments):
        st.write(f"### Clip {i} at {clip_start_times[i]}s")

        audio_bytes = io.BytesIO()
        clip_segment.export(audio_bytes, format="wav")

        init_image = streamlit_util.spectrogram_image_from_audio(
            clip_segment,
            params=params,
            device=device,
        )

        if show_clip_details:
            left, right = st.columns(2)

            left.write("##### Source Clip")
            left.image(init_image, use_column_width=False)
            left.audio(audio_bytes)

            right.write("##### Riffed Clip")
            empty_bin = right.empty()
            with empty_bin.container():
                st.info("Riffing...")
                progress = st.progress(0.0)

        image = streamlit_util.run_img2img(
            prompt=prompt,
            init_image=init_image,
            denoising_strength=denoising_strength,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            negative_prompt=negative_prompt,
            seed=seed,
            progress_callback=progress.progress,
            device=device,
        )

        result_images.append(image)

        if show_clip_details:
            empty_bin.empty()
            right.image(image, use_column_width=False)

        riffed_segment = streamlit_util.audio_segment_from_spectrogram_image(
            image=image,
            params=params,
            device=device,
        )
        result_segments.append(riffed_segment)

        audio_bytes = io.BytesIO()
        riffed_segment.export(audio_bytes, format="wav")

        if show_clip_details:
            right.audio(audio_bytes)

    # Combine clips with a crossfade based on overlap
    crossfade_ms = int(overlap_duration_s * 1000)
    combined_segment = result_segments[0]
    for segment in result_segments[1:]:
        combined_segment = combined_segment.append(segment, crossfade=crossfade_ms)

    audio_bytes = io.BytesIO()
    combined_segment.export(audio_bytes, format="mp3")
    st.write(f"#### Final Audio ({combined_segment.duration_seconds}s)")
    st.audio(audio_bytes)


@st.cache
def test(segment: pydub.AudioSegment, counter: int) -> int:
    st.write("#### Trimmed")
    st.write(segment.duration_seconds)
    return counter


if __name__ == "__main__":
    render_audio_to_audio()