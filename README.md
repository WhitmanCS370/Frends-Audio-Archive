# Johns-Frends

* Andrew Tate

* John Leeds

* Luke Samuels

* Rhys Sorenson-Graff

## Contributions:

* Andrew Tate: Andrew worked on the initial setup of our repository and our first functions to play audio.  He also worked on the playback speed audio modification.

* John Leeds: John contributed to the organization of the repository, testing, and code review.

* Luke Samuels: Luke helped refactor to separate our source code and tests.  Luke also worked on the reverse audio modification.

* Rhys Sorenson-Graff: Rhys researched and contributed conversion of `.wav` files to numpy arrays. This is how we originally intended to handle audio modifications before discovering the built in `audioop` library.

## Usage:

There are currently three commands (`play`, `list`, and `rename`).  Run `python cli.py --help` for more information.

By default, `play` plays every sound passed to it back to back.  There are several optional flags such as `-p`, which plays all sounds simultaneously, `-s [FLOAT]`, which changes the speed of the sounds, `-v [FLOAT]`, which changes the volume of the sounds, and `-r` which plays the sounds backwards.

## Installation:

* Create a virtual environment with `python3.11 -m venv venv`

* Activate it with `venv/Scripts/activate` (Windows) or `source venv/bin/activate` (Linux and Mac).

* Install dependencies with `python -m pip install -r requirements.txt`.

* Note: Deactivate the virtual environment with `deactivate`.

* Source: [Python Virtual Environments: A Primer](https://realpython.com/python-virtual-environments-a-primer)

## Testing:

Tests are written with the built in `unittest` library and can be executed with `python -m unittest`.

Currently, only `list` and `rename` have unit tests as this is the only functionality that does not involve audio.  In our tests, the `test/sounds` directory is duplicated so that it can be modified without breaking future tests.

Our audio functions are all tested manually.

Note that when creating new tests, the file must begin with `test_` in order for them to be discovered.

## Challenges:

One of the biggest challenges we faced was creating audio modifications (such as changing the speed or volume).  Because the `simpleaudio` documentation references using numpy arrays, we thought we would need to modify the `.wav` files using a similar process.  However, we eventually discovered the `audioop` library that is built into Python, which had all of the features that we wanted.

In particular, we struggled to implement modifying playback speed.  When using `pydub` (which seems to be commonly suggested online), our audio was corrupted when we exported it and then opened it with `wave`.  Interestingly, the `.wav` file was fine when using a built-in audio player.  We were able to work around this by first exporting it as an mp3, reading that as a `pydub` `AudioSegment`, exporting that as a wav, and then reading that.  Obviously, this is not how we would like to handle this, but we can change it later if necessary.

We also are currently deciding how to store sounds in the archive.  Right now, we just are throwing all the sounds in the `sounds/` directory, but this is subject to change.
