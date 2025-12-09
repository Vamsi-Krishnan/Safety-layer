"""
Safety layer class for text profanity filtering.
Uses better-profanity and simple synonym logic to mask/replace abusive words.
"""

from dataclasses import dataclass
from typing import Dict, List

from better_profanity import profanity


@dataclass
class ProfanityFilterResult:
    original_text: str
    cleaned_text: str
    profane_words: List[str]
    replacements: Dict[str, str]


class SafetyLayer:
    def __init__(self, language: str = "en") -> None:
        self.language = language
        profanity.load_censor_words()

        # Minimal demo dictionaries; expand later
        self.custom_words: Dict[str, List[str]] = {
            "en": ["stupid", "idiot"],
            "hi": ["बेवकूफ", "मूर्ख", "bewakoof"],
            "ta": ["முட்டாள்", "loosu"],
            "te": ["మూర్ఖుడు", "vedava"],
        }
        self.synonyms: Dict[str, Dict[str, str]] = {
            "en": {"stupid": "unwise", "idiot": "inexperienced person"},
            "hi": {"बेवकूफ": "अनजान", "bewakoof": "anjaan"},
            "ta": {"முட்டாள்": "அறியாதவர்", "loosu": "theriyadhavar"},
            "te": {"మూర్ఖుడు": "తెలియని వ్యక్తి", "vedava": "అనుభవం లేని వారు"},
        }

        if language in self.custom_words:
            profanity.add_censor_words(self.custom_words[language])

    def profanity_filter_text(self, text: str, use_synonyms: bool = True) -> ProfanityFilterResult:
        if not text:
            return ProfanityFilterResult(text, text, [], {})

        found: List[str] = []
        lower = text.lower()
        for w in self.custom_words.get(self.language, []):
            if w.lower() in lower:
                found.append(w)

        cleaned = text
        replacements: Dict[str, str] = {}

        if use_synonyms:
            for w in found:
                rep = self._get_replacement(w)
                cleaned = self._replace_word(cleaned, w, rep)
                replacements[w] = rep
        else:
            cleaned = profanity.censor(text)
            for w in found:
                replacements[w] = "*" * len(w)

        return ProfanityFilterResult(text, cleaned, list(set(found)), replacements)

    def _get_replacement(self, word: str) -> str:
        m = self.synonyms.get(self.language, {})
        rep = m.get(word.lower()) or m.get(word)  # simple lookup
        return rep if rep else "*" * len(word)

    def _replace_word(self, text: str, word: str, replacement: str) -> str:
        import re

        pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)

        def _m(mo):
            return replacement

        return pattern.sub(_m, text)
