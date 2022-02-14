import sqlite3
import signal
import sys
import getopt
import pandas
import csv

DB_NAME = "gateway_storage.db"

example_data = {
    'audio': "file_name_left.wve",
    'confidence_level': 1.0,
    'classification': "left",
    'time': "2021-02-10T12:50:19+00:00"
    }

def connect_to_database():
    # Create a connection to the database.
    dbconnect = sqlite3.connect(DB_NAME)
    # Creating a cursor which is a process that will be able to run SQL queries.
    cursor = dbconnect.cursor()
    return dbconnect, cursor

def insert_result(result):
    dbconnect, cursor = connect_to_database()
    insert_query = '''INSERT INTO classification_results (audio_file_name, confidence_level, classification, time)
        values ('{audio_file_name}', {confidence_level}, '{classification}', '{time}')'''.format(
        audio_file_name = result.get('audio'),
        confidence_level = result.get('confidence_level'),
        classification = result.get('classification'),
        time = result.get('time')
        )
        
    cursor.execute(insert_query);
    dbconnect.commit();
    dbconnect.close()
    print("Successfully inserted the result")

def list_classifications():
    dbconnect, cursor = connect_to_database()
    # Using Panads to pretty print results.
    print(pandas.read_sql_query('SELECT * FROM classification_results', dbconnect))
    dbconnect.close();

def list_classifications_by_label(label):
    dbconnect, cursor = connect_to_database()
    print(pandas.read_sql_query(f'SELECT * FROM classification_results WHERE classification="{label}"', dbconnect))
    dbconnect.close();

def export(path):
    dbconnect, cursor = connect_to_database()
    data = cursor.execute('SELECT * FROM classification_results')
    column_names = [desc[0] for desc in data.description]

    with open(path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        for row in data:
            writer.writerow(row)

    dbconnect.close();
    print(f"Successfully exported to - {path}")

def list_to_results():
    # Listens to Lora messages and saves them to the database.
    # if msg:
        # # Save image and get file location.
        # # Decrypt message
        # decrypted_result = {
        # 'audio': audio_file_location,
        # 'confidence_level': confidence_level,
        # 'classification': classification,
        # 'time': time
        # }
        # insert_result(decrypted_result)

def signal_handler(sig, frame):
    # On interrupting, will shut down the model and exit the program.
    print('Interrupted')
    sys.exit(0)

# Listens to interrupt from keyboard (CTRL + C)
signal.signal(signal.SIGINT, signal_handler)

def help():
    print('python3 gateway_framework.py --list_classifications --list_classifications_by_label <label> --export </location/file_name.csv> --listen_to_results' )

def main(argv):
    try:
        # For more information about opts - https://docs.python.org/3/library/getopt.html
        opts, args = getopt.getopt(argv, "h", ["help", "list_classifications", "list_classifications_by_label=", "export=", "listen_to_results"])
    except getopt.GetoptError:
        # On passed in arguments not being in the allowed list of args.
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()
        elif opt in ('--list_classifications'):
            list_classifications()
        elif opt in ('--list_classifications_by_label'):
            list_classifications_by_label(arg)
        elif opt in ('--export'):
            export(arg)
        elif opt in ('--listen_to_results'):
            listen_to_results()
        else:
            assert False, "unhandled option"

    if len(opt) == 0:
        help()
        sys.exit(2)

    # with AudioImpulseRunner(modelfile) as runner:
        # try:
            # model_info = runner.init()
            # print("Model parameters:")
            # print(model_info["model_parameters"])
            # labels = model_info['model_parameters']['labels']
            # print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
# 
            # # Let the library choose an audio interface suitable for this model, or pass device ID parameter to manually select a specific audio interface.
            # selected_device_id = None
            # if len(args) >= 2:
                # selected_device_id=int(args[1])
                # print("Device ID "+ str(selected_device_id) + " has been provided as an argument.")
# 
            # i = 0
            # combined_audio = b''
            # for res, audio in runner.classifier(device_id=selected_device_id):
                # print_classification_result(res, labels)
# 
                # predictions = res['result']['classification']
                # prediction_label, prediction_confidence = highest_prediction(predictions)
                # threshold = os.getenv("CONFIDENCE_THRESHOLD") or 0.7
# 
                # i = i + 1
                # combined_audio = b''.join([combined_audio, audio])
                # with open("/home/pi/final_year_project/sounds/test.txt", "a") as file:
                    # file.write(prediction_label+"\n")
                # # if i == 10:
                    # # break
                # 
                # # If the predicted class has confidence over or equal to the confidence threshold
                # # And if the prediction label doesn't start with "_" so it wouldn't capture the generic classes like _background_noise.
                # 
                # # if prediction_confidence >= threshold and not prediction_label.startswith("_"):
                    # # print("Classified " + prediction_label + " at confidence level of " + str(round(prediction_confidence, 2)))
                    # # current_time = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
                    # # print("start")
                    # # {
                    # # "sound_file": audio,
                    # # "confidence_level": prediction_confidence,
                    # # "classification": prediction_label,
                    # # "time": current_time
                    # # }
            # # sound_array = numpy.array(bytearray(combined_audio), dtype=numpy.int16)
            # # scipy.io.wavfile.write("sounds/" + current_time + "-" + prediction_label + ".wav", 16000, sound_array)
                    # # print("end")
                    # # with open("sounds/" + current_time + "-" + prediction_label + ".wav", "bx") as file:
                        # # file.write(audio)
                    # 
                # 
# 
        # finally:
            # # If for any reason the model stops classifying, the model will be stopped.
            # if (runner):
                # runner.stop()

if __name__ == '__main__':
    # Main function will be executed when running the source file.
    # Passes in a list of all arguments, taking everything after the script name.
    main(sys.argv[1:])
