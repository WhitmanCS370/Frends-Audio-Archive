class Cache:
    """
    This cache implements a LRU caching strategy in order to eliminate database queries
    when possible.

    Internally, it relies on a doubly linked list and a dictionary to provide constant time
    retrieval and deletion.

    Attributes:
        soundNames: String -> DLL_Node dictionary.
        head: DLL_Node - the most recently accessed AudioMetadata Object (or None if the
            cache is empty). head.prev will always be None.
        tail: DLL_Node - the least recently accessed AudioMetadata Object (or None if the
            cache is empty). tail.next will always be None.
        maxCacheSize: The maximum number of sounds to cache (capped at 10,000).
    """

    def __init__(self, maxCacheSize=10000):
        """Constructor.

        Args:
            maxCacheSize: The maximum number of sounds to cache (capped at 10,000).
        """
        self.soundNames = {}
        self.maxCacheSize = min(maxCacheSize, 10000)
        self.head = None
        self.tail = None

    def add(self, sound):
        """Add a sound to the cache, or move it to the front of the DLL if it already exists.

        Args:
            sound: An AudioMetadata object.
        """
        if sound.name in self.soundNames:
            self.removeByName(sound.name)

        new_node = DLL_Node(val=sound, prev=None, next=self.head)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.head.prev = new_node
            self.head = new_node
        self.soundNames[sound.name] = new_node
        if self._isCacheFull():
            oldest_sound = self.tail.val
            self.removeByName(oldest_sound.name)

    def getByName(self, name):
        """Get a sound from the archive with its name.

        Args:
            name: String name of sound

        Returns:
            Either an AudioMetadata object if the sound is cached or None.
        """
        node = self.soundNames.get(name)
        if node is None:
            return None
        # Reset to front of DLL
        self.removeByName(name)
        self.add(node.val)
        return node.val

    def removeByName(self, name):
        """Remove a sound from the cache.

        Args:
            name: The name of the sound to remove.
        """
        if name not in self.soundNames:
            return
        node = self.soundNames[name]
        del self.soundNames[node.val.name]
        if node == self.head:
            if node == self.tail:
                self.head, self.tail = None, None
                return
            self.head = self.head.next
            self.head.prev = None
            return
        elif node == self.tail:
            self.tail = self.tail.prev
            self.tail.next = None
            return

        before, after = node.prev, node.next
        before.next = after
        after.prev = before

    def rename(self, oldName, newSound):
        """Called when a sound is renamed.

        Args:
            oldName: The former name of the sound (string).
            newSound: An up-to-date AudioMetadata object.
        """
        self.removeByName(oldName)
        self.add(newSound)

    def _isCacheFull(self):
        return len(self.soundNames) > self.maxCacheSize


class DLL_Node:
    """Doubly linked list node to be used for the LRU cache."""

    def __init__(self, val=None, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next

    def __eq__(self, other):
        return self.val == other.val
