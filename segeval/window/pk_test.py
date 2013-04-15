'''
Tests the WindowDiff evaluation metric.

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
'''
import unittest
from decimal import Decimal
from ..utils import AlmostTestCase
from ..window.pk import pk, pairwise_pk
from ..data.samples import (KAZANTSEVA2012_G5, KAZANTSEVA2012_G2, 
    COMPLETE_AGREEMENT, LARGE_DISAGREEMENT)


class TestPk(unittest.TestCase):
    '''
    Test Pk.
    '''
    # pylint: disable=R0904

    def test_identical(self):
        '''
        Test whether identical segmentations produce 0.0.
        '''
        # pylint: disable=C0324,C0103
        a = [1,1,1,1,1,2,2,2,3,3,3,3,3]
        b = [1,1,1,1,1,2,2,2,3,3,3,3,3]
        self.assertEqual(pk(a, b), 0.0)
        self.assertEqual(pk(a, b, one_minus=True), 1.0)

    def test_no_boundaries(self):
        '''
        Test whether no segments versus some segments produce 1.0.
        '''
        # pylint: disable=C0324,C0103
        a = [1,1,1,1,1,1,1,1,1,1,1,1,1]
        b = [1,1,1,1,2,2,2,2,3,3,3,3,3]
        self.assertEqual(pk(b, a),
                         Decimal('1.0'))
        self.assertEqual(pk(a, b),
                         Decimal('0.3636363636363636363636363636'))

    def test_all_boundaries(self):
        '''
        Test whether all segments versus some segments produces 7/11 = 0.636
        erroneous windows.
        '''
        # pylint: disable=C0324,C0103
        a = [1,2,3,4,5,6,7,8,9,10,11,12,13]
        b = [1,1,1,1,2,2,2,2,3,3,3,3,3]
        self.assertEqual(pk(a, b),
                         Decimal('0.6363636363636363636363636364'))
        self.assertEqual(pk(b, a),
                         Decimal('0.8333333333333333333333333333'))

    def test_all_and_no_boundaries(self):
        '''
        Test whether all segments versus no segments produces 1.0.
        '''
        # pylint: disable=C0324,C0103
        a = [1,2,3,4,5,6,7,8,9,10,11,12,13]
        b = [1,1,1,1,1,1,1,1,1,1,1,1,1]
        self.assertEqual(pk(a, b), 1.0)
        self.assertEqual(pk(b, a), 1.0)

    def test_translated_boundary(self):
        '''
        Test whether 2/3 total segments participate in mis-alignment produces
        0.182.
        '''
        # pylint: disable=C0324,C0103
        a = [1,1,1,1,1,2,2,2,3,3,3,3,3]
        b = [1,1,1,1,2,2,2,2,3,3,3,3,3]
        self.assertEqual(pk(a, b),
                         Decimal('0.1818181818181818181818181818'))
        self.assertEqual(pk(b, a),
                         Decimal('0.1818181818181818181818181818'))
    
    def test_extra_boundary(self):
        '''
        Test whether 1/3 segments that are non-existent produces 0.091.
        '''
        # pylint: disable=C0324,C0103
        a = [1,1,1,1,1,2,2,2,3,3,3,3,3]
        b = [1,1,1,1,1,2,3,3,4,4,4,4,4]
        self.assertEqual(pk(a, b),
                         Decimal('0.09090909090909090909090909091'))
        self.assertEqual(pk(b, a),
                         Decimal('0.09090909090909090909090909091'))
    
    def test_full_miss_and_misaligned(self):
        '''
        Test whether a full miss and a translated boundary out of 4 produces
        0.273. 
        '''
        # pylint: disable=C0324,C0103
        a = [1,1,1,1,2,2,2,2,3,3,3,3,3]
        b = [1,1,1,1,1,2,3,3,4,4,4,4,4]
        self.assertEqual(pk(a, b),
                         Decimal('0.2727272727272727272727272727'))
        self.assertEqual(pk(b, a),
                         Decimal('0.2727272727272727272727272727'))


class TestPairwisePkMeasure(AlmostTestCase):
    # pylint: disable=R0904,E1101,W0232
    '''
    Test pairwise Pk.
    '''
    
    def test_kazantseva2012_g5(self):
        '''
        Calculate permuted pairwise Pk on Group 5 from the dataset
        collected in [KazantsevaSzpakowicz2012]_.
        '''
        self.assertAlmostEquals(pairwise_pk(KAZANTSEVA2012_G5,
                                     convert_from_masses=True),
                         (Decimal('0.3535644717128558192094873348'),
                          Decimal('0.1076460428373522560756592115'),
                          Decimal('0.01158767053854107695378913407'),
                          Decimal('0.01553736795233582786561405771'),
                          48))
    
    def test_kazantseva2012_g2(self):
        '''
        Calculate mean permuted pairwise Pk on Group 2 from the dataset
        collected in [KazantsevaSzpakowicz2012]_.
        '''
        self.assertAlmostEquals(pairwise_pk(KAZANTSEVA2012_G2,
                                     convert_from_masses=True),
                         (Decimal('0.2882256923776327507173609771'),
                          Decimal('0.1454395656787966169084191445'),
                          Decimal('0.02115266726483699483402909754'),
                          Decimal('0.01327675514600517730547602481'),
                          120))
    
    def test_large_disagreement(self):
        '''
        Calculate mean permuted pairwise Pk on a theoretical dataset
        containing large disagreement.
        '''
        self.assertAlmostEquals(pairwise_pk(LARGE_DISAGREEMENT,
                                     convert_from_masses=True),
                         (1.0,
                          0.0,
                          0.0,
                          0.0,
                          8))
    
    def test_complete_agreement(self):
        '''
        Calculate mean permuted pairwise Pk on a theoretical dataset
        containing complete agreement.
        '''
        self.assertAlmostEquals(pairwise_pk(COMPLETE_AGREEMENT,
                                     convert_from_masses=True),
                         (0.0,
                          0.0,
                          0.0,
                          0.0,
                          48))
