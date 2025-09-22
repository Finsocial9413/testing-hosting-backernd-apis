def language_check(language_code):
    """
    Check if the given language is supported.
    
    Args:
        language (str): The language to check.
    
    Returns:
        bool: True if the language is supported, False otherwise.
    """
    if language_code == 'eng_Latn':
        return True
    return False

# Ensure the LanguageTranslator class is defined
class LanguageTranslator:
    async def translate_text_async(self, text: str, source_lang: str, target_lang: str) -> str:
        # Mock implementation for translation
        return f"{text}"