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

    def playAudio(
        self,
        name,
        options #playback options
        # reverse=False,
        # volume=None,
        # speed=None,
        # start_percent=None,
        # end_percent=None,
        # start_sec=None,
        # end_sec=None,
        # save=None,
        # transpose=None,
    ):
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

        if options.transpose:
            y, sr = librosa.load(file_path)
            steps = options.transpose
            new_y = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
            file_path = file_path[:-4] + "_.wav"
            soundfile.write(file_path, new_y, sr)

        with wave.open(str(file_path), "rb") as wave_read:
            audio_data = wave_read.readframes(wave_read.getnframes())
            num_channels = wave_read.getnchannels()
            bytes_per_sample = wave_read.getsampwidth()
            sample_rate = wave_read.getframerate()

        if options.transpose:
            os.remove(file_path)

        if options.reverse:
            audio_data = audioop.reverse(audio_data, bytes_per_sample)
        if options.volume is not None and options.volume >= 0:
            audio_data = audioop.mul(audio_data, bytes_per_sample, options.volume)
        if options.speed is not None and options.speed > 0:
            audio_data, num_channels, bytes_per_sample, sample_rate = self._changeSpeed(
                audio_data, bytes_per_sample, sample_rate, num_channels, speed
            )

        if options.start_sec is not None or options.end_sec is not None:
            options.start_percent, options.end_percent = self._calculatePercent(
                audio_data,
                bytes_per_sample,
                num_channels,
                sample_rate,
                options.start_sec,
                options.end_sec,
            )

        if options.start_percent is not None or options.end_percent is not None:
            audio_data = self._cropSound(
                audio_data, bytes_per_sample, num_channels, options.start_percent, options.end_percent
            )

        wave_obj = sa.WaveObject(
            audio_data, num_channels, bytes_per_sample, sample_rate
        )
        play_obj = wave_obj.play()

        if options.save is not None:
            if options.save == name:
                self.removeSound(name)
            self._saveAudio(
                options.save, num_channels, audio_data, bytes_per_sample, sample_rate
            )

        return play_obj

    def playAudioWait(
        self,
        name,
        options # playback options
    ):
        """Plays an audio file and waits for it to be done playing.

        Args:
            name: String name of sound.
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: [name] does not exist in storage.
        """

        return self.playAudio(
            name,
            options
        ).wait_done()

    def playSequence(
        self,
        names,
        options
    ):
        """Plays a list of audio files back to back.

        Args:
            names: String list names of sounds (played in order of list).
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: There is a name in [names] that does not exist in storage.
            NotImplementedError: Attempting to play and save multiple sounds at once.
        """
        if len(names) > 1 and options.save is not None:
            raise NotImplementedError("Cannot save multiple sounds at once")
        for name in names:
            self.playAudioWait(
                name,
                options
            )

    def playParallel(
        self,
        names,
        options
    ):
        """Plays a list of audio files simultaneously.

        Args:
            names: String list names of sounds.
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: There is a name in [names] that does not exist in storage.
            NotImplementedError: Attempting to play and save multiple sounds at once.
        """
        if len(names) > 1 and options.save is not None:
            raise NotImplementedError("Cannot save multiple sounds at once")
        play_objs = []
        for name in names:
            play_objs.append(
                self.playAudio(
                    name,
                    options
                )
            )
        for play_obj in play_objs:
            play_obj.wait_done()

    def _calculatePercent(
        self,
        audio_data,
        bytes_per_sample,
        num_channels,
        sample_rate,
        start_sec=None,
        end_sec=None,
    ):
        """Calculates the start and end percent of the audio data based on the start and end seconds.

        start_sec and end_sec will both be returned as floats, even if they are not None.

        Args:
            audio_data: bytes of audio data
            sample_rate: int sample rate of audio data
            num_channels: int number of channels in audio data.
            start_sec: The start position of the audio in seconds.
            end_sec: The end position of the audio in seconds.

        Raises:
            None
        """
        total_duration_seconds = len(audio_data) / (
            sample_rate * bytes_per_sample * num_channels
        )

        # Calculate start percent
        if start_sec is None:
            start_percent = 0
        else:
            start_percent = start_sec / total_duration_seconds

        # Calculate end percent
        if end_sec is None:
            end_percent = 1
        else:
            end_percent = end_sec / total_duration_seconds

        return start_percent, end_percent

    def _cropSound(
        self,
        audio_data,
        bytes_per_sample,
        num_channels,
        start_percent=None,
        end_percent=None,
    ):
        """Returns modified audio data for the cropped sound starting at start_percent and ending at end_percent.

        Make the buffer size a multiple of bytes-per-sample and the number of channels.

        Args:
            audio_data: bytes of audio data
            sample_rate: int sample rate of audio data
            num_channels: int number of channels in audio data.
            start_percent: The start position of the audio as a percent, ranges from 0 to 1.
            end_percent: The end position of the audio as a percent, ranges from 0 to 1.

        Raises:
            ValueError: start_percent is greater than end_percent or one of the values is
                less than 0 or greater than 1.
        """
        # Reset null positions
        if start_percent is None:
            start_percent = 0
        if end_percent is None:
            end_percent = 1

        # Check for invalid values
        if min(start_percent, end_percent) < 0 or max(start_percent, end_percent) > 1:
            raise ValueError("Start and end percent must be between 0 and 1")
        if start_percent >= end_percent:
            raise ValueError("Start must be less than end")

        # Calculate start and end indices
        def calculate_index(percent):
            return int(
                percent * len(audio_data) / (bytes_per_sample * num_channels)
            ) * (bytes_per_sample * num_channels)

        start_index = calculate_index(start_percent)
        stop_index = calculate_index(end_percent)

        return audio_data[start_index:stop_index]

    def _saveAudio(self, name, num_channels, audio_data, bytes_per_sample, sample_rate):
        """Saves the edited sound to a file and to the database.

        Args:
            name: String name of sound.
            audio_data: bytes of audio data.
            file_path: String path to save the sound to.

        """
        path = f"sounds/{name}output.wav"
        with wave.open(path, "wb") as wave_write:
            wave_write.setnchannels(num_channels)
            wave_write.setsampwidth(bytes_per_sample)
            wave_write.setframerate(sample_rate)
            wave_write.writeframes(audio_data)

        self.addSound(path, name)

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
