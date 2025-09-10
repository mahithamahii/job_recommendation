import re
from pathlib import Path
from typing import Iterable, List, Set

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

_NLTK_RESOURCES = [
    ("stopwords", "corpora/stopwords"),
    ("wordnet", "corpora/wordnet"),
    ("omw-1.4", "corpora/omw-1.4"),
]


def ensure_nltk() -> None:
    for pkg, path in _NLTK_RESOURCES:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)


ensure_nltk()


_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+.#/\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9+.#/\-]+", text.lower())
    return [t for t in tokens if t and t not in _stop_words]


def lemmatize_tokens(tokens: Iterable[str]) -> List[str]:
    return [_lemmatizer.lemmatize(t) for t in tokens]


def load_skills_master(path: Path) -> List[str]:
    if not path.exists():
        return []
    skills = [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()]
    return [s for s in skills if s]


def extract_skills(text: str, skill_phrases: Iterable[str]) -> Set[str]:
    """
    Extract skills by case-insensitive phrase matching.
    Handles both single and multi-word skills.
    """
    normalized = f" {normalize_text(text)} "
    found: Set[str] = set()
    for phrase in skill_phrases:
        p = phrase.strip().lower()
        if not p:
            continue
        # match whole word/phrase boundaries crudely by padding spaces
        if f" {p} " in normalized:
            found.add(phrase)
    return found



