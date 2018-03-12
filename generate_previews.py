from __future__ import division
import musdb
import numpy as np
from scipy.stats.mstats import gmean
import csv
import librosa
import scipy.signal


def crop_track(track, start_pos, end_pos):
    estimates = {}
    # crop target track and save it as estimate
    for target_name, target_track in track.targets.items():
        estimates[target_name] = target_track.audio[start_pos:end_pos]

    estimates['mixture'] = track.audio[start_pos:end_pos]
    return estimates


def create_activation_annotation(
    track,
    win_len=4096,
    lpf_cutoff=0.075,
    theta=0.15,
    binarize=False
):

    H = []

    # MATLAB equivalent to @hanning(win_len)
    win = scipy.signal.windows.hann(win_len + 2)[1:-1]

    for key, source in track.sources.items():
        H.append(track_activation(source.audio, win_len, win))

    # list to numpy array
    H = np.array(H)

    # normalization (to overall energy and # of sources)
    E0 = np.sum(H, axis=0)

    H = len(track.sources) * H / np.max(E0)

    # binary thresholding for low overall energy events
    mask = np.ones(H.shape)
    mask[:, E0 < 0.01] = 0
    H = H * mask

    # LP filter
    b, a = scipy.signal.butter(2, lpf_cutoff, 'low')
    H = scipy.signal.filtfilt(b, a, H, axis=1)

    # add time column
    time_in_samples = librosa.core.frames_to_samples(
        np.arange(H.shape[1]), hop_length=win_len // 2
    )

    # logistic function to semi-binarize the output; confidence value
    H = 1 - 1 / (1 + np.exp(np.dot(20, (H - theta))))

    return np.sum(H.T, axis=1), time_in_samples


def track_activation(wave, win_len, win):
    hop_len = win_len // 2

    wave = np.mean(wave, axis=1)

    wave = np.lib.pad(
        wave,
        pad_width=(
            win_len-hop_len,
            0
        ),
        mode='constant',
        constant_values=0
    )

    # post padding
    wave = librosa.util.fix_length(
        wave, int(win_len * np.ceil(len(wave) / win_len))
    )

    # cut into frames
    wavmat = librosa.util.frame(
        wave,
        frame_length=win_len,
        hop_length=hop_len
    )

    # Envelope follower
    wavmat = hwr(wavmat) ** 0.5  # half-wave rectification + compression

    return np.mean((wavmat.T * win), axis=1)


def hwr(x):
    ''' half-wave rectification'''
    return (x + np.abs(x)) / 2


def compute_H_max(
    track,
    preview_length=30,
    short_window=4096,
    short_hop=2
):

    # compute track_activity
    H, time_in_samples = create_activation_annotation(
        track,
        win_len=short_window
    )

    longterm_win = int(
        track.rate * preview_length / short_window * short_hop
    )
    H_frames = librosa.util.frame(
        H,
        frame_length=longterm_win,
        hop_length=1
    )

    H_time_in_samples = librosa.util.frame(
        time_in_samples,
        frame_length=longterm_win,
        hop_length=1
    )

    activities = gmean(np.maximum(H_frames, np.finfo(float).eps), axis=0)

    excerpt = H_time_in_samples[(0, -1), np.argmax(activities)]
    excerpt[-1] = excerpt[0] + (preview_length * track.rate)

    if excerpt[-1] >= track.audio.shape[0]:
        # shift excerpt to left
        print("Shift was needed")
        excerpt -= excerpt[-1] - track.audio.shape[0]

    start_sample = excerpt[0]
    end_sample = excerpt[1]

    return start_sample, end_sample


def generate_previews(dsd, write_estimates=True, preview_length=30):
    with open('previews.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for i, track in enumerate(mus.load_mus_tracks()):
            if track.duration < preview_length:
                continue

            print(track.name)
            start_sample, end_sample = compute_H_max(
                track, preview_length=preview_length
            )
            writer.writerow([track.name, start_sample, end_sample])

            if write_estimates:
                mus._save_estimates(
                    crop_track(track, start_sample, end_sample),
                    track,
                    estimates_dir='.'
                )


if __name__ == '__main__':
    mus = musdb.DB()
    generate_previews(mus, write_estimates=True)
