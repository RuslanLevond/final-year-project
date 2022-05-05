# IoT Edge Framework

This will be a framework that will be used by both Raspberry Pi and Arduino edge devices
which will be deployed in the the wild to listen to animal sounds, classify and
wirelessly send the results. Two different versions of framework will be developed
for each of the hardware solutions; in Python for RPI and in C++ for Arduino.

## IoT Framework Design

### Initialisation

On booting up either of devices, the framework will start classifying sounds straight away,
on condition that ML model is present and if microphone input device is available.

#### Arduino Version

On booting up the Arduino, framework will be initialised within the setup block,
after which the whole of framework and classification code will be started within the loop block.

#### Raspberry Pi Version

On booting up the Raspberry Pi, python file containing the framework will be ran
as one of the boot up processes with model and microphone input device id as arguments.
The `.bashrc` file will be used to run the model on the system start up.

### Machine Learning Model: Collecting Audio and Classification

The audio collection and classification both will be done in real time, meaning that
no audio will be missed during classification.

#### Raspberry Pi Version

The next step of the framework would be the classification. Edge Impulse supplies
[Python SDK](https://github.com/edgeimpulse/linux-sdk-python) for RPI which collects
sensor data and provides API functions to the model. Firstly, it will be used
to collect audio data as fast as it can process. The next step would be classification,
SDK will automatically forward sound to the model for classification, which will
return predictions.

Machine Learning Model will be manually exported from Edge Impulse as an `.eim` file
that is compatible with the provided Python SDK. This can be done with the following command:
`edge-impulse-linux-runner --download modelfile.eim`.

#### Arduino Version

Two buffers are going to be used to store audio data, one is used for inference and another for
sampling data. Both buffers will be switched between. When the sampling buffer becomes full of audio slices,
the process will pass full buffer to the inference process and then will clear and fill up the old buffer with new data.

### Storing Audio Locally

Due to limited 256 bytes Lora message size, audio will not be sent over the Lora protocol.
Instead, it will be saved locally which can be then retrieved manually over SSH.

#### Raspberry Pi Version

After a successful inference for the targeted classification, the raw audio will be converted
into `.wav` file and saved locally.

#### Arduino Version

Due to lack of non-volatile memory in Arduino Nano 33 BLE Sense, audio will not be saved
on the device.

### Transferring Results Wirelessly

On specified confidence threshold, the results with metadata will be wirelessly transmitted
over the Lora protocol. Before data will be sent, it will be converted to binary
as that is the only format Lora supports. The following data will be sent:

* Audio File Name - Path and name of the audio file stored on the edge device.
* Confidence level - Between 0.0 and 1.0, how confident is the model on the classification.
* Classification - the animal name that the model predicted.
* Time - the time at which the prediction was made, in ISO 8601 format.

#### Both Raspberry Pi and Arduino Versions

To not hold the machine learning inference process, sending lora message task will be spawned as a process,
which would finish in its own time.
