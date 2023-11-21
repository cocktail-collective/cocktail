__all__ = ["FixedLengthMapping"]

import collections


class FixedLengthMapping(collections.abc.MutableMapping):
    """
    A dictionary-like object that stores only a maximum number of items, evicting the least recently used item when
    necessary.
    """

    def __init__(self, max_entries=200):
        super().__init__()
        self._store = collections.OrderedDict()
        self._max_entries = max_entries

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, item):
        if len(self._store) >= self._max_entries and key not in self._store:
            self._store.pop(next(iter(self._store)))

        self._store[key] = item

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)
