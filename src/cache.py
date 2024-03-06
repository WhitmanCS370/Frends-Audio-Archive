import random


# CR: I think that we should rethink the internal data structures used
# Typically, LRU caches have an O(1) time complexity for insertion, updating, and
# removing.  I think you can achieve this with either a doubly linked list and a
# dictionary, or you might consider looking to see if there's a package you can use if
# you'd prefer.  I'm happy to talk about this more if you want.
# (Also, this doesn't need to be fixed before we merge PR)
class Cache:
    """
    This class is for use with the audioObj objects for quicker retrieval
    of more frequently used sounds
    """

    def __init__(self, size):
        self.cache = {}
        # CR: What do you think about setting maxCacheSize to something like
        # min(size, 10000)?
        self.maxCacheSize = size

    def getByName(self, name):
        # parse dictionary for sounds that have the given title
        return self.cache.get(name)

    # CR: I don't know what the right answer is, but I'm not sure if returning
    # strings from this is a good idea. I think one common idiom is to return True
    # if something is added (and False if it wasn't added)
    def cacheData(self, soundObj):
        # check if object is already cached
        if soundObj.name in self.cache:
            # update the time accessed and return early
            soundObj.updateLastAccessed()
            return "object already in cache"
        if not self.isCacheFull():  # cache miss with a partially empty cache
            # add soundObj to cache
            self.cache[soundObj.name] = soundObj
        else:  # cache miss with a full cache
            # evict oldest sound
            titleToEvict = self.getOldestEntry()
            self.cache.pop(titleToEvict)
            # add soundObj to cache
            self.cache[soundObj.name] = soundObj
        soundObj.updateLastAccessed()
        return "object cached"

    # This should be called before a name change of an audio object
    def rename(self, name, newName):
        if name in self.cache:
            tempObject = self.cache[name]
            self.cache.pop(name)
            self.cache[newName] = tempObject

    def isCacheFull(self):
        # CR: return len(self.cache) >= self.maxCacheSize
        if len(self.cache) < self.maxCacheSize:
            return False
        return True

    def getOldestEntry(self):
        # CR: Why are we initializing oldest to a random value?
        _, oldest = random.choice(list(self.cache.items()))
        for name in self.cache:
            if self.cache[name].last_accessed < oldest.last_accessed:
                oldest = self.cache[name]
        return oldest.name
