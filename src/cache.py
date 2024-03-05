# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:34:06 2024

@author: creek
"""
import random

class Cache:
    """
    This class is for use with the audioObj objects for quicker retrieval
    of more frequently used sounds
    """
    def __init__(self, size):
        self.cache = dict()
        self.maxCacheSize = size
        
    def getByName(self, name):
        #parse dictionary for sounds that have the given title
        if name in self.cache:
            return self.cache[name]
        return None
        
    def cacheData(self, soundObj):
        #check if object is already cached
        if soundObj.name in self.cache:
            #update the time accessed and return early
            soundObj.updateLastAccessed()
            return "object already in cache"
        if not self.isCacheFull(): #cache miss with a partially empty cache
            #add soundObj to cache
            self.cache[soundObj.name] = soundObj
        else: #cache miss with a full cache
            #evict oldest sound
            titleToEvict = self.getOldestEntry()
            self.cache.pop(titleToEvict)
            #add soundObj to cache
            self.cache[soundObj.name] = soundObj
        soundObj.updateLastAccessed()
        return "object cached"
    
    #This should be called before a name change of an audio object
    def rename(self, name, newName):
        if name in self.cache:
            tempObject = self.cache[name]
            self.cache.pop(name)
            self.cache[newName] = tempObject
        
    
    def isCacheFull(self):
        if len(self.cache) < self.maxCacheSize:
            return False
        return True
    
    def getOldestEntry(self):
        notNeeded, oldest = random.choice(list(self.cache.items()))
        for name in self.cache:
            if self.cache[name].last_accessed < oldest.last_accessed:
                oldest = self.cache[name]
        return oldest.name
            

        
        