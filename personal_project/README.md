# Assignment 2a: Personal code project - Workshop feedback analysis
This project folder contains the script `main.py` for summarising and visualising feedback given by workshop participants. A group of linguistics students from Projekt Lingvistikling at Aarhus University have recently begun hosting linguistics-related workshops and presentations at different educational institutions, primarily highschools, with the aim of making more young people interested in linguistics and the university's linguistics programme. At the end of the workshops, we ask the participants to give us feedback by responding to an eight-question survey created and distributed through SurveyXact. Their responses are exported as a csv-file; the `main.py` script loads that csv-file, cleans it, and generates five barcharts, a Likert summary, and a list of their comments.

## Data
While the survey is anonymous, the participants have only consented to their responses being used for Projekt Lingvistikling's improvement; not for this assignment. The `survey_data.csv` csv-file found in the `in` folder has therefore been scrambled from an original, genuine survey dataset (not provided) using `scrambler.ipynb`. The scrambling method preserves the original results (with the exception of the fully anonymised comments), but the responses no longer "belong" to any one person.

## Repo structure
```
in/
  └── survey_data.csv                                       
out/
  ├── interesse_lingvistik_20261117_191342.png  
  ├── interesse_studie_20261117_191342.png  
  ├── kommentarer_20261117_191342.txt
  ├── likert_brugbart_20261117_191342.png 
  ├── likert_conlang_20261117_191342.png 
  ├── likert_gennemsnit_20261117_191342.txt
  └── likert_lingvistik_20261117_191342.png
src/
  ├── main.py                              
  └── scrambler.ipynb
README.md                  
requirements.txt                               
setup.sh                                        
```
## Instructions for running code
Open a terminal and navigate to the `personal_project` folder.

### 1. Set up the virtual environment
The included setup.sh script creates a virtual environment and installs all dependencies from `requirements.txt`. To set up the virtual environment, run the following terminal command:
```
bash setup.sh
```

### 2. Activate the virtual environment
After setup, activate the virtual environment:
```
source ./env/bin/activate
```

### 3. Run the scripts
Run the `main.py` script using the scrambled `survey_data.csv`:
```
python src/main.py -f survey_data.csv
```
Since they are timestamped, the generated barcharts, Likert summary, and comment list will not overwrite the ones already found in the `/out` folder (they will, however, be identical).

### 4. Deactivate the virtual environment
When finished running the script, deactivate the virtual environment:
```
deactivate
```

## Discussion
A future version of the script should be able to take multiple csv-files with survey data from multiple workshops at once. The plotting functions are already set up to handle this. A second script that can also compare responses from workshops hosted at different educational levels or on different topics is also in the plans; however, as Projekt Lingvistikling is still in its early stages, it may be a while before this becomes relevant.