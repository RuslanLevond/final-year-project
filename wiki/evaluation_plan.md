Evaluation Plan
===============

The created model and Microsoft model's performances will be evaluated and compared,
both on paper and in real world. As well, systematic evaluation and measurement of both
Arduino and Raspberry Pi architectures will be carried out running the created model.

## Evaluate model using metrics

All metrics will be captured on the already trained model using unseen data from testing dataset.
The following metrics will be captured:
* Accuracy - number of classifications a model correctly predicts divided by the
total number of predictions made. Implies how well can model identify patterns in data.
* Precision - Correctness of classification. Number of correct positive classifications
divided by the total number of predicted positive classifications.
* Recall - measure of model correctly identifying true positives. Number of correct positive
classifications divided by the total number of actual positive cases.
* F1 Score - weighted average of precision and recall, balances strengths of each. Takes into
account both false positives and false negatives, more useful than accuracy.
* Confusion matrix - accuracy for specific classes.

## Evaluate model in real world

### False Negative Test

For this type of evaluation, both models will be deployed to both Raspberry Pi and Arduino hardware
and will be subjected to test in various conditions. The evaluation will test how well
the model can classify the targeted test in different environments.

The following conditions will be considered:
* Environment - wild vs controlled environment.
* Distance - how far is the device from the sound.
* Noise - a variety of unknown noises and other birds sounds active as background noise
during classification.
* Target Volume - the volume of targeted sounds, in dB.
* Noise Volume - the volume of background noise, in dB.
* TP Result - out of 5 different target samples, how many did it got right. 0.8 counts as classification.

### False Positive Test

For this evaluation, both models will be deployed to the same hardware and will be tested against
all kinds of sounds to see if the model classifies random sounds incorrectly as target.
All of the sounds will be evaluated in the same condition (1 meter distance and
60 dB sound volume)

The following parameters will be considered:
* Sound - a variety of unknown noises and other birds sounds active during classification. Will
also include birds signing with similar pitch and call to the target bird (e.g. with similar call
and pitch 'Carolina Wren' and same family 'Helmeted Manakin').
* FP Result - given 5 different sound samples, how many did the model classify incorrectly. 0.8 counts as classification.

### Note

For both evaluations, Microsoft model will not be evaluated on Arduino due to lack of support of
Python's SVM classifier module in C++ which is used by the Microsoft model.

## Evaluate Architectures

The following metrics will be captured to compare Raspberry Pi and Arduino architectures:

* Battery capacity - how big is the battery in mAh.
* Energy usage - electrical current the architecture requires while running the model,
measured in mA.
* Operating Time - the total time the architecture can run on battery before it needs
to be recharged.
* Processing time for feature extraction - how long it takes to extract features.
* Processing time for inference - how long it takes for the model to run inference.
* Total processing time - the latter two combined.
* Total RAM usage average - how much does the architecture use RAM on average, while
running the model. This also includes the OS.
