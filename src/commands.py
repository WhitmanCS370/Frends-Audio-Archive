"""This module is in charge of handling audio archive commands, such as listening to
sounds, adding sounds to the archive, renaming them, etc.
"""

import audioop
from pydub import AudioSegment
from pydub.effects import speedup
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

    def playAudio(self, name, reverse=False, volume=None, speed=None, start_sec=None, end_sec=None, save=None):
        """Plays an audio file after applying effects to the sound.

        Note that multiple effects can be applied simultaneously.

        Args:
            name: String name of sound.
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

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

        with wave.open(str(file_path), "rb") as wave_read:
            audio_data = wave_read.readframes(wave_read.getnframes())
            num_channels = wave_read.getnchannels()
            bytes_per_sample = wave_read.getsampwidth()
            sample_rate = wave_read.getframerate()

        if reverse:
            audio_data = audioop.reverse(audio_data, bytes_per_sample)
        if volume is not None and volume >= 0:
            audio_data = audioop.mul(audio_data, bytes_per_sample, volume)
        if speed is not None and speed > 0:
            audio_data, num_channels, bytes_per_sample, sample_rate = self._changeSpeed(
                audio_data, bytes_per_sample, sample_rate, num_channels, speed
            )
        if start_sec is not None or end_sec is not None:
            audio_data = self.cropSound(audio_data, sample_rate, start_sec, end_sec)

        wave_obj = sa.WaveObject(
            audio_data, num_channels, bytes_per_sample, sample_rate
        )
        play_obj = wave_obj.play()

        if save is not None:
            if save == name:
                self.removeSound(name)
            self.saveAudio(save, num_channels, audio_data, bytes_per_sample, sample_rate)

        return play_obj

    def playAudioWait(self, name, reverse=False, volume=None, speed=None, start_sec=None, end_sec=None, save=None):
        """Plays an audio file and waits for it to be done playing.

        Args:
            name: String name of sound.
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: [name] does not exist in storage.
        """
        return self.playAudio(name, reverse=reverse, volume=volume, speed=speed, start_sec=start_sec, end_sec=end_sec, save=save).wait_done()

    def playSequence(self, names, reverse=False, volume=None, speed=None, start_sec=None, end_sec=None, save=None):
        """Plays a list of audio files back to back.

        Args:
            names: String list names of sounds (played in order of list).
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: There is a name in [names] that does not exist in storage.
        """
        if len(names) > 1 and save is not None:
            raise NotImplementedError("Cannot save multiple sounds at once")
        for name in names:
            self.playAudioWait(name, reverse=reverse, volume=volume, speed=speed, start_sec=start_sec, end_sec=end_sec, save=save)

    def playParallel(self, names, reverse=False, volume=None, speed=None, start_sec=None, end_sec=None, save=None):
        """Plays a list of audio files simultaneously.

        Args:
            names: String list names of sounds.
            reverse: Boolean whether to reverse the sound.
            volume: Float volume to play the sound at (1.0 is normal) or None which means don't change the volume.
            speed: Float speed to play the sound at (1.0 is normal) or None which means don't change the speed.

        Raises:
            NameMissing: There is a name in [names] that does not exist in storage.
        """
        if len(names) > 1 and save is not None:
            raise NotImplementedError("Cannot save multiple sounds at once")
        play_objs = []
        for name in names:
            play_objs.append(
                self.playAudio(name, reverse=reverse, volume=volume, speed=speed, start_sec=start_sec, end_sec=end_sec, save=save)
            )
        for play_obj in play_objs:
            play_obj.wait_done()
    
    def cropSound(self, audio_data, sample_rate, start_sec=None, end_sec=None):
        """ Returns modiefied audio data for the cropped sound starting at start_sec and ending at end_sec.
        
        Args: 
            audio_data: bytes of audio data
            sample_rate: int sample rate of audio data
            start_sec: float start time of cropped audio in seconds
            end_sec: float end time of cropped audio in seconds

        Raises:
            ValueError: start must be greater than or equal to 0
            ValueError: end must be less than or equal to the length of the audio data
            ValueError: start must be less than the length of the audio data
            ValueError: start must be less than end

        """
        start_frame = int(start_sec * sample_rate) if start_sec is not None else 0
        end_frame = int(end_sec * sample_rate) if end_sec is not None else len(audio_data)

        if start_frame < 0:
            raise ValueError("Start must be greater than or equal to 0")
        if end_frame > len(audio_data):
            raise ValueError("End must be less than or equal to the length of the audio data")
        if start_frame >= len(audio_data):
            raise ValueError("Start must be less than the length of the audio data")
        if start_frame >= end_frame:
            raise ValueError("Start must be less than end")
        
        # print(f"start_frame: {start_frame}")
        # print(f"end_frame: {end_frame}")
        # print(f"len(audio_data): {len(audio_data * sample_rate)}")

        cropped_audio = audio_data[start_frame:end_frame]

        return cropped_audio
    
    def saveAudio(self, name, num_channels, audio_data, bytes_per_sample, sample_rate):
        """Saves the edited sound to a file and to the database.

        Args:
            name: String name of sound.
            audio_data: bytes of audio data.
            file_path: String path to save the sound to.

        """
        path = 'sounds/'+name+'output.wav'
        with wave.open(path, 'wb') as wave_write:
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
