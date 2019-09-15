import os
import python_speech_features as mfcc
from sklearn import preprocessing
from pysndfx import AudioEffectsChain
import scipy.io.wavfile as wav
# import voice_recognition as vr
import pyaudio
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from six.moves import queue
import numpy as np
import ast
from sklearn.neighbors import KDTree

# Sampling rate of your microphone and desired chunk size
rate = 44100
chunk = int(rate/10)

# Insert your access token here
access_token = "02F4Okh0ju6Ug5Yq-VoSAsLRBdUVbD71P0m_-MoqBy4HJ0YjwHajPeQh4kFWqj4RZHBnacBJC-Tx7TAZ7ah6sPlnTim7Q"

# Creates a media config with the settings set for a raw microphone input
example_mc = MediaConfig('audio/x-raw', 'interleaved', 44100, 'S16LE', 1)

streamclient = RevAiStreamingClient(access_token, example_mc)

SPEAKERS = queue.Queue()


class VoiceRecognition():
    def __init__(self, calibration_vectors_dict):
        calibration_vectors = []
        self.all_names = []
        for name in calibration_vectors_dict:
            self.all_names.append(name)
            calibration_vectors += calibration_vectors_dict[name]
        self.kd_tree = KDTree(np.array(calibration_vectors))

    def predict(self, voice_vector):
        dist, ind = self.kd_tree.query([voice_vector])
        ind_1 = ind[0][0]
        dist_1 = dist[0][0]
        if ind_1 % 2 == 0:
            ind_1 = ind_1 // 2
        else:
            ind_1 = (ind_1 - 1) // 2
        if dist_1 <= 10:
            return self.all_names[ind_1]
        return 'Suggested: ' + self.all_names[ind_1]


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk, names, filenames):

        self._vec_map = {}
        for i in range(len(names)-1):
            vec1 = get_mfcc_wav(filenames[2*i])
            vec2 = get_mfcc_wav(filenames[2*i+1])
            self._vec_map[names[i]] = [vec1.flatten(), vec2.flatten()]

        self._predictor = VoiceRecognition(self._vec_map)

        self._rate = rate
        self._chunk = chunk
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            mfcc_vec = get_mfcc(rate, np.frombuffer(chunk, "Int16"))
            current_speaker = self._predictor.predict(mfcc_vec.flatten())

            SPEAKERS.put(current_speaker)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

def get_mfcc_wav(wav_file):
    (rate, sig) = wav.read(wav_file)
    return get_mfcc(rate, sig)

## called by front end
def get_mfcc(rate, sig):
    features = mfcc.mfcc(sig,rate, nfft = 1024)
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

    features = mfcc.mfcc(y_speech_boosted, rate, 0.025, 0.01, 16, nfilt=40, nfft=1024, appendEnergy = False, winfunc=np.hamming)

    features = preprocessing.scale(features) #scaling to ensure that all values are within 0 and 1

    return features[1:5, :]

# ## called by front end
# def get_name(features):
#     k = vr.VoiceRecognition()
#     # print(features.flatten())
#     return k.predict(features.flatten())

# ## called by front end
# def reassign(name):
#     k = vr.VoiceRecognition()
#     k.reassign_name(name)

def get_speaker():
    names = ["Dan", "Angel", "Katherine", "Julia"]
    filenames = ["a00001_dan.wav", "a00002_dan.wav", "new_angel1.wav", "new_angel2.wav", "new_kat1.wav", "new_kat1.wav", "new_julia1.wav", "new_julia2.wav"]

    with MicrophoneStream(rate, chunk, names, filenames) as stream:
        # Uses try method to allow users to manually close the stream
        try:
            # Starts the server connection and thread sending microphone audio
            response_gen = streamclient.start(stream.generator())

            # Iterates through responses and prints them
            for response in response_gen:
                a = ast.literal_eval(response)
                a["speaker"] = SPEAKERS.get()
                yield a 

        except KeyboardInterrupt:
            # Ends the websocket connection.
            streamclient.client.send("EOS")
            pass

# dic = {}
# names = ["Dan", "Angel", "Katherine", "Julia"]
# filenames = ["a00001_dan.wav", "a00002_dan.wav", "new_angel1.wav", "new_angel2.wav", "new_kat1.wav", "new_kat1.wav", "new_julia1.wav", "new_julia2.wav"]
#
# for i in range(len(names)-1):
#     vec1 = get_mfcc_wav(filenames[2*i])
#     vec2 = get_mfcc_wav(filenames[2*i+1])
#     dic[names[i]] = [vec1.flatten(), vec2.flatten()]
#
# kd = vr.VoiceRecognition(dic)
# current_vector = get_mfcc_wav("test_angel.wav")
# print(kd.predict(current_vector.flatten()))

# all_files = ["a00001_dan.wav", "a00002_dan.wav", "a00002_tina.wav", "a00002_tina2.wav", "a00001_sylvia.wav", "a00002_sylvia.wav", "julia1.wav", "julia2.wav"]
# rate, sig = wav.read(all_files[0])
# print(len(sig))
# dan1 = get_mfcc(all_files[0])
# print(get_name(dan1))
# reassign("Dan")
# print('-----')
# dan2 = get_mfcc(all_files[1])
# print(get_name(dan2))
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
