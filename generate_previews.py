from __future__ import division
import musdb
import numpy as np
from scipy.stats.mstats import gmean
import csv
import librosa
import scipy.signal
import argparse


def create_activation_annotation(
    track,
    win_len=4096,
    lpf_cutoff=0.075,
    theta=0.15,
    binarize=False,
    var_lambda=20.0,
    amplitude_threshold=0.01
):
    """
    Create the activation confidence annotation for a multitrack. The final
    activation matrix is computed as:
        `C[i, t] = 1 - (1 / (1 + e**(var_lambda * (H[i, t] - theta))))`
    where H[i, t] is the energy of stem `i` at time `t`

    Taken from
    https://github.com/marl/medleydb/blob/master/medleydb/annotate/activation_conf.py

    Parameters
    ----------
    track : Track
        Musdb Track Object
    win_len : int, default=4096
        Number of samples in each window
    lpf_cutoff : float, default=0.075
        Lowpass frequency cutoff fraction
    theta : float
        Controls the threshold of activation.
    var_labmda : float
        Controls the slope of the threshold function.
    amplitude_threshold : float
        Energies below this value are set to 0.0
    Returns
    -------
    C : np.array
        Array of activation confidence values shape (n_conf, n_stems)
    stem_index_list : list
        List of stem indices in the order they appear in C

    """
    H = []

    # MATLAB equivalent to @hanning(win_len)
    win = scipy.signal.windows.hann(win_len + 2)[1:-1]

    for name, source in track.sources.items():
        H.append(track_energy(source.audio, win_len, win))

    # list to numpy array
    H = np.array(H)

    # normalization (to overall energy and # of sources)
    E0 = np.sum(H, axis=0)

    H = len(track.sources) * H / np.max(E0)

    # binary thresholding for low overall energy events
    H[:, E0 < amplitude_threshold] = 0.0

    # LP filter
    b, a = scipy.signal.butter(2, lpf_cutoff, 'low')
    H = scipy.signal.filtfilt(b, a, H, axis=1)

    # logistic function to semi-binarize the output; confidence value
    C = 1.0 - (1.0 / (1.0 + np.exp(np.dot(var_lambda, (H - theta)))))

    # add time column
    time = librosa.core.frames_to_time(
        np.arange(C.shape[1]), sr=track.rate, hop_length=win_len // 2
    )

    # sum up all sources as we are only interested in the peak joint activity
    return np.sum(C.T, axis=1), time


def track_energy(wave, win_len, win):
    """Compute the energy of an audio signal
    Parameters
    ----------
    wave : np.array
        The signal from which to compute energy
    win_len: int
        The number of samples to use in energy computation
    win : np.array
        The windowing function to use in energy computation
    Returns
    -------
    energy : np.array
        Array of track energy
    """
    hop_len = win_len // 2

    # convert to mono
    wave = np.mean(wave, axis=1)

    wave = np.lib.pad(
        wave,
        pad_width=(win_len-hop_len, 0),
        mode='constant',
        constant_values=0
    )

    # post padding
    wave = librosa.util.fix_length(
        wave, int(win_len * np.ceil(len(wave) / win_len))
    )

    # cut into frames
    wavmat = librosa.util.frame(wave, frame_length=win_len, hop_length=hop_len)

    # Envelope follower
    wavmat = hwr(wavmat) ** 0.5  # half-wave rectification + compression

    return np.mean((wavmat.T * win), axis=1)


def hwr(x):
    """ Half-wave rectification.
    Parameters
    ----------
    x : array-like
        Array to half-wave rectify
    Returns
    -------
    x_hwr : array-like
        Half-wave rectified array
    """

    return (x + np.abs(x)) / 2


def compute_H_max(
    track,
    preview_length=30,
    short_window=4096,
):

    # compute track_activity
    H, time_in_seconds = create_activation_annotation(
        track,
        win_len=short_window
    )

    longterm_win = int(track.rate * preview_length / (short_window // 2))

    H_frames = librosa.util.frame(
        H,
        frame_length=longterm_win,
        hop_length=1
    )

    H_time_in_seconds = librosa.util.frame(
        time_in_seconds,
        frame_length=longterm_win,
        hop_length=1
    )

    activities = gmean(np.maximum(H_frames, np.finfo(float).eps), axis=0)

    excerpt = H_time_in_seconds[(0, -1), np.argmax(activities)]

    excerpt[-1] = excerpt[0] + preview_length

    if excerpt[-1] >= track.audio.shape[0]:
        # shift excerpt to left
        print("Shift was needed")
        excerpt -= excerpt[-1] - track.audio.shape[0]

    start_second = int(np.floor(excerpt[0]))
    end_second = int(np.floor(excerpt[1]))

    # round to nearest second
    start_sample = start_second * track.rate
    end_sample = end_second * track.rate

    sample_pos = (start_sample, end_sample)
    time_pos = (start_second, end_second)

    return sample_pos, time_pos


def generate_previews(mus, preview_length=30, test_length=7):

    with open('previews.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for i, track in enumerate(mus.load_mus_tracks(subsets=['test'])):
            if track.duration < preview_length:
                continue

            print(track.name)
            sample_pos, time_pos = compute_H_max(
                track, preview_length=preview_length
            )
            writer.writerow(
                [
                    track.name,
                    sample_pos[0],
                    sample_pos[1],
                    time_pos[0],
                    time_pos[1]
                ]
            )


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--musdb',
        help='Path to the musdb dataset.',
        type=str,
    )

    parser.add_argument(
        '--iswav',
        help='Read musdb wav instead of stems',
        action='store_true',
    )

    parser.add_argument(
        '--duration',
        help='Duration of the preview in seconds (default is 30s)',
        type=int,
        default=30,
    )

    args = parser.parse_args()

    mus = musdb.DB(args.musdb, is_wav=args.iswav)

    generate_previews(mus, args.duration)
