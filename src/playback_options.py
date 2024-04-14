class PlaybackOptions:
    def __init__(
        self,
        speed,
        volume,
        reverse,
        start_percent,
        end_percent,
        start_sec,
        end_sec,
        save,
        transpose,
    ):
        self.speed = speed
        self.volume = volume
        self.reverse = reverse
        self.start_percent = start_percent
        self.end_percent = end_percent
        self.start_sec = start_sec
        self.end_sec = end_sec
        self.save = save
        self.transpose = transpose
