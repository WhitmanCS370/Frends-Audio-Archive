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
        """Constructor.

        Args:
            speed: float > 0.01
            volume: float > 0
            reverse: bool
            start_percent/end_percent: float, 0 <= start_percent < end_percent < 1
            start_sec/end_sec: float >= 0

        Raises:
            ValueError: invalid option.
        """
        if speed is not None and speed <= 0.01:
            raise ValueError("Speed must be greater than 0.01")
        if volume is not None and volume < 0:
            raise ValueError("Volume must be nonnegative.")
        if (
            start_percent is not None and end_percent is not None
        ) and start_percent <= end_percent:
            raise ValueError("start_percent must be less than end_percent")
        if (start_sec is not None and end_sec is not None) and start_sec <= end_sec:
            raise ValueError("start_sec must be less than end_sec")
        if (start_percent is not None and (start_percent < 0 or start_percent > 1)) or (
            end_percent is not None and (end_percent < 0 or end_percent > 1)
        ):
            raise ValueError("Start/end percentages must be between 0 and 1.")
        if (start_sec is not None and start_sec < 0) or (
            end_sec is not None and end_sec < 0
        ):
            raise ValueError("Start/end second must be nonnegative")
        num_percent_fields = int(start_percent is not None) + int(
            end_percent is not None
        )
        num_sec_fields = int(start_sec is not None) + int(end_sec is not None)
        if num_percent_fields != 0 and num_sec_fields != 0:
            raise ValueError("You must only specify start/end seconds or percentages.")
        self.speed = speed
        self.volume = volume
        self.reverse = reverse
        self.start_percent = start_percent
        self.end_percent = end_percent
        self.start_sec = start_sec
        self.end_sec = end_sec
        self.save = save
        self.transpose = transpose
