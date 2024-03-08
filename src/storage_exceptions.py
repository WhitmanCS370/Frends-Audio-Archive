class StorageException(Exception):
    """Problem with storage"""


class DatabaseException(StorageException):
    """Problem with database"""


class NameMissing(DatabaseException):
    """No sound associated with a name in the database"""


class NameExists(DatabaseException):
    """There exists a sound with the name in the database"""
