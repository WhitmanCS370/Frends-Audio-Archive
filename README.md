# Johns-Frends

* Andrew Tate

* John Leeds

* Luke Samuels

* Rhys Sorenson-Graff

# Current Progress:

So far, we have been working on getting our project set up.  We have worked on
creating a reproducable development environment as well as discussing how we will
manage work.

We changed `cli_example.py` so that it plays every file passed to it.
By default, they are played in sequence. However, you can play them simultaneously
by specifying `-p` or `--parallel`.
For example `python cli_example.py mysound1.wav mysound2.wav` would play 
`mysound1.wav` followed by `mysound2.wav`.
`python cli_example.py mysound1.wav mysound2.wav` would play 
`mysound1.wav` and `mysound2.wav` simultaneously.

We used `argparse` to parse arguments.  While it probably makes this simple
example more complicated, it will hopefully make extending a CLI easier if we
choose to do so.

# Installation:

* Create a virtual environment with `python3.11 -m venv venv`

* Activate it with `venv/Scripts/activate` (Windows) or `source venv/bin/activate` (Linux and Mac).

* Install dependencies with `python -m pip install -r requirements.txt`.

* Note: Deactivate the virtual environment with `deactivate`.

* Source: [Python Virtual Environments: A Primer](https://realpython.com/python-virtual-environments-a-primer)
