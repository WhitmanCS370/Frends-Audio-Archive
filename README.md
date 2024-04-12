# Johns-Frends

* Andrew Tate

* John Leeds

* Luke Samuels

* Rhys Sorenson-Graff

## Contributions:

* Andrew Tate: Andrew worked on a first implementation of a cache and the soundMetaData class for organizing data.

* John Leeds: John added many commands to interact with the storage such as adding and removing sounds, cleaning the archive, adding and removing tags, and searching by tags.

* Luke Samuels: Luke worked on new playback options like transpose and prototyped a manual low/high-pass filter 

* Rhys Sorenson-Graff: Rhys worked on a method to crop sounds and save user's playback options as new sounds

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

* Other commands: `rename`, `list`, `remove`, `clean`, `tag`.

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

### Testing:

Tests are written with the built in `unittest` library and can be executed with `python -m unittest`.

Our automatic tests are located in the `tests/` directory, and we have written tests for as many of our commands as possible.
There are tests for adding, renaming, and removing sounds as well as tests for adding and removing tags.
There are also tests for the basic cache operations.

Our audio functions are all tested manually.

Note that when creating new tests, the file must begin with `test_` in order for them to be discovered.

### Additional Notes:

We have written docstrings according to the [Google Style Guide](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings).

Our project is formatted with [`black`](https://black.readthedocs.io/en/stable/).

We have implemented fuzzy searching to use with our GUI, but our approach will not scale well if someone stores a large number of sounds.
We may be able to optimize our approach to a certain point, but in order to handle fuzzy searching at a large scale, we would need to switch away from sqlite.

## Challenges:

One of the biggest challenges for handling the organization and characterization of sounds in this epoch was error handling.
For example, there are many possible exceptions when a user is trying to rename a sound.
Some of the possible problems are the sound might not exist, there might already be a sound associated with the new name, or the metadata database might not even be initialized.

Another challenge we faced was copy and pasting docstrings.
The `Storage Commander` relies upon a database implementation, like the one in `src/sqlite_storage.py`.
When a user tries to add a sound to the database, the `Commander` calls `self.storage.addSound()` which then adds the sound to both the cache and the database.
This means that there is an `addSound` function in the `src/sqlite_storage.py`, `src/storage_commander.py`, and `src/commands.py`, and all of these functions have the same purpose and effectively have the same doc string.
We are currently questioning if there is a better way to handle the documentation than effectively copy and pasting the same doc string in three different places, or if the commander calling `addSound` which calls `addSound` in the database is a code smell.

Another challenge Faced was with the Cache Testing, as the cache was so quick that it was impossible to really tell what order an eviction would be in, as the time stamp for some cases was arbritrarly small. This was solved by manually setting the timeStamp, but didn't feel super elegant. 

Another challenge was wrestling with WAV encodings and signal processing. The format for these files is really unintuitive, and most documentationassumes a high level of knowledge about signal processing. For example, even for a task like cropping the sound, we had to find a way to inuit orsnap to whatever the nearest audio frame was, although that's not clearly explained in any of the resources we found to explain WAV encodings. Signal processing is a completely different field of encoding than what we've studied in classes like 310.

In the future, we still have a few more edge cases to catch for interacting with the archive so we will need to account for those.
As of now, the user can add any file they want to the archive when we only have support for playing `.wav` files, so we will need to introduce some way to handle that.
In addition, we also anticipate other refactoring ideas to pop up as we continue to develop.
