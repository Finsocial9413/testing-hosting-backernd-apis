import logging
from enum import Enum

import re
from googletrans import Translator
import asyncio
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from .translator_setup.translating import translate_text as translating_user_text

class LanguageCode(str, Enum):
    ENGLISH = "eng_Latn"
    HINDI = "hin_Deva"
    BENGALI = "ben_Beng"
    GUJARATI = "guj_Gujr"
    KANNADA = "kan_Knda"
    MALAYALAM = "mal_Mlym"
    MARATHI = "mar_Deva"
    NEPALI = "npi_Deva"
    ORIYA = "ory_Orya"
    PUNJABI = "pan_Guru"
    SANSKRIT = "san_Deva"
    TAMIL = "tam_Taml"
    TELUGU = "tel_Telu"
    URDU = "urd_Arab"
    ASSAMESE = "asm_Beng"
    KASHMIRI = "kas_Arab"
    MANIPURI = "mni_Mtei"
    SINDHI = "snd_Arab"
    AFRIKAANS = "af"
    ALBANIAN = "sq"
    AMHARIC = "am"
    ARABIC = "ar"
    ARMENIAN = "hy"
    AZERBAIJANI = "az"
    BASQUE = "eu"
    BELARUSIAN = "be"
    BOSNIAN = "bs"
    BULGARIAN = "bg"
    CATALAN = "ca"
    CEBUANO = "ceb"
    CHICHEWA = "ny"
    CHINESE_SIMPLIFIED = "zh-cn"
    CHINESE_TRADITIONAL = "zh-tw"
    CORSICAN = "co"
    CROATIAN = "hr"
    CZECH = "cs"
    DANISH = "da"
    DUTCH = "nl"
    ESPERANTO = "eo"
    ESTONIAN = "et"
    FILIPINO = "tl"
    FINNISH = "fi"
    FRENCH = "fr"
    FRISIAN = "fy"
    GALICIAN = "gl"
    GEORGIAN = "ka"
    GERMAN = "de"
    GREEK = "el"
    HAITIAN_CREOLE = "ht"
    HAUSA = "ha"
    HAWAIIAN = "haw"
    HEBREW = "he"
    HMONG = "hmn"
    HUNGARIAN = "hu"
    ICELANDIC = "is"
    IGBO = "ig"
    INDONESIAN = "id"
    IRISH = "ga"
    ITALIAN = "it"
    JAPANESE = "ja"
    JAVANESE = "jw"
    KAZAKH = "kk"
    KHMER = "km"
    KOREAN = "ko"
    KURDISH = "ku"
    KYRGYZ = "ky"
    LAO = "lo"
    LATIN = "la"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    LUXEMBOURGISH = "lb"
    MACEDONIAN = "mk"
    MALAGASY = "mg"
    MALAY = "ms"
    MALTESE = "mt"
    MAORI = "mi"
    MONGOLIAN = "mn"
    MYANMAR = "my"
    NORWEGIAN = "no"
    ODIA = "or"
    PASHTO = "ps"
    PERSIAN = "fa"
    POLISH = "pl"
    PORTUGUESE = "pt"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SAMOAN = "sm"
    SCOTS_GAELIC = "gd"
    SERBIAN = "sr"
    SESOTHO = "st"
    SHONA = "sn"
    SINHALA = "si"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    SOMALI = "so"
    SPANISH = "es"
    SUNDANESE = "su"
    SWAHILI = "sw"
    SWEDISH = "sv"
    TAJIK = "tg"
    THAI = "th"
    TURKISH = "tr"
    UKRAINIAN = "uk"
    UYGHUR = "ug"
    UZBEK = "uz"
    VIETNAMESE = "vi"
    WELSH = "cy"
    XHOSA = "xh"
    YIDDISH = "yi"
    YORUBA = "yo"
    ZULU = "zu"

class LanguageTranslator:
    """
    A translator class that normally would translate between languages
    but now simply returns the original text unchanged.
    """
    
    def __init__(self):
        logger.info("Initializing LanguageTranslator in pass-through mode")
    
    async def translate_text_async(self, text: str, source_lang: str = None, target_lang: str = None) -> str:
        """
        Bypass translation and return the original text unchanged.
        
        Args:
            text: The input text that would normally be translated
            source_lang: The source language code (ignored)
            target_lang: The target language code (ignored)
            
        Returns:
            The original text unchanged
        """
        LANGUAGES_codes_for_translating = {
            "eng_Latn": "EN",
            "hin_Deva": "HI",
            "ben_Beng": "BN",
            "guj_Gujr": "GU",
            "kan_Knda": "KA",
            "mal_Mlym": "ML",
            "mar_Deva": "MR",
            "npi_Deva": "Ne",
            "ory_Orya": "OR",
            "pan_Guru": "PA",
            "san_Deva": "SA",
            "tam_Taml": "TA",
            "tel_Telu": "TE",
            "urd_Arab": "UR",
            "asm_Beng": "AS",
            "kas_Arab": "KS",
            "mni_Mtei": "MN",
            "snd_Arab": "SI",
            "af": "AF",
            "sq": "SQ",
            "am": "AM",
            "ar": "AR",
            "hy": "HY",
            "az": "AZ",
            "eu": "EU",
            "be": "BE",
            "bs": "BS",
            "bg": "BG",
            "ca": "CA",
            "ceb": "CEB",
            "ny": "NY",
            "zh-cn": "ZH_CN",
            "zh-tw": "ZH_TW",
            "co": "CO",
            "hr": "HR",
            "cs": "CS",
            "da": "DA",
            "nl": "NL",
            "eo": "EO",
            "et": "ET",
            "tl": "TL",
            "fi": "FI",
            "fr": "FR",
            "fy": "FY",
            "gl": "GL",
            "ka": "KA",
            "de": "DE",
            "el": "EL",
            "ht": "HT",
            "ha": "HA",
            "haw": "HAW",
            "he": "HE",
            "hmn": "HMN",
            "hu": "HU",
            "is": "IS",
            "ig": "IG",
            "id": "ID",
            "ga": "GA",
            "it": "IT",
            "ja": "JA",
            "jw": "JW",
            "kk": "KK",
            "km": "KM",
            "ko": "KO",
            "ku": "KU",
            "ky": "KY",
            "lo": "LO",
            "la": "LA",
            "lv": "LV",
            "lt": "LT",
            "lb": "LB",
            "mk": "MK",
            "mg": "MG",
            "ms": "MS",
            "mt": "MT",
            "mi": "MI",
            "mn": "MN",
            "my": "MY",
            "ne": "NE",
            "no": "NO",
            "or": "OR",
            "ps": "PS",
            "fa": "FA",
            "pl": "PL",
            "pt": "PT",
            "ro": "RO",
            "ru": "RU",
            "sm": "SM",
            "gd": "GD",
            "sr": "SR",
            "st": "ST",
            "sn": "SN",
            "sd": "SD",
            "si": "SI",
            "sk": "SK",
            "sl": "SL",
            "so": "SO",
            "es": "ES",
            "su": "SU",
            "sw": "SW",
            "sv": "SV",
            "tg": "TG",
            "ta": "TA",
            "te": "TE",
            "th": "TH",
            "tr": "TR",
            "uk": "UK",
            "ur": "UR",
            "ug": "UG",
            "uz": "UZ",
            "vi": "VI",
            "cy": "CY",
            "xh": "XH",
            "yi": "YI",
            "yo": "YO",
            "zu": "ZU"
        }
        

        translating_text = await translating_user_text(text, LANGUAGES_codes_for_translating[source_lang], LANGUAGES_codes_for_translating[target_lang])
        return translating_text
    def translate_text(self, text: str, source_lang: str = None, target_lang: str = None) -> str:
        """
        Synchronous wrapper for the async translation function
        """
        return asyncio.run(self.translate_text_async(text, source_lang, target_lang))
    def available_languages(self): 
        """Return a list of available languages based on the LanguageCode enum"""
        language_names = {
            LanguageCode.ENGLISH: "English",
            LanguageCode.HINDI: "Hindi",
            LanguageCode.BENGALI: "Bengali",
            LanguageCode.GUJARATI: "Gujarati",
            LanguageCode.KANNADA: "Kannada",
            LanguageCode.MALAYALAM: "Malayalam",
            LanguageCode.MARATHI: "Marathi",
            LanguageCode.NEPALI: "Nepali",
            LanguageCode.ORIYA: "Oriya",
            LanguageCode.PUNJABI: "Punjabi",
            LanguageCode.SANSKRIT: "Sanskrit",
            LanguageCode.TAMIL: "Tamil",
            LanguageCode.TELUGU: "Telugu",
            LanguageCode.URDU: "Urdu",
            LanguageCode.ASSAMESE: "Assamese",
            LanguageCode.KASHMIRI: "Kashmiri",
            LanguageCode.MANIPURI: "Manipuri",
            LanguageCode.SINDHI: "Sindhi",
            LanguageCode.AFRIKAANS: "Afrikaans",
            LanguageCode.ALBANIAN: "Albanian",
            LanguageCode.AMHARIC: "Amharic",
            LanguageCode.ARABIC: "Arabic",
            LanguageCode.ARMENIAN: "Armenian",
            LanguageCode.AZERBAIJANI: "Azerbaijani",
            LanguageCode.BASQUE: "Basque",
            LanguageCode.BELARUSIAN: "Belarusian",
            LanguageCode.BOSNIAN: "Bosnian",
            LanguageCode.BULGARIAN: "Bulgarian",
            LanguageCode.CATALAN: "Catalan",
            LanguageCode.CEBUANO: "Cebuano",
            LanguageCode.CHICHEWA: "Chichewa",
            LanguageCode.CHINESE_SIMPLIFIED: "Chinese (Simplified)",
            LanguageCode.CHINESE_TRADITIONAL: "Chinese (Traditional)",
            LanguageCode.CORSICAN: "Corsican",
            LanguageCode.CROATIAN: "Croatian",
            LanguageCode.CZECH: "Czech",
            LanguageCode.DANISH: "Danish",
            LanguageCode.DUTCH: "Dutch",
            LanguageCode.ESPERANTO: "Esperanto",
            LanguageCode.ESTONIAN: "Estonian",
            LanguageCode.FILIPINO: "Filipino",
            LanguageCode.FINNISH: "Finnish",
            LanguageCode.FRENCH: "French",
            LanguageCode.FRISIAN: "Frisian",
            LanguageCode.GALICIAN: "Galician",
            LanguageCode.GEORGIAN: "Georgian",
            LanguageCode.GERMAN: "German",
            LanguageCode.GREEK: "Greek",
            LanguageCode.HAITIAN_CREOLE: "Haitian Creole",
            LanguageCode.HAUSA: "Hausa",
            LanguageCode.HAWAIIAN: "Hawaiian",
            LanguageCode.HEBREW: "Hebrew",
            LanguageCode.HMONG: "Hmong",
            LanguageCode.HUNGARIAN: "Hungarian",
            LanguageCode.ICELANDIC: "Icelandic",
            LanguageCode.IGBO: "Igbo",
            LanguageCode.INDONESIAN: "Indonesian",
            LanguageCode.IRISH: "Irish",
            LanguageCode.ITALIAN: "Italian",
            LanguageCode.JAPANESE: "Japanese",
            LanguageCode.JAVANESE: "Javanese",
            LanguageCode.KAZAKH: "Kazakh",
            LanguageCode.KHMER: "Khmer",
            LanguageCode.KOREAN: "Korean",
            LanguageCode.KURDISH: "Kurdish",
            LanguageCode.KYRGYZ: "Kyrgyz",
            LanguageCode.LAO: "Lao",
            LanguageCode.LATIN: "Latin",
            LanguageCode.LATVIAN: "Latvian",
            LanguageCode.LITHUANIAN: "Lithuanian",
            LanguageCode.LUXEMBOURGISH: "Luxembourgish",
            LanguageCode.MACEDONIAN: "Macedonian",
            LanguageCode.MALAGASY: "Malagasy",
            LanguageCode.MALAY: "Malay",
            LanguageCode.MALTESE: "Maltese",
            LanguageCode.MAORI: "Maori",
            LanguageCode.MONGOLIAN: "Mongolian",
            LanguageCode.MYANMAR: "Myanmar",
            LanguageCode.NORWEGIAN: "Norwegian",
            LanguageCode.ODIA: "Odia",
            LanguageCode.PASHTO: "Pashto",
            LanguageCode.PERSIAN: "Persian",
            LanguageCode.POLISH: "Polish",
            LanguageCode.PORTUGUESE: "Portuguese",
            LanguageCode.ROMANIAN: "Romanian",
            LanguageCode.RUSSIAN: "Russian",
            LanguageCode.SAMOAN: "Samoan",
            LanguageCode.SCOTS_GAELIC: "Scots Gaelic",
            LanguageCode.SERBIAN: "Serbian",
            LanguageCode.SESOTHO: "Sesotho",
            LanguageCode.SHONA: "Shona",
            LanguageCode.SINHALA: "Sinhala",
            LanguageCode.SLOVAK: "Slovak",
            LanguageCode.SLOVENIAN: "Slovenian",
            LanguageCode.SOMALI: "Somali",
            LanguageCode.SPANISH: "Spanish",
            LanguageCode.SUNDANESE: "Sundanese",
            LanguageCode.SWAHILI: "Swahili",
            LanguageCode.SWEDISH: "Swedish",
            LanguageCode.TAJIK: "Tajik",
            LanguageCode.THAI: "Thai",
            LanguageCode.TURKISH: "Turkish",
            LanguageCode.UKRAINIAN: "Ukrainian",
            LanguageCode.UYGHUR: "Uyghur",
            LanguageCode.UZBEK: "Uzbek",
            LanguageCode.VIETNAMESE: "Vietnamese",
            LanguageCode.WELSH: "Welsh",
            LanguageCode.XHOSA: "Xhosa",
            LanguageCode.YIDDISH: "Yiddish",
            LanguageCode.YORUBA: "Yoruba",
            LanguageCode.ZULU: "Zulu"
        }
        
        return [{"code": lang.value, "name": language_names[lang]} for lang in LanguageCode]

def show_language_menu():
    """
    Display language selection menu (kept for UI consistency)
    Returns selected language name and code
    """
    translator = LanguageTranslator()
    languages = translator.available_languages()
    
    print("\nAvailable Languages:")
    for i, lang in enumerate(languages, 1):
        print(f"{i}. {lang['name']}")
    
    while True:
        try:
            choice = input("\nSelect your language (1-18, or enter 'English'): ")
            if choice.isdigit() and 1 <= int(choice) <= len(languages):
                selected = languages[int(choice) - 1]
                return selected["name"], selected["code"]
            elif choice.strip().lower() == "english":
                return "English", "eng_Latn"
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {str(e)}. Please try again.")
    
    # Default to English if something goes wrong
    return "English", "eng_Latn"



