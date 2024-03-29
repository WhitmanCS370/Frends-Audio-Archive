import unittest
from src.cache import Cache
from src.audio_metadata import AudioMetadata


def makeDummySound(name):
    """Make an AudioMetadata with only the name filled out."""
    return AudioMetadata(
        filePath=".", name=name, duration=0, dateAdded="", author="", tags=set()
    )


class CacheTests(unittest.TestCase):
    def test_add(self):
        cache = Cache()
        sounds = [makeDummySound(str(i)) for i in range(10)]
        for sound in sounds:
            cache.add(sound)

        self.assertSetEqual(set(cache.soundNames.keys()), {str(i) for i in range(10)})

    def test_getByName(self):
        cache = Cache()
        cache.add(makeDummySound("stuff"))
        self.assertEqual(cache.getByName("stuff").name, "stuff")

    def test_removeByName(self):
        cache = Cache()
        names = [str(i) for i in range(10)]
        for name in names:
            cache.add(makeDummySound(name))
        for name in names:
            cache.removeByName(name)
        self.assertEqual(len(cache.soundNames), 0)
        self.assertIsNone(cache.head)
        self.assertIsNone(cache.tail)

    def test_cacheEviction(self):
        """Add sounds named 30 to 0 to a cache with max size 10 - all sounds should be
        evicted except 0-9.
        """
        cache = Cache(10)
        names = [str(i) for i in range(30, -1, -1)]
        for name in names:
            cache.add(makeDummySound(name))
        remaining_names = set(cache.soundNames.keys())
        self.assertSetEqual(remaining_names, {str(i) for i in range(10)})
        self.assertEqual(cache.head.val.name, "0")
        self.assertEqual(cache.tail.val.name, "9")
        self.assertIsNone(cache.head.prev)
        self.assertIsNone(cache.tail.next)

    def test_rename(self):
        cache = Cache()
        cache.add(makeDummySound("stuff"))
        cache.rename("stuff", makeDummySound("thing"))
        self.assertIsNone(cache.getByName("stuff"))
        self.assertEqual(cache.getByName("thing").name, "thing")


if __name__ == "__main__":
    unittest.main()
