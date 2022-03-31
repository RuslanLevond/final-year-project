import os
import sys, getopt
import signal
import datetime
from scipy.io.wavfile import write
from edge_impulse_linux.audio import AudioImpulseRunner
import json
import sx126x
import multiprocessing

runner = None
all_processes = []

def signal_handler(sig, frame):
    # On interrupting, will shut down the model and exit the program.
    print('Interrupted')
    if (runner):
        runner.stop()
    # Stop all of the spawned threads.
    print("Stopping all processes")
    for process in all_processes:
        process.terminate()
    print("All processes have been terminated")
    sys.exit(0)

# Listens to interrupt from keyboard (CTRL + C)
signal.signal(signal.SIGINT, signal_handler)

def help():
    print('python edge_framework.py <path_to_model.eim> <audio_device_ID>' )

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

def send_lora_message(node, payload):
    # Starts a process that will send result as Lora message over 433MHz to node with address 0.

    # Converts result into json string and encodes into binary.
    binary_payload = json.dumps(payload).encode('utf-8')

    # Splitting address into two 8 bit numbers.
    receiving_node_high_8bit_address = bytes([0>>8])
    receiving_node_low_8bit_address = bytes([0&0xff])
    receiving_offset_frequency = bytes([433 - 410])

    own_high_8bit_address = bytes([100>>8])
    own_low_8bit_address = bytes([100&0xff])
    own_offset_frequency = bytes([node.offset_freq])

    data = receiving_node_high_8bit_address + receiving_node_low_8bit_address + receiving_offset_frequency + own_high_8bit_address + own_low_8bit_address + own_offset_frequency + binary_payload
    node.send(data)
    print("Sent Lora message.")

def save_audio(audio, classification, time, frequency):
    # Saves the raw audio as .wav file in ./sounds dir to be able to retreive it when needed.
    directory_name = os.path.realpath("./sounds")
    directory = os.path.dirname(directory_name)
    if not os.path.exists(directory):
        # Create the sounds directory if it doesn't exist
        os.makedirs(directory)

    filename = directory_name + time + "-" + classification + ".wav"
    write(filename, frequency, audio)
    return filename

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

            # Initialise Lora transceiver on 433MHz with address 100.
            node = sx126x.sx126x(serial_num="/dev/ttyS0", freq=433, addr=100, power=22, rssi=False, air_speed=2400, relay=False)

            for res, features in runner.classifier(device_id=selected_device_id):
                print_classification_result(res, labels)

                predictions = res['result']['classification']
                prediction_label, prediction_confidence = highest_prediction(predictions)
                threshold = 0.8

                # If the predicted class has confidence over or equal to the confidence threshold
                # And if the prediction label doesn't start with "_" so it wouldn't capture generic classes like _noise and _unknown.
                # Then send the result to the Gateway device.
                if prediction_confidence >= threshold and not prediction_label.startswith("_"):
                    print("Classified " + prediction_label + " at confidence level of " + str(round(prediction_confidence, 2)))
                    current_time = datetime.datetime.now().astimezone().isoformat()
                    frequency = model_info['model_parameters']['frequency']
                    filename = save_audio(features, prediction_label, current_time, frequency)

                    res = {
                            "filename": filename,
                            "confidence_level": prediction_confidence,
                            "classification": prediction_label,
                            "time": current_time
                    }

                    process = multiprocessing.Process(target=send_lora_message, args=(node, res))
                    process.start()
                    all_processes.append(process)

        finally:
            # If for any reason the model stops classifying, the model will be stopped.
            if (runner):
                runner.stop()

if __name__ == '__main__':
    # Main function will be executed when running the source file.
    # Passes in a list of all arguments, taking everything after the script name.
    main(sys.argv[1:])
