import os
import re
import unittest
from unittest.mock import patch

from gooey.gui.processor import ProcessController


class TestProcessor(unittest.TestCase):

    def test_extract_progress(self):
        # should pull out a number based on the supplied
        # regex and expression
        processor = ProcessController(r"^progress: (\d+)%$", None, False, 'utf-8')
        self.assertEqual(processor._extract_progress(b'progress: 50%'), 50)

        processor = ProcessController(r"total: (\d+)%$", None, False, 'utf-8')
        self.assertEqual(processor._extract_progress(b'my cool total: 100%'), 100)

    def test_extract_progress_returns_none_if_no_regex_supplied(self):
        processor = ProcessController(None, None, False, 'utf-8')
        self.assertIsNone(processor._extract_progress(b'Total progress: 100%'))


    def test_extract_progress_returns_none_if_no_match_found(self):
        processor = ProcessController(r'(\d+)%$', None, False, 'utf-8')
        self.assertIsNone(processor._extract_progress(b'No match in dis string'))


    def test_eval_progress(self):
        # given a match in the string, should eval the result
        regex = r'(\d+)/(\d+)$'
        processor = ProcessController(regex, r'x[0] / x[1]', False,False, 'utf-8')
        match = re.search(regex, '50/50')
        self.assertEqual(processor._eval_progress(match), 1.0)
    def test_eval_progress_returns_none_on_failure(self):
        # given a match in the string, should eval the result
        regex = r'(\d+)/(\d+)$'
        processor = ProcessController(regex, r'x[0] *^/* x[1]', False, False,'utf-8')
        match = re.search(regex, '50/50')
        self.assertIsNone(processor._eval_progress(match))

    def test_get_env_force_color(self):
        # Programs run under Gooey write to a pipe, so color libraries such as
        # colored 2.x emit no ANSI codes unless FORCE_COLOR is set. Gooey sets it
        # when the rich text console is enabled so it can render the colors.
        testcases = [
            # C1: Rich text console is disabled.
            # Expected: FORCE_COLOR is not set.
            (False, {}, None),
            # C2: Rich text console is enabled.
            # Expected: FORCE_COLOR is set to '1'.
            (True, {}, '1'),
            # C3: Rich text console is enabled and the user already set FORCE_COLOR.
            # Expected: The user's FORCE_COLOR value is kept.
            (True, {'FORCE_COLOR': '0'}, '0'),
        ]
        for input_richtext, input_environment, expected_force_color in testcases:
            with self.subTest(richtext=input_richtext, environment=input_environment):
                with patch.dict(os.environ, input_environment):
                    if 'FORCE_COLOR' not in input_environment:
                        os.environ.pop('FORCE_COLOR', None)
                    processor = ProcessController(None, None, False, 'utf-8', richtext=input_richtext)
                    actual_force_color = processor._get_env().get('FORCE_COLOR')
                self.assertEqual(actual_force_color, expected_force_color)
