import sys
from votemapbf3.bf3string import width, ljust, center, rjust

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class Test_padright(unittest.TestCase):

    def test_ljust(self):
        self.assertAlmostEqual(50, width(ljust('<[({ hello world ! })]>', 50)), delta=2)
        self.assertAlmostEqual(50, width(ljust('               ', 50)), delta=2)
        self.assertAlmostEqual(50, width(ljust('fqs 654651 sq1fqs ]@ /o', 50)), delta=2)

    def test_center(self):
        self.assertAlmostEqual(50, width(center('<[({ hello world ! })]>', 50)), delta=2)
        self.assertAlmostEqual(50, width(center('               ', 50)), delta=2)
        self.assertAlmostEqual(50, width(center('fqs 654651 sq1fqs ]@ /o', 50)), delta=2)

    def test_rjust(self):
        self.assertAlmostEqual(50, width(rjust('<[({ hello world ! })]>', 50)), delta=2)
        self.assertAlmostEqual(50, width(rjust('               ', 50)), delta=2)
        self.assertAlmostEqual(50, width(rjust('fqs 654651 sq1fqs ]@ /o', 50)), delta=2)

    @unittest.skipUnless(__name__ == '__main__', "test requiring human verification")
    def test_in_game(self):
        print """admin.say "%s | %s" all """ % (ljust('<[({ hello world ! })]>', 48), ljust('<[({ hello world ! })]>', 48))
        print """admin.say "%s | %s" all """ % (center('<[({ hello world ! })]>', 48), center('<[({ hello world ! })]>', 48))
        print """admin.say "%s | %s" all """ % (rjust('<[({ hello world ! })]>', 48), rjust('<[({ hello world ! })]>', 48))

if __name__ == '__main__':
    unittest.main()