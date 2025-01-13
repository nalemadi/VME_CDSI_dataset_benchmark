# For DOTA-v2.0

1- Install the images and annotation files and follow the instructions given by the authors to construct DOTA-v2.0.

2- Create a folder with each split train-val-test, each has ``images`` and ``labelTxt`` subdirectories.

3- Under each one, create a symbolic link to the desired files in X_train.txt, X_val.txt, X_test.txt (X --> extract DOTA-v2.0 from Original_SPLIT.txt | CDSI_other_SPLIT.txt | CDSI_SPLIT.txt).


run the following for each split, specifiying its directory: 
```bash
dotadevkit convert --version VERSION_NO DIRECTORY
```

