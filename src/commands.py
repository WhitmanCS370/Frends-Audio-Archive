"""This module is in charge of handling audio archive commands, such as listening to
sounds, adding sounds to the archive, renaming them, etc.
"""

import audioop
from pydub import AudioSegment
from pydub.effects import speedup
import simpleaudio as sa
import tempfile
import wave
import librosa
import soundfile
import os

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

    def playAudio(self, name, reverse=False, volume=None, speed=None, transpose=None):
        """Plays an audio file after applying effects to the sound.

        Note that multiple effects can be applied simultaneously.

        Args:
            name: String name of sound.
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.
            transpose: Int amount to transpose by (in semitones, negative values shift downwards)

        Returns:
            A PlayObject.

        Raises:
            NameMissing: [name] does not exist in storage.
            FileNotFoundError: The file path associated with [name] is not a valid file.
        """
        audio = self.storage.getByName(name)
        file_path = audio.file_path
        if not file_path.is_file():
            raise FileNotFoundError(f"Path not found: {str(file_path)}")
        
        if transpose:
            y, sr = librosa.load(file_path)
            steps = transpose
            new_y = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
            file_path = "_.wav"
            soundfile.write(file_path, new_y, sr)
            

        with wave.open(str(file_path), "rb") as wave_read:
            audio_data = wave_read.readframes(wave_read.getnframes())
            num_channels = wave_read.getnchannels()
            bytes_per_sample = wave_read.getsampwidth()
            sample_rate = wave_read.getframerate()
        
        if transpose:
            os.remove(file_path)
        
        if reverse:
            audio_data = audioop.reverse(audio_data, bytes_per_sample)
        if volume is not None and volume >= 0:
            audio_data = audioop.mul(audio_data, bytes_per_sample, volume)
        if speed is not None and speed > 0:
            audio_data, num_channels, bytes_per_sample, sample_rate = self._changeSpeed(
                audio_data, bytes_per_sample, sample_rate, num_channels, speed
            )
        wave_obj = sa.WaveObject(
            audio_data, num_channels, bytes_per_sample, sample_rate
        )
        play_obj = wave_obj.play()


        return play_obj

    def playAudioWait(self, name, reverse=False, volume=None, speed=None, transpose=None):
        """Plays an audio file and waits for it to be done playing.

        Args:
            name: String name of sound.
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: [name] does not exist in storage.
        """
        self.playAudio(name, reverse=reverse, volume=volume, speed=speed, transpose=transpose).wait_done()

    def playSequence(self, names, reverse=False, volume=None, speed=None, transpose=None):
        """Plays a list of audio files back to back.

        Args:
            names: String list names of sounds (played in order of list).
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: There is a name in [names] that does not exist in storage.
        """
        for name in names:
            self.playAudioWait(name, reverse=reverse, volume=volume, speed=speed, transpose=transpose)

    def playParallel(self, names, reverse=False, volume=None, speed=None, transpose=None):
        """Plays a list of audio files simultaneously.

        Args:
            names: String list names of sounds.
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: There is a name in [names] that does not exist in storage.
        """
        play_objs = []
        for name in names:
            play_objs.append(
                self.playAudio(name, reverse=reverse, volume=volume, speed=speed, transpose=transpose)
            )
        for play_obj in play_objs:
            play_obj.wait_done()

    def getSounds(self):
        """Returns all sounds in audio archive.

        Returns:
            A list of AudioMedata objects.
        """
        return self.storage.getAll()

    def getByTags(self, tags):
        """Get all sounds associated with the given tags.

        Caches sounds that are not already cached.

        Args:
            tags: String list of tags.

        Returns:
            A list AudioMetadata objects for all sounds associated with the given tags.
        """
        return self.storage.getByTags(tags)

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

    def _changeSpeed(
        self, audio_data, bytes_per_sample, sample_rate, num_channels, speed
    ):
        """Change the speed of a sound."""
        # source: https://stackoverflow.com/questions/74136596/how-do-i-change-the-speed-of-an-audio-file-in-python-like-in-audacity-without
        audio = AudioSegment(
            data=audio_data,
            sample_width=bytes_per_sample,
            frame_rate=sample_rate,
            channels=num_channels,
        )
        if speed > 1:
            audio = speedup(audio, playback_speed=speed)
        else:
            altered_audio = audio._spawn(
                audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)}
            )
            audio = altered_audio.set_frame_rate(audio.frame_rate)
        # if we directly export this as a wav, it's somehow corrupted when we tried to read
        # it back and play it.
        # But, if we export it as a mp3, load it, export it as a wav, and then play that,
        # everything works as intended 💯😁
        with tempfile.NamedTemporaryFile(suffix=".mp3") as mp3_file:
            audio.export(mp3_file.name, format="mp3")
            audio = AudioSegment.from_mp3(mp3_file.name)
            with tempfile.NamedTemporaryFile(suffix=".wav") as wav_file:
                audio.export(wav_file.name, format="wav")
                with wave.open(wav_file.name, "rb") as wave_read:
                    audio_data = wave_read.readframes(wave_read.getnframes())
                    num_channels = wave_read.getnchannels()
                    bytes_per_sample = wave_read.getsampwidth()
                    sample_rate = wave_read.getframerate()
        return audio_data, num_channels, bytes_per_sample, sample_rate