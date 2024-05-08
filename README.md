# Frends Audio Archive

* Andrew Tate

* John Leeds

* Luke Samuels

* Rhys Sorenson-Graff

## Contributions:

* Andrew Tate: Created the play screen and brought all of the GUI screens together with the GUI Manager.

* John Leeds: John added a fuzzy search function to the storage and added it to the CLI.

* Luke Samuels: Used John's fuzzy search to make a search screen and search results screen.

* Rhys Sorenson-Graff: Rhys created the sound edit menu.

## Installation:

* Create a virtual environment with `python3.11 -m venv venv`.

* Activate it with `venv/Scripts/activate` (Windows) or `source venv/bin/activate` (Linux and Mac).

* Install dependencies with `python -m pip install -r requirements.txt`.

* In order to change the speed of a sound, you must have [FFmpeg](https://ffmpeg.org/) installed.

* Note: Deactivate the virtual environment with `deactivate`.

* Source: [Python Virtual Environments: A Primer](https://realpython.com/python-virtual-environments-a-primer).

## Getting Started:

* First, initialize the database by running `python src/sqlite_init.py`.

* From here, you can add whatever sounds you want with `python src/cli.py add [path to sound] [name (optional)]`.

* Once you have added sounds to the archive, you can play them with `python src/cli.py play [name]`.

* You can optionally specify audio effects to apply such as reversing the sound (`-r`), changing the volume (`-v [volume]`), changing the speed (`-s [speed]`), or playing multiple sounds in parallel (`-p`).

* Other commands: `rename`, `list`, `remove`, `clean`, `tag`, `help`.

* For more information, run `python src/cli.py -h` or `python src/cli.py [command] -h`.

* For more details on the technical design, see `design.md`.

## Sample Interaction:

These are commands you might run when getting started with the archive.

1. Make sure that you have followed the steps in the `Installation` section.

2. Iniatilize the database - `python src/sqlite_init.py`

3. Add sounds - we have provided starter sounds for testing purposes, but feel free to remove them once no longer needed.
    * `python src/cli.py add sounds/coffee.wav` (will be named `coffee`)
    * `python src/cli.py add sounds/toaster.wav -n toast` (will be named `toast`)

4. Make sure that they were properly added - `python src/cli.py list`

5. Add the tags `drink` and `yum` to coffee - `python src/cli.py tag coffee drink yum`

6. List all sounds with the tag `drink` - `python src/cli.py list drink`

7. Play the `toaster` sound - `python src/cli.py play toast`

8. Play the `coffee` and `toast` sounds back to back and reversed - `python src/cli.py play coffee toast -r`

9. Remove the `coffee` sound - `python src/cli.py remove coffee`

10. Verify that `coffee` was removed - `python src/cli.py list`

## Development Notes:

## GUI Instructions:

1. Navigate to the src directory and run: `python -m GUI_Main`
2. The Database will automatically initialize if it hasn't, sounds can be added with the text box on the left
   for instance `../sounds/coffee.wav` will add the sound coffee to the software and name it "`coffee`."
3. Click `Play`
4. Now the search screen will be open, search for the name or tags of the sound and it will use fuzzy search to
   pick the 5 closest sounds to what was searched
5. Select the sound(s) you would like to play and click `submit`
6. The settings screen will be open, clicking `"open popup"` will give a list of modifications that can be applied
   to all of the sounds
7. Click `submit` to progress to the next screen and apply those effects
8. The play screen will be open, click `play` to start playing the sounds and `stop` to stop, sounds can be replayed after
   clicking stop
9. Click `back to menu` to navigate back to the homescreen
10. Press `escape` at anytime to close the program

### Testing:

Tests are written with the built in `unittest` library and can be executed with `python -m unittest`.

Our automatic tests are located in the `tests/` directory, and we have written tests for as many of our commands as possible.
There are tests for adding, renaming, and removing sounds as well as tests for adding and removing tags.

Our audio functions are all tested manually.

Note that when creating new tests, the file must begin with `test_` in order for them to be discovered.

### Additional Notes:

We have written docstrings according to the [Google Style Guide](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings).

Our project is formatted with [`black`](https://black.readthedocs.io/en/stable/).

We have implemented fuzzy searching to use with our GUI, but our approach will not scale well if someone stores a large number of sounds.
We may be able to optimize our approach to a certain point, but in order to handle fuzzy searching at a large scale, we would need to switch away from sqlite.

## Challenges:

One challenge we faced was that Sqlite does not natively support something like [fuzzystrmatch](https://www.postgresql.org/docs/current/fuzzystrmatch.html) from Postgresql.
We implemented fuzzy search by fetching every row from the database and sorting them by edit distance.
However, this will not scale well.
If we were to continue working on this project, we would need to rethink how we implemented this feature.
We think that this project is a good use case for Sqlite, but there are likely better ways to implement fuzzy searching.

Learning Kivy was a challenge in itself, but not for the normal reasons that frontend brings - kivy allows two ways of
writing its code - an entirely python implementation, as well as its own markup language in files suffixed .kv. Using .kv
files is excellent for understanding the hierarchical structure of a gui, but passing data to and from them is difficult,
especially when the rest of the GUI is written entirely in python (no .kv files). One team member learned to use .kv files
and wrote their components in it, which didn't mesh well with the other teammates, and had to rewrite those components entirely.

Another big challenge was tying all of the GUI components together. We initially intended to do a chain of command
pattern to have the different screens directly send information to eachother (homescreen -> search -> settings -> play), but 
due to the all of us learning the Kivy API, our seperate GUIs were not designed to be integrated seamlessly, and required an 
extra class to organize the seperate GUIs and fetch/send data to each screen. This was pretty challenging, especially since 
prematuraly closing any screen would not terminate the program, as the GUI manager would simply toggle to the next screen. So
we needed a token system where each GUI would refresh the token when not exited early, allowing the program to halt early if needed.
The manager also has to pass itself to each screen, so that each GUI can send data back to the manager to call the next screen with. 

We also ran into a program where some of the audio functions relied on temp files, which worked on linux, but were not tested until later on Windows, which can't edit temp files, so we had to figure out away around that. 
