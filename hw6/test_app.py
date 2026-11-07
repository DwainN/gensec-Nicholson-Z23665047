"""Behavior and adversarial-input checks; no third-party dependencies."""
import contextlib
import io
import unittest
from unittest.mock import patch
import app


class CheckerTests(unittest.TestCase):
    def test_common(self):
        self.assertEqual(app.analyze("PASSWORD123!").rating, "Weak")

    def test_repeated(self):
        self.assertEqual(app.analyze("a" * 20).rating, "Weak")

    def test_length_boundaries(self):
        for value in ("", "a" * 257, None, 123):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(ValueError):
                    app.analyze(value)
        self.assertEqual(app.analyze("ab" * 128).length, 256)

    def test_control_characters(self):
        for value in ("abc\n123", "abc\x1b[31m", "abc\x00123"):
            with self.assertRaises(ValueError):
                app.analyze(value)

    def test_long_and_unicode(self):
        self.assertEqual(app.analyze("harbor cactus violet lantern").rating,
                         "Stronger candidate")
        self.assertEqual(app.analyze("café lune rivière soleil").length, 24)

    def test_sequences(self):
        self.assertEqual(app.analyze("qwerty mountains 987!").rating, "Moderate")

    def test_adversarial_text_is_data(self):
        text = "$(touch /tmp/should-not-exist); ' OR 1=1 -- <script>"
        with patch("builtins.eval", side_effect=AssertionError("eval called")), \
             patch("os.system", side_effect=AssertionError("shell called")):
            result = app.analyze(text)
        self.assertEqual(result.length, len(text))
        self.assertNotIn(text, repr(result))

    def test_interactive_output_never_echoes_input(self):
        secret = "fake-secret-never-echo-31415"
        output = io.StringIO()
        with patch("sys.stdin.isatty", return_value=True), \
             patch("getpass.getpass", return_value=secret), \
             contextlib.redirect_stdout(output):
            self.assertEqual(app.main([]), 0)
        self.assertNotIn(secret, output.getvalue())

    def test_insecure_terminal_fails_closed(self):
        with patch("sys.stdin.isatty", return_value=True), \
             patch("getpass.getpass", side_effect=app.getpass.GetPassWarning("No hidden input")), \
             contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(app.main([]), 2)

    def test_demo(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(app.main(["--demo"]), 0)
        self.assertIn("Rejected:", output.getvalue())


if __name__ == "__main__":
    unittest.main()
