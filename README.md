_Codistancing_ is a Python code formatter that makes sure tokens in your code
does not infect each other. By using it, you agree to cede control over the 
looks of your code. In return, _Codistancing_ gives you determinism and 
extremely unreadable code - but at least it is disease free.

## Installation and Usage

### Installation
Just clone this project.

### Usage
```
codistancing.py [-h] [-l] (-f FILE [FILE ...] | -s STRING)

optional arguments:
  -h, --help            show this help message and exit
  -l, --line            Include distancing between lines
  -f FILE [FILE ...], --file FILE [FILE ...]
                        Files to reformat (in place)
  -s STRING, --string STRING
                        String to reformat
```