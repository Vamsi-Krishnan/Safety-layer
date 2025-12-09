"""
Example usage script for SafetyLayer class.
Run this in PowerShell to test the profanity filter.

Usage:
    python example_usage.py
"""

from safety_layer import SafetyLayer, ProfanityFilterResult


def test_english():
    print("\n" + "="*70)
    print("TESTING ENGLISH")
    print("="*70)
    
    safety = SafetyLayer(language="en")
    
    test_texts = [
        "You are so stupid for doing that!",
        "What an idiot move.",
        "This is a clean sentence.",
    ]
    
    for text in test_texts:
        result = safety.profanity_filter_text(text, use_synonyms=True)
        print(f"\nOriginal:  {result.original_text}")
        print(f"Cleaned:   {result.cleaned_text}")
        if result.profane_words:
            print(f"Found:     {result.profane_words}")
            print(f"Replaced:  {result.replacements}")


def test_hindi():
    print("\n" + "="*70)
    print("TESTING HINDI")
    print("="*70)
    
    safety = SafetyLayer(language="hi")
    
    test_texts = [
        "तुम बेवकूफ हो",
        "This is such a bewakoof idea",
        "यह एक साफ वाक्य है",
    ]
    
    for text in test_texts:
        result = safety.profanity_filter_text(text, use_synonyms=True)
        print(f"\nOriginal:  {result.original_text}")
        print(f"Cleaned:   {result.cleaned_text}")
        if result.profane_words:
            print(f"Found:     {result.profane_words}")
            print(f"Replaced:  {result.replacements}")


def test_tamil():
    print("\n" + "="*70)
    print("TESTING TAMIL")
    print("="*70)
    
    safety = SafetyLayer(language="ta")
    
    test_texts = [
        "நீ முட்டாள்",
        "He is such a loosu",
        "இது ஒரு சுத்தமான வாக்கியம்",
    ]
    
    for text in test_texts:
        result = safety.profanity_filter_text(text, use_synonyms=True)
        print(f"\nOriginal:  {result.original_text}")
        print(f"Cleaned:   {result.cleaned_text}")
        if result.profane_words:
            print(f"Found:     {result.profane_words}")
            print(f"Replaced:  {result.replacements}")


def test_telugu():
    print("\n" + "="*70)
    print("TESTING TELUGU")
    print("="*70)
    
    safety = SafetyLayer(language="te")
    
    test_texts = [
        "నువ్వు మూర్ఖుడు",
        "Stop being such a vedava",
        "ఇది ఒక శుభ్రమైన వాక్యం",
    ]
    
    for text in test_texts:
        result = safety.profanity_filter_text(text, use_synonyms=True)
        print(f"\nOriginal:  {result.original_text}")
        print(f"Cleaned:   {result.cleaned_text}")
        if result.profane_words:
            print(f"Found:     {result.profane_words}")
            print(f"Replaced:  {result.replacements}")


def interactive_mode():
    print("\n" + "="*70)
    print("INTERACTIVE MODE")
    print("="*70)
    print("\nSelect language:")
    print("1. English (en)")
    print("2. Hindi (hi)")
    print("3. Tamil (ta)")
    print("4. Telugu (te)")
    
    lang_map = {"1": "en", "2": "hi", "3": "ta", "4": "te"}
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice not in lang_map:
        print("Invalid choice!")
        return
    
    language = lang_map[choice]
    safety = SafetyLayer(language=language)
    
    print(f"\nLanguage set to: {language}")
    print("Enter text to filter (or 'quit' to exit):\n")
    
    while True:
        text = input(">> ")
        if text.lower() in ['quit', 'exit', 'q']:
            break
        
        result = safety.profanity_filter_text(text, use_synonyms=True)
        print(f"\nCleaned: {result.cleaned_text}")
        
        if result.profane_words:
            print(f"Profane words found: {result.profane_words}")
            print(f"Replacements made: {result.replacements}")
        else:
            print("No profanity detected.")
        print()


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + " "*20 + "SAFETY LAYER DEMO" + " "*31 + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    # Run all tests
    test_english()
    test_hindi()
    test_tamil()
    test_telugu()
    
    # Interactive mode
    print("\n\n")
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70 + "\n")
