"""chatbot.py の応答ロジックに対する簡単なテスト。

会話ループ（input/print）の部分はテストしにくいので、
「メッセージを渡したら、期待した返答が返ってくるか」という
generate_reply() / is_exit_command() の部分だけをテストする。

実行方法:
    python -m unittest test_chatbot.py
"""

import unittest

from chatbot import DEFAULT_REPLY, generate_reply, is_exit_command


class GenerateReplyTests(unittest.TestCase):
    def test_greeting_returns_greeting_reply(self) -> None:
        self.assertEqual(generate_reply("こんにちは"), "こんにちは！今日はどんなご用件ですか？")

    def test_keyword_matching_is_case_insensitive_for_english(self) -> None:
        self.assertEqual(
            generate_reply("HELLO there"), "こんにちは！今日はどんなご用件ですか？"
        )

    def test_thanks_returns_thanks_reply(self) -> None:
        self.assertEqual(generate_reply("ありがとう！"), "どういたしまして！お役に立てて嬉しいです。")

    def test_unknown_message_returns_default_reply(self) -> None:
        message = "散歩に行きたいです"  # どのルールにも一致しないメッセージ
        self.assertEqual(generate_reply(message), DEFAULT_REPLY.format(message=message))

    def test_weather_keyword_returns_weather_reply(self) -> None:
        self.assertIn("天気情報", generate_reply("明日の天気を教えて"))


class IsExitCommandTests(unittest.TestCase):
    def test_exit_words_are_detected(self) -> None:
        for word in ["exit", "quit", "終了", "bye", "さようなら", "  exit  ", "EXIT"]:
            with self.subTest(word=word):
                self.assertTrue(is_exit_command(word))

    def test_normal_message_is_not_exit_command(self) -> None:
        self.assertFalse(is_exit_command("こんにちは"))


if __name__ == "__main__":
    unittest.main()
