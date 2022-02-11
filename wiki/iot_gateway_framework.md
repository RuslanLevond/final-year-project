# IoT Gateway Framework

A gateway framework will be required to listen to edge devices results transmissions
that will be collected and stored locally. The user is then able to manually connect to the gateway
over SSH to extract the results. This framework will be deployed to the Raspberry Pi
with Lora transceiver module.

## IoT Framework Design

### Initialisation

On booting up the device, the framework will start constantly listening to Lora messages.
The framework will be contained within the Python file that will be ran as one of
the boot up processes. Python file execution will be specified within the `.bashrc` file.

### Decoding and Storing messages

On receiving a message, it will convert the message from binary into its original format.
For audio file data, it will be converted into `.wav` file and stored locally.
The rest of the metadata including path to the audio file, will be stored within SQLite
table. The reason why it will be stored in SQLite is because it is energy efficient with rich ability
to query data that CSV format doesn't have.

### CLI Functionality

The framework does not only listen to the Lora messages, but it can also be used
to query and export data that the gateway stores.

#### Exporting

`--export </location/file_name.csv>` option can be specified to export all of the
data into CSV file. The option requires file path as argument that specifies the location
and file name data will be exported to.

#### Listing Classifications

`--list_classifications` option can be used to query all data that is stored on the gateway.
Will print out all classifications within the database.

#### Listing Classifications by Label

`--list_classifications_by_label <label>` option can be used to list all classification data
specific to a certain class. The command requires a label as argument.

#### Listening to Results

`--listen_to_results` option can be used to start a process that will listen to any
incoming Lora messages and save them into the database. It will be used by the `.bashrc` on startup.
