import unittest
import sys
sys.path.insert(1, '../src')
from cache import Cache
import audio_metadata
import os
import pathlib

#helper function that is needed to set up each cache test
def getMetadataList():
    soundObjs = []
    temp = 0
    direct = pathlib.Path("test_sounds")
    for sound in os.listdir(direct):
        filename = os.fsdecode(sound)
        if filename.endswith(".wav") or filename.endswith(".mp3"): 
            filepath = os.path.join("test/test_sounds/", filename)            
        tempSoundMetaData = audio_metadata.AudioMetadata(filePath = filepath,
                                              name = str(temp),
                                              duration = None,
                                              dateAdded = None,
                                              author = None,
                                              tags = ["test"])
        soundObjs.append(tempSoundMetaData)
        temp += 1
    return soundObjs
    

class CacheTests(unittest.TestCase):    
    def test_setUpCache(self):
        tempCache = Cache(5)
        self.assertFalse(tempCache.isCacheFull())
    
    #should also account for testing for a standard cache hit
    def test_emptyCacheMiss(self):
        soundObjs = getMetadataList()
        tempCache = Cache(5)
        self.assertIsNone(tempCache.getByName("0"))
        tempCache.cacheData(soundObjs[0])
        self.assertEqual(tempCache.getByName("0").name,
                         "0")
    
    def test_fillCache(self):   
        soundObjs = getMetadataList()
        tempCache = Cache(5)
        tempCache.cacheData(soundObjs[0])
        tempCache.cacheData(soundObjs[1])
        tempCache.cacheData(soundObjs[2])
        tempCache.cacheData(soundObjs[3])
        tempCache.cacheData(soundObjs[4])
        self.assertTrue(tempCache.isCacheFull())
    
    #Testing for a full cache and checks to see if it evicts properly
    def test_cacheMissAndEvict(self):
        soundObjs = getMetadataList()
        tempCache = Cache(5)
        tempCache.cacheData(soundObjs[0])
        tempCache.cacheData(soundObjs[1])
        tempCache.cacheData(soundObjs[2])
        tempCache.cacheData(soundObjs[3])
        tempCache.cacheData(soundObjs[4])
        self.assertIsNone(tempCache.getByName("5"))
        tempCache.cacheData(soundObjs[5])
        self.assertEqual(tempCache.getByName("5").name,
                         "5")
     
    #Fills the cache and evicts and checks to see if it evicts the correct value
    def test_cacheHits(self):
        soundObjs = getMetadataList()
        tempCache = Cache(5)
        for i in range(0,5):
            tempCache.cacheData(soundObjs[i])
            soundObjs[i].last_accessed = i #simulate a time difference between caches
        self.assertIsNone(tempCache.getByName("5"))
        tempCache.cacheData(soundObjs[5])
        self.assertEqual(tempCache.getByName("5").name,
                         "5")
        self.assertEqual(tempCache.getByName("1").name,
                         "1")
        self.assertEqual(tempCache.getByName("2").name,
                         "2")
        self.assertEqual(tempCache.getByName("3").name,
                         "3")
        self.assertEqual(tempCache.getByName("4").name,
                         "4")
        self.assertEqual(tempCache.getByName("5").name,
                         "5")

if __name__ == "__main__":
    unittest.main()    
        