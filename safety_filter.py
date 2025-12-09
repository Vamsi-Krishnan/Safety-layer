"""
Safety Filter Module for Content Localization Engine

This module provides profanity filtering functionality for multilingual text.
Can be imported and used as a module in other Python projects.

Filtering Strategy:
- Highly abusive/explicit words: MASKED with asterisks (***)
- Racial slurs and derogatory terms: REPLACED with appropriate synonyms

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
from typing import Dict, List, Optional, Set

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
    and context-aware filtering:
    - Highly abusive/explicit words are MASKED (***)
    - Racial slurs and derogatory terms are REPLACED with appropriate synonyms
    
    Attributes:
        language (str): Target language code ('en', 'hi', 'ta', 'te')
        highly_abusive (dict): Words to be masked per language
        racial_slurs (dict): Words to be replaced per language
        synonyms (dict): Appropriate replacements for racial slurs
    
    Example:
        >>> filter = SafetyFilter(language='en')
        >>> result = filter.filter("This is stupid you bastard")
        >>> print(result)
        'This is unwise you ****'
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
        self.highly_abusive = self._load_highly_abusive_words()
        self.racial_slurs = self._load_racial_slurs()
        self.synonyms = self._load_synonyms()
        
        # Add all words to better-profanity for detection
        if BETTER_PROFANITY_AVAILABLE and language in self.highly_abusive:
            all_words = self.highly_abusive.get(language, []) + self.racial_slurs.get(language, [])
            profanity.add_censor_words(all_words)
    
    def _load_highly_abusive_words(self) -> Dict[str, List[str]]:
        """
        Load highly abusive/explicit words that should be MASKED.
        These are extreme profanity, sexual explicit terms, etc.
        """
        return {
            "en": [
                # Extreme profanity (to be masked)
                "fuck", "fucking", "shit", "bitch", "asshole", "bastard",
                "dickhead", "prick", "cock", "pussy", "crap", "damn", "hell",
                "ass", "dumbass"
            ],
            "hi": [
                # Highly abusive Hindi words (to be masked)
                "चूतिया", "chutiya", "मादरचोद", "madarchod",
                "बहनचोद", "behenchod", "भोसडीके", "bhosadike",
                "लौडा", "lauda", "लंड", "lund", "गांडू", "gandu",
                "झाटू", "jhatu", "भोसडा", "bhosda", "रांड", "randi",
                "चुतियापा", "chutiyapa", "बकचोद", "bakchod"
            ],
            "ta": [
                # Highly abusive Tamil words (to be masked)
                "புண்டா", "punda", "ஓத்தா", "otha",
                "ஓம்பு", "ombu", "தேவடியா", "thevidiya",
                "குத்தி", "koothi", "பூல்", "pul"
            ],
            "te": [
                # Highly abusive Telugu words (to be masked)
                "పూకు", "pooku", "లండ", "land",
                "బోడు", "bodu", "కూతురు", "kothuru",
                "పూరి", "poori", "lanjakoduku"
            ]
        }
    
    def _load_racial_slurs(self) -> Dict[str, List[str]]:
        """
        Load racial slurs and derogatory terms that should be REPLACED with synonyms.
        These include identity-based insults, mild profanity, etc.
        """
        return {
            "en": [
                # Racial/derogatory slurs (to be replaced)
                "stupid", "idiot", "fool", "dumb", "moron",
                "retard", "retarded", "imbecile", "jerk", "loser",
                "scum", "trash", "garbage", "worthless", "pathetic"
            ],
            "hi": [
                # Derogatory Hindi terms (to be replaced)
                "बेवकूफ़", "बेवकूफ", "bewakoof", "bewakuf",
                "मूर्ख", "गधा", "gadha", "उल्लू", "ullu",
                "हरामी", "harami", "हरामज़ादा", "haramzada",
                "कमीना", "kamina", "कमीने", "kamine",
                "कुत्ता", "kutta", "कुत्ते", "kutte",
                "सुअर", "suar", "बकवास", "bakwas",
                "गाली", "gaali", "गंदा", "ganda", "ब्लडी फूल", "bloody fool"
            ],
            "ta": [
                # Derogatory Tamil terms (to be replaced)
                "முட்டாள்", "muttaal", "பைத்தியம்", "paithiyam",
                "கழுதை", "kazhudhai", "நாய்", "naai",
                "பன்னி", "panni", "பண்ணி",
                "loosu", "porukki", "kirukku"
            ],
            "te": [
                # Derogatory Telugu terms (to be replaced)
                "మూర్ఖుడు", "moorkhhudu", "వెధవ", "vedava",
                "గాడిదేడు", "gadidhedu", "గోవు", "govu",
                "కుక్క", "kukka", "పంది", "pandi",
                "ద్రోహి", "drohi", "gadu"
            ]
        }
    
    def _load_synonyms(self) -> Dict[str, Dict[str, str]]:
        """Load appropriate synonym replacements for racial slurs and derogatory terms"""
        return {
            "en": {
                "stupid": "unwise", "idiot": "inexperienced person",
                "fool": "naive person", "dumb": "uninformed",
                "moron": "confused person", "retard": "challenged person",
                "retarded": "developmentally different", "imbecile": "uninformed person",
                "jerk": "rude person", "loser": "unsuccessful person",
                "scum": "unpleasant person", "trash": "undesirable",
                "garbage": "poor quality", "worthless": "unvalued",
                "pathetic": "unfortunate"
            },
            "hi": {
                "बेवकूफ़": "अनजान", "बेवकूफ": "अनजान",
                "bewakoof": "anjaan", "bewakuf": "anjaan",
                "मूर्ख": "अज्ञानी", "गधा": "नासमझ", "gadha": "nasamajh",
                "उल्लू": "भोला", "ullu": "bhola",
                "हरामी": "बुरा व्यक्ति", "harami": "bura vyakti",
                "हरामज़ादा": "अविश्वासी व्यक्ति", "haramzada": "avishvaasi vyakti",
                "कमीना": "बुरा व्यक्ति", "kamina": "bura vyakti",
                "कमीने": "बुरे लोग", "kamine": "bure log",
                "कुत्ता": "नीच व्यक्ति", "kutta": "neech vyakti",
                "कुत्ते": "नीच लोग", "kutte": "neech log",
                "सुअर": "अस्वच्छ व्यक्ति", "suar": "asvachh vyakti",
                "बकवास": "बेकार बात", "bakwas": "bekaar baat",
                "गाली": "अपमानजनक शब्द", "gaali": "apmaanjanak shabd",
                "गंदा": "अशुभ", "ganda": "ashubh",
                "ब्लडी फूल": "मूर्ख", "bloody fool": "moorkhh"
            },
            "ta": {
                "முட்டாள்": "அறியாதவர்", "muttaal": "ariyathavar",
                "பைத்தியம்": "குழப்பமானவர்", "paithiyam": "kuzhhappamanavar",
                "கழுதை": "மூடனம்றவர்", "kazhudhai": "mudanamravar",
                "நாய்": "தீயவர்", "naai": "theeyavar",
                "பன்னி": "தீயவர்", "panni": "theeyavar",
                "loosu": "theriyadhavar", "porukki": "kettavar",
                "kirukku": "pizhhaiyaanavar"
            },
            "te": {
                "మూర్ఖుడు": "తెలియని వ్యక్తి", "moorkhhudu": "teliyani vyakthi",
                "వెధవ": "అనుభవం లేని వారు", "vedava": "anubhavam leni vaaru",
                "గాడిదేడు": "మూర్ఖుడు", "gadidhedu": "moorkhhudu",
                "గోవు": "మూఢనంమైన వ్యక్తి", "govu": "mudanamaina vyakthi",
                "కుక్క": "తప్పుడు వ్యక్తి", "kukka": "thappudu vyakthi",
                "పంది": "మూఢనంమైన వ్యక్తి", "pandi": "mudanamaina vyakthi",
                "ద్రోహి": "తప్పు మనసు ఉన్న వ్యక్తి", "drohi": "thappu manasu unna vyakthi",
                "gadu": "chedda vyakthi"
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
    
    def filter(self, text: str) -> str:
        """
        Filter profanity from text (simple interface).
        Uses smart filtering: masks highly abusive words, replaces racial slurs.
        
        Args:
            text: Input text to filter
        
        Returns:
            Cleaned text string
        """
        result = self.filter_detailed(text)
        return result.cleaned_text
    
    def filter_detailed(self, text: str) -> FilterResult:
        """
        Filter profanity from text with smart categorization:
        - Highly abusive words: MASKED (***)
        - Racial slurs/derogatory: REPLACED with synonyms
        
        Args:
            text: Input text to filter
        
        Returns:
            FilterResult object with detailed information
        """
        if not text:
            return FilterResult(text, text, [], {}, self.language)
        
        # Auto-detect language if enabled
        lang = self.detect_language(text) if self.auto_detect else self.language
        
        # Find highly abusive words (to mask)
        highly_abusive_found = []
        lower = text.lower()
        for word in self.highly_abusive.get(lang, []):
            if word.lower() in lower:
                highly_abusive_found.append(word)
        
        # Find racial slurs (to replace)
        racial_slurs_found = []
        for word in self.racial_slurs.get(lang, []):
            if word.lower() in lower:
                racial_slurs_found.append(word)
        
        cleaned = text
        replacements = {}
        
        # First, MASK highly abusive words
        for word in highly_abusive_found:
            masked = '*' * len(word)
            cleaned = self._replace_word(cleaned, word, masked)
            replacements[word] = masked
        
        # Then, REPLACE racial slurs with synonyms
        for word in racial_slurs_found:
            synonym = self._get_synonym(word, lang)
            cleaned = self._replace_word(cleaned, word, synonym)
            replacements[word] = synonym
        
        all_found = highly_abusive_found + racial_slurs_found
        
        return FilterResult(text, cleaned, list(set(all_found)), replacements, lang)
    
    def _get_synonym(self, word: str, lang: str) -> str:
        """Get appropriate synonym for a racial slur or derogatory term"""
        synonyms = self.synonyms.get(lang, {})
        rep = synonyms.get(word.lower()) or synonyms.get(word)
        return rep if rep else word  # If no synonym, keep original
    
    def _replace_word(self, text: str, word: str, replacement: str) -> str:
        """Replace word in text while preserving boundaries"""
        import re
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        return pattern.sub(replacement, text)


# Convenience function for quick filtering
def filter_text(text: str, language: str = 'en') -> str:
    """
    Quick profanity filter function with smart categorization.
    
    Args:
        text: Text to filter
        language: Language code ('en', 'hi', 'ta', 'te')
    
    Returns:
        Cleaned text
    
    Example:
        >>> clean = filter_text("You stupid bastard!", language='en')
        >>> print(clean)
        'You unwise *******!'  # stupid→unwise, bastard→masked
    """
    filter = SafetyFilter(language=language)
    return filter.filter(text)


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
