import json
import logging
import threading
from typing import Dict, List, Optional, Type

logger = logging.getLogger("pycountry.db")


class Data:
    def __init__(self, **fields: str):
        self._fields = fields

    def __getattr__(self, key: str) -> str:
        if key not in self._fields:
            raise AttributeError
        return self._fields[key]

    def __setattr__(self, key: str, value: str) -> None:
        if key != "_fields":
            self._fields[key] = value
        super().__setattr__(key, value)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        fields = ", ".join("%s=%r" % i for i in sorted(self._fields.items()))
        return f"{cls_name}({fields})"

    def __dir__(self) -> List[str]:
        return dir(self.__class__) + list(self._fields)


class Script(Data):
    pass


class Currency(Data):
    pass


class Language(Data):
    pass


class LanguageFamily(Data):
    pass


class Country(Data):
    def __getattr__(self, key):
        if key in ("common_name", "official_name"):
            if key not in self._fields:
                return self._fields["name"]
        return super().__getattr__(key)


def lazy_load(f: Type) -> Type:
    def load_if_needed(self: Type, *args: Type, **kw: Type) -> Type:
        if not self._is_loaded:
            with self._load_lock:
                self._load()
        return f(self, *args, **kw)

    return load_if_needed


class Database:
    data_class = None
    data_class_base: Type = Data
    data_class_name: Optional[str] = None
    root_key: Optional[str] = None
    no_index: List[str] = []

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._is_loaded = False
        self._load_lock = threading.Lock()

    def _load(self) -> None:
        if self._is_loaded:
            # Help keeping the _load_if_needed code easier
            # to read.
            return
        self.objects = []
        self.index_names = set()
        self.indices = {}

        if not self.data_class:
            self.data_class = type(
                self.data_class_name, (self.data_class_base,), {}
            )

        with open(self.filename, encoding="utf-8") as f:
            tree = json.load(f)

        for entry in tree[self.root_key]:
            obj = self.data_class(**entry)
            self.objects.append(obj)
            # Inject into index.
            for key, value in entry.items():
                # Lookups and searches are case insensitive. Normalize
                # here.
                value = value.lower()
                if key in self.no_index:
                    continue
                index = self.indices.setdefault(key, {})
                if value in index:
                    logger.debug(
                        "%s %r already taken in index %r and will be "
                        "ignored. This is an error in the databases."
                        % (self.data_class_name, value, key)
                    )
                index[value] = obj

        self._is_loaded = True

    # Public API

    @lazy_load
    def __iter__(self) -> Type:
        return iter(self.objects)

    @lazy_load
    def __len__(self) -> int:
        return len(self.objects)

    @lazy_load
    def get(self, **kw: str) -> Type:
        kw.setdefault("default", None)
        default = kw.pop("default")
        if len(kw) != 1:
            raise TypeError("Only one criteria may be given")
        field, value = kw.popitem()
        if not isinstance(value, str):
            raise LookupError()
        # Normalize for case-insensitivity
        value = value.lower()
        index = self.indices[field]
        try:
            return index[value]
        except KeyError:
            # Pythonic APIs implementing     get() shouldn't raise KeyErrors.
            # Those are a bit unexpected and they should rather support
            # returning `None` by default and allow customization.
            return default

    @lazy_load
    def lookup(self, value: str) -> Type:
        if not isinstance(value, str):
            raise LookupError()

        # Normalize for case-insensitivity
        value = value.lower()

        # Use indexes first
        for key in self.indices:
            try:
                return self.indices[key][value]
            except LookupError:
                pass

        # Use non-indexed values now. Avoid going through indexed values.
        for candidate in self:
            for k in self.no_index:
                v = candidate._fields.get(k)
                if v is None:
                    continue
                if v.lower() == value:
                    return candidate

        raise LookupError("Could not find a record for %r" % value)
