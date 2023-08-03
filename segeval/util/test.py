from __future__ import absolute_import
import unittest
from decimal import Decimal
from segeval.util import SegmentationMetricError, __fnc_metric__


class TestCase(unittest.TestCase):

    '''
    A test case that supports performing assertAlmostEquals upon lists, tuples,
    or dicts of values.
    '''

    DECIMAL_PLACES = 4

    def assertEqualSet(self, first, second):
        '''
        Convert the arguments into a list of sets.
        '''
        return self.assertEqual([set(position) for position in first],
                                [set(position) for position in second])

    def assertAlmostEquals(self, first, second, places=DECIMAL_PLACES,
                           msg=None):
        '''
        Automatically converts values to floats.
        '''

        if isinstance(first, dict) and isinstance(second, dict):
            for item in set(list(first.keys()) + list(second.keys())):
                if not msg:
                    msg = '{0} != {1}'.format(first, second)
                if item not in first:
                    raise Exception(
                        '{0} not in {1}; expected {2}'.format(item, first,
                                                              second))
                if item not in second:
                    raise Exception(
                        '{0} not in {1}; expected {2}'.format(item, second,
                                                              first))
                self.assertAlmostEquals(first[item], second[item], places, msg)
        elif (isinstance(first, list) or isinstance(first, tuple)) and \
                (isinstance(second, list) or isinstance(second, tuple)):
            if len(first) != len(second):
                raise Exception(
                    'Size mismatch; {0} != {1}'.format(first, second))
            for item in zip(first, second):
                if not msg:
                    msg = '{0} != {1}'.format(first, second)
                self.assertAlmostEquals(item[0], item[1], places, msg)
        elif not isinstance(first, type(second)):
            if not isinstance(first, float) and not isinstance(first, Decimal) and \
                    not isinstance(second, float) and not isinstance(second, Decimal):
                raise Exception('Type mismatch; {0} != {1}'.format(
                    type(first), type(second)))
        else:
            return unittest.TestCase.assertAlmostEquals(self,
                                                        float(first),
                                                        float(second),
                                                        places=places,
                                                        msg=msg)
