"""
Sample songs repository with rich karaoke metadata, word tokens, and timestamps.
"""

SAMPLE_SONGS = [
    {
        "id": "sample-moon",
        "title": "月亮代表我的心 (The Moon Represents My Heart)",
        "artist": "邓丽君 (Teresa Teng)",
        "audioUrl": "/static/audio/the_moon_represents_my_heart.wav",
        "difficulty": "HSK 1-2 • Beginner Favorite",
        "languageTip": "Notice how '你问我' uses 3rd tone sandhi: when two 3rd tones appear together, the first changes to 2nd tone (nǐ wèn wǒ -> ní wèn wǒ).",
        "lines": [
            {
                "id": 0,
                "startTime": 3.6,
                "endTime": 8.2,
                "hanzi": "你问我爱你有多深",
                "pinyin": "nǐ wèn wǒ ài nǐ yǒu duō shēn",
                "english": "You ask me how deep my love for you is",
                "words": [
                    {"hanzi": "你", "pinyin": "nǐ", "translation": "you", "tone": 3, "hsk": 1},
                    {"hanzi": "问", "pinyin": "wèn", "translation": "ask", "tone": 4, "hsk": 2},
                    {"hanzi": "我", "pinyin": "wǒ", "translation": "me / I", "tone": 3, "hsk": 1},
                    {"hanzi": "爱", "pinyin": "ài", "translation": "to love", "tone": 4, "hsk": 1},
                    {"hanzi": "你", "pinyin": "nǐ", "translation": "you", "tone": 3, "hsk": 1},
                    {"hanzi": "有多深", "pinyin": "yǒu duō shēn", "translation": "how deep", "tone": 3, "hsk": 3}
                ]
            },
            {
                "id": 1,
                "startTime": 8.2,
                "endTime": 12.0,
                "hanzi": "我爱你有几分",
                "pinyin": "wǒ ài nǐ yǒu jǐ fēn",
                "english": "How much do I love you?",
                "words": [
                    {"hanzi": "我", "pinyin": "wǒ", "translation": "I / me", "tone": 3, "hsk": 1},
                    {"hanzi": "爱", "pinyin": "ài", "translation": "love", "tone": 4, "hsk": 1},
                    {"hanzi": "你", "pinyin": "nǐ", "translation": "you", "tone": 3, "hsk": 1},
                    {"hanzi": "有", "pinyin": "yǒu", "translation": "have / is there", "tone": 3, "hsk": 1},
                    {"hanzi": "几分", "pinyin": "jǐ fēn", "translation": "to what degree / how much", "tone": 3, "hsk": 2}
                ]
            },
            {
                "id": 2,
                "startTime": 12.0,
                "endTime": 15.8,
                "hanzi": "我的情也真",
                "pinyin": "wǒ de qíng yě zhēn",
                "english": "My feelings are true",
                "words": [
                    {"hanzi": "我", "pinyin": "wǒ", "translation": "my", "tone": 3, "hsk": 1},
                    {"hanzi": "的", "pinyin": "de", "translation": "possessive particle ('s)", "tone": 5, "hsk": 1},
                    {"hanzi": "情", "pinyin": "qíng", "translation": "affection / feelings", "tone": 2, "hsk": 3},
                    {"hanzi": "也", "pinyin": "yě", "translation": "also / too", "tone": 3, "hsk": 1},
                    {"hanzi": "真", "pinyin": "zhēn", "translation": "real / true / genuine", "tone": 1, "hsk": 2}
                ]
            },
            {
                "id": 3,
                "startTime": 15.8,
                "endTime": 19.6,
                "hanzi": "我的爱也真",
                "pinyin": "wǒ de ài yě zhēn",
                "english": "My love is also real",
                "words": [
                    {"hanzi": "我", "pinyin": "wǒ", "translation": "my", "tone": 3, "hsk": 1},
                    {"hanzi": "的", "pinyin": "de", "translation": "possessive particle", "tone": 5, "hsk": 1},
                    {"hanzi": "爱", "pinyin": "ài", "translation": "love", "tone": 4, "hsk": 1},
                    {"hanzi": "也", "pinyin": "yě", "translation": "also", "tone": 3, "hsk": 1},
                    {"hanzi": "真", "pinyin": "zhēn", "translation": "true / sincere", "tone": 1, "hsk": 2}
                ]
            },
            {
                "id": 4,
                "startTime": 19.6,
                "endTime": 25.5,
                "hanzi": "月亮代表我的心",
                "pinyin": "yuè liang dài biǎo wǒ de xīn",
                "english": "The moon represents my heart",
                "words": [
                    {"hanzi": "月亮", "pinyin": "yuè liang", "translation": "moon", "tone": 4, "hsk": 3},
                    {"hanzi": "代表", "pinyin": "dài biǎo", "translation": "represents / stands for", "tone": 4, "hsk": 4},
                    {"hanzi": "我", "pinyin": "wǒ", "translation": "my", "tone": 3, "hsk": 1},
                    {"hanzi": "的", "pinyin": "de", "translation": "'s", "tone": 5, "hsk": 1},
                    {"hanzi": "心", "pinyin": "xīn", "translation": "heart / feeling", "tone": 1, "hsk": 2}
                ]
            },
            {
                "id": 5,
                "startTime": 25.5,
                "endTime": 30.0,
                "hanzi": "轻轻的一个吻",
                "pinyin": "qīng qīng de yī gè wěn",
                "english": "A gentle, tender kiss",
                "words": [
                    {"hanzi": "轻轻", "pinyin": "qīng qīng", "translation": "gently / softly", "tone": 1, "hsk": 3},
                    {"hanzi": "的", "pinyin": "de", "translation": "adjective connector", "tone": 5, "hsk": 1},
                    {"hanzi": "一个", "pinyin": "yī gè", "translation": "one / a single", "tone": 1, "hsk": 1},
                    {"hanzi": "吻", "pinyin": "wěn", "translation": "kiss", "tone": 3, "hsk": 4}
                ]
            },
            {
                "id": 6,
                "startTime": 30.0,
                "endTime": 33.8,
                "hanzi": "曾经打动你的心",
                "pinyin": "céng jīng dǎ dòng nǐ de xīn",
                "english": "Once moved and touched your heart",
                "words": [
                    {"hanzi": "曾经", "pinyin": "céng jīng", "translation": "once / at one time", "tone": 2, "hsk": 3},
                    {"hanzi": "打动", "pinyin": "dǎ dòng", "translation": "moved / touched emotionally", "tone": 3, "hsk": 5},
                    {"hanzi": "你", "pinyin": "nǐ", "translation": "your", "tone": 3, "hsk": 1},
                    {"hanzi": "的", "pinyin": "de", "translation": "'s", "tone": 5, "hsk": 1},
                    {"hanzi": "心", "pinyin": "xīn", "translation": "heart", "tone": 1, "hsk": 2}
                ]
            },
            {
                "id": 7,
                "startTime": 33.8,
                "endTime": 37.6,
                "hanzi": "深深的一段情",
                "pinyin": "shēn shēn de yī duàn qíng",
                "english": "A deep and profound love",
                "words": [
                    {"hanzi": "深深", "pinyin": "shēn shēn", "translation": "deeply / profound", "tone": 1, "hsk": 3},
                    {"hanzi": "的", "pinyin": "de", "translation": "particle", "tone": 5, "hsk": 1},
                    {"hanzi": "一段", "pinyin": "yī duàn", "translation": "a passage of / an episode of", "tone": 1, "hsk": 3},
                    {"hanzi": "情", "pinyin": "qíng", "translation": "affection / relationship", "tone": 2, "hsk": 3}
                ]
            },
            {
                "id": 8,
                "startTime": 37.6,
                "endTime": 42.0,
                "hanzi": "叫我思念到如今",
                "pinyin": "jiào wǒ sī niàn dào rú jīn",
                "english": "Has made me yearn for you to this very day",
                "words": [
                    {"hanzi": "叫", "pinyin": "jiào", "translation": "causes / makes", "tone": 4, "hsk": 1},
                    {"hanzi": "我", "pinyin": "wǒ", "translation": "me", "tone": 3, "hsk": 1},
                    {"hanzi": "思念", "pinyin": "sī niàn", "translation": "to miss / yearn for", "tone": 1, "hsk": 5},
                    {"hanzi": "到如今", "pinyin": "dào rú jīn", "translation": "up until today / even now", "tone": 4, "hsk": 4}
                ]
            },
            {
                "id": 9,
                "startTime": 42.0,
                "endTime": 47.5,
                "hanzi": "你去想一想，你去看一看",
                "pinyin": "nǐ qù xiǎng yī xiǎng, nǐ qù kàn yī kàn",
                "english": "Go and think about it, go and take a look",
                "words": [
                    {"hanzi": "你", "pinyin": "nǐ", "translation": "you", "tone": 3, "hsk": 1},
                    {"hanzi": "去看", "pinyin": "qù kàn", "translation": "go see / look", "tone": 4, "hsk": 1},
                    {"hanzi": "去想", "pinyin": "qù xiǎng", "translation": "go think", "tone": 4, "hsk": 1},
                    {"hanzi": "一想", "pinyin": "yī xiǎng", "translation": "ponder a moment", "tone": 1, "hsk": 2},
                    {"hanzi": "一看", "pinyin": "yī kàn", "translation": "glance / observe", "tone": 1, "hsk": 2}
                ]
            },
            {
                "id": 10,
                "startTime": 47.5,
                "endTime": 54.0,
                "hanzi": "月亮代表我的心",
                "pinyin": "yuè liang dài biǎo wǒ de xīn",
                "english": "The moon represents my heart",
                "words": [
                    {"hanzi": "月亮", "pinyin": "yuè liang", "translation": "moon", "tone": 4, "hsk": 3},
                    {"hanzi": "代表", "pinyin": "dài biǎo", "translation": "represents", "tone": 4, "hsk": 4},
                    {"hanzi": "我", "pinyin": "wǒ", "translation": "my", "tone": 3, "hsk": 1},
                    {"hanzi": "的", "pinyin": "de", "translation": "'s", "tone": 5, "hsk": 1},
                    {"hanzi": "心", "pinyin": "xīn", "translation": "heart", "tone": 1, "hsk": 2}
                ]
            }
        ]
    }
]
