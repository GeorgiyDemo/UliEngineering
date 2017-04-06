#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from numpy.testing import assert_approx_equal, assert_allclose, assert_array_equal
from nose.tools import assert_equal, assert_true, assert_false, raises, assert_less, assert_is_none, assert_raises, assert_is_instance
from UliEngineering.SignalProcessing.Utils import *
from nose_parameterized import parameterized
import concurrent.futures
import numpy as np
import datetime

unstairMethods = [
    ("left",),
    ("middle",),
    ("right",),
    ("reduce",),
]

class TestUnstair(object):
    @parameterized(unstairMethods)
    def testNoReduction(self, method):
        # Test if unstair returns the original array for a non-step function
        x = np.arange(10)
        y = np.square(x)
        xres, yres = unstair(x, y, method=method)
        assert_array_equal(xres, x)
        assert_array_equal(yres, y)

    def testSimpleLeft(self):
        y = np.asarray([0, 0, 0, 1, 2, 2, 2, 3, 4, 5, 5])
        x = np.arange(y.size)
        xexpected = [0, 3, 4, 7, 8, 9, 10]
        yexpected = y[xexpected]
        xres, yres = unstair(x, y, method="left")
        assert_array_equal(xres, xexpected)
        assert_array_equal(yres, yexpected)

    def testSimpleRight(self):
        y = np.asarray([0, 0, 0, 1, 2, 2, 2, 3, 4, 5, 5])
        x = np.arange(y.size)
        xexpected = [0, 2, 3, 6, 7, 8, 10]
        yexpected = y[xexpected]
        xres, yres = unstair(x, y, method="right")
        assert_array_equal(xres, xexpected)
        assert_array_equal(yres, yexpected)

    def testSimpleMiddle(self):
        y = np.asarray([0, 0, 0, 1, 2, 2, 2, 3, 4, 5, 5])
        x = np.arange(y.size)
        xexpected = [0, 1, 3, 5, 7, 8, 10]
        yexpected = y[xexpected]
        xres, yres = unstair(x, y, method="middle")
        assert_array_equal(xres, xexpected)
        assert_array_equal(yres, yexpected)

    def testSimpleReduce(self):
        y = np.asarray([0, 0, 0, 1, 2, 2, 2, 3, 4, 5, 5])
        x = np.arange(y.size)
        xexpected = [0, 2, 3, 4, 6, 7, 8, 9, 10]
        yexpected = y[xexpected]
        xres, yres = unstair(x, y, method="reduce")
        assert_array_equal(xres, xexpected)
        assert_array_equal(yres, yexpected)

    @parameterized(unstairMethods)
    def testSine(self, method):
        # Test with a rounded sine function. Data should be reduced
        sx = np.arange(1000) * .02
        rsine = np.round(np.sin(sx) * 10.) / 10.
        rx, ry = unstair(sx, rsine, method=method)
        assert_less(rx.size, sx.size)
        assert_less(ry.size, rsine.size)

class TestOptimumPolyfit(object):
    def testBasic(self):
        x = np.linspace(-100., 100., 10000)
        y = np.square(x)
        poly, deg, score = optimum_polyfit(x, y)
        assert_less(score, 1e-10)
        assert_equal(np.max(np.abs(y - poly(x))), score)

    def testRandom(self):
        x = np.linspace(-100., 100., 1000)
        y = np.random.random(x.size)
        poly, deg, score = optimum_polyfit(x, y)


class TestLinSpace(object):
    @parameterized([
        (0.0, 100.0, 101, True),
        (0.0, 100.0, 202, True),
        (0.0, 100.0, 735, True),
        (0.0, 200.0, 101, True),
        (12.5, 202.3, 101, True),
        (0.0, 100.0, 101, False),
        (0.0, 100.0, 202, False),
        (0.0, 100.0, 735, False),
        (0.0, 200.0, 101, False),
        (12.5, 202.3, 101, False),
    ])
    def testBasic(self, start, end, n, endpoint):
        params = (start, end, n)
        spc = LinRange(*params, endpoint=endpoint)
        linspc = np.linspace(*params, endpoint=endpoint)
        assert_equal(len(spc), params[2])
        assert_equal(len(spc), linspc.size)
        assert_equal((len(spc),), linspc.shape)
        assert_allclose(spc[:], linspc)
        # Test some slice
        istart, iend = len(spc) // 3, len(spc) // 2
        assert_allclose(spc[istart:iend], linspc[istart:iend])
        # Test negative indices
        assert_allclose(spc[-istart], linspc[-istart])
        # Test mid
        assert_equal(spc.mid, (start + end) / 2.)
        # Test view
        assert_allclose(spc.view(0, None).size, linspc.size)
        assert_allclose(spc.view(0, None)[:], linspc)

    def test_equal(self):
        l1 = LinRange(0., 100., 100, endpoint=False)
        l2 = LinRange(0., 100., 100, endpoint=False)
        l3 = LinRange(0., 100., 100, endpoint=True)
        assert_true(l1 == l2)
        assert_true(l2 == l1)
        assert_false(l3 == l1)
        assert_false(l3 == l2)

    def test_repr(self):
        l = LinRange(0., 100., 100, endpoint=False)
        assert_equal("LinRange(0.0, 100.0, 1.0)", str(l))
        l = LinRange(0., 100., 100, endpoint=False, dtype=np.int)
        assert_equal("LinRange(0.0, 100.0, 1.0, dtype=int)", str(l))

    def testDtype(self):
        lin1 = LinRange(0.0, 100.0, 101)
        assert_is_instance(lin1, LinRange)
        assert_is_instance(lin1.view(0, 5), LinRange)
