'''
Tests for the console commands provided by __main__.py

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
'''
#===============================================================================
# Copyright (c) 2012, Chris Fournier
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#       
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================
import os
import re
import unittest
from decimal import Decimal
from .__main__ import main
from . import DECIMAL_PLACES

class TestMain(unittest.TestCase):
    '''
    Test command line functions.
    '''
    # pylint: disable=R0904
    
    test_data_dir = os.path.join(os.path.split(__file__)[0], 'data')
    
    print_output = False
    test_help    = False
    
    REGEX_TEST_OUTPUT = re.compile('([^\s]+)\t= ([\-]?[0-1]{1}[\.]?[0-9]{0,})')

    
    @classmethod
    def extract_values(cls, text):
        '''
        Extracts ordered decimals from text.
        '''
        decimals = dict()
        matches = TestMain.REGEX_TEST_OUTPUT.findall(text)
        for match in matches:
            decimals[match[0]] = Decimal(match[1])
        return decimals
    
    
    def perform_comparison(self, text, expected_values):
        '''
        Extracts decimal values from text and compares them to an ordered list
        of expected decimals.
        '''
        actual_values = TestMain.extract_values(text)
        if TestMain.test_help:
            print actual_values
        else:
            self.assertEqual(len(expected_values), len(actual_values))
            for key, value in expected_values.items():
                self.assertAlmostEqual(value, actual_values[key],
                                       DECIMAL_PLACES)
    
    
    def test_perform_comparison(self):
        '''
        Test the decimal list comparison from string test (perform_comparison)
        '''
        expected_value = \
            {'1+2+3+4+5+6+7':   Decimal('0.7165532879818594104308390023')}
        self.perform_comparison('Pi*_s \n \t1+2+3+4+5+6+7\t= 0.7165532879818'+\
                                '594104308390023',
                                expected_value)
        expected_value = \
            {'1+2+3+4+5+6+7':   Decimal('0.7165532879818594104308390023'),
             'an1+an2+an3+an4': Decimal('1'),
             'an5+an6':         Decimal('-0.5757942099675148626179719687')}

        self.perform_comparison('Pi*_s \n \t1+2+3+4+5+6+7\t= 0.7165532879818'+\
                                '594104308390023\n\tan1+an2+an3+an4\t= 1\n\t'+\
                                'an5+an6\t= -0.5757942099675148626179719687',
                                expected_value)

    
    def test_load_files(self):
        '''
        Test the different ways to load files.
        '''
        metric = 'pi'
        expected = {'all': Decimal('0.7165532879818594104308390023')}
        argv = [metric, os.path.join(self.test_data_dir,
                                     'hearst1997.json')]
        self.perform_comparison(main(argv),
                                expected)
        
        argv = [metric, '-f', 'json', os.path.join(self.test_data_dir,
                                                   'hearst1997.json')]
        self.perform_comparison(main(argv),
                                expected)
        
        argv = [metric, '-f', 'tsv', os.path.join(self.test_data_dir,
                                                  'hearst1997.tsv')]
        self.perform_comparison(main(argv),
                                expected)


    def test_all_but_winpr_folder(self):
        '''
        Run through each metric and load from a file.
        '''
        metrics = ['pi', 'k', 'b', 'f', 'p', 'r', 'pr', 's', 'pk', 'wd']
        expected = \
        {
         'pi':  {u'1+2+3+4+5+6+7': Decimal('0.7165532879818594104308390023'),
                 u'an1+an2+an3+an4': Decimal('1'),
                 u'an5+an6': Decimal('-0.5757942099675148626179719687')},
         'k':   {u'1+2+3+4+5+6+7': Decimal('0.7170345217883418222976796831'),
                 u'an1+an2+an3+an4': Decimal('1'),
                 u'an5+an6': Decimal('-0.05952156715012243360331512524')},
         'b':   {u'1+2+3+4+5+6+7': Decimal('0.0014285714285714285714285714'),
                 u'an1+an2+an3+an4': Decimal('0.01455229356727327645713789012'),
                 u'an5+an6': Decimal('0.3092215912041560442272265692')},
         'f':   {'std': Decimal('0.3239626640547745286898970139'),
                 'var': Decimal('0.1049518077014667004704471820'),
                 'stderr': Decimal('0.03306430094362011655292214134'),
                 'mean': Decimal('0.7286033348388224549215261291')},
         'p':   {'std': Decimal('0.3279705495284159011523508245'),
                 'var': Decimal('0.1075646813579711076817558297'),
                 'stderr': Decimal('0.03347335404186737660944801052'),
                 'mean': Decimal('0.7371817129629629629629629628')},
         'r':   {'std': Decimal('0.3284145188345961520541514860'),
                 'var': Decimal('0.1078560961813593106995884774'),
                 'stderr': Decimal('0.03351866646943400531044047662'),
                 'mean': Decimal('0.7367187499999999999999999999')},
         'pr':  {'std': Decimal('0.3625647993833832786266975493'),
                 'var': Decimal('0.1314532337519129638574819243'),
                 'stderr': Decimal('0.0517949713404833255180996499'),
                 'mean': Decimal('0.6583591012162440733869305296')},
         's':   {'std': Decimal('0.2726266332053075620573546387'),
                 'var': Decimal('0.07432528113286130778842149112'),
                 'stderr': Decimal('0.03894666188647250886533637696'),
                 'mean': Decimal('0.8163265306122448979591836735')},
         'pk':  {'std': Decimal('0.2861761390187296559346246595'),
                 'var': Decimal('0.08189678254366728224068944295'),
                 'stderr': Decimal('0.02920772988148629676621594996'),
                 'mean': Decimal('0.2148574561403508771929824560')},
         'wd':  {'std': Decimal('0.2606392427999016685892492029'),
                 'var': Decimal('0.06793281488730609379111692261'),
                 'stderr': Decimal('0.02660138132521389342956902872'),
                 'mean': Decimal('0.2078058574929563376289948819')},
        }
        for metric in metrics:
            argv = [metric, os.path.abspath(os.path.join(self.test_data_dir,
                                                         '..'))]
            self.perform_comparison(main(argv), expected[metric])


    def test_all_but_winpr_metrics(self):
        '''
        Run through each metric and load from a file.
        '''
        expected = \
        {
         'pi':  {'all': Decimal('0.7165532879818594104308390023')},
         'k':   {'all': Decimal('0.7170345217883418222976796831')},
         'b':   {'all': Decimal('0.0014285714285714285714285714')},
         'f':   {'std': Decimal('0.1579255315223177090093893588'),
                 'var': Decimal('0.02494047350660656436483838610'),
                 'stderr': Decimal('0.02497021901516212390630353805'),
                 'mean': Decimal('0.5486480036131738918116627095')},
         'p':   {'std': Decimal('0.1958928076552311369113250286'),
                 'var': Decimal('0.03837399209104938271604938265'),
                 'stderr': Decimal('0.03097337247178993532437300487'),
                 'mean': Decimal('0.569236111111111111111111111')},
         'r':   {'std': Decimal('0.1967217706661170373652606882'),
                 'var': Decimal('0.03869945505401234567901234565'),
                 'stderr': Decimal('0.03110444303231145532699747261'),
                 'mean': Decimal('0.56812500000000000000000000')},
         'pr':  {'std': Decimal('0.1432599301657948205815072907'),
                 'var': Decimal('0.02052340759110840880922651004'),
                 'stderr': Decimal('0.03126187971613534798006584564'),
                 'mean': Decimal('0.3933140933140933140933140933')},
         's':   {'std': Decimal('0.07055015423823358837798727192'),
                 'var': Decimal('0.004977324263038548752834467119'),
                 'stderr': Decimal('0.01539530581369118988034410932'),
                 'mean': Decimal('0.7619047619047619047619047619')},
         'pk':  {'std': Decimal('0.08777992422503512612187275157'),
                 'var': Decimal('0.00770531509695290858725761773'),
                 'stderr': Decimal('0.01387922466940508585272027736'),
                 'mean': Decimal('0.3156578947368421052631578948')},
         'wd':  {'std': Decimal('0.1029019507162951530657009250'),
                 'var': Decimal('0.01058881146121883656509695291'),
                 'stderr': Decimal('0.01627022699689438611144696952'),
                 'mean': Decimal('0.3295394736842105263157894738')}
        }
        metrics = ['pi', 'k', 'b', 'f', 'p', 'r', 'pr', 's', 'pk', 'wd']
        for metric in metrics:
            argv = [metric, os.path.join(self.test_data_dir,
                                         'hearst1997.json')]
            self.perform_comparison(main(argv), expected[metric])


    def test_winpr_metrics(self):
        '''
        Run through each metric and load from a file.
        '''
        expected = \
        {
         'f':   {'std': Decimal('0.1236455519317746814817957631'),
                 'var': Decimal('0.01528822251251318966753632424'),
                 'stderr': Decimal('0.02698167147961670318171997192'),
                 'mean': Decimal('0.6456795045749048402741458914')},
         'p':   {'std': Decimal('0.1507757229665850876837615814'),
                 'var': Decimal('0.02273331863609641387419165197'),
                 'stderr': Decimal('0.03290196016457466023981727858'),
                 'mean': Decimal('0.6652777777777777777777777776')},
         'r':   {'std': Decimal('0.1967985488316959486974703074'),
                 'var': Decimal('0.03872966882226141485400744661'),
                 'stderr': Decimal('0.04294496412755761321481451299'),
                 'mean': Decimal('0.6740740740740740740740740743')}
        }
        submetrics = ['f', 'p', 'r']
        for submetric in submetrics:
            argv = ['wpr', submetric, os.path.join(self.test_data_dir,
                                                   'hearst1997.json')]
            self.perform_comparison(main(argv), expected[submetric])


    def test_om_metrics(self):
        '''
        Run through each metric and load from a file.
        '''
        expected = \
        {
         'pk':  {'std': Decimal('0.08777992422503512612187275150'),
                 'var': Decimal('0.007705315096952908587257617718'),
                 'stderr': Decimal('0.01387922466940508585272027735'),
                 'mean': Decimal('0.684342105263157894736842106')},
         'wd':  {'std': Decimal('0.1029019507162951530657009249'),
                 'var': Decimal('0.01058881146121883656509695289'),
                 'stderr': Decimal('0.01627022699689438611144696950'),
                 'mean': Decimal('0.670460526315789473684210527')},
        }
        metrics = ['pk', 'wd']
        for metric in metrics:
            argv = [metric, '-om', os.path.join(self.test_data_dir,
                                         'hearst1997.json')]
            self.perform_comparison(main(argv), expected[metric])


    def test_file(self):
        '''
        Run through each metric and load from a file.
        '''
        metrics = ['pi', 'k', 'b', 'f', 'p', 'r', 'pr', 's', 'pk', 'wd']
        filesizes = [49, 48, 47, 1628, 1628, 1628, 806, 688, 1415, 1422]
        for metric, expected_filesize in zip(metrics, filesizes):
            filename = 'testfile.tsv'
            if os.path.exists(filename):
                os.remove(filename)
            self.assertFalse(os.path.exists(filename))
            argv = [metric, '-o', filename, os.path.join(self.test_data_dir,
                                                         'hearst1997.json')]
            try:
                main(argv)
                self.assertTrue(os.path.exists(filename))
                actual_filesize = len(open(filename).read())
                self.assertEqual(expected_filesize, actual_filesize, 
                                 '%(metric)s %(expected)i != %(actual)i' % \
                                 {'metric'   : metric,
                                  'expected' : expected_filesize,
                                  'actual'   : actual_filesize})
            finally:
                if os.path.exists(filename):
                    os.remove(filename)
            
            self.assertFalse(os.path.exists(filename))


    def test_file_om(self):
        '''
        Run through each metric and load from a file.
        '''
        metrics = ['pk', 'wd']
        filesizes = [1419, 1426]
        for metric, expected_filesize in zip(metrics, filesizes):
            filename = 'testfile.tsv'
            if os.path.exists(filename):
                os.remove(filename)
            self.assertFalse(os.path.exists(filename))
            argv = [metric, '-om', '-o', filename,
                    os.path.join(self.test_data_dir, 'hearst1997.json')]
            try:
                main(argv)
                self.assertTrue(os.path.exists(filename))
                actual_filesize = len(open(filename).read())
                self.assertEqual(expected_filesize, actual_filesize, 
                                 '%(metric)s %(expected)i != %(actual)i' % \
                                 {'metric'   : metric,
                                  'expected' : expected_filesize,
                                  'actual'   : actual_filesize})
            finally:
                if os.path.exists(filename):
                    os.remove(filename)
            
            self.assertFalse(os.path.exists(filename))


    def test_file_winpr(self):
        '''
        Run through each metric and load from a file.
        '''
        submetrics = ['f', 'p', 'r']
        filesizes = [1734, 1734, 1734]
        for submetric, expected_filesize in zip(submetrics, filesizes):
            
            filename = 'testfile.tsv'
            if os.path.exists(filename):
                os.remove(filename)
            self.assertFalse(os.path.exists(filename))
            argv = ['wpr', submetric, '-o', filename,
                    os.path.join(self.test_data_dir, 'hearst1997.json')]
            try:
                main(argv)
                self.assertTrue(os.path.exists(filename))
                actual_filesize = len(open(filename).read())
                self.assertEqual(expected_filesize, actual_filesize, 
                                 '%(metric)s %(expected)i != %(actual)i' % \
                                 {'metric'   : submetric,
                                  'expected' : expected_filesize,
                                  'actual'   : actual_filesize})
            finally:
                if os.path.exists(filename):
                    os.remove(filename)
            
            self.assertFalse(os.path.exists(filename))


    def test_file_s_detailed(self):
        '''
        Test detailed S output.
        '''
        expected_filesize = 2630
        filename = 'testfile.tsv'
        if os.path.exists(filename):
            os.remove(filename)
        self.assertFalse(os.path.exists(filename))
        argv = ['s', '-de', '-o', filename, os.path.join(self.test_data_dir,
                                                         'hearst1997.json')]
        try:
            main(argv)
            self.assertTrue(os.path.exists(filename))
            actual_filesize = len(open(filename).read())
            self.assertEqual(expected_filesize, actual_filesize, 
                             '%(metric)s %(expected)i != %(actual)i' % \
                             {'metric'   : 's',
                              'expected' : expected_filesize,
                              'actual'   : actual_filesize})
        finally:
            if os.path.exists(filename):
                os.remove(filename)
        
        self.assertFalse(os.path.exists(filename))


    def test_help_output(self):
        '''
        Test the help output.
        '''
        argv = ['-h']
        if self.print_output:
            print main(argv)


    def test_help_s_output(self):
        '''
        Test the help output.
        '''
        argv = ['s', '-h']
        if self.print_output :
            print main(argv)


    def test_s_output(self):
        '''
        Test the help output.
        '''
        argv = ['s', os.path.join(self.test_data_dir, 'hearst1997.json')]
        if self.print_output:
            print main(argv)
