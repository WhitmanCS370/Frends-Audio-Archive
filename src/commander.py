"""This module is in charge of handling audio archive commands, such as listening to
sounds, adding sounds to the archive, renaming them, etc.
"""

from audio_edits import edit
import simpleaudio as sa
import tempfile
import wave

from storage_commander import StorageCommander
from sqlite_storage import Sqlite

# Note: adding this import is not needed for this file but makes the tests work.
# I don't know why, but I think maybe because if I import src.storage_exceptions in
# the tests, it doesn't think that storage_exceptions.ExampleError is equal to
# src.storage_exceptions.ExampleError
from storage_exceptions import *


class Commander:
    """Apply commands to audio archive.

    This class receives commands from an interface for the audio archive.
    From here, it interacts with the storage and applies audio effects in order
    to complete the desired action.

    Attributes:
        storage: A Storage object.
    """

    def __init__(self, sounds_directory="sounds/", database_path="audio_archive.db"):
        """Constructor. Creates a storage object.

        Args:
            sounds_directory: String path to directory containing archive sounds.
            database_path: String name of database file.

        Raises:
            FileNotFoundError: Not able to connect to the database.
        """
        self.storage = StorageCommander(Sqlite(database_path), sounds_directory)

    #getter method required to use fuzzy search in Luke's search screen GUI
    def fetchStorageCommander(self):
        return self.storage

    def playAudio(self, names, options):
        """Play a audio files after applying audio effects to them.

        Note that multiple effects can be applied simultaneously and that the
        edited sound can be saved as a new sound.

        Args:
            names: String List names of sounds.
            options: A playback_options object.

        Raises:
            NameMissing: A sound does not exist in storage.
            NameExists: options.save is not None and options.save is already in the archive.
            ValueError: options.save is longer than the maximum length for a sound.
            FileNotFoundError: The file path associated with a name is not a valid file.
        """
        file_paths = []
        for name in names:
            audio = self.storage.getByName(name)
            file_path = audio.file_path
            if not file_path.is_file():
                raise FileNotFoundError(f"Path not found: {str(file_path)}")
            file_paths.append(str(file_path))

        for name in names:
            self.storage.updateLastPlayed(name)
            self.storage.incrementPlayCount(name)

        wav_data = edit(file_paths, options)

        wave_obj = sa.WaveObject(
            wav_data.frames,
            wav_data.params.nchannels,
            wav_data.params.sampwidth,
            wav_data.params.framerate,
        )
        play_obj = wave_obj.play()

        if options.save is not None:
            try:
                self._saveWavData(wav_data, options.save)
            except Exception as e:
                play_obj.wait_done()
                raise e

        play_obj.wait_done()

    def _saveWavData(self, wav_data, name):
        """Saves the edited sound to a file and to the database.

        Args:
            wav_data: WavData object.
            name: String name of sound.

        Raises:
            NameExists: [name] already exists in the archive.
            ValueError: [name] is too long.
        """
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            with wave.open(f.name, "wb") as wav_file:
                wav_file.setparams(wav_data.params)
                wav_file.writeframes(wav_data.frames)
            self.storage.addSound(f.name, name)
