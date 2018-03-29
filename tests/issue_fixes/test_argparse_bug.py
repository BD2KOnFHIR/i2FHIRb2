import unittest

from argparse import ArgumentParser


class ArgparseBugTestCase(unittest.TestCase):
    """ ``file_aware_parser.decode_file_args`` depends on the fact that ArgumentParser will overwrite arguments
    if they appear more than once.  If this test ever fails, you need to fix decode_file_args

    """
    def test_1(self):
        parser = ArgumentParser()
        parser.add_argument("-u", "--ufield", type=int)
        opts = parser.parse_args("-u 123 -u 456 --ufield 789".split())
        self.assertEqual(789, opts.ufield)


if __name__ == '__main__':
    unittest.main()
