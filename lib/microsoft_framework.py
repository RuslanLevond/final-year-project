import sounddevice as sd
import soundfile
from scipy.io.wavfile import write
import numpy as np
import preprocess as cmi
import joblib
from tflite_runtime.interpreter import Interpreter
import tensorflow as tf

def saveAudio():
    fs = 22050  # Sample rate
    seconds = 6  # Duration of recording

    print("Starting to record")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    write('./sound.wav', fs, myrecording)  # Save as WAV file
    print("Stopped recording")

def convertAudioToFeatures():
    # Reading sounds
    wav, fs = soundfile.read('./sound.wav')
    window_len = 2 # seconds
    samples_per_window = fs * window_len
    curr_data = None

    # generate all 2 seconds windows as a list, then round down
    # the label start time to the nearest 2 second window.
    all_windows = np.arange(0, np.ceil(len(wav) / samples_per_window).astype(np.int))

    for w in all_windows:
        start = w * samples_per_window
        end = start + samples_per_window
        length = end - start

        window = wav[start:end]
        if (not len(window) == length):
            padding = length - len(window)
            window = np.pad(window, (0, padding), 'constant')

        if curr_data is None:
            curr_data = np.array([window])
        else:
            curr_data = np.append(curr_data, [window], axis=0)
    fbank_import = np.array([cmi.make_fbank(x) for x in curr_data])
    return fbank_import

def runInference(fbank):
    # First we need to normalize the fbank input to be in line
    # with what the pre-trained model expects. [We scale and also
    # drop the final frequency bin]
    scale = 33.15998
    features_normal = fbank[:,:40,:] / scale
    # reshape the batches for the model.
    normal_batch = features_normal.reshape(features_normal.shape[0],
                                       features_normal.shape[1],
                                       features_normal.shape[2],
                                       1)
    # Importing classification and feature model.
    imported_svm = joblib.load('./svm.pkl')
    imported_model = tf.keras.models.load_model('./microsoft_model')

    # Carrying out inference.
    features = imported_model(normal_batch)
    results = imported_svm.predict(features[-1])
    return results

def main():
    print("Running main")
    saveAudio()
    fbank = convertAudioToFeatures()
    results = runInference(fbank)
    print("Results:")
    print(results)
    print("Done.")

if __name__ == '__main__':
    main()
