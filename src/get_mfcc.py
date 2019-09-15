import python_speech_features as mfcc
from sklearn import preprocessing
from pysndfx import AudioEffectsChain
import scipy.io.wavfile as wav
import voice_recognition as vr
import pyaudio
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from six.moves import queue
import numpy as np
import ast


# Sampling rate of your microphone and desired chunk size
rate = 44100
chunk = int(rate/10)

# Insert your access token here
access_token = "02F4Okh0ju6Ug5Yq-VoSAsLRBdUVbD71P0m_-MoqBy4HJ0YjwHajPeQh4kFWqj4RZHBnacBJC-Tx7TAZ7ah6sPlnTim7Q"

# Creates a media config with the settings set for a raw microphone input
example_mc = MediaConfig('audio/x-raw', 'interleaved', 44100, 'S16LE', 1)

streamclient = RevAiStreamingClient(access_token, example_mc)

SPEAKERS = queue.Queue()

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk, names, filenames):
        self._vec_map = {}
        for i in range(len(names)):
            vec1 = get_mfcc(filenames[i])
            vec2 = get_mfcc(filenames[i+1])
            self._vec_map[names[i]] = [vec1.flatten(), vec2.flatten()]
        kdt = vr.VoiceRecognition(_vec_map)

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
            current_speaker = get_name(get_mfcc(np.frombuffer(chunk, "Int16"), rate))

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
    # print(features.flatten())
    return k.predict(features.flatten())

## called by front end
def reassign(name):
    k = vr.VoiceRecognition()
    k.reassign_name(name)

with MicrophoneStream(rate, chunk) as stream:
    # Uses try method to allow users to manually close the stream
    try:
        # Starts the server connection and thread sending microphone audio
        response_gen = streamclient.start(stream.generator())

        # Iterates through responses and prints them
        for response in response_gen:
            a = ast.literal_eval(response)
            a["speaker"] = SPEAKERS.get()
            print(a)

    except KeyboardInterrupt:
        # Ends the websocket connection.
        streamclient.client.send("EOS")
        pass

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
