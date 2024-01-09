import json
import logging
import threading
import warnings
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

logger = logging.getLogger("pycountry.db")
D = TypeVar("D", bound="Data")
F = TypeVar("F", bound=Callable)


class Data:
    def __init__(self, **fields: str) -> None:
        self._fields = fields

    def __getattr__(self, key: str) -> str:
        if key in self._fields:
            return self._fields[key]
        raise AttributeError()

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

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        # allow casting into a dict
        return iter(self._fields.items())


class Country(Data):
    def __getattr__(self, key: str) -> str:
        if key in ("common_name", "official_name"):
            # First try to get the common_name or official_name
            value = self._fields.get(key)
            if value is not None:
                return value
            # Fall back to name if common_name or official_name is not found
            name = self._fields.get("name")
            if name is not None:
                warning_message = (
                    f"Country's {key} not found. Country name provided instead."
                )
                warnings.warn(warning_message, UserWarning)
                return name
            raise AttributeError()
        else:
            # For other keys, simply return the value or raise an error
            if key in self._fields:
                return self._fields[key]
            raise AttributeError()


class Subdivision(Data):
    pass


def lazy_load(f: F) -> F:
    def load_if_needed(self: Any, *args: Any, **kw: Any) -> Any:
        if not self._is_loaded:
            with self._load_lock:
                self._load()
        return f(self, *args, **kw)

    return cast(F, load_if_needed)


class Database(Generic[D]):
    factory: Type[D]
    indices: Dict[str, Dict[str, D]]
    no_index: List[str] = []
    objects: List[D]
    root_key: Optional[str] = None

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._is_loaded = False
        self._load_lock = threading.Lock()

    def _clear(self) -> None:
        self._is_loaded = False
        self.objects = []
        self.indices = {}

    def _load(self) -> None:
        if self._is_loaded:
            # Help keeping the _load_if_needed code easier
            # to read.
            return
        self._clear()

        with open(self.filename, encoding="utf-8") as f:
            tree = json.load(f)

        for entry in tree[self.root_key]:
            obj = self.factory(**entry)
            self.objects.append(obj)
            # Inject into index.
            for key, value in entry.items():
                if key in self.no_index:
                    continue
                # Lookups and searches are case insensitive. Normalize
                # here.
                index = self.indices.setdefault(key, {})
                value = value.lower()
                if value in index:
                    logger.debug(
                        "%s %r already taken in index %r and will be "
                        "ignored. This is an error in the databases."
                        % (self.factory.__name__, value, key)
                    )
                index[value] = obj

        self._is_loaded = True

    # Public API

    @lazy_load
    def add_entry(self, **kw: str) -> None:
        # create the object with the correct dynamic type
        obj = self.factory(**kw)

        # append object
        self.objects.append(obj)

        # update indices
        for key, value in kw.items():
            if key in self.no_index:
                continue
            value = value.lower()
            index = self.indices.setdefault(key, {})
            index[value] = obj

    @lazy_load
    def remove_entry(self, *, default: Optional[D] = None, **kw: str) -> None:
        # ignore the default to receive None if no entry found
        obj = self.get(default=None, **kw)
        if not obj:
            raise KeyError(
                f"{self.factory.__name__} not found and cannot be removed: {kw}"
            )

        # remove object
        self.objects.remove(obj)

        # update indices
        for key, value in obj:
            if key in self.no_index:
                continue
            value = value.lower()
            index = self.indices.setdefault(key, {})
            if value in index:
                del index[value]

    @lazy_load
    def __iter__(self) -> Iterator[D]:
        return iter(self.objects)

    @lazy_load
    def __len__(self) -> int:
        return len(self.objects)

    @lazy_load
    def get(self, *, default: Optional[D] = None, **kw: str) -> Optional[D]:
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
    def lookup(self, value: str) -> D:
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
