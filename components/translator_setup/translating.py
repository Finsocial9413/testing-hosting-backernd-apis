
import re
from googletrans import Translator

LANGUAGES = {
    "ENGLISH": {"code": "eng_Latn", "symbol": "EN"},
    "HINDI": {"code": "hin_Deva", "symbol": "HI"},
    "BENGALI": {"code": "ben_Beng", "symbol": "BN"},
    "GUJARATI": {"code": "guj_Gujr", "symbol": "GU"},
    "KANNADA": {"code": "kan_Knda", "symbol": "KA"},
    "MALAYALAM": {"code": "mal_Mlym", "symbol": "ML"},
    "MARATHI": {"code": "mar_Deva", "symbol": "MR"},
    "NEPALI": {"code": "npi_Deva", "symbol": "NP"},
    "ORIYA": {"code": "ory_Orya", "symbol": "OR"},
    "PUNJABI": {"code": "pan_Guru", "symbol": "Pa"},
    "SANSKRIT": {"code": "san_Deva", "symbol": "SA"},
    "TAMIL": {"code": "tam_Taml", "symbol": "TA"},
    "TELUGU": {"code": "tel_Telu", "symbol": "TE"},
    "URDU": {"code": "urd_Arab", "symbol": "UR"},
    "ASSAMESE": {"code": "asm_Beng", "symbol": "AS"},
    "KASHMIRI": {"code": "kas_Arab", "symbol": "KS"},
    "MANIPURI": {"code": "mni_Mtei", "symbol": "MN"},
    "SINDHI": {"code": "snd_Arab", "symbol": "SI"},
    "AFRIKAANS": {"code": "af", "symbol": "AF"},
    "ALBANIAN": {"code": "sq", "symbol": "SQ"},
    "AMHARIC": {"code": "am", "symbol": "AM"},
    "ARABIC": {"code": "ar", "symbol": "AR"},
    "ARMENIAN": {"code": "hy", "symbol": "HY"},
    "AZERBAIJANI": {"code": "az", "symbol": "AZ"},
    "BASQUE": {"code": "eu", "symbol": "EU"},
    "BELARUSIAN": {"code": "be", "symbol": "BE"},
    "BOSNIAN": {"code": "bs", "symbol": "BS"},
    "BULGARIAN": {"code": "bg", "symbol": "BG"},
    "CATALAN": {"code": "ca", "symbol": "CA"},
    "CEBUANO": {"code": "ceb", "symbol": "CEB"},
    "CHICHEWA": {"code": "ny", "symbol": "NY"},
    "CHINESE_SIMPLIFIED": {"code": "zh-cn", "symbol": "ZH_CN"},
    "CHINESE_TRADITIONAL": {"code": "zh-tw", "symbol": "ZH_TW"},
    "CORSICAN": {"code": "co", "symbol": "CO"},
    "CROATIAN": {"code": "hr", "symbol": "HR"},
    "CZECH": {"code": "cs", "symbol": "CS"},
    "DANISH": {"code": "da", "symbol": "DA"},
    "DUTCH": {"code": "nl", "symbol": "NL"},
    "ESPERANTO": {"code": "eo", "symbol": "EO"},
    "ESTONIAN": {"code": "et", "symbol": "ET"},
    "FILIPINO": {"code": "tl", "symbol": "TL"},
    "FINNISH": {"code": "fi", "symbol": "FI"},
    "FRENCH": {"code": "fr", "symbol": "FR"},
    "FRISIAN": {"code": "fy", "symbol": "FY"},
    "GALICIAN": {"code": "gl", "symbol": "GL"},
    "GEORGIAN": {"code": "ka", "symbol": "KA"},
    "GERMAN": {"code": "de", "symbol": "DE"},
    "GREEK": {"code": "el", "symbol": "EL"},
    "HAITIAN_CREOLE": {"code": "ht", "symbol": "HT"},
    "HAUSA": {"code": "ha", "symbol": "HA"},
    "HAWAIIAN": {"code": "haw", "symbol": "HAW"},
    "HEBREW": {"code": "he", "symbol": "HE"},
    "HMONG": {"code": "hmn", "symbol": "HMN"},
    "HUNGARIAN": {"code": "hu", "symbol": "HU"},
    "ICELANDIC": {"code": "is", "symbol": "IS"},
    "IGBO": {"code": "ig", "symbol": "IG"},
    "INDONESIAN": {"code": "id", "symbol": "ID"},
    "IRISH": {"code": "ga", "symbol": "GA"},
    "ITALIAN": {"code": "it", "symbol": "IT"},
    "JAPANESE": {"code": "ja", "symbol": "JA"},
    "JAVANESE": {"code": "jw", "symbol": "JW"},
    "KANNADA": {"code": "kn", "symbol": "KN"},
    "KAZAKH": {"code": "kk", "symbol": "KK"},
    "KHMER": {"code": "km", "symbol": "KM"},
    "KOREAN": {"code": "ko", "symbol": "KO"},
    "KURDISH": {"code": "ku", "symbol": "KU"},
    "KYRGYZ": {"code": "ky", "symbol": "KY"},
    "LAO": {"code": "lo", "symbol": "LO"},
    "LATIN": {"code": "la", "symbol": "LA"},
    "LATVIAN": {"code": "lv", "symbol": "LV"},
    "LITHUANIAN": {"code": "lt", "symbol": "LT"},
    "LUXEMBOURGISH": {"code": "lb", "symbol": "LB"},
    "MACEDONIAN": {"code": "mk", "symbol": "MK"},
    "MALAGASY": {"code": "mg", "symbol": "MG"},
    "MALAY": {"code": "ms", "symbol": "MS"},
    "MALTESE": {"code": "mt", "symbol": "MT"},
    "MAORI": {"code": "mi", "symbol": "MI"},
    "MONGOLIAN": {"code": "mn", "symbol": "MN"},
    "MYANMAR": {"code": "my", "symbol": "MY"},
    "NEPALI": {"code": "ne", "symbol": "NE"},
    "NORWEGIAN": {"code": "no", "symbol": "NO"},
    "ODIA": {"code": "or", "symbol": "OR"},
    "PASHTO": {"code": "ps", "symbol": "PS"},
    "PERSIAN": {"code": "fa", "symbol": "FA"},
    "POLISH": {"code": "pl", "symbol": "PL"},
    "PORTUGUESE": {"code": "pt", "symbol": "PT"},
    "PUNJABI": {"code": "pa", "symbol": "PA"},
    "ROMANIAN": {"code": "ro", "symbol": "RO"},
    "RUSSIAN": {"code": "ru", "symbol": "RU"},
    "SAMOAN": {"code": "sm", "symbol": "SM"},
    "SCOTS_GAELIC": {"code": "gd", "symbol": "GD"},
    "SERBIAN": {"code": "sr", "symbol": "SR"},
    "SESOTHO": {"code": "st", "symbol": "ST"},
    "SHONA": {"code": "sn", "symbol": "SN"},
    "SINDHI": {"code": "sd", "symbol": "SD"},
    "SINHALA": {"code": "si", "symbol": "SI"},
    "SLOVAK": {"code": "sk", "symbol": "SK"},
    "SLOVENIAN": {"code": "sl", "symbol": "SL"},
    "SOMALI": {"code": "so", "symbol": "SO"},
    "SPANISH": {"code": "es", "symbol": "ES"},
    "SUNDANESE": {"code": "su", "symbol": "SU"},
    "SWAHILI": {"code": "sw", "symbol": "SW"},
    "SWEDISH": {"code": "sv", "symbol": "SV"},
    "TAJIK": {"code": "tg", "symbol": "TG"},
    "TAMIL": {"code": "ta", "symbol": "TA"},
    "TELUGU": {"code": "te", "symbol": "TE"},
    "THAI": {"code": "th", "symbol": "TH"},
    "TURKISH": {"code": "tr", "symbol": "TR"},
    "UKRAINIAN": {"code": "uk", "symbol": "UK"},
    "URDU": {"code": "ur", "symbol": "UR"},
    "UYGHUR": {"code": "ug", "symbol": "UG"},
    "UZBEK": {"code": "uz", "symbol": "UZ"},
    "VIETNAMESE": {"code": "vi", "symbol": "VI"},
    "WELSH": {"code": "cy", "symbol": "CY"},
    "XHOSA": {"code": "xh", "symbol": "XH"},
    "YIDDISH": {"code": "yi", "symbol": "YI"},
    "YORUBA": {"code": "yo", "symbol": "YO"},
    "ZULU": {"code": "zu", "symbol": "ZU"}
}

# Helper function to decide whether to translate a segment.


def should_translate_llm(segment: str) -> bool:
    # Skip if the segment is enclosed in any backticks (inline or triple)
    if segment.startswith("`") and segment.endswith("`"):
        return False
    # Skip if the segment contains a URL.
    if re.search(r'\bhttps?://\S+\b', segment) or re.search(r'\bwww\.\S+\b', segment):
        return False
    return True


import re
from googletrans import Translator

# Other code remains unchanged...

async def main(text, source_len, desti_len):
    translator = Translator()
    pattern = r'(```[\s\S]+?```)|(`[^`]+`)|(\bhttps?://\S+\b)|(\bwww\.\S+\b)'
    
    # Keep track of all matches to preserve formatting
    matches = list(re.finditer(pattern, text))
    segments = []
    last_end = 0
    
    # Split the text while preserving the position of special segments
    for match in matches:
        start, end = match.span()
        if start > last_end:
            segments.append((text[last_end:start], False))  # Normal text
        segments.append((text[start:end], True))  # Special text (don't translate)
        last_end = end
    
    # Add any remaining text
    if last_end < len(text):
        segments.append((text[last_end:], False))
    
    translated_text = ""
    
    # Process each segment
    for segment_text, is_special in segments:
        if not segment_text:
            continue
            
        if is_special or not should_translate_llm(segment_text.strip()):
            # Keep special segments as they are
            translated_text += segment_text
        else:
            # Split by newlines to maintain paragraph structure
            paragraphs = segment_text.split('\n')
            translated_paragraphs = []
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Only translate non-empty paragraphs
                    seg_clean = paragraph.strip()
                    try:
                        # Use the translate method synchronously - fixed line
                        translated = await translator.translate(seg_clean, src=source_len, dest=desti_len)
                        translated_paragraphs.append(translated.text if hasattr(translated, 'text') else str(seg_clean))
                    except Exception as e:
                        # Fallback in case of translation error
                        print(f"Translation error: {e}")
                        translated_paragraphs.append(seg_clean)
                else:
                    # Keep empty lines as they are
                    translated_paragraphs.append('')
            
            # Join paragraphs with the original newline characters
            translated_text += '\n'.join(translated_paragraphs)
    
    # Clean up extra spaces before punctuation
    translated_text = re.sub(r'\s+([.,;?!])', r'\1', translated_text)
    # Remove stray period immediately following closing backticks
    translated_text = re.sub(r'(`+)\.', r'\1', translated_text)
    
    return translated_text

async def translate_text(text, source_lang, desti_lang):
    return await main(text, source_lang, desti_lang)
