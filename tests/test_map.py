from unittest.case import skip
from mock import patch

import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from votemapbf3.map import get_n_next_maps, get_n_random_maps


available_maps = ['A', 'B', 'C', 'D', 'B', 'E']

class commonTestsMixin(object):
    
    def test_n0(self):
        self.assertListEqual([], self.__class__.sut_func(available_maps, n=0, current_indice=0))
        self.assertListEqual([], self.__class__.sut_func(available_maps, n=0, current_indice=0, ignored_indices=[]))
        self.assertListEqual([], self.__class__.sut_func(available_maps, n=0, current_indice=0, ignored_indices=[1, 2]))

    def test_n1(self):
        self.assertListEqual([1], self.__class__.sut_func(available_maps, n=1, current_indice=0))
        self.assertListEqual([1], self.__class__.sut_func(available_maps, n=1, current_indice=0, ignored_indices=[]))
        self.assertListEqual([3], self.__class__.sut_func(available_maps, n=1, current_indice=0, ignored_indices=[1, 2]))

        self.assertListEqual([2], self.__class__.sut_func(available_maps, n=1, current_indice=1))
        self.assertListEqual([2], self.__class__.sut_func(available_maps, n=1, current_indice=1, ignored_indices=[]))
        self.assertListEqual([3], self.__class__.sut_func(available_maps, n=1, current_indice=1, ignored_indices=[1, 2]))

        self.assertListEqual([3], self.__class__.sut_func(available_maps, n=1, current_indice=2))
        self.assertListEqual([3], self.__class__.sut_func(available_maps, n=1, current_indice=2, ignored_indices=[]))
        self.assertListEqual([3], self.__class__.sut_func(available_maps, n=1, current_indice=2, ignored_indices=[1, 2]))

        self.assertListEqual([4], self.__class__.sut_func(available_maps, n=1, current_indice=3))
        self.assertListEqual([4], self.__class__.sut_func(available_maps, n=1, current_indice=3, ignored_indices=[]))
        self.assertListEqual([4], self.__class__.sut_func(available_maps, n=1, current_indice=3, ignored_indices=[1, 2]))

        self.assertListEqual([5], self.__class__.sut_func(available_maps, n=1, current_indice=4))
        self.assertListEqual([5], self.__class__.sut_func(available_maps, n=1, current_indice=4, ignored_indices=[]))
        self.assertListEqual([5], self.__class__.sut_func(available_maps, n=1, current_indice=4, ignored_indices=[1, 2]))

        self.assertListEqual([0], self.__class__.sut_func(available_maps, n=1, current_indice=5))
        self.assertListEqual([0], self.__class__.sut_func(available_maps, n=1, current_indice=5, ignored_indices=[]))
        self.assertListEqual([0], self.__class__.sut_func(available_maps, n=1, current_indice=5, ignored_indices=[1, 2]))


    def test_n3(self):
        self.assertListEqual([1, 2, 3], self.__class__.sut_func(available_maps, n=3, current_indice=0))
        self.assertListEqual([3, 4, 5],
            self.__class__.sut_func(available_maps, n=3, current_indice=0, ignored_indices=[1, 2]))

        self.assertListEqual([2, 3, 4], self.__class__.sut_func(available_maps, n=3, current_indice=1))
        self.assertListEqual([3, 4, 5],
            self.__class__.sut_func(available_maps, n=3, current_indice=1, ignored_indices=[1, 2]))

        self.assertListEqual([3, 4, 5], self.__class__.sut_func(available_maps, n=3, current_indice=2))
        self.assertListEqual([3, 4, 5],
            self.__class__.sut_func(available_maps, n=3, current_indice=2, ignored_indices=[1, 2]))

        self.assertListEqual([4, 5, 0], self.__class__.sut_func(available_maps, n=3, current_indice=3))
        self.assertListEqual([4, 5, 0],
            self.__class__.sut_func(available_maps, n=3, current_indice=3, ignored_indices=[1, 2]))

        self.assertListEqual([5, 0, 1], self.__class__.sut_func(available_maps, n=3, current_indice=4))
        self.assertListEqual([5, 0, 3],
            self.__class__.sut_func(available_maps, n=3, current_indice=4, ignored_indices=[1, 2]))

        self.assertListEqual([0, 1, 2], self.__class__.sut_func(available_maps, n=3, current_indice=5))
        self.assertListEqual([0, 3, 4],
            self.__class__.sut_func(available_maps, n=3, current_indice=5, ignored_indices=[1, 2]))


    def test_n10(self):
        self.assertListEqual([1, 2, 3, 4, 5, 0], self.__class__.sut_func(available_maps, n=10, current_indice=0))
        self.assertListEqual([3, 4, 5, 0],
            self.__class__.sut_func(available_maps, n=10, current_indice=0, ignored_indices=[1, 2]))

        self.assertListEqual([2, 3, 4, 5, 0, 1], self.__class__.sut_func(available_maps, n=10, current_indice=1))
        self.assertListEqual([3, 4, 5, 0],
            self.__class__.sut_func(available_maps, n=10, current_indice=1, ignored_indices=[1, 2]))

        self.assertListEqual([3, 4, 5, 0, 1, 2], self.__class__.sut_func(available_maps, n=10, current_indice=2))
        self.assertListEqual([3, 4, 5, 0],
            self.__class__.sut_func(available_maps, n=10, current_indice=2, ignored_indices=[1, 2]))

        self.assertListEqual([4, 5, 0, 1, 2, 3], self.__class__.sut_func(available_maps, n=10, current_indice=3))
        self.assertListEqual([4, 5, 0, 3],
            self.__class__.sut_func(available_maps, n=10, current_indice=3, ignored_indices=[1, 2]))

        self.assertListEqual([5, 0, 1, 2, 3, 4], self.__class__.sut_func(available_maps, n=10, current_indice=4))
        self.assertListEqual([5, 0, 3, 4],
            self.__class__.sut_func(available_maps, n=10, current_indice=4, ignored_indices=[1, 2]))

        self.assertListEqual([0, 1, 2, 3, 4, 5], self.__class__.sut_func(available_maps, n=10, current_indice=5))
        self.assertListEqual([0, 3, 4, 5],
            self.__class__.sut_func(available_maps, n=10, current_indice=5, ignored_indices=[1, 2]))



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


