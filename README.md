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

#### Download library for sending messages over Lora

Use ["Using with Raspberry Pi"](https://www.waveshare.com/wiki/SX1268_433M_LoRa_HAT) guide to change jumpers on the transceiver and download `sx126x.py` file. Place the file in the same directory as the `edge_framework.py`.

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
