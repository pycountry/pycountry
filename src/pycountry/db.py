import gettext
import json
import logging
import threading
from functools import lru_cache
from typing import Any, Dict, Iterator, List, Optional, Sequence, Type, Union

logger = logging.getLogger("pycountry.db")


class Data:
    def __init__(self, **fields: str):
        self._fields = fields

    def __getattr__(self, key):
        if key in self._fields:
            return self._fields[key]
        raise AttributeError(key)

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

    def __iter__(self):
        # allow casting into a dict
        for field in self._fields:
            yield field, getattr(self, field)


class Country(Data):
    pass


class Subdivision(Data):
    pass


def lazy_load(f):
    def load_if_needed(self, *args, **kw):
        if not self._is_loaded:
            with self._load_lock:
                self._load()
        return f(self, *args, **kw)

    return load_if_needed


class Database:
    data_class: Union[Type, str]
    root_key: Optional[str] = None
    no_index: List[str] = []

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._is_loaded = False
        self._load_lock = threading.Lock()

        if isinstance(self.data_class, str):
            self.factory = type(self.data_class, (Data,), {})
        else:
            self.factory = self.data_class
        # Language specific indices.
        self.translations: Dict[str, dict] = {}
        # Cached gettext objects.
        self._trans_objs: Dict[str, gettext.NullTranslations] = {}

    def _clear(self):
        self._is_loaded = False
        self.objects = []
        self.index_names = set()
        self.indices = {}
        self.translations = {}

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

    @lru_cache
    def _get_trans(self, language: str) -> gettext.NullTranslations:
        """Return gettext translation object for the language."""
        from . import LOCALES_DIR

        # Ignore missing gettext languages.
        return gettext.translation(
            "iso3166-1", LOCALES_DIR, languages=[language], fallback=True
        )

    def _load_translations(self, languages: Sequence[str]) -> None:
        """Load translations for provided languages."""
        with self._load_lock:
            for language in languages:
                if language in self.translations:
                    # Skip languages that are already loaded.
                    continue
                trans = self._get_trans(language)
                indices = self.translations.setdefault(language, {})
                for obj in self.objects:
                    # Inject into language index.
                    for key in self.indices:
                        index = indices.setdefault(key, {})
                        value = trans.gettext(getattr(obj, key)).lower()
                        if value in index:
                            logger.debug(
                                "%s %r already taken in index %r and will be "
                                "ignored. This is an error in the databases."
                                % (self.factory.__name__, value, key)
                            )
                        index[value] = obj

    # Public API

    @lazy_load
    def add_entry(self, **kw):
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
    def remove_entry(self, **kw):
        # make sure that we receive None if no entry found
        if "default" in kw:
            del kw["default"]
        obj = self.get(**kw)
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
    def __iter__(self) -> Iterator["Database"]:
        return iter(self.objects)

    @lazy_load
    def __len__(self) -> int:
        return len(self.objects)

    @lazy_load
    def get(
        self,
        *,
        default: Optional[Any] = None,
        languages: Optional[Sequence[str]] = None,
        **kw: Optional[str],
    ) -> Optional[Any]:
        if len(kw) != 1:
            raise TypeError("Only one criteria may be given")
        field, value = kw.popitem()
        if not isinstance(value, str):
            raise LookupError()

        languages = languages or ()
        self._load_translations(languages)

        # Normalize for case-insensitivity
        value = value.lower()
        for index in [self.indices[field]] + [
            self.translations[lang][field] for lang in languages
        ]:
            try:
                return index[value]
            except KeyError:
                pass
        else:
            # Pythonic APIs implementing     get() shouldn't raise KeyErrors.
            # Those are a bit unexpected and they should rather support
            # returning `None` by default and allow customization.
            return default

    @lazy_load
    def lookup(
        self, value: str, *, languages: Optional[Sequence[str]] = None
    ) -> Type:
        if not isinstance(value, str):
            raise LookupError()

        languages = languages or ()
        self._load_translations(languages)

        # Normalize for case-insensitivity
        value = value.lower()

        # Use indexes first
        for indices in [self.indices] + [
            self.translations[lang] for lang in languages
        ]:
            for key in indices:
                try:
                    return indices[key][value]
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
