import sqlite3
import signal
import sys
import getopt
import pandas
import csv
import json
import sx126x

DB_NAME = "gateway_storage.db"

example_data = {
    'audio_file_name': "file_name_left.wve",
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
    insert_query = '''INSERT INTO classification_results (confidence_level, classification, time)
        values ('{confidence_level}', '{classification}', '{time}')'''.format(
        # audio_file_name = result.get('audio'),
        confidence_level = result.get('confidence_level'),
        classification = result.get('classification'),
        time = result.get('time')
        )

    cursor.execute(insert_query);
    dbconnect.commit();
    dbconnect.close()

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

def listen_to_results():
    # Listens to Lora messages and saves them to the database.
    address = 0
    node = sx126x.sx126x(serial_num="/dev/ttyS0", freq=433, addr=address, power=22, rssi=False, air_speed=2400, relay=False)
    print(f'Listening to Lora messages at address {address}')
    
    while True:
        result = node.receive()
        if result != None:
            try:
                decoded_result = json.loads(result.decode('utf-8'))
                insert_result(decoded_result)
                print(f'Saved result - {decoded_result}')
            except:
                # In case of packet loss or mixed packets.
                print(f'Packet loss - {result}')

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

    if len(opts) == 0:
        help()
        sys.exit(2)

    # listener = listen_to_lora_messages()
    # for message in listener:
    #     Import audio and write to wav file.
    #     imported_res = json.loads(binary_res.decode('utf-8'))
    #     imported_res["audio"] = numpy.array(imported_res["audio"], dtype="int16")
    #     write("/home/pi/final_year_project/sounds/" + imported_res["time"] + "-" + imported_res["classification"] + ".wav", imported_res["frequency"], imported_res["audio"])

if __name__ == '__main__':
    # Main function will be executed when running the source file.
    # Passes in a list of all arguments, taking everything after the script name.
    main(sys.argv[1:])
