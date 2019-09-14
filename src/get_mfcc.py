import python_speech_features as mfcc
import scipy.io.wavfile as wav
import numpy as np
from sklearn import preprocessing
from pysndfx import AudioEffectsChain
import voice_recognition as vr
from sklearn.neighbors import KDTree



## called by front end
def get_mfcc(wav_file):
    (rate, sig) = wav.read(wav_file)
    sig = sig[10000:40000]
    features = mfcc.mfcc(sig,rate)
    features = mfcc.logfbank(sig)
    features = mfcc.lifter(features)

    sum_of_squares = []
    index = -1
    for r in features:
        sum_of_squares.append(0)
        index = index + 1
        for n in r:
            sum_of_squares[index] = sum_of_squares[index] + n**2

    strongest_frame = sum_of_squares.index(max(sum_of_squares))
    hz = mfcc.mel2hz(features[strongest_frame])

    min_hz = min(hz)

    speech_booster = AudioEffectsChain().lowshelf(frequency=min_hz*(-1), gain=12.0, slope=0.5).highshelf(frequency=min_hz*(-1)*1.2, gain=-12.0, slope=0.5).limiter(gain=8.0)
    y_speech_boosted = speech_booster(sig)

    features = mfcc.mfcc(y_speech_boosted, rate, 0.025, 0.01, 16, nfilt=40, nfft=512, appendEnergy = False, winfunc=np.hamming)

    features = preprocessing.scale(features) #scaling to ensure that all values are within 0 and 1

    return features[1:5, :]

## called by front end
def get_name(features):
    k = vr.VoiceRecognition()
    return k.predict(features.flatten())

## called by front end
def reassign(name):
    k = vr.VoiceRecognition()
    k.reassign_name(name)

all_files = ["a00001_dan.wav", "a00002_dan.wav", "a00002_tina.wav", "a00002_tina2.wav", "a00001_sylvia.wav", "a00002_sylvia.wav", "julia1.wav", "julia2.wav"]
dan1 = get_mfcc(all_files[0])
print(get_name(dan1))
reassign("Dan")
print('-----')
dan2 = get_mfcc(all_files[1])
print(get_name(dan2))
# tina1 = get_mfcc(all_files[2])
# tina2 = get_mfcc(all_files[3])
# sylvia1 = get_mfcc(all_files[4])
# sylvia2 = get_mfcc(all_files[5])
# julia1 = get_mfcc(all_files[6])
# julia2 = get_mfcc(all_files[7])

# total = np.array([dan1.flatten(), julia2.flatten(), sylvia1.flatten(), tina2.flatten(), dan2.flatten(), tina1.flatten(), julia1.flatten()])
#
# tree = KDTree(total, leaf_size=2)
# dist, ind = tree.query([sylvia2.flatten()], k=2)
# print(dist, ind)
