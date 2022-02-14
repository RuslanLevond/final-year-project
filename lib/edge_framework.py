import os
import sys, getopt
import signal
import time
import datetime
import numpy
import scipy.io.wavfile
import soundfile
import wave
from edge_impulse_linux.audio import AudioImpulseRunner

runner = None

def signal_handler(sig, frame):
    # On interrupting, will shut down the model and exit the program.
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

# Listens to interrupt from keyboard (CTRL + C)
signal.signal(signal.SIGINT, signal_handler)

def help():
    print('python3 edge_framework.py <path_to_model.eim> <audio_device_ID>' )

def print_classification_result(res, labels):
    # Calculates processing time by addition of Digital Signal Processing time and Classification time.
    processing_time = res['timing']['dsp'] + res['timing']['classification']
    print('Result (%d ms.) ' % (processing_time), end='')
    # Prints out each label with the confidence rounded to two decimal points.
    for label in labels:
        score = res['result']['classification'][label]
        print('%s: %.2f\t' % (label, score), end='')
    print('', flush=True)

def highest_prediction(predictions):
    max_prediction = max(predictions, key=predictions.get)
    return max_prediction, predictions.get(max_prediction)

def main(argv):
    try:
        # For more information about opts - https://docs.python.org/3/library/getopt.html
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.GetoptError:
        # On passed in arguments not being in the allowed list of args.
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'): 
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    # Gets path to the model.
    model = args[0]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    with AudioImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print("Model parameters:")
            print(model_info["model_parameters"])
            labels = model_info['model_parameters']['labels']
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')

            # Let the library choose an audio interface suitable for this model, or pass device ID parameter to manually select a specific audio interface.
            selected_device_id = None
            if len(args) >= 2:
                selected_device_id=int(args[1])
                print("Device ID "+ str(selected_device_id) + " has been provided as an argument.")

            i = 0
            combined_audio = b''
            for res, audio in runner.classifier(device_id=selected_device_id):
                print_classification_result(res, labels)

                predictions = res['result']['classification']
                prediction_label, prediction_confidence = highest_prediction(predictions)
                threshold = os.getenv("CONFIDENCE_THRESHOLD") or 0.7

                i = i + 1
                combined_audio = b''.join([combined_audio, audio])
                with open("/home/pi/final_year_project/sounds/test.txt", "a") as file:
                    file.write(prediction_label+"\n")
                current_time = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()

                if i == 10:
                    break
                    
            audio_final = numpy.frombuffer(combined_audio, dtype=numpy.int16)
            print(audio_final)
            soundfile.write("sounds/test.wav", audio_final, 16000)
                # sound_array = numpy.array(bytearray(audio), dtype=numpy.int16)
                # scipy.io.wavfile.write("sounds/" + current_time + "-" + prediction_label + ".wav", 16000, sound_array)
                 
                # res = {
                    # "sound_file": audio,
                    # "confidence_level": prediction_confidence,
                    # "classification": prediction_label,
                    # "time": current_time
                # }
                # print("Result:")
                # print(res)
                # if i == 10:
                    # break
                
                # If the predicted class has confidence over or equal to the confidence threshold
                # And if the prediction label doesn't start with "_" so it wouldn't capture the generic classes like _background_noise.
                
                # if prediction_confidence >= threshold and not prediction_label.startswith("_"):
                    # print("Classified " + prediction_label + " at confidence level of " + str(round(prediction_confidence, 2)))
                    # current_time = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
                    # print("start")
                    # {
                    # "sound_file": audio,
                    # "confidence_level": prediction_confidence,
                    # "classification": prediction_label,
                    # "time": current_time
                    # }
            # sound_array = numpy.array(bytearray(combined_audio), dtype=numpy.int16)
            # scipy.io.wavfile.write("sounds/" + current_time + "-" + prediction_label + ".wav", 16000, sound_array)
                    # print("end")
                    # with open("sounds/" + current_time + "-" + prediction_label + ".wav", "bx") as file:
                        # file.write(audio)
                    
                

        finally:
            # If for any reason the model stops classifying, the model will be stopped.
            if (runner):
                runner.stop()

if __name__ == '__main__':
    # Main function will be executed when running the source file.
    # Passes in a list of all arguments, taking everything after the script name.
    main(sys.argv[1:])
