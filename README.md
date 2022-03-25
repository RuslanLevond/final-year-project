# Develop an IoT Edge device to Capture and Classify Species using Sounds to Support Wildlife Conservation Activities

## Design

Please go to `/wiki` for more information.

## Raspberry Pi Configurations

By following the described procedures, you would be able to run either of the frameworks
on the Raspberry Pi 4 Model B. Before starting, the correct version of Raspberry Pi OS
should be installed:

1. Using [Raspberry Pi Imager](https://www.raspberrypi.com/software/), write Debian Bullseye 64-bit
OS to the SD card.
2. Go through the setup wizard to set name, password and connect the RPI to the network.
3. For easier development, enable SSH and VNC through Preferences > Raspberry Pi Configuration > Interfaces,
allowing to connect to the RPI wirelessly through the network instead of by the cable.
4. Make sure that Python >=3.9 version is installed `python --version`.
5. Update the OS by `sudo apt-get update` and `sudo apt-get upgrade`.

Connect via SSH:
```
ssh <user>@<host>
```

Connect via VNC: Download [VNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) and install it on your computer.

### Configuring for Edge Framework

#### Installing Required Packages

```
pip install scipy
pip install soundfile

# Install PyAudio for Edge Impulse Python SDK.
sudo apt-get install portaudio19-dev
sudo pip install pyaudio

# Finally install Edge Impulse Python SDK itself.
pip install edge_impulse_linux
```

#### Change Microphone Capture Volume

By default, the added microphone will have 40% volume. Increase it to 100% using `alsamixer`.

#### Change AudioImpulseRunner to Return Audio

By default, the AudioImpulseRunner returns small fragments of audio captured by microphone.
Instead, we want to return audio features that were classified. Go to audio.py
(location can be found by `pip show edge_impulse_linux`) and return features instead of audio.

For more information [here](https://forum.edgeimpulse.com/t/exporting-audio-from-audioimpulserunner/3698).

#### Download the Model from Edge Impulse

1. Install Dependencies using the guide [here](https://docs.edgeimpulse.com/docs/raspberry-pi-4#2-installing-dependencies).
2. Download the model `edge-impulse-linux-runner --download <filename>.eim`

You can verify the model is working on the device using `edge-impulse-linux-runner`

#### Setup Lora Transceiver

Use ["Using with Raspberry Pi"](https://www.waveshare.com/wiki/SX1268_433M_LoRa_HAT) guide to change jumpers on the transceiver and enable Serial port. Then download `sx126x.py` file from tools and place it in the same directory as the `edge_framework.py`.

#### Launching the Framework on Startup

1. First make the system to open terminal on startup by adding `@lxterminal` to `/etc/xdg/lxsession/LXDE-pi/autostart`.
2. Then add `python /home/pi/final_year_project/edge_framework.py test.eim 10` at the end of `.bashrc` file.
10 is the OS's default microphone.

### Configuring for Microsoft Framework

Running the [Microsoft Acoustic Bird Detection](https://github.com/microsoft/acoustic-bird-detection) model
on RPI.

#### Installing Required Packages

```
pip install sounddevice
pip install soundfile
pip install scipy
pip install pandas
pip install python_speech_features
pip install joblib
pip install sklearn
```

##### Installing Tensorflow

Use [this](https://qengineering.eu/install-tensorflow-2.7-on-raspberry-64-os.html) guide to install Tensorflow 2.8.0 version on RPI.

##### Download Preprocess File from Microsoft

Microsoft Framework relies on `preprocess.py` file from Microsoft to extract features.
Download the file and put it in the same directory as the framework. Can be found [here](https://github.com/microsoft/acoustic-bird-detection/blob/main/preprocess.py).

#### Export ML models

The ML models can be accessed through Jupyter Notebook tutorial found on git. Run the whole
notebook and add a cell at the end with the following code:

```
# Exporting Feature Model
feature_model.save(<export_path>)

# Exporting SVM Classifer
# Choosing maximum compression = 9 to make the file size as small as possible.
joblib.dump(svm, '<export_path>/<file_name>.pkl', compress=9)
```

Afterwards, copy both models to the `/ml_models` directory under the Microsoft Framework.

### Configuring for Gateway Framework

#### Installing Required Packages

```
pip install pandas

# Install SQLite3 command tool
sudo apt-get install sqlite3
```

#### Create Gateway Database

1. Create database using `sqlite3 gateway_storage.db`
2. Create table with the following command `CREATE TABLE classification_results(id INTEGER PRIMARY KEY AUTOINCREMENT, audio_file_name TEXT, confidence_level REAL, classification TEXT, time DATETIME);`

#### Repeat steps from 'Configuring for Edge Framework'

* Launching the Framework on Startup
* Setup Lora Transceiver

#### Configuring SSH key to download audio from Edge without password

Gateway Raspberry Pi can download audio saved on the Edge Raspberry Pi when they are connected to the same network.
To not be prompted for password for every audio file download, use [this tutorial](https://pimylifeup.com/raspberry-pi-ssh-keys/) to generate SSH keys
and copy them over to the Edge.

## Arduino Configurations

By following the described procedures, you would be able to run edge Arduino framework
on the Arduino Nano 33 BLE Sense. Before starting, install Arduino IDE which will be used to upload
Edge Framework to your Arduino device:

1. Navigate to [arduino website](https://www.arduino.cc/en/software), download and install Arduino IDE 1.8.19 on your computer.
2. On launching IDE, install core for Nano board by going to Tools > Board > Board Manager. Install `Arduino Mbed OS Nano Boards` core.

### Import Edge Framework

Upload edge framework sketch by navigating to Sketch > Add File.

### Export Edge Impulse ML Model

Download machine learning model as Arduino library using Edge Impulse GUI by going to
Deployment > Arduino Library > Build. This will download a .zip folder, do not unzip it.

### Import Edge Impulse ML Model

Before starting, make sure that old library has been removed if installed previously, can be found in `/Users/<user>/Documents/Arduino/libraries/final-year-project_inferencing`.
Import the downloaded Arduino library by going to Sketch > Include Library > Add .ZIP library, select your downloaded .zip folder.

### Configure Arduino board and port

Before starting, make to connect your Arduino to your computer using USB. To be able to upload the model and sketch to Arduino device,
you will need to configure its board and port. Navigate to Tools > Boards > Arduino Mbed OS Nano Boards and
select Arduino Nano 33 BLE Sense. After, go to Tools > Port and select the USB port you connected to your Arduino.

### Uploading Sketch to Arduino Device

To compile and upload your sketch to your Arduino Device, click the "Upload" button.
After the upload is finished, the library will start inferencing straight away. To see the logs,
click on "Serial Monitor".
