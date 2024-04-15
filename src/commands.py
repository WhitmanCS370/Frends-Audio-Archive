"""This module is in charge of handling audio archive commands, such as listening to
sounds, adding sounds to the archive, renaming them, etc.
"""

from audio_edits import edit
import simpleaudio as sa
import tempfile
import wave

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

    def __init__(self, storage):
        """Constructor.

        Attributes:
            storage: A Storage object
        """
        self.storage = storage

    def playAudio(self, name, options):
        """Plays an audio file after applying effects to the sound.

        Note that multiple effects can be applied simultaneously.

        Args:
            name: String name of sound.
            options: A playback_options object.

        Returns:
            A PlayObject.

        Raises:
            NameMissing: [name] does not exist in storage.
            FileNotFoundError: The file path associated with [name] is not a valid file.
        """
        audio = self.storage.getByName(name)
        self.storage.updateLastPlayed(name)
        file_path = audio.file_path
        if not file_path.is_file():
            raise FileNotFoundError(f"Path not found: {str(file_path)}")

        wav_data = edit(str(file_path), options)

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

        return play_obj

    def playAudioWait(self, name, options):
        """Plays an audio file and waits for it to be done playing.

        Args:
            name: String name of sound.
            options: A playback_options object.

        Raises:
            NameMissing: [name] does not exist in storage.
        """

        return self.playAudio(name, options).wait_done()

    def playSequence(self, names, options):
        """Plays a list of audio files back to back.

        Args:
            names: String list names of sounds (played in order of list).
            options: A playback_options object.

        Raises:
            NameMissing: There is a name in [names] that does not exist in storage.
            NotImplementedError: Attempting to play and save multiple sounds at once.
        """
        if len(names) > 1 and options.save is not None:
            raise NotImplementedError("Cannot save multiple sounds at once")
        for name in names:
            self.playAudioWait(name, options)

    def playParallel(self, names, options):
        """Plays a list of audio files simultaneously.

        Args:
            names: String list names of sounds.
            options: A playback_options object.

        Raises:
            NameMissing: There is a name in [names] that does not exist in storage.
            NotImplementedError: Attempting to play and save multiple sounds at once.
        """
        if len(names) > 1 and options.save is not None:
            raise NotImplementedError("Cannot save multiple sounds at once")
        play_objs = []
        for name in names:
            play_objs.append(self.playAudio(name, options))
        for play_obj in play_objs:
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
            self.addSound(f.name, name)

    def getSounds(self):
        """Returns all sounds in audio archive.

        Returns:
            A list of AudioMedata objects.
        """
        return self.storage.getAll()

    def getByTags(self, tags):
        """Get all sounds associated with the given tags.

        Args:
            tags: String list of tags.

        Returns:
            A list AudioMetadata objects for all sounds associated with the given tags.
        """
        return self.storage.getByTags(tags)

    def fuzzySearch(self, target, n):
        """Get n sounds with smallest edit distance when compared to target.

        Args:
            target: String to search for.
            n: Int maximum number of sounds to return.

        Returns:
            A list of AudioMetadata objects in non-descending order of edit distance
            from target. If there are fewer than n sounds in the archive, all sounds
            will be returned.
        """
        return self.storage.fuzzySearch(target, n)

    def rename(self, old_name, new_name):
        """Renames a sound in the archive.

        Args:
            old_name: String original name of the sound.
            new_name: String new name for the sound.

        Returns:
            Boolean representing whether the operation was successful.

        Raises:
            NameExists: [new_name] already exists in the archive.
            NameMissing: [old_name] does not exist in the archive.
        """
        return self.storage.rename(old_name, new_name)

    def addSound(self, file_path, name=None, author=None):
        """Add a sound to the archive.

        Args:
            file_path: A String with a path to the sound to add.
            name: Either a string with the name for the sound or None.
                If the name is None, it will default to the stem of the file path.
            author: Either a string with the name of the author or None.

        Returns:
            A boolean representing whether the sound was successfully added.

        Raises:
            NameExists: [name] is already in the archive.
            FileNotFoundError: [file_path] is not a valid path to a file.
            ValueError: [name] or [author] is too long.
        """
        return self.storage.addSound(file_path, name=name, author=author)

    def removeSound(self, name):
        """Remove a sound from the archive.

        This also removes the file from the base_directory.

        Args:
            name: String name of sound.

        Returns:
            A boolean representing whether the operation was successful.

        Raises:
            NameMissing: [name] does not exist in the archive.
        """
        return self.storage.removeSound(name)

    def addTag(self, name, tag):
        """Add a tag to a sound.

        Args:
            name: String name of sound to add a tag to.
            tag: String name of tag.

        Raises:
            NameMissing: [name] isn't in the archive.
            ValueError: [tag] is too long.
        """
        return self.storage.addTag(name, tag)

    def removeTag(self, name, tag):
        """Remove a tag from a sound.

        Args:
            name: String name of sound to remove a tag from.
            tag: String name of tag.

        Raises:
            NameMissing: [name] isn't in the archive.
        """
        return self.storage.removeTag(name, tag)

    def clean(self):
        """Remove all sounds from the archive without an associated file.

        Returns:
            A list of AudioMetadata objects that were removed.
        """
        return self.storage.clean()
