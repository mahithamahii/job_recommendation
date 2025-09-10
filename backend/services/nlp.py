from pathlib import Path
from typing import Iterable, List, Set

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer


_nlp = None


def load_spacy() -> None:
	global _nlp
	if _nlp is None:
		try:
			_nlp = spacy.load("en_core_web_sm")
		except Exception:
			# lazy load blank model if not available
			_nlp = spacy.blank("en")


def extract_skills_spacy(text: str, skills_phrases: Iterable[str]) -> Set[str]:
	load_spacy()
	doc = _nlp(text)
	lower_text = f" {text.lower()} "
	found: Set[str] = set()
	for phrase in skills_phrases:
		p = phrase.strip().lower()
		if not p:
			continue
		if f" {p} " in lower_text:
			found.add(phrase)
	return found


def build_tfidf(corpus: List[str]) -> TfidfVectorizer:
	return TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=50000)
