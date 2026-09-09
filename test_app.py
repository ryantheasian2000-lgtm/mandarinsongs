"""
Automated unit and integration test suite for HuayuKaraoke.
"""

import unittest
import json
import os
import app
import dictionary_service

class HuayuKaraokeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        self.app.testing = True
        self.original_songs = app.load_custom_songs()

    def tearDown(self):
        app.save_custom_songs(self.original_songs)

    def test_homepage(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"HuayuKaraoke", response.data)
        self.assertIn(b"Pinyin", response.data)

    def test_get_songs(self):
        response = self.app.get("/api/songs")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("songs", data)
        self.assertTrue(len(data["songs"]) > 0)
        first_song = data["songs"][0]
        self.assertEqual(first_song["id"], "sample-moon")

    def test_get_song_detail(self):
        response = self.app.get("/api/songs/sample-moon")
        self.assertEqual(response.status_code, 200)
        song = json.loads(response.data)
        self.assertIn("lines", song)
        self.assertTrue(len(song["lines"]) > 5)
        first_line = song["lines"][0]
        self.assertIn("hanzi", first_line)
        self.assertIn("pinyin", first_line)
        self.assertIn("startTime", first_line)
        self.assertIn("words", first_line)

    def test_dictionary_lookup(self):
        # Direct service test
        entry = dictionary_service.lookup_word("月亮")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["pinyin"], "yuè liang")
        self.assertEqual(entry["hsk"], 3)

        # API test
        response = self.app.post(
            "/api/dictionary/lookup",
            data=json.dumps({"word": "爱"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["pinyin"], "ài")
        self.assertEqual(data["tone"], 4)

    def test_pinyin_tone_converter(self):
        accented, tone = dictionary_service.tone_number_to_accent("ni3")
        self.assertEqual(accented, "nǐ")
        self.assertEqual(tone, 3)

        accented, tone = dictionary_service.tone_number_to_accent("hao3")
        self.assertEqual(accented, "hǎo")
        self.assertEqual(tone, 3)

        accented, tone = dictionary_service.tone_number_to_accent("ma")
        self.assertEqual(accented, "ma")
        self.assertEqual(tone, 5)

    def test_lrc_parsing(self):
        lrc_sample = """
        [00:03.50]你问我爱你有多深
        [00:08.20]我爱你有几分
        """
        # Create a mock song in custom songs for testing
        test_song = {
            "id": "test-lrc-song",
            "title": "Test LRC",
            "artist": "Tester",
            "audioUrl": "/static/audio/the_moon_represents_my_heart.wav",
            "lines": []
        }
        app.save_custom_songs([test_song])

        response = self.app.post(
            "/api/parse-lrc",
            data=json.dumps({
                "songId": "test-lrc-song",
                "lrcText": lrc_sample
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["lines"]), 2)
        self.assertEqual(data["lines"][0]["startTime"], 3.5)
        self.assertEqual(data["lines"][1]["startTime"], 8.2)
        self.assertEqual(data["lines"][0]["hanzi"], "你问我爱你有多深")

    def test_vocab_lifecycle(self):
        # Save a word
        save_res = self.app.post(
            "/api/vocab",
            data=json.dumps({
                "hanzi": "测试",
                "pinyin": "cè shì",
                "translation": "test",
                "tone": 4,
                "hsk": 3
            }),
            content_type="application/json"
        )
        self.assertEqual(save_res.status_code, 200)

        # Get list
        get_res = self.app.get("/api/vocab")
        self.assertEqual(get_res.status_code, 200)
        vocab_data = json.loads(get_res.data)
        self.assertTrue(any(v["hanzi"] == "测试" for v in vocab_data["vocab"]))

        # Delete word
        del_res = self.app.delete("/api/vocab/测试")
        self.assertEqual(del_res.status_code, 200)

    def test_pypinyin_generation(self):
        line_pinyin = dictionary_service.generate_line_pinyin("风吹过雨下过")
        self.assertEqual(line_pinyin, "fēng chuī guò yǔ xià guò")

        tokens = dictionary_service.segment_and_annotate_line("今天天气很好")
        self.assertTrue(all(t["pinyin"] != "" for t in tokens if not t.get("isPunctuation")))

    def test_delete_song(self):
        # Create dummy custom song
        dummy_song = {
            "id": "dummy-to-delete",
            "title": "Dummy Song",
            "artist": "Dummy Artist",
            "audioUrl": "/uploads/dummy.mp3",
            "isCustom": True,
            "lines": []
        }
        app.save_custom_songs([dummy_song])

        # Delete it
        del_res = self.app.delete("/api/songs/dummy-to-delete")
        self.assertEqual(del_res.status_code, 200)
        data = json.loads(del_res.data)
        self.assertTrue(data.get("success"))

        # Confirm deleted from list
        get_res = self.app.get("/api/songs")
        songs_data = json.loads(get_res.data)
        self.assertFalse(any(s["id"] == "dummy-to-delete" for s in songs_data["songs"]))

    def test_sample_audio_file_exists(self):
        audio_path = os.path.join(app.BASE_DIR, "static", "audio", "the_moon_represents_my_heart.wav")
        self.assertTrue(os.path.exists(audio_path))
        self.assertTrue(os.path.getsize(audio_path) > 10000)

    def test_translate_song_no_key(self):
        # Should return 500/error if no Gemini key is provided
        res = self.app.post("/api/songs/sample-moon/translate", json={"apiKey": ""})
        self.assertEqual(res.status_code, 500)
        data = json.loads(res.data)
        self.assertIn("error", data)

    def test_translate_song_mocked(self):
        # Mock gemini_service.translate_lyrics
        original_func = app.gemini_service.translate_lyrics
        try:
            app.gemini_service.translate_lyrics = lambda lines, **kwargs: [
                {**l, "english": "Translated test line"} for l in lines
            ]
            res = self.app.post("/api/songs/sample-moon/translate", json={"apiKey": "mock-key"})
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertTrue(data.get("success"))
            self.assertEqual(data["song"]["lines"][0]["english"], "Translated test line")
        finally:
            app.gemini_service.translate_lyrics = original_func

    def test_extract_youtube_id(self):
        import youtube_lrclib_service
        self.assertEqual(youtube_lrclib_service.extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertEqual(youtube_lrclib_service.extract_youtube_id("https://youtu.be/dQw4w9WgXcQ?t=10"), "dQw4w9WgXcQ")
        self.assertEqual(youtube_lrclib_service.extract_youtube_id("https://www.youtube.com/shorts/dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertEqual(youtube_lrclib_service.extract_youtube_id("dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertIsNone(youtube_lrclib_service.extract_youtube_id("https://google.com"))

    def test_import_youtube_validation(self):
        # Empty URL
        res = self.app.post("/api/import-youtube", json={"youtubeUrl": ""})
        self.assertEqual(res.status_code, 400)

        # Invalid URL
        res = self.app.post("/api/import-youtube", json={"youtubeUrl": "https://invalid-url.com/abc"})
        self.assertEqual(res.status_code, 400)

    def test_import_youtube_mocked(self):
        import youtube_lrclib_service
        # Mock external dependencies to test end-to-end endpoint logic
        orig_video_info = youtube_lrclib_service.get_youtube_video_info
        orig_extract_meta = app.gemini_service.extract_song_metadata_from_youtube
        orig_fetch_lrc = youtube_lrclib_service.fetch_lrclib_lyrics
        orig_download = youtube_lrclib_service.download_youtube_audio
        orig_translate = app.gemini_service.translate_lyrics

        try:
            youtube_lrclib_service.get_youtube_video_info = lambda url: {
                "title": "田馥甄 Hebe Tien [ 小幸運 A Little Happiness ] Official Music Video",
                "author": "Hebe Tien",
                "duration": 265
            }
            app.gemini_service.extract_song_metadata_from_youtube = lambda **kw: {
                "track_name": "小幸運",
                "artist_name": "田馥甄",
                "english_title": "A Little Happiness"
            }
            youtube_lrclib_service.fetch_lrclib_lyrics = lambda **kw: {
                "syncedLyrics": "[00:15.50]我聽見雨滴落在青青草地\n[00:22.00]我聽見遠方下課鐘聲響起"
            }
            # Mock download to return a dummy file without hitting network
            dummy_file = os.path.join(app.UPLOAD_FOLDER, "test_yt.m4a")
            with open(dummy_file, "wb") as f:
                f.write(b"dummy audio data")
            youtube_lrclib_service.download_youtube_audio = lambda **kw: {
                "filepath": dummy_file,
                "filename": "test_yt.m4a"
            }
            app.gemini_service.translate_lyrics = lambda lines, **kw: [
                {**l, "english": "I hear raindrops falling on the green grass"} for l in lines
            ]

            res = self.app.post(
                "/api/import-youtube",
                json={"youtubeUrl": "https://www.youtube.com/watch?v=_sQSXwdtNxY", "apiKey": "fake-key"}
            )
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertTrue(data.get("success"))
            self.assertIn("song", data)
            song = data["song"]
            self.assertEqual(song["artist"], "田馥甄")
            self.assertEqual(len(song["lines"]), 2)
            self.assertEqual(song["lines"][0]["hanzi"], "我聽見雨滴落在青青草地")
            self.assertEqual(song["lines"][0]["english"], "I hear raindrops falling on the green grass")
            self.assertEqual(song["lines"][0]["startTime"], 15.5)

            if os.path.exists(dummy_file):
                os.remove(dummy_file)

        finally:
            youtube_lrclib_service.get_youtube_video_info = orig_video_info
            app.gemini_service.extract_song_metadata_from_youtube = orig_extract_meta
            youtube_lrclib_service.fetch_lrclib_lyrics = orig_fetch_lrc
            youtube_lrclib_service.download_youtube_audio = orig_download
            app.gemini_service.translate_lyrics = orig_translate


if __name__ == "__main__":
    unittest.main()
