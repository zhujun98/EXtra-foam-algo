import unittest
import pytest
from queue import Empty, Full
from threading import Thread

import numpy as np

from pyfoamalgo import (
    OrderedSet, Stack,
    SimpleSequence, SimpleVectorSequence, SimplePairSequence, OneWayAccuPairSequence,
    SimpleQueue,
)
from pyfoamalgo.data_structures import _StatDataItem
from pyfoamalgo import MovingAverageArray, MovingAverageScalar


class TestDataStructures(unittest.TestCase):
    def testStack(self):
        stack = Stack()

        self.assertTrue(stack.empty())
        stack.push(4)
        stack.push(6)
        stack.push(8)
        self.assertFalse(stack.empty())
        self.assertEqual(3, len(stack))
        self.assertEqual(8, stack.top())
        self.assertEqual(8, stack.pop())
        self.assertEqual(2, len(stack))
        self.assertEqual(6, stack.pop())
        stack.push(1)
        self.assertEqual(1, stack.pop())
        self.assertEqual(4, stack.top())
        self.assertEqual(4, stack.pop())
        self.assertTrue(stack.empty())

        with self.assertRaises(IndexError):
            stack.pop()
        with self.assertRaises(IndexError):
            stack.top()

    def testOrderedSet(self):
        x = OrderedSet([1, 3, 0])
        self.assertEqual('OrderedSet([1, 3, 0])', repr(x))
        x.add(0)  # add an existing item
        x.add(100)
        x.add('A')

        self.assertIn(1, x)
        self.assertEqual(5, len(x))
        self.assertListEqual([1, 3, 0, 100, 'A'], list(x))

        # delete a non-existing item
        x.discard(4)
        self.assertListEqual([1, 3, 0, 100, 'A'], list(x))

        # delete an existing item
        x.discard(3)
        self.assertListEqual([1, 0, 100, 'A'], list(x))

        # test 'remove' mixin method
        with self.assertRaises(KeyError):
            x.remove('B')
        x.remove(100)

        self.assertEqual(1, x.pop())
        self.assertEqual(0, x.pop())
        self.assertListEqual(['A'], list(x))
        x.clear()
        self.assertEqual(0, len(x))

        # test comparison

        x.add(1)
        x.add(2)

        y = set()
        y.add(1)
        y.add(2)

        # compare with a normal Set
        self.assertEqual(y, x)

        # TODO: more


class TestSequenceData(unittest.TestCase):
    def testSimpleSequence(self):
        MAX_LENGTH = 100

        hist = SimpleSequence(max_len=MAX_LENGTH)
        self.assertEqual(0, len(hist))

        hist.append(3)
        hist.append(4)
        hist.extend([1, 2])
        ax = hist.data()
        np.testing.assert_array_almost_equal([3, 4, 1, 2], ax)

        # test Sequence protocol
        self.assertEqual(3, hist[0])
        self.assertEqual(2, hist[-1])
        with self.assertRaises(IndexError):
            hist[4]
        self.assertEqual(4, len(hist))

        # more test on extend
        hist.extend([3] * (MAX_LENGTH - 2))
        np.testing.assert_array_almost_equal([1, 2] + [3] * (MAX_LENGTH - 2), hist.data())
        self.assertEqual(100, len(hist))

        # test reset
        hist.reset()
        np.testing.assert_array_almost_equal([], hist.data())

        # ----------------------------
        # test when max length reached
        # ----------------------------

        overflow = 10
        for i in range(MAX_LENGTH + overflow):
            hist.append(i)
        ax = hist.data()
        self.assertEqual(MAX_LENGTH, len(ax))
        self.assertEqual(overflow, ax[0])
        self.assertEqual(MAX_LENGTH + overflow - 1, ax[-1])

        # ----------------------------
        # test when capacity reached
        # ----------------------------
        for i in range(MAX_LENGTH):
            hist.append(i)
        ax = hist.data()
        self.assertEqual(MAX_LENGTH, len(ax))
        self.assertEqual(0, ax[0])
        self.assertEqual(MAX_LENGTH - 1, ax[-1])

        # ----------------------------
        # test constructing from array
        # ----------------------------
        hist = SimpleSequence.from_array([1, 2, 3])
        self.assertEqual(3, len(hist))

    def testSimpleVectorSequence(self):
        MAX_LENGTH = 100

        hist = SimpleVectorSequence(2, max_len=MAX_LENGTH)
        self.assertEqual(0, len(hist))
        self.assertTrue(hist.data().flags['C_CONTIGUOUS'])
        hist = SimpleVectorSequence(2, max_len=MAX_LENGTH, order='F')
        self.assertTrue(hist.data().flags['F_CONTIGUOUS'])

        with self.assertRaises(TypeError):
            hist.append(3)

        with self.assertRaises(TypeError):
            hist.append(None)

        with self.assertRaises(ValueError):
            hist.append(np.array([[1, 2], [3, 4]]))

        hist.append([3, 4])
        hist.append(np.array([1, 2]))
        ax = hist.data()
        np.testing.assert_array_almost_equal([[3, 4], [1, 2]], ax)

        # test Sequence protocol
        np.testing.assert_array_almost_equal([3, 4], hist[0])
        np.testing.assert_array_almost_equal([1, 2], hist[-1])
        with self.assertRaises(IndexError):
            hist[4]
        self.assertEqual(2, len(hist))

        # test reset
        hist.reset()
        self.assertEqual(0, len(hist.data()))

        # ----------------------------
        # test when max length reached
        # ----------------------------

        overflow = 10
        for i in range(MAX_LENGTH + overflow):
            hist.append([i, i])
        ax = hist.data()
        self.assertEqual(MAX_LENGTH, len(ax))
        np.testing.assert_array_almost_equal([overflow, overflow], ax[0])
        np.testing.assert_array_almost_equal([MAX_LENGTH + overflow - 1,
                                              MAX_LENGTH + overflow - 1], ax[-1])

        # ----------------------------
        # test when capacity reached
        # ----------------------------
        for i in range(MAX_LENGTH):
            hist.append([i, i])
        ax = hist.data()
        self.assertEqual(MAX_LENGTH, len(ax))
        np.testing.assert_array_almost_equal([0, 0], ax[0])
        np.testing.assert_array_almost_equal([MAX_LENGTH - 1, MAX_LENGTH - 1], ax[-1])

        # ----------------------------
        # test constructing from array
        # ----------------------------
        with self.assertRaises(ValueError):
            SimpleVectorSequence.from_array([[1, 2, 3], [2, 3], [3, 4]], 2)

        hist = SimpleVectorSequence.from_array([[1, 2], [2, 3], [3, 4]], 2)
        self.assertEqual(3, len(hist))

    def testSimplePairSequence(self):
        MAX_LENGTH = 100

        hist = SimplePairSequence(max_len=MAX_LENGTH)
        self.assertEqual(0, len(hist))

        hist.append((3, 200))
        hist.append((4, 220))
        ax, ay = hist.data()
        np.testing.assert_array_almost_equal([3, 4], ax)
        np.testing.assert_array_almost_equal([200, 220], ay)

        # test Sequence protocol
        self.assertTupleEqual((3, 200), hist[0])
        self.assertTupleEqual((4, 220), hist[-1])
        with self.assertRaises(IndexError):
            hist[2]
        self.assertEqual(2, len(hist))

        # test reset
        hist.reset()
        ax, ay = hist.data()
        np.testing.assert_array_almost_equal([], ax)
        np.testing.assert_array_almost_equal([], ay)

        # ----------------------------
        # test when max length reached
        # ----------------------------

        overflow = 10
        for i in range(MAX_LENGTH + overflow):
            hist.append((i, i))
        ax, ay = hist.data()
        self.assertEqual(MAX_LENGTH, len(ax))
        self.assertEqual(MAX_LENGTH, len(ay))
        self.assertEqual(overflow, ax[0])
        self.assertEqual(overflow, ay[0])
        self.assertEqual(MAX_LENGTH + overflow - 1, ax[-1])
        self.assertEqual(MAX_LENGTH + overflow - 1, ay[-1])

        # ----------------------------
        # test when capacity reached
        # ----------------------------
        for i in range(MAX_LENGTH):
            hist.append((i, i))
        ax, ay = hist.data()
        self.assertEqual(MAX_LENGTH, len(ax))
        self.assertEqual(MAX_LENGTH, len(ay))
        self.assertEqual(0, ax[0])
        self.assertEqual(0, ay[0])
        self.assertEqual(MAX_LENGTH - 1, ax[-1])
        self.assertEqual(MAX_LENGTH - 1, ay[-1])

        # ----------------------------
        # test constructing from array
        # ----------------------------

        with self.assertRaises(ValueError):
            SimplePairSequence.from_array([], [1, 2])

        hist = SimplePairSequence.from_array([0, 1, 2], [1, 2, 3])
        self.assertEqual(3, len(hist))

    def testOneWayAccuPairSequence(self):
        MAX_LENGTH = 100

        # resolution is missing
        with self.assertRaises(TypeError):
            OneWayAccuPairSequence()
        # resolution == 0
        with self.assertRaises(ValueError):
            OneWayAccuPairSequence(0.0)
        # resolution < 0
        with self.assertRaises(ValueError):
            OneWayAccuPairSequence(-1)

        hist = OneWayAccuPairSequence(0.1, max_len=MAX_LENGTH, min_count=2)
        self.assertEqual(0, len(hist))

        for _ in range(2):
            # test reset
            hist.reset()

            # first data
            self.assertTrue(hist.append_dry(1))
            hist.append((1, 0.3))
            self.assertEqual(0, len(hist))

            # distance between two adjacent data > resolution
            self.assertTrue(hist.append_dry(2))
            hist.append((2, 0.4))
            self.assertEqual(0, len(hist))
            ax, ay = hist.data()
            np.testing.assert_array_equal([], ax)
            np.testing.assert_array_equal([], ay.avg)
            np.testing.assert_array_equal([], ay.min)
            np.testing.assert_array_equal([], ay.max)
            np.testing.assert_array_equal([], ay.count)

            # new data within resolution
            self.assertFalse(hist.append_dry(2.02))
            hist.append((2.02, 0.5))
            self.assertEqual(1, len(hist))
            ax, ay = hist.data()
            np.testing.assert_array_equal([2.01], ax)
            np.testing.assert_array_equal([0.45], ay.avg)
            np.testing.assert_array_almost_equal([0.425], ay.min)
            np.testing.assert_array_almost_equal([0.475], ay.max)
            np.testing.assert_array_equal([2], ay.count)

            # new data within resolution
            self.assertFalse(hist.append_dry(2.10))
            hist.append((2.10, 0.6))
            self.assertEqual(1, len(hist))
            ax, ay = hist.data()
            np.testing.assert_array_equal([2.04], ax)
            np.testing.assert_array_equal([0.5], ay.avg)
            np.testing.assert_array_almost_equal([0.4591751709536137], ay.min)
            np.testing.assert_array_almost_equal([0.5408248290463863], ay.max)
            np.testing.assert_array_equal([3], ay.count)

            # new point outside resolution
            self.assertTrue(hist.append_dry(2.31))
            hist.append((2.31, 1))
            self.assertFalse(hist.append_dry(2.40))
            hist.append((2.40, 2))
            self.assertEqual(2, len(hist))
            ax, ay = hist.data()
            np.testing.assert_array_equal([0.5, 1.5], ay.avg)
            np.testing.assert_array_almost_equal([0.4591751709536137, 1.25], ay.min)
            np.testing.assert_array_almost_equal([0.5408248290463863, 1.75], ay.max)
            np.testing.assert_array_equal([3, 2], ay.count)

            # test Sequence protocol
            x, y = hist[0]
            self.assertAlmostEqual(2.04, x)
            self.assertEqual(_StatDataItem(0.5, 0.4591751709536137, 0.5408248290463863, 3), y)
            x, y = hist[-1]
            self.assertAlmostEqual(2.355, x)
            self.assertEqual(_StatDataItem(1.5, 1.25, 1.75, 2), y)
            with self.assertRaises(IndexError):
                hist[2]

        # ----------------------------
        # test when max length reached
        # ----------------------------
        hist.reset()
        overflow = 5
        for i in range(2 * MAX_LENGTH + 2 * overflow):
            # two adjacent data point will be grouped together since resolution is 0.1
            hist.append((0.09 * i, i))
        ax, ay = hist.data()
        self.assertEqual(MAX_LENGTH, len(ax))
        self.assertEqual(MAX_LENGTH, len(ay.count))
        self.assertEqual(MAX_LENGTH, len(ay.avg))
        self.assertAlmostEqual(0.18 * overflow + 0.09 * 0.5, ax[0])
        self.assertAlmostEqual(2 * overflow + 0.5, ay.avg[0])
        self.assertAlmostEqual(0.18 * (MAX_LENGTH + overflow - 1) + 0.09 * 0.5, ax[-1])
        self.assertAlmostEqual(2 * (MAX_LENGTH + overflow - 1) + 0.5, ay.avg[-1])

        # ----------------------------
        # test when capacity reached
        # ----------------------------
        for i in range(2 * MAX_LENGTH):
            # two adjacent data point will be grouped together since resolution is 0.1
            hist.append((0.09 * i, i))
        ax, ay = hist.data()
        self.assertEqual(MAX_LENGTH, len(ax))
        self.assertEqual(MAX_LENGTH, len(ay.count))
        self.assertEqual(MAX_LENGTH, len(ay.avg))
        self.assertAlmostEqual(0.09 * 0.5, ax[0])
        self.assertAlmostEqual(0.5, ay.avg[0])
        self.assertAlmostEqual(0.18 * (MAX_LENGTH - 1) + 0.09 * 0.5, ax[-1])
        self.assertAlmostEqual(2 * (MAX_LENGTH - 1) + 0.5, ay.avg[-1])

        # ----------------------------
        # test constructing from array
        # ----------------------------

        with self.assertRaises(ValueError):
            OneWayAccuPairSequence.from_array([], [1, 2])

        hist = OneWayAccuPairSequence.from_array([0, 0.9, 1.8], [1, 2, 3], resolution=1)
        self.assertEqual(1, len(hist))

    def testOneWayAccuPairSequence2(self):
        MAX_LENGTH = 100
        min_count = 20

        hist = OneWayAccuPairSequence(0.1, max_len=MAX_LENGTH, min_count=min_count)

        for i in range(min_count):
            hist.append((0.001 * i, i))
            if i == min_count - 1:
                self.assertEqual(1, len(hist))
            else:
                self.assertEqual(0, len(hist))

        for i in range(min_count - 1):
            hist.append((1 + 0.001 * i, i))
            self.assertEqual(1, len(hist))

        for i in range(min_count):
            hist.append((2 + 0.001 * i, i))
            if i == min_count - 1:
                self.assertEqual(2, len(hist))
            else:
                self.assertEqual(1, len(hist))


class TestMovingAverageScalar(unittest.TestCase):
    def testGeneral(self):
        class Dummy:
            data = MovingAverageScalar()

        dm = Dummy()

        dm.data = 1.0
        self.assertEqual(1, Dummy.data.window)
        self.assertEqual(1.0, dm.data)

        Dummy.data.window = 5
        self.assertEqual(5, Dummy.data.window)
        self.assertEqual(1, Dummy.data.count)
        dm.data = 2.0
        self.assertEqual(5, Dummy.data.window)
        self.assertEqual(2, Dummy.data.count)
        self.assertEqual(1.5, dm.data)
        dm.data = 3.0
        self.assertEqual(5, Dummy.data.window)
        self.assertEqual(3, Dummy.data.count)
        self.assertEqual(2.0, dm.data)

        # set a ma window which is smaller than the current window
        Dummy.data.window = 3
        self.assertEqual(3, Dummy.data.window)
        self.assertEqual(3, Dummy.data.count)
        self.assertEqual(2.0, dm.data)

        del dm.data
        self.assertIsNone(dm.data)
        self.assertEqual(3, Dummy.data.window)
        self.assertEqual(0, Dummy.data.count)

        dm.data = 1.0
        self.assertEqual(1.0, dm.data)
        dm.data = None
        self.assertIsNone(dm.data)
        self.assertEqual(3, Dummy.data.window)
        self.assertEqual(0, Dummy.data.count)


class TestMovingAverageArray:
    @pytest.mark.parametrize("n_dims", [1, 2, 3])
    def testArray(self, n_dims):
        class Dummy:
            data = MovingAverageArray()

        dm = Dummy()

        if n_dims == 1:
            arr_gt = np.array([1, np.nan, 3], dtype=np.float32)
        elif n_dims == 2:
            arr_gt = np.ones((3, 3), dtype=np.float32)
            arr_gt[0][2] = np.nan
        else:  # n_dims == 3
            arr_gt = np.ones((3, 4, 4), dtype=np.float32)
            arr_gt[1][2][1] = np.nan

        dm.data = arr_gt.copy()
        assert Dummy.data.window == 1

        Dummy.data.window = 5
        assert Dummy.data.window == 5
        assert Dummy.data.count == 1
        dm.data = 2. * arr_gt.copy()
        assert Dummy.data.window == 5
        assert Dummy.data.count == 2
        np.testing.assert_array_equal(1.5 * arr_gt, dm.data)

        # set a ma window which is smaller than the current window
        Dummy.data.window = 3
        assert Dummy.data.window == 3
        assert Dummy.data.count == 2
        np.testing.assert_array_equal(1.5 * arr_gt, dm.data)

        # set an array with a different shape
        if n_dims == 1:
            new_arr = 3 * np.ones(6, dtype=np.float32)
        elif n_dims == 2:
            new_arr = 3 * np.ones((5, 5), dtype=np.float32)
        else:  # n_dims == 3
            new_arr = 3 * np.ones((5, 4, 4), dtype=np.float32)

        dm.data = new_arr
        assert Dummy.data.window == 3
        assert Dummy.data.count == 1
        np.testing.assert_array_equal(new_arr, dm.data)

        del dm.data
        assert dm.data is None
        assert Dummy.data.window == 3
        assert Dummy.data.count == 0

        dm.data = new_arr.copy()
        np.testing.assert_array_equal(new_arr, dm.data)
        dm.data = None
        assert dm.data is None
        assert Dummy.data.window == 3
        assert Dummy.data.count == 0

    def testCopyFirst(self):
        class Dummy:
            data = MovingAverageArray(copy_first=True)

        dm = Dummy()

        arr = np.ones((3, 4, 4), dtype=np.float32)
        dm.data = arr
        assert dm.data is not arr


class TestSimpleQueue(unittest.TestCase):
    def testGeneral(self):
        queue = SimpleQueue(maxsize=2)
        self.assertTrue(queue.empty())
        queue.put(1)
        queue.put(2)
        with self.assertRaises(Full):
            queue.put(3)
        self.assertTrue(queue.full())
        self.assertEqual(2, queue.qsize())
        self.assertEqual(1, queue.get())
        self.assertEqual(2, queue.get())
        with self.assertRaises(Empty):
            queue.get()
        self.assertTrue(queue.empty())

        # test no maxsize
        queue = SimpleQueue()
        for i in range(100):
            queue.put(i)
        self.assertEqual(100, queue.qsize())
        self.assertFalse(queue.full())
        queue.clear()
        self.assertTrue(queue.empty())

    def testMultiThreads(self):
        def worker1(queue):
            for i in range(100):
                queue.put(i)

        def worker2(queue):
            for _ in range(100):
                queue.get()

        queue = SimpleQueue()
        t1 = Thread(target=worker1, args=(queue,))
        t2 = Thread(target=worker2, args=(queue,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertTrue(queue.empty())
