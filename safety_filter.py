"""
Safety Filter Module for Content Localization Engine

This module provides profanity filtering functionality for multilingual text.
Can be imported and used as a module in other Python projects.

Usage as a module:
    from safety_filter import SafetyFilter
    
    # Initialize
    filter = SafetyFilter(language='hi')
    
    # Filter text
    clean_text = filter.filter("text with profanity")

Usage from command line:
    python safety_filter.py input.txt output.txt

Author: Vamsi Krishnan
Project: SIH 2025 - Content Localization Engine
"""

import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from better_profanity import profanity
    BETTER_PROFANITY_AVAILABLE = True
except ImportError:
    BETTER_PROFANITY_AVAILABLE = False
    print("Warning: better-profanity not installed. Install with: pip install better-profanity")


@dataclass
class FilterResult:
    """Result of profanity filtering operation"""
    original_text: str
    cleaned_text: str
    profane_words: List[str]
    replacements: Dict[str, str]
    detected_language: str


class SafetyFilter:
    """
    Multilingual profanity filter for English, Hindi, Tamil, and Telugu.
    
    This class provides text filtering functionality with automatic language detection
    and appropriate synonym replacement or masking of offensive words.
    
    Attributes:
        language (str): Target language code ('en', 'hi', 'ta', 'te')
        custom_words (dict): Dictionary of offensive words per language
        synonyms (dict): Dictionary of appropriate replacements per language
    
    Example:
        >>> filter = SafetyFilter(language='en')
        >>> result = filter.filter("This is stupid")
        >>> print(result)
        'This is unwise'
    """
    
    SUPPORTED_LANGUAGES = ['en', 'hi', 'ta', 'te']
    
    def __init__(self, language: str = 'en', auto_detect: bool = False):
        """
        Initialize the SafetyFilter.
        
        Args:
            language: Language code ('en', 'hi', 'ta', 'te'). Default: 'en'
            auto_detect: If True, automatically detect language from input text
        
        Raises:
            ValueError: If language is not supported
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )
        
        self.language = language
        self.auto_detect = auto_detect
        
        # Load better-profanity if available
        if BETTER_PROFANITY_AVAILABLE:
            profanity.load_censor_words()
        
        # Initialize wordlists
        self.custom_words = self._load_custom_words()
        self.synonyms = self._load_synonyms()
        
        # Add custom words to better-profanity
        if BETTER_PROFANITY_AVAILABLE and language in self.custom_words:
            profanity.add_censor_words(self.custom_words[language])
    
    def _load_custom_words(self) -> Dict[str, List[str]]:
        """Load offensive words dictionary for all supported languages"""
        return {
            "en": [
                "stupid", "idiot", "fool", "dumb", "moron", "dumbass", "ass",
                "bastard", "bitch", "damn", "hell", "crap", "shit", "fuck",
                "fucking", "asshole", "dickhead", "prick", "cock", "pussy",
                "retard", "retarded", "imbecile", "jerk", "loser", "scum",
                "trash", "garbage", "worthless", "pathetic"
            ],
            "hi": [
                # Devanagari
                "बेवकूफ़", "बेवकूफ", "मूर्ख", "गधा", "उल्लू", "ब्लडी फूल",
                "चूतिया", "हरामी", "हरामज़ादा", "कमीना", "कमीने", "कुत्ता", "कुत्ते",
                "मादरचोद", "बहनचोद", "भोसडीके", "लौडा", "लंड",
                "गांडू", "झाटू", "भोसडा", "रांड", "सुअर",
                "चुतियापा", "बकवास", "बकचोद", "गाली", "गंदा",
                # Romanized
                "bewakoof", "bewakuf", "gadha", "ullu", "bloody fool",
                "chutiya", "harami", "haramzada", "kamina", "kamine",
                "kutta", "kutte", "madarchod", "behenchod", "bhosadike",
                "lauda", "lund", "gandu", "jhatu", "bhosda", "randi",
                "suar", "chutiyapa", "bakwas", "bakchod", "gaali", "ganda"
            ],
            "ta": [
                "முட்டாள்", "பைத்தியம்", "கழுதை", "நாய்",
                "புண்டா", "ஓத்தா", "ஓம்பு", "தேவடியா",
                "குத்தி", "பன்னி", "பூல்", "பண்ணி",
                "muttaal", "paithiyam", "kazhudhai", "naai", "punda",
                "otha", "ombu", "thevidiya", "koothi", "panni", "pul",
                "loosu", "porukki", "kirukku"
            ],
            "te": [
                "మూర్ఖుడు", "వెధవ", "గాడిదేడు", "గోవు",
                "కుక్క", "పంది", "పూకు", "ద్రోహి",
                "లండ", "బోడు", "కూతురు", "పూరి",
                "moorkhhudu", "vedava", "gadidhedu", "govu", "kukka",
                "pandi", "pooku", "drohi", "land", "bodu", "kothuru",
                "poori", "gadu", "lanjakoduku"
            ]
        }
    
    def _load_synonyms(self) -> Dict[str, Dict[str, str]]:
        """Load synonym replacements for offensive words"""
        return {
            "en": {
                "stupid": "unwise", "idiot": "inexperienced person",
                "fool": "naive person", "dumb": "uninformed",
                "moron": "confused person", "dumbass": "misguided individual",
                "bastard": "difficult person", "damn": "darn",
                "hell": "heck", "crap": "nonsense",
                "jerk": "rude person", "loser": "unsuccessful person",
                "scum": "unpleasant person", "trash": "worthless",
                "garbage": "poor quality", "pathetic": "unfortunate"
            },
            "hi": {
                "बेवकूफ़": "अनजान", "बेवकूफ": "अनजान",
                "मूर्ख": "अज्ञानी", "गधा": "नासमझ",
                "उल्लू": "भोला", "ब्लडी फूल": "मूर्ख",
                "कमीना": "बुरा व्यक्ति", "कमीने": "बुरे लोग",
                "कुत्ता": "नीच व्यक्ति", "कुत्ते": "नीच लोग",
                "बकवास": "बेकार बात", "गाली": "अपमानजनक शब्द",
                "गंदा": "अशुभ",
                "bewakoof": "anjaan", "bewakuf": "anjaan",
                "gadha": "nasamajh", "ullu": "bhola",
                "bloody fool": "moorkhh", "kamina": "bura vyakti",
                "kamine": "bure log", "kutta": "neech vyakti",
                "kutte": "neech log", "bakwas": "bekaar baat",
                "gaali": "apmaanjanak shabd", "ganda": "ashubh"
            },
            "ta": {
                "முட்டாள்": "அறியாதவர்", "பைத்தியம்": "குழப்பமானவர்",
                "கழுதை": "மூடனம்றவர்", "நாய்": "தீயவர்",
                "குத்தி": "தீயவர்",
                "muttaal": "ariyathavar", "paithiyam": "kuzhhappamanavar",
                "kazhudhai": "mudanamravar", "naai": "theeyavar",
                "loosu": "theriyadhavar", "porukki": "kettavar",
                "kirukku": "pizhhaiyaanavar"
            },
            "te": {
                "మూర్ఖుడు": "తెలియని వ్యక్తి", "వెధవ": "అనుభవం లేని వారు",
                "గాడిదేడు": "మూర్ఖుడు", "గోవు": "మూఢనంమైన వ్యక్తి",
                "కుక్క": "తప్పుడు వ్యక్తి", "పంది": "మూఢనంమైన వ్యక్తి",
                "ద్రోహి": "తప్పు మనసు ఉన్న వ్యక్తి",
                "moorkhhudu": "teliyani vyakthi", "vedava": "anubhavam leni vaaru",
                "gadidhedu": "moorkhhudu", "govu": "mudanamaina vyakthi",
                "kukka": "thappudu vyakthi", "pandi": "mudanamaina vyakthi",
                "drohi": "thappu manasu unna vyakthi", "gadu": "chedda vyakthi"
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Auto-detect language from Unicode script"""
        devanagari = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        tamil = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        telugu = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
        
        if devanagari > 0:
            return 'hi'
        elif tamil > 0:
            return 'ta'
        elif telugu > 0:
            return 'te'
        return 'en'
    
    def filter(self, text: str, use_synonyms: bool = True) -> str:
        """
        Filter profanity from text (simple interface).
        
        Args:
            text: Input text to filter
            use_synonyms: Replace with synonyms if True, mask with * if False
        
        Returns:
            Cleaned text string
        """
        result = self.filter_detailed(text, use_synonyms)
        return result.cleaned_text
    
    def filter_detailed(self, text: str, use_synonyms: bool = True) -> FilterResult:
        """
        Filter profanity from text (detailed interface).
        
        Args:
            text: Input text to filter
            use_synonyms: Replace with synonyms if True, mask with * if False
        
        Returns:
            FilterResult object with detailed information
        """
        if not text:
            return FilterResult(text, text, [], {}, self.language)
        
        # Auto-detect language if enabled
        lang = self.detect_language(text) if self.auto_detect else self.language
        
        # Find profane words
        found = []
        lower = text.lower()
        for word in self.custom_words.get(lang, []):
            if word.lower() in lower:
                found.append(word)
        
        cleaned = text
        replacements = {}
        
        if use_synonyms:
            for word in found:
                rep = self._get_replacement(word, lang)
                cleaned = self._replace_word(cleaned, word, rep)
                replacements[word] = rep
        else:
            if BETTER_PROFANITY_AVAILABLE:
                cleaned = profanity.censor(text)
            for word in found:
                replacements[word] = '*' * len(word)
        
        return FilterResult(text, cleaned, list(set(found)), replacements, lang)
    
    def _get_replacement(self, word: str, lang: str) -> str:
        """Get appropriate replacement for a profane word"""
        synonyms = self.synonyms.get(lang, {})
        rep = synonyms.get(word.lower()) or synonyms.get(word)
        return rep if rep else '*' * len(word)
    
    def _replace_word(self, text: str, word: str, replacement: str) -> str:
        """Replace word in text while preserving boundaries"""
        import re
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        return pattern.sub(replacement, text)


# Convenience function for quick filtering
def filter_text(text: str, language: str = 'en', use_synonyms: bool = True) -> str:
    """
    Quick profanity filter function.
    
    Args:
        text: Text to filter
        language: Language code ('en', 'hi', 'ta', 'te')
        use_synonyms: Replace with synonyms if True, mask if False
    
    Returns:
        Cleaned text
    
    Example:
        >>> clean = filter_text("This is stupid", language='en')
        >>> print(clean)
        'This is unwise'
    """
    filter = SafetyFilter(language=language)
    return filter.filter(text, use_synonyms=use_synonyms)


# Command-line interface
def main():
    """CLI entry point"""
    if len(sys.argv) != 3:
        print("Usage: python safety_filter.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file, output_file = sys.argv[1], sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Filter with auto-detection
    filter = SafetyFilter(auto_detect=True)
    result = filter.filter_detailed(text)
    
    # Create output directory
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result.cleaned_text)
    
    print(f"Done: {output_file}")


if __name__ == '__main__':
    main()
