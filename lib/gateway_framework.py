import sqlite3
import signal
import sys
import getopt
import pandas
import csv
import json
import sx126x
import os

DB_NAME = "gateway_storage.db"
# Make sure not to truncate columns.
pandas.set_option('display.max_colwidth', None)

def connect_to_database():
    # Create a connection to the database.
    dbconnect = sqlite3.connect(DB_NAME)
    # Creating a cursor which is a process that will be able to run SQL queries.
    cursor = dbconnect.cursor()
    return dbconnect, cursor

def insert_result(result):
    dbconnect, cursor = connect_to_database()
    insert_query = '''INSERT INTO classification_results (audio_file_name, confidence_level, classification, time)
        values ('{audio_file_name}', '{confidence_level}', '{classification}', '{time}')'''.format(
        audio_file_name = result.get('filename'),
        confidence_level = result.get('confidence_level'),
        classification = result.get('classification'),
        time = result.get('time')
        )

    cursor.execute(insert_query);
    dbconnect.commit();
    dbconnect.close()

def list_classifications():
    dbconnect, cursor = connect_to_database()
    # Using Pandas to pretty print results.
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

def download_audio_from_edge(destination_directory):
    # Goes through all of the classifications stored locally and downloads audio using SSH.
    # Make sure that both Raspberry Pis have SSH enabled and Edge Raspberry Pi is connected to the same network.
    dbconnect, cursor = connect_to_database()
    data = cursor.execute('SELECT * FROM classification_results')
    column_names = [desc[0] for desc in data.description]
    audio_file_name_index = column_names.index("audio_file_name")
    try:
        for row in data:
            os.system(f'scp pi@raspberrypi-personal:{row[audio_file_name_index]} {destination_directory}')
    except Exception as e:
        print(e)
        print("NOTE: Make sure that both Raspberry Pis have SSH enabled and Edge Raspberry Pi is connected to the same network.")

def signal_handler(sig, frame):
    # On interrupting, will shut down the model and exit the program.
    print('Interrupted')
    sys.exit(0)

# Listens to interrupt from keyboard (CTRL + C)
signal.signal(signal.SIGINT, signal_handler)

def help():
    print('python3 gateway_framework.py --listen_to_results --list_classifications --list_classifications_by_label <label> --export </location/file_name.csv> --download_audio_from_edge </path_to_local_dir>')

def main(argv):
    try:
        # For more information about opts - https://docs.python.org/3/library/getopt.html
        opts, args = getopt.getopt(argv, "h", ["help", "list_classifications", "list_classifications_by_label=", "export=", "listen_to_results", "download_audio_from_edge="])
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
        elif opt in ('--download_audio_from_edge'):
            download_audio_from_edge(arg)
        else:
            assert False, "unhandled option"

    if len(opts) == 0:
        help()
        sys.exit(2)

if __name__ == '__main__':
    # Main function will be executed when running the source file.
    # Passes in a list of all arguments, taking everything after the script name.
    main(sys.argv[1:])
