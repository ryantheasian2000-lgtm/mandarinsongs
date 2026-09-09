"""
Mandarin Dictionary & Pinyin Service
Provides character/word lookup, tone marks, HSK levels, and segmentation.
"""

import re
from typing import Dict, List, Optional, Tuple

# Tone mapping table
TONE_MARKS = {
    'a': ['a', 'ā', 'á', 'ǎ', 'à'],
    'e': ['e', 'ē', 'é', 'ě', 'è'],
    'i': ['i', 'ī', 'í', 'ǐ', 'ì'],
    'o': ['o', 'ō', 'ó', 'ǒ', 'ò'],
    'u': ['u', 'ū', 'ú', 'ǔ', 'ù'],
    'v': ['ü', 'ǖ', 'ǘ', 'ǚ', 'ǜ'],
    'ü': ['ü', 'ǖ', 'ǘ', 'ǚ', 'ǜ'],
}

def tone_number_to_accent(pinyin_token: str) -> Tuple[str, int]:
    """
    Converts a single pinyin syllable with tone number (e.g., 'ni3')
    into tone-accented pinyin ('nǐ') and returns (accented_str, tone_int).
    Tone 5 or no tone number is neutral (tone 5).
    """
    token = pinyin_token.strip().lower()
    if not token:
        return "", 5
    
    # Check if last char is a digit 1-5
    tone = 5
    if token[-1].isdigit():
        t = int(token[-1])
        if 1 <= t <= 5:
            tone = t
            token = token[:-1]
    
    if tone == 5 or tone == 0:
        return token.replace('v', 'ü'), 5

    # Determine which vowel gets the tone mark
    # Rules:
    # 1. 'a' and 'e' always take the mark
    # 2. 'ou' takes mark on 'o'
    # 3. Otherwise the final vowel takes the mark
    accented = token.replace('v', 'ü')
    target_idx = -1
    target_char = ''

    if 'a' in accented:
        target_idx = accented.find('a')
        target_char = 'a'
    elif 'e' in accented:
        target_idx = accented.find('e')
        target_char = 'e'
    elif 'ou' in accented:
        target_idx = accented.find('o')
        target_char = 'o'
    else:
        # Find the last vowel
        vowels = 'iouü'
        for i in range(len(accented) - 1, -1, -1):
            if accented[i] in vowels:
                target_idx = i
                target_char = accented[i]
                break

    if target_idx != -1 and target_char in TONE_MARKS:
        replacement = TONE_MARKS[target_char][tone]
        accented = accented[:target_idx] + replacement + accented[target_idx + 1:]

    return accented, tone


def convert_pinyin_string(pinyin_str: str) -> List[Dict]:
    """
    Converts a space-separated pinyin string with tone numbers into accented pinyin.
    Returns list of dicts: [{"pinyin": "nǐ", "tone": 3}, ...]
    """
    tokens = pinyin_str.strip().split()
    results = []
    for tok in tokens:
        accented, tone = tone_number_to_accent(tok)
        results.append({
            "original": tok,
            "pinyin": accented,
            "tone": tone
        })
    return results


# Comprehensive starter lexicon for Mandarin learning (frequently appearing in songs & HSK 1-6)
COMMON_DICTIONARY: Dict[str, Dict] = {
    "你": {"pinyin": "nǐ", "tone": 3, "traditional": "你", "translation": "you (singular)", "hsk": 1, "pos": "pronoun"},
    "我": {"pinyin": "wǒ", "tone": 3, "traditional": "我", "translation": "I, me", "hsk": 1, "pos": "pronoun"},
    "他": {"pinyin": "tā", "tone": 1, "traditional": "他", "translation": "he, him", "hsk": 1, "pos": "pronoun"},
    "她": {"pinyin": "tā", "tone": 1, "traditional": "她", "translation": "she, her", "hsk": 1, "pos": "pronoun"},
    "它": {"pinyin": "tā", "tone": 1, "traditional": "它", "translation": "it", "hsk": 2, "pos": "pronoun"},
    "我们": {"pinyin": "wǒ men", "tone": 3, "traditional": "我們", "translation": "we, us", "hsk": 1, "pos": "pronoun"},
    "你们": {"pinyin": "nǐ men", "tone": 3, "traditional": "你們", "translation": "you (plural)", "hsk": 1, "pos": "pronoun"},
    "他们": {"pinyin": "tā men", "tone": 1, "traditional": "他們", "translation": "they, them (male/mixed)", "hsk": 1, "pos": "pronoun"},
    "问": {"pinyin": "wèn", "tone": 4, "traditional": "問", "translation": "to ask, inquire", "hsk": 2, "pos": "verb"},
    "爱": {"pinyin": "ài", "tone": 4, "traditional": "愛", "translation": "love, to love", "hsk": 1, "pos": "noun/verb"},
    "有": {"pinyin": "yǒu", "tone": 3, "traditional": "有", "translation": "to have, there is/are", "hsk": 1, "pos": "verb"},
    "多": {"pinyin": "duō", "tone": 1, "traditional": "多", "translation": "many, much, how (much/far/deep)", "hsk": 1, "pos": "adjective/adverb"},
    "深": {"pinyin": "shēn", "tone": 1, "traditional": "深", "translation": "deep, profound, dark (color)", "hsk": 3, "pos": "adjective"},
    "有多深": {"pinyin": "yǒu duō shēn", "tone": 3, "traditional": "有多深", "translation": "how deep (it is)", "hsk": 3, "pos": "phrase"},
    "情": {"pinyin": "qíng", "tone": 2, "traditional": "情", "translation": "feeling, sentiment, love, affection", "hsk": 3, "pos": "noun"},
    "感情": {"pinyin": "gǎn qíng", "tone": 3, "traditional": "感情", "translation": "emotion, affection, feelings", "hsk": 4, "pos": "noun"},
    "情深": {"pinyin": "qíng shēn", "tone": 2, "traditional": "情深", "translation": "deeply affectionate, deep love", "hsk": 4, "pos": "adjective"},
    "真": {"pinyin": "zhēn", "tone": 1, "traditional": "真", "translation": "real, true, genuine, truly", "hsk": 2, "pos": "adjective/adverb"},
    "月亮": {"pinyin": "yuè liang", "tone": 4, "traditional": "月亮", "translation": "moon", "hsk": 3, "pos": "noun"},
    "代表": {"pinyin": "dài biǎo", "tone": 4, "traditional": "代表", "translation": "to represent, stand for, delegate", "hsk": 4, "pos": "verb/noun"},
    "心": {"pinyin": "xīn", "tone": 1, "traditional": "心", "translation": "heart, mind, feelings", "hsk": 2, "pos": "noun"},
    "轻": {"pinyin": "qīng", "tone": 1, "traditional": "輕", "translation": "light, gentle, soft", "hsk": 3, "pos": "adjective"},
    "轻轻": {"pinyin": "qīng qīng", "tone": 1, "traditional": "輕輕", "translation": "gently, softly, lightly", "hsk": 3, "pos": "adverb"},
    "一个": {"pinyin": "yī gè", "tone": 1, "traditional": "一個", "translation": "one, a single", "hsk": 1, "pos": "measure word phrase"},
    "吻": {"pinyin": "wěn", "tone": 3, "traditional": "吻", "translation": "kiss, to kiss", "hsk": 4, "pos": "noun/verb"},
    "已经": {"pinyin": "yǐ jīng", "tone": 3, "traditional": "已經", "translation": "already", "hsk": 2, "pos": "adverb"},
    "打动": {"pinyin": "dǎ dòng", "tone": 3, "traditional": "打動", "translation": "to move, touch (emotionally)", "hsk": 5, "pos": "verb"},
    "一段": {"pinyin": "yī duàn", "tone": 1, "traditional": "一段", "translation": "a period of, a passage of", "hsk": 3, "pos": "phrase"},
    "叫": {"pinyin": "jiào", "tone": 4, "traditional": "叫", "translation": "to call, to make/cause", "hsk": 1, "pos": "verb"},
    "思念": {"pinyin": "sī niàn", "tone": 1, "traditional": "思念", "translation": "to miss, yearn for, longing", "hsk": 5, "pos": "verb/noun"},
    "到如今": {"pinyin": "dào rú jīn", "tone": 4, "traditional": "到如今", "translation": "up until now, even today", "hsk": 4, "pos": "phrase"},
    "去看": {"pinyin": "qù kàn", "tone": 4, "traditional": "去看", "translation": "go and look/see", "hsk": 1, "pos": "phrase"},
    "去想": {"pinyin": "qù xiǎng", "tone": 4, "traditional": "去想", "translation": "go and think/wonder", "hsk": 1, "pos": "phrase"},
    "看": {"pinyin": "kàn", "tone": 4, "traditional": "看", "translation": "to look, watch, read, see", "hsk": 1, "pos": "verb"},
    "想": {"pinyin": "xiǎng", "tone": 3, "traditional": "想", "translation": "to think, miss, want to", "hsk": 1, "pos": "verb"},
    "一想": {"pinyin": "yī xiǎng", "tone": 1, "traditional": "一想", "translation": "to think for a moment, ponder", "hsk": 2, "pos": "verb"},
    "一看": {"pinyin": "yī kàn", "tone": 1, "traditional": "一看", "translation": "to take a look, glance", "hsk": 2, "pos": "verb"},
    "是": {"pinyin": "shì", "tone": 4, "traditional": "是", "translation": "to be (am/is/are), yes", "hsk": 1, "pos": "verb"},
    "不": {"pinyin": "bù", "tone": 4, "traditional": "不", "translation": "no, not", "hsk": 1, "pos": "adverb"},
    "移": {"pinyin": "yí", "tone": 2, "traditional": "移", "translation": "to shift, move, change", "hsk": 4, "pos": "verb"},
    "不移": {"pinyin": "bù yí", "tone": 4, "traditional": "不移", "translation": "unwavering, steadfast, unshifting", "hsk": 4, "pos": "adjective"},
    "变": {"pinyin": "biàn", "tone": 4, "traditional": "變", "translation": "to change, transform, alter", "hsk": 3, "pos": "verb"},
    "不变": {"pinyin": "bù biàn", "tone": 4, "traditional": "不變", "translation": "unchanging, constant", "hsk": 3, "pos": "adjective"},
    "对": {"pinyin": "duì", "tone": 4, "traditional": "對", "translation": "towards, correct, opposite", "hsk": 2, "pos": "preposition/adjective"},
    "面": {"pinyin": "miàn", "tone": 4, "traditional": "面", "translation": "face, side, surface", "hsk": 2, "pos": "noun"},
    "对面": {"pinyin": "duì miàn", "tone": 4, "traditional": "對面", "translation": "opposite side, across the way", "hsk": 3, "pos": "noun"},
    "女孩": {"pinyin": "nǚ hái", "tone": 3, "traditional": "女孩", "translation": "girl, young woman", "hsk": 2, "pos": "noun"},
    "看过来": {"pinyin": "kàn guò lái", "tone": 4, "traditional": "看過來", "translation": "look over here, turn your gaze here", "hsk": 2, "pos": "phrase"},
    "过来": {"pinyin": "guò lái", "tone": 4, "traditional": "過來", "translation": "come over, over here", "hsk": 2, "pos": "verb"},
    "这里": {"pinyin": "zhè lǐ", "tone": 4, "traditional": "這裡", "translation": "here, this place", "hsk": 1, "pos": "pronoun"},
    "表演": {"pinyin": "biǎo yǎn", "tone": 3, "traditional": "表演", "translation": "performance, to perform/act", "hsk": 3, "pos": "noun/verb"},
    "精彩": {"pinyin": "jīng cǎi", "tone": 1, "traditional": "精彩", "translation": "wonderful, brilliant, splendid", "hsk": 4, "pos": "adjective"},
    "很": {"pinyin": "hěn", "tone": 3, "traditional": "很", "translation": "very, quite", "hsk": 1, "pos": "adverb"},
    "请": {"pinyin": "qǐng", "tone": 3, "traditional": "請", "translation": "please, to invite", "hsk": 1, "pos": "verb"},
    "不要": {"pinyin": "bù yào", "tone": 4, "traditional": "不要", "translation": "do not, don't", "hsk": 1, "pos": "phrase"},
    "假装": {"pinyin": "jiǎ zhuāng", "tone": 3, "traditional": "假裝", "translation": "to pretend, feign, disguise", "hsk": 5, "pos": "verb"},
    "理": {"pinyin": "lǐ", "tone": 3, "traditional": "理", "translation": "to pay attention to, reason", "hsk": 4, "pos": "verb"},
    "不理": {"pinyin": "bù lǐ", "tone": 4, "traditional": "不理", "translation": "to ignore, pay no attention to", "hsk": 4, "pos": "verb"},
    "默默": {"pinyin": "mò mò", "tone": 4, "traditional": "默默", "translation": "silently, quietly, quietly by oneself", "hsk": 5, "pos": "adverb"},
    "等待": {"pinyin": "děng dài", "tone": 3, "traditional": "等待", "translation": "to wait for, await", "hsk": 4, "pos": "verb"},
    "等": {"pinyin": "děng", "tone": 3, "traditional": "等", "translation": "to wait, and so on", "hsk": 1, "pos": "verb"},
    "童话": {"pinyin": "tóng huà", "tone": 2, "traditional": "童話", "translation": "fairy tale", "hsk": 4, "pos": "noun"},
    "故事": {"pinyin": "gù shì", "tone": 4, "traditional": "故事", "translation": "story, tale", "hsk": 3, "pos": "noun"},
    "里": {"pinyin": "lǐ", "tone": 3, "traditional": "裏", "translation": "inside, within", "hsk": 1, "pos": "noun/preposition"},
    "都是": {"pinyin": "dōu shì", "tone": 1, "traditional": "都是", "translation": "all are, are all", "hsk": 1, "pos": "phrase"},
    "骗人": {"pinyin": "piàn rén", "tone": 4, "traditional": "騙人", "translation": "to deceive people, lie, deceptive", "hsk": 4, "pos": "verb/adjective"},
    "可能": {"pinyin": "kě néng", "tone": 3, "traditional": "可能", "translation": "maybe, possible, probable", "hsk": 2, "pos": "adverb/adjective"},
    "天使": {"pinyin": "tiān shǐ", "tone": 1, "traditional": "天使", "translation": "angel", "hsk": 4, "pos": "noun"},
    "张开": {"pinyin": "zhāng kāi", "tone": 1, "traditional": "張開", "translation": "to open wide, spread out (wings)", "hsk": 4, "pos": "verb"},
    "双手": {"pinyin": "shuāng shǒu", "tone": 1, "traditional": "雙手", "translation": "both hands, pair of hands", "hsk": 3, "pos": "noun"},
    "变成": {"pinyin": "biàn chéng", "tone": 4, "traditional": "變成", "translation": "to turn into, become", "hsk": 3, "pos": "verb"},
    "守护": {"pinyin": "shǒu hù", "tone": 3, "traditional": "守護", "translation": "to guard, protect, watch over", "hsk": 5, "pos": "verb"},
    "相信": {"pinyin": "xiāng xìn", "tone": 1, "traditional": "相信", "translation": "to believe, trust", "hsk": 3, "pos": "verb"},
    "幸福": {"pinyin": "xìng fú", "tone": 4, "traditional": "幸福", "translation": "happiness, blessed, happy", "hsk": 4, "pos": "noun/adjective"},
    "快乐": {"pinyin": "kuài lè", "tone": 4, "traditional": "快樂", "translation": "happy, joyful, merry", "hsk": 1, "pos": "adjective"},
    "结局": {"pinyin": "jié jú", "tone": 2, "traditional": "結局", "translation": "ending, conclusion, finale", "hsk": 4, "pos": "noun"},
    "会": {"pinyin": "huì", "tone": 4, "traditional": "會", "translation": "can, will, know how to", "hsk": 1, "pos": "verb/modal"},
    "的": {"pinyin": "de", "tone": 5, "traditional": "的", "translation": "possessive particle, 's", "hsk": 1, "pos": "particle"},
    "地": {"pinyin": "de", "tone": 5, "traditional": "地", "translation": "adverbial particle (-ly)", "hsk": 2, "pos": "particle"},
    "得": {"pinyin": "de", "tone": 5, "traditional": "得", "translation": "structural complement particle", "hsk": 2, "pos": "particle"},
    "了": {"pinyin": "le", "tone": 5, "traditional": "了", "translation": "aspect particle (completed action/change)", "hsk": 1, "pos": "particle"},
    "吗": {"pinyin": "ma", "tone": 5, "traditional": "嗎", "translation": "question particle", "hsk": 1, "pos": "particle"},
    "呢": {"pinyin": "ne", "tone": 5, "traditional": "呢", "translation": "aspect/question particle (what about...?)", "hsk": 1, "pos": "particle"},
    "吧": {"pinyin": "ba", "tone": 5, "traditional": "吧", "translation": "suggestion/modal particle", "hsk": 1, "pos": "particle"},
    "啊": {"pinyin": "a", "tone": 5, "traditional": "啊", "translation": "exclamation/modal particle", "hsk": 2, "pos": "particle"},
}

def lookup_word(word: str) -> Optional[Dict]:
    """Look up a word or character in the dictionary."""
    clean_word = word.strip()
    if clean_word in COMMON_DICTIONARY:
        data = COMMON_DICTIONARY[clean_word].copy()
        data["hanzi"] = clean_word
        return data
    
    if len(clean_word) > 1:
        chars_info = []
        for char in clean_word:
            if char in COMMON_DICTIONARY:
                c_data = COMMON_DICTIONARY[char].copy()
                c_data["hanzi"] = char
                chars_info.append(c_data)
        if chars_info:
            combined_pinyin = " ".join(c["pinyin"] for c in chars_info)
            combined_trans = " + ".join(c["translation"] for c in chars_info)
            return {
                "hanzi": clean_word,
                "traditional": clean_word,
                "pinyin": combined_pinyin,
                "tone": chars_info[0]["tone"] if chars_info else 1,
                "translation": f"Compound: {combined_trans}",
                "hsk": max(c.get("hsk", 1) for c in chars_info),
                "pos": "compound",
                "breakdown": chars_info
            }
            
    return None

try:
    from pypinyin import pinyin, Style
    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False


def get_character_pinyin(char: str) -> Tuple[str, int]:
    """Generates accented pinyin and tone integer (1-5) for a single Chinese character using pypinyin."""
    if HAS_PYPINYIN and char:
        try:
            res_tone = pinyin(char, style=Style.TONE)
            res_num = pinyin(char, style=Style.TONE3)
            if res_tone and res_tone[0] and res_num and res_num[0]:
                acc_py = res_tone[0][0]
                num_py = res_num[0][0]
                tone = 5
                if num_py and num_py[-1].isdigit():
                    t = int(num_py[-1])
                    if 1 <= t <= 5:
                        tone = t
                return acc_py, tone
        except Exception:
            pass
    return char, 5


def generate_line_pinyin(hanzi_line: str) -> str:
    """
    Generates complete space-separated Pinyin string for any Mandarin sentence or lyric line.
    """
    tokens = segment_and_annotate_line(hanzi_line)
    pinyin_parts = [t["pinyin"] for t in tokens if t.get("pinyin") and not t.get("isPunctuation")]
    return " ".join(pinyin_parts)


def segment_and_annotate_line(hanzi_line: str, pinyin_line: Optional[str] = None) -> List[Dict]:
    """
    Segments a Chinese line into word tokens with pinyin, definition, and tone.
    Uses dictionary matching with pypinyin fallback.
    """
    cleaned = hanzi_line.strip()
    i = 0
    n = len(cleaned)
    tokens = []
    
    pinyin_words = pinyin_line.split() if pinyin_line else []
    p_idx = 0

    while i < n:
        char = cleaned[i]
        
        # Skip punctuation or whitespace
        if char in " ，。！？、；：“”‘’（）《》…—,.!?:;\"'() \t\n":
            tokens.append({
                "hanzi": char,
                "pinyin": "",
                "tone": 5,
                "translation": "",
                "isPunctuation": True
            })
            i += 1
            continue

        matched = False
        for match_len in range(4, 0, -1):
            if i + match_len <= n:
                sub = cleaned[i:i + match_len]
                if sub in COMMON_DICTIONARY:
                    info = COMMON_DICTIONARY[sub]
                    tokens.append({
                        "hanzi": sub,
                        "traditional": info.get("traditional", sub),
                        "pinyin": info.get("pinyin", ""),
                        "tone": info.get("tone", 1),
                        "translation": info.get("translation", ""),
                        "hsk": info.get("hsk", 1),
                        "pos": info.get("pos", ""),
                        "isPunctuation": False
                    })
                    i += match_len
                    matched = True
                    break
        
        if not matched:
            if p_idx < len(pinyin_words):
                char_pinyin = pinyin_words[p_idx]
                acc_pinyin, tone = tone_number_to_accent(char_pinyin)
                p_idx += 1
            else:
                acc_pinyin, tone = get_character_pinyin(char)

            tokens.append({
                "hanzi": char,
                "traditional": char,
                "pinyin": acc_pinyin,
                "tone": tone,
                "translation": "Character",
                "hsk": 1,
                "pos": "character",
                "isPunctuation": False
            })
            i += 1

    return tokens
