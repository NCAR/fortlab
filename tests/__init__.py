import unittest
from pyloco.test import TestSuite

from .test_parse import test_classes as parse_tests


def fortlab_unittest_suite():

    loader = unittest.TestLoader()
    suite = TestSuite()

    all_tests = parse_tests

    for test_class in all_tests:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite
