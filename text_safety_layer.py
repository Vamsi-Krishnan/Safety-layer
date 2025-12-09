"""
Text Safety Layer for Content Localization Engine
Handles profanity detection and filtering for English, Hindi, Tamil, and Telugu.

This module processes translated text and either masks or replaces abusive words
with appropriate synonyms across multiple Indian languages.

Dependencies:
    pip install better-profanity

Author: Vamsi Krishnan
Project: SIH 2025 - Content Localization Engine
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from better_profanity import profanity


@dataclass
class FilterResult:
    """Result of text filtering operation"""
    original_text: str
    filtered_text: str
    is_profane: bool
    profane_words_found: List[str]
    replacements_made: Dict[str, str]  # {original_word: replacement}


class TextSafetyLayer:
    """
    Multilingual text safety filter for English, Hindi, Tamil, and Telugu.
    
    Features:
    - Profanity detection using better-profanity
    - Custom wordlists for Indian languages
    - Smart replacement with synonyms when available
    - Masking fallback for words without synonyms
    """
    
    SUPPORTED_LANGUAGES = ['en', 'hi', 'ta', 'te']
    
    def __init__(self, language: str = 'en', custom_wordlist_path: Optional[str] = None):
        """
        Initialize the Text Safety Layer.
        
        Args:
            language: Language code ('en', 'hi', 'ta', 'te')
            custom_wordlist_path: Optional path to custom profanity wordlist JSON file
        
        Raises:
            ValueError: If language is not supported
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )
        
        self.language = language
        
        # Load better-profanity default English words
        profanity.load_censor_words()
        
        # Load custom wordlists for Indian languages
        self.custom_profane_words = self._load_custom_wordlist(custom_wordlist_path)
        
        # Load synonym mappings for smart replacement
        self.synonym_map = self._load_synonyms()
        
        # Add custom words to profanity checker
        if self.language in self.custom_profane_words:
            profanity.add_censor_words(self.custom_profane_words[self.language])
    
    
    def _load_custom_wordlist(self, wordlist_path: Optional[str]) -> Dict[str, List[str]]:
        """
        Load custom profanity wordlists for Indian languages.
        
        Args:
            wordlist_path: Path to JSON file containing wordlists
        
        Returns:
            Dictionary mapping language codes to lists of profane words
        """
        if wordlist_path and os.path.exists(wordlist_path):
            with open(wordlist_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default wordlists (placeholder - expand with real words)
        # In production, load from external JSON files
        return {
            'hi': [
                # Hindi profane words (Devanagari script)
                'बेवकूफ', 'मूर्ख', 'गधा', 'चूतिया', 'हरामी',
                # Hinglish (romanized)
                'bewakoof', 'chutiya', 'harami', 'madarchod', 'bhenchod'
            ],
            'ta': [
                # Tamil profane words
                'முட்டாள்', 'பைத்தியம்', 'கழுதை',
                # Romanized Tamil
                'punda', 'otha', 'loosu'
            ],
            'te': [
                # Telugu profane words
                'మూర్ఖుడు', 'వెధవ', 'గాడిద',
                # Romanized Telugu
                'gadu', 'vedava', 'kukka'
            ],
            'en': [
                # Additional English words not in better-profanity default
                'stupid', 'idiot', 'moron'
            ]
        }
    
    
    def _load_synonyms(self) -> Dict[str, Dict[str, str]]:
        """
        Load synonym mappings for appropriate word replacements.
        
        Returns:
            Nested dictionary: {language: {profane_word: appropriate_synonym}}
        """
        # In production, load from external JSON files
        return {
            'en': {
                'stupid': 'unwise',
                'idiot': 'inexperienced person',
                'moron': 'confused person',
                'damn': 'darn',
                'hell': 'heck'
            },
            'hi': {
                'बेवकूफ': 'अनजान',  # bewakoof -> anjaan (unknowing)
                'मूर्ख': 'अज्ञानी',  # moorkh -> agyaani (ignorant)
                'bewakoof': 'anjaan',
                'chutiya': 'nasamajh',  # foolish person
            },
            'ta': {
                'முட்டாள்': 'அறியாதவர்',  # muttaal -> ariyathavar (unknowing person)
                'பைத்தியம்': 'குழப்பமானவர்',  # paithiyam -> kuzhappam (confused)
                'loosu': 'theriyadhavar',
            },
            'te': {
                'మూర్ఖుడు': 'తెలియని వ్యక్తి',  # moorkhhudu -> teliyani vyakthi
                'వెధవ': 'అనుభవం లేని వారు',  # vedhava -> anubhavam leni vaaru
                'vedava': 'anubhavam leni vaaru',
            }
        }
    
    
    def filter_text(self, text: str, use_synonyms: bool = True) -> FilterResult:
        """
        Filter profane words from text.
        
        Args:
            text: Input text to filter
            use_synonyms: If True, replace with synonyms; if False, mask with asterisks
        
        Returns:
            FilterResult object containing original text, filtered text, and metadata
        """
        if not text or not text.strip():
            return FilterResult(
                original_text=text,
                filtered_text=text,
                is_profane=False,
                profane_words_found=[],
                replacements_made={}
            )
        
        # Check if text contains profanity
        is_profane = profanity.contains_profanity(text)
        
        # Find specific profane words
        profane_words = self._find_profane_words(text)
        
        # Apply filtering
        if not profane_words:
            return FilterResult(
                original_text=text,
                filtered_text=text,
                is_profane=is_profane,
                profane_words_found=[],
                replacements_made={}
            )
        
        filtered_text = text
        replacements = {}
        
        if use_synonyms:
            # Try to replace with appropriate synonyms
            for word in profane_words:
                replacement = self._get_synonym(word)
                filtered_text = self._replace_word(filtered_text, word, replacement)
                replacements[word] = replacement
        else:
            # Use better-profanity's default censoring (masking with *)
            filtered_text = profanity.censor(text)
            for word in profane_words:
                replacements[word] = '*' * len(word)
        
        return FilterResult(
            original_text=text,
            filtered_text=filtered_text,
            is_profane=is_profane,
            profane_words_found=profane_words,
            replacements_made=replacements
        )
    
    
    def _find_profane_words(self, text: str) -> List[str]:
        """
        Identify specific profane words in text.
        
        Args:
            text: Text to analyze
        
        Returns:
            List of profane words found
        """
        words_found = []
        text_lower = text.lower()
        
        # Check against custom wordlist for current language
        if self.language in self.custom_profane_words:
            for word in self.custom_profane_words[self.language]:
                if word.lower() in text_lower:
                    words_found.append(word)
        
        # Also check using better-profanity's built-in detection
        # This handles leetspeak and variations
        words = text.split()
        for word in words:
            # Clean punctuation
            clean_word = word.strip('.,!?;:()[]{}"\\'')
            if profanity.contains_profanity(clean_word) and clean_word not in words_found:
                words_found.append(clean_word)
        
        return list(set(words_found))  # Remove duplicates
    
    
    def _get_synonym(self, word: str) -> str:
        """
        Get appropriate synonym for a profane word.
        
        Args:
            word: Profane word to replace
        
        Returns:
            Synonym if available, otherwise masked version (****)
        """
        word_lower = word.lower()
        
        # Check synonym map for current language
        if self.language in self.synonym_map:
            if word_lower in self.synonym_map[self.language]:
                synonym = self.synonym_map[self.language][word_lower]
                # Preserve original case pattern
                return self._match_case(synonym, word)
        
        # Fallback to masking
        return '*' * len(word)
    
    
    def _match_case(self, replacement: str, original: str) -> str:
        """
        Match the case pattern of original word.
        
        Args:
            replacement: Replacement word
            original: Original word to match case from
        
        Returns:
            Replacement with matched case
        """
        if original.isupper():
            return replacement.upper()
        elif original[0].isupper() if original else False:
            return replacement.capitalize()
        else:
            return replacement.lower()
    
    
    def _replace_word(self, text: str, word: str, replacement: str) -> str:
        """
        Replace word in text while preserving case.
        
        Args:
            text: Original text
            word: Word to replace
            replacement: Replacement string
        
        Returns:
            Text with word replaced
        """
        import re
        
        # Create pattern that matches word boundaries
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        
        def replace_match(match):
            return self._match_case(replacement, match.group())
        
        return pattern.sub(replace_match, text)
    
    
    def add_custom_words(self, words: List[str]):
        """
        Add custom profane words to the filter.
        
        Args:
            words: List of words to add
        """
        profanity.add_censor_words(words)
        
        if self.language not in self.custom_profane_words:
            self.custom_profane_words[self.language] = []
        
        self.custom_profane_words[self.language].extend(words)
    
    
    def add_synonym(self, profane_word: str, synonym: str):
        """
        Add a synonym mapping for a profane word.
        
        Args:
            profane_word: The profane word
            synonym: The appropriate replacement
        """
        if self.language not in self.synonym_map:
            self.synonym_map[self.language] = {}
        
        self.synonym_map[self.language][profane_word.lower()] = synonym


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

def main():
    """Example usage of TextSafetyLayer"""
    
    print("=" * 70)
    print("TEXT SAFETY LAYER - MULTILINGUAL PROFANITY FILTER")
    print("=" * 70)
    
    # Test English
    print("\n1. ENGLISH FILTERING:")
    print("-" * 70)
    en_filter = TextSafetyLayer(language='en')
    
    test_texts_en = [
        "This is a damn good example.",
        "You're such an idiot for saying that!",
        "What the hell is going on here?",
        "This is a completely clean sentence."
    ]
    
    for text in test_texts_en:
        result = en_filter.filter_text(text, use_synonyms=True)
        print(f"\nOriginal: {result.original_text}")
        print(f"Filtered: {result.filtered_text}")
        print(f"Profane: {result.is_profane}")
        if result.replacements_made:
            print(f"Replacements: {result.replacements_made}")
    
    # Test Hindi
    print("\n\n2. HINDI FILTERING:")
    print("-" * 70)
    hi_filter = TextSafetyLayer(language='hi')
    
    test_texts_hi = [
        "तुम बेवकूफ हो",
        "This is bewakoof behavior",
        "यह एक साफ वाक्य है"
    ]
    
    for text in test_texts_hi:
        result = hi_filter.filter_text(text, use_synonyms=True)
        print(f"\nOriginal: {result.original_text}")
        print(f"Filtered: {result.filtered_text}")
        print(f"Profane: {result.is_profane}")
        if result.replacements_made:
            print(f"Replacements: {result.replacements_made}")
    
    # Test masking vs synonym replacement
    print("\n\n3. MASKING vs SYNONYM REPLACEMENT:")
    print("-" * 70)
    test_text = "You're such a stupid person!"
    
    result_synonym = en_filter.filter_text(test_text, use_synonyms=True)
    result_masked = en_filter.filter_text(test_text, use_synonyms=False)
    
    print(f"Original:           {test_text}")
    print(f"With synonyms:      {result_synonym.filtered_text}")
    print(f"With masking:       {result_masked.filtered_text}")
    
    print("\n" + "=" * 70)
    print("Testing complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
