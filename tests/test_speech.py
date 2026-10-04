import unittest

from services.speech_service import transcribe_audio


class TestSpeechService(unittest.TestCase):

    def test_missing_audio_file(self):

        with self.assertRaises(Exception):

            transcribe_audio(
                "this_file_does_not_exist.wav"
            )


if __name__ == "__main__":
    unittest.main()