# Universal Marking Graphical User Interface (U_Marking_GUI)

This program allows to efficiently and consistently mark assignments in a graphical way, allowing the grader to:
- Easily provide general and specific feedback to the student
- Grade students fairly and consistently
- Save grading progress to continue later by loading saved grading files
- Create grade reports (spreadsheets) that can be used directly or to upload to grade servers


## Dependencies
- tkinter
- numpy
- xlsxwriter

## Install
You first need to have python installed in your system, Anaconda is a good option (https://docs.anaconda.com/anaconda/install/)

It is recommended you create an environment to install this package, this can be done by starting terminal (linux, mac) or the command prompt (windows) and running:

`conda create -n ENVIRONMENT_NAME`

ENVIRONMENT_NAME can be any name, something like marking_environment could be a good choice

Activate this environment by running:
`conda activate ENVIRONMENT_NAME`

Then you can install this package by running:

`python -m pip install git+https://github.com/ackermannluis/U_Marking_GUI`


You might need to install git to get this last command to work, follow these instructions to install it on your system (https://github.com/git-guides/install-git) 

## Use

### Tutorial
A video showing you the way to use this GUI can be find here
(link_to_video_is_pending)

### Files needed before starting to grade
Two files need to be created before the marking starts, one with the structure of the assignment (.txt) and one with the information of the students (.csv).
Sample files are included in this repository, and will be downloaded during installation. Below you can find the description of these files

#### The Rubric file
This is a text file that contains the information about the assignment. It will tell the program how many questions the assignment has; how many marks per question; what evaluation criteria inside each question, and a list of general feedback that can be selected during grading. The format of the file must be kept for the program to find each field. See the video tutorial for further information.

#### The Student list file
This is a csv file that contains the information about the students to be graded. It can be opened in a spreadsheet program as long as care is taken when saving the file such that it is kept as a csv.
This file contains the student's id number, first name, surname, and email address. The sample file is populated with artificial data for easier identification of each field. Note that the student id numbers most be unique.  


## The GUI
As you can see the GUI is far from pretty, but it does the job, if you can give me a hand in making it nicer let me know.
<img src="https://some_url.png" width="250">


