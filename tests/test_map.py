import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from mock import patch
from votemapbf3.map import get_n_next_maps, get_n_random_maps

available_maps = [
        {'name': 'mapA', 'gamemode': 'modeA', 'num_of_rounds': 0},
        {'name': 'mapB', 'gamemode': 'modeB', 'num_of_rounds': 1},
        {'name': 'mapC', 'gamemode': 'modeC', 'num_of_rounds': 2},
        {'name': 'mapD', 'gamemode': 'modeD', 'num_of_rounds': 3},
        {'name': 'mapB', 'gamemode': 'modeB', 'num_of_rounds': 1},
        {'name': 'mapE', 'gamemode': 'modeE', 'num_of_rounds': 5},
        {'name': 'mapC', 'gamemode': 'modeC', 'num_of_rounds': 2},
]

class commonTestsMixin(object):
    
    def assertStrategy(self, expected_indices, n, current_indice, ignored_indices=list()):
        expected_maps = []
        for i in expected_indices:
            expected_maps.append(available_maps[i])
        current_map = available_maps[current_indice]
        ignored_maps = []
        for i in ignored_indices:
            ignored_maps.append(available_maps[i])
        self.assertListEqual(expected_maps, self.__class__.sut_func(available_maps, n, current_map, ignored_maps))

    
    def test_n0(self):
        self.assertStrategy([], 0, 0)
        self.assertStrategy([], 0, current_indice=0, ignored_indices=[])
        self.assertStrategy([], 0, current_indice=0, ignored_indices=[1, 2])

    def test_n1(self):
        self.assertStrategy([1], 1, current_indice=0)
        self.assertStrategy([1], 1, current_indice=0, ignored_indices=[])
        self.assertStrategy([3], 1, current_indice=0, ignored_indices=[1, 2])

        self.assertStrategy([2], 1, current_indice=1)
        self.assertStrategy([2], 1, current_indice=1, ignored_indices=[])
        self.assertStrategy([3], 1, current_indice=1, ignored_indices=[1, 2])

        self.assertStrategy([3], 1, current_indice=2)
        self.assertStrategy([3], 1, current_indice=2, ignored_indices=[])
        self.assertStrategy([3], 1, current_indice=2, ignored_indices=[1, 2])

        self.assertStrategy([1], 1, current_indice=3)
        self.assertStrategy([1], 1, current_indice=3, ignored_indices=[])
        self.assertStrategy([5], 1, current_indice=3, ignored_indices=[1, 2])

        self.assertStrategy([2], 1, current_indice=5)
        self.assertStrategy([2], 1, current_indice=5, ignored_indices=[])
        self.assertStrategy([0], 1, current_indice=5, ignored_indices=[1, 2])


    def test_n3(self):
        self.assertStrategy([1, 2, 3], 3, current_indice=0)
        self.assertStrategy([3, 5, 0], 3, current_indice=0, ignored_indices=[1, 2])

        self.assertStrategy([2, 3, 4], 3, current_indice=1)
        self.assertStrategy([3, 5, 0], 3, current_indice=1, ignored_indices=[1, 2])

        self.assertStrategy([3, 4, 5], 3, current_indice=2)
        self.assertStrategy([3, 5, 0], 3, current_indice=2, ignored_indices=[1, 2])

        self.assertStrategy([1, 5, 2], 3, current_indice=3)
        self.assertStrategy([5, 0, 3], 3, current_indice=3, ignored_indices=[1, 2])

        self.assertStrategy([2, 3, 1], 3, current_indice=4)
        self.assertStrategy([3, 5, 0], 3, current_indice=4, ignored_indices=[1, 2])

        self.assertStrategy([2, 0, 1], 3, current_indice=5)
        self.assertStrategy([0, 3, 5], 3, current_indice=5, ignored_indices=[1, 2])





class Test_get_n_next_maps(commonTestsMixin, unittest.TestCase):
    @staticmethod
    def sut_func(*args, **kwargs):
        return get_n_next_maps(*args, **kwargs)


class Test_get_n_random_maps2(commonTestsMixin, unittest.TestCase):
    @staticmethod
    def sut_func(*args, **kwargs):
        return get_n_random_maps(*args, **kwargs)

    def setUp(self):
        self.shuffle_patcher = patch("votemapbf3.map.shuffle")
        self.shuffle_mock = self.shuffle_patcher.start()

    def tearDown(self):
        self.assertTrue(self.shuffle_mock.called)
        self.shuffle_patcher.stop()


