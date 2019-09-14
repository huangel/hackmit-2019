from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank
import scipy.io.wavfile as wav
import numpy as np

from sklearn.neighbors import KDTree

def get_mfcc(wav_file):
    (rate, sig) = wav.read(wav_file)
    sig = sig[10000:40000]
    mfcc_feat = mfcc(sig,rate)
    d_mfcc_feat = delta(mfcc_feat, 2)
    fbank_feat = logfbank(sig,rate)
    ret = fbank_feat[1:3,:]
    return ret

all_files = ["a00001_dan.wav", "a00002_dan.wav", "a00002_tina.wav", "a00002_tina2.wav", "a00001_sylvia.wav", "a00002_sylvia.wav", "julia1.wav", "julia2.wav"]
dan1 = get_mfcc(all_files[0])
dan2 = get_mfcc(all_files[1])
tina1 = get_mfcc(all_files[2])
tina2 = get_mfcc(all_files[3])
sylvia1 = get_mfcc(all_files[4])
sylvia2 = get_mfcc(all_files[5])
julia1 = get_mfcc(all_files[6])
julia2 = get_mfcc(all_files[7])

total = np.array([dan2.flatten(), dan1.flatten(), sylvia1.flatten(), tina1.flatten(), sylvia2.flatten(), julia1.flatten(), julia2.flatten()])

tree = KDTree(total, leaf_size=2)
dist, ind = tree.query([tina2.flatten()], k=2)
print(dist, ind)
