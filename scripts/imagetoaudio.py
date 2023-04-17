# Code from https://github.com/enlyth/sd-webui-riffusion
import io
import torch
import torchaudio
from PIL import Image
import typing as T
from scipy.io import wavfile
import numpy as np


def spectrogram_from_image(
        image: Image.Image, max_volume: float = 50, power_for_image: float = 0.25
) -> np.ndarray:
    """
    Compute a spectrogram magnitude array from a spectrogram image.
    TODO(hayk): Add image_from_spectrogram and call this out as the reverse.
    """
    # Convert to a numpy array of floats
    data = np.array(image).astype(np.float32)

    # Flip Y take a single channel
    data = data[::-1, :, 0]

    # Invert
    data = 255 - data

    # Rescale to max volume
    data = data * max_volume / 255

    # Reverse the power curve
    data = np.power(data, 1 / power_for_image)

    return data


def waveform_from_spectrogram(
        Sxx: np.ndarray,
        n_fft: int,
        hop_length: int,
        win_length: int,
        sample_rate: int,
        mel_scale: bool = True,
        n_mels: int = 512,
        max_mel_iters: int = 200,
        num_griffin_lim_iters: int = 32,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    """
    Reconstruct a waveform from a spectrogram.
    This is an approximate inverse of spectrogram_from_waveform, using the Griffin-Lim algorithm
    to approximate the phase.
    """
    Sxx_torch = torch.from_numpy(Sxx).to(device)

    if mel_scale:
        mel_inv_scaler = torchaudio.transforms.InverseMelScale(
            n_mels=n_mels,
            sample_rate=sample_rate,
            f_min=0,
            f_max=10000,
            n_stft=n_fft // 2 + 1,
            norm=None,
            mel_scale="htk",
            max_iter=max_mel_iters,
        ).to(device)

        Sxx_torch = mel_inv_scaler(Sxx_torch)

    griffin_lim = torchaudio.transforms.GriffinLim(
        n_fft=n_fft,
        win_length=win_length,
        hop_length=hop_length,
        power=1.0,
        n_iter=num_griffin_lim_iters,
    ).to(device)

    waveform = griffin_lim(Sxx_torch).cpu().numpy()

    return waveform


def wav_bytes_from_spectrogram_image(
        image: Image.Image,
) -> T.Tuple[io.BytesIO, float]:
    """
    Reconstruct a WAV audio clip from a spectrogram image. Also returns the duration in seconds.
    """

    max_volume = 50
    power_for_image = 0.25
    Sxx = spectrogram_from_image(
        image, max_volume=max_volume, power_for_image=power_for_image
    )

    sample_rate = 44100  # [Hz]

    n_mels = image.height

    # FFT parameters
    window_duration_ms = 100  # [ms]
    padded_duration_ms = 400  # [ms]
    step_size_ms = 10  # [ms]

    # Derived parameters
    n_fft = int(padded_duration_ms / 1000.0 * sample_rate)
    hop_length = int(step_size_ms / 1000.0 * sample_rate)
    win_length = int(window_duration_ms / 1000.0 * sample_rate)

    samples = waveform_from_spectrogram(
        Sxx=Sxx,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        sample_rate=sample_rate,
        mel_scale=True,
        n_mels=n_mels,
        max_mel_iters=200,
        num_griffin_lim_iters=32,
    )

    wav_bytes = io.BytesIO()
    wavfile.write(wav_bytes, sample_rate, samples.astype(np.int16))
    wav_bytes.seek(0)

    duration_s = float(len(samples)) / sample_rate

    return wav_bytes, duration_s


def image_to_audio(image, audio):
    image_file = Image.open(image)
    wav_bytes, duration_s = wav_bytes_from_spectrogram_image(image_file)

    with open(audio, "wb") as f:
        f.write(wav_bytes.getbuffer())
    print(f"Wrote {audio}")