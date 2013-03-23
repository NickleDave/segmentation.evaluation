'''
Created on Sep 4, 2012

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
'''
from decimal import Decimal
from .distance.MultipleBoundary import boundary_edit_distance
from segeval import compute_pairwise, compute_pairwise_values
from . import boundary_string_from_masses, weight_a, weight_s_scale, weight_t_scale
from .. import SegmentationMetricError, compute_pairwise, \
    compute_pairwise_values, create_tsv_rows
from ..data import load_file
from ..data.TSV import write_tsv
from ..data.Display import render_mean_values, render_mean_micro_values


DEFAULT_PERMUTED = False
DEFAULT_N_T = 2
DEFAULT_BOUNDARY_TYPES = set([1])
DEFAULT_WEIGHT = (weight_a, weight_s_scale, weight_t_scale)
DEFAULT_CONVERT_TO_BOUNDARY_STRINGS = True


def __boundary_similarity__(segs_a, segs_b,
                            boundary_types=DEFAULT_BOUNDARY_TYPES,
                            n_t=DEFAULT_N_T, weight=DEFAULT_WEIGHT,
                            convert_to_boundary_strings=\
                                DEFAULT_CONVERT_TO_BOUNDARY_STRINGS):
    '''
    Compute boundary similarity applying the weighting functions specified.
    '''
    # pylint: disable=C0103,R0913,R0914
    # Count boundaries
    bs_a = segs_a
    bs_b = segs_b
    if convert_to_boundary_strings:
        bs_a = boundary_string_from_masses(segs_a)
        bs_b = boundary_string_from_masses(segs_b)
    # Compute edits
    additions, substitutions, transpositions = \
        boundary_edit_distance(bs_a, bs_b, n_t=n_t)
    # Calculate the total pbs
    pbs = len(bs_b) * len(boundary_types)
    # Apply weighting functions
    fnc_weight_a, fnc_weight_s, fnc_weight_t = weight
    count_additions      = fnc_weight_a(additions)
    count_substitutions  = fnc_weight_s(substitutions,
                                        max(boundary_types),
                                        min(boundary_types))
    count_transpositions = fnc_weight_t(transpositions, n_t)
    count_edits = count_additions + count_substitutions + count_transpositions
    # Compute
    full_misses = 0
    boundaries_all = 0
    matches = 0
    for set_a, set_b in zip(bs_a, bs_b):
        matches += len(set_a.intersection(set_b))
        full_misses += len(set_a.symmetric_difference(set_b))
        boundaries_all += len(set_a) + len(set_b)
    return pbs, count_edits, additions, substitutions, transpositions, \
            full_misses, boundaries_all, matches


def boundary_similarity(segs_a, segs_b,
                        boundary_types=DEFAULT_BOUNDARY_TYPES,
                        n_t=DEFAULT_N_T, weight=DEFAULT_WEIGHT,
                        convert_to_boundary_strings=\
                        DEFAULT_CONVERT_TO_BOUNDARY_STRINGS,
                        return_parts=False):
    '''
    BS type b.
    '''
    # pylint: disable=C0103,R0913,R0914
    values = __boundary_similarity__(segs_a, segs_b,
                                     boundary_types=boundary_types, n_t=n_t,
                                     weight=weight,
                                     convert_to_boundary_strings=\
                                        convert_to_boundary_strings)
    matches        = values[7]
    count_edits    = values[1] # Weighted
    additions      = values[2]
    substitutions  = values[3]
    transpositions = values[4]
    count_unweighted = len(additions) + len(substitutions) + len(transpositions)
    # Fraction
    denominator = count_unweighted + matches
    numerator   = denominator - count_edits
    if return_parts:
        return numerator, denominator, additions, substitutions, transpositions
    else:
        return numerator / denominator if denominator > 0 else 1


def confusion_matrix(segs_a, segs_b,
                        boundary_types=DEFAULT_BOUNDARY_TYPES,
                        n_t=DEFAULT_N_T, weight=DEFAULT_WEIGHT,
                        convert_to_boundary_strings=\
                        DEFAULT_CONVERT_TO_BOUNDARY_STRINGS,
                        return_parts=False):
    '''
    Create a confusion matrix using boundary edit distance.
    '''
    # pylint: disable=C0103,R0913,R0914
    # Count boundaries
    bs_a = segs_a
    bs_b = segs_b
    if convert_to_boundary_strings:
        bs_a = boundary_string_from_masses(segs_a)
        bs_b = boundary_string_from_masses(segs_b)
    # Compute edits
    additions, substitutions, transpositions = \
        boundary_edit_distance(bs_a, bs_b, n_t=n_t)
    # Calculate the total pbs
    pbs = len(bs_b) * len(boundary_types)
    # Apply weighting functions
    fnc_weight_a, fnc_weight_s, fnc_weight_t = weight
    count_additions      = fnc_weight_a(additions)
    count_substitutions  = fnc_weight_s(substitutions,
                                        max(boundary_types),
                                        min(boundary_types))
    count_transpositions = fnc_weight_t(transpositions, n_t)
    count_edits = count_additions + count_substitutions + count_transpositions
    # Compute
    full_misses = 0
    boundaries_all = 0
    matches = 0
    for set_a, set_b in zip(bs_a, bs_b):
        matches += len(set_a.intersection(set_b))
        full_misses += len(set_a.symmetric_difference(set_b))
        boundaries_all += len(set_a) + len(set_b)
    
    
def pairwise_similarity(dataset_masses, n=DEFAULT_N_T, weight=DEFAULT_WEIGHT,
            convert_to_boundary_strings=DEFAULT_CONVERT_TO_BOUNDARY_STRINGS):
    '''
    Calculate mean pairwise boundary similarity (B).
    
    .. seealso:: :func:`similarity`
    .. seealso:: :func:`segeval.compute_pairwise`
    
    :param dataset_masses: Segmentation mass dataset (including multiple \
                           codings).
    :type dataset_masses: dict
        
    :returns: Mean, standard deviation, variance, and standard error of a \
        segmentation metric.
    :rtype: :class:`decimal.Decimal`, :class:`decimal.Decimal`, \
        :class:`decimal.Decimal`, :class:`decimal.Decimal`
    '''
    # pylint: disable=C0103,R0913,R0914
    def wrapper(segment_masses_a, segment_masses_b, return_parts=False):
        '''
        Wrapper to provide parameters.
        '''
        return boundary_similarity(segment_masses_a, segment_masses_b,
                                   dataset_masses.boundary_types, n,
                                   weight,
                                   convert_to_boundary_strings,
                                   return_parts)
    # Compute values for pairs and return mean ,etc.
    return compute_pairwise(dataset_masses, wrapper, permuted=DEFAULT_PERMUTED)


def pairwise_similarity_micro(dataset_masses, n=DEFAULT_N_T,
                              weight=DEFAULT_WEIGHT,
                              return_parts=False,
                              fnc_similarity=boundary_similarity):
    '''
    Calculate mean pairwise boundary similarity (B).
    
    .. seealso:: :func:`boundary_similarity`
    .. seealso:: :func:`segeval.compute_pairwise`
    
    :param dataset_masses: Segmentation mass dataset (including multiple \
                           codings).
    :param return_parts:   If false, returns a :class:`decimal.Decimal`, \
                                else, return the statistics used to create \
                                the decimal
    :type dataset_masses: dict
    
    :returns: Mean (micro)
    :rtype: :class:`decimal.Decimal`, or :func:`int`, :func:`int`
    '''
    # pylint: disable=C0103,R0913,R0914
    def wrapper(segment_masses_a, segment_masses_b, return_parts=True):
        '''
        Wrapper to provide parameters.
        '''
        return fnc_similarity(segment_masses_a, segment_masses_b,
                              dataset_masses.boundary_types, n,
                              weight, return_parts=return_parts)
    # Compute values for pairs
    pairs = compute_pairwise_values(dataset_masses, wrapper,
                                    permuted=DEFAULT_PERMUTED,
                                    return_parts=True)
    # Sum and extend for each pair
    pbs, count_edits = 0, 0
    additions, substitutions, transpositions = list(), list(), list()
    for values in pairs.values():
        # Get
        current_pbs, current_count_edits, current_additions, \
            current_substitutions, current_transpositions = values
        # Sum
        pbs         += current_pbs
        count_edits += current_count_edits
        # Construct overall edit sets
        additions.extend(current_additions)
        substitutions.extend(current_substitutions)
        transpositions.extend(current_transpositions)
    # Return
    if return_parts:
        return pbs, count_edits, additions, substitutions, transpositions
    else:
        return (Decimal(count_edits) / Decimal(pbs))




def pairwise_b(dataset_masses, n_t=DEFAULT_N_T, weight=DEFAULT_WEIGHT,
               return_parts=False):
    '''
    Calculate mean pairwise S.
    
    .. seealso:: :func:`similarity`
    .. seealso:: :func:`segeval.compute_pairwise`
    
    :param dataset_masses: Segmentation mass dataset (including multiple \
                           codings).
    :type dataset_masses: dict
        
    :returns: Mean, standard deviation, variance, and standard error of a \
        segmentation metric.
    :rtype: :class:`decimal.Decimal`, :class:`decimal.Decimal`, \
        :class:`decimal.Decimal`, :class:`decimal.Decimal`
    '''
    # pylint: disable=C0103,R0913,R0914
    def wrapper(segment_masses_a, segment_masses_b, return_parts=return_parts):
        '''
        Wrapper to provide parameters.
        '''
        return boundary_similarity(segment_masses_a, segment_masses_b, n_t,
                                   weight, return_parts)
    
    return compute_pairwise(dataset_masses, wrapper, permuted=DEFAULT_PERMUTED)


def pairwise_b_micro(dataset_masses, n_t=DEFAULT_N_T,
                              weight=DEFAULT_WEIGHT,
                              return_parts=False):
    '''
    Calculate mean pairwise B.
    
    .. seealso:: :func:`similarity`
    .. seealso:: :func:`segeval.compute_pairwise`
    
    :param dataset_masses: Segmentation mass dataset (including multiple \
                           codings).
    :param return_parts:   If false, returns a :class:`decimal.Decimal`, \
                                else, return the statistics used to create \
                                the decimal
    :type dataset_masses: dict
    
    :returns: Mean (micro)
    :rtype: :class:`decimal.Decimal`, or :func:`int`, :func:`int`
    '''
    # pylint: disable=C0103,R0913,R0914
    def wrapper(segment_masses_a, segment_masses_b, return_parts=True):
        '''
        Wrapper to provide parameters.
        '''
        return boundary_similarity(segment_masses_a, segment_masses_b, n_t,
                                   weight, return_parts)
    
    pairs = compute_pairwise_values(dataset_masses, wrapper,
                                   permuted=DEFAULT_PERMUTED,
                                   return_parts=True)
    
    pbs_unedited, pbs_total, set_errors_total, set_transpositions_total = \
        0, 0, 0, 0
    set_errors = list()
    transpostions = list()
    for values in pairs.values():
        # get
        pair_pbs_unedited, pair_pbs_total, pair_set_errors_total, \
            pair_set_transpositions_total, pair_set_errors, \
            pair_set_transpositions = values
        # sum
        pbs_unedited             += pair_pbs_unedited
        pbs_total                += pair_pbs_total
        set_errors_total         += pair_set_errors_total
        set_transpositions_total += pair_set_transpositions_total
        # extend
        set_errors.extend(pair_set_errors)
        transpostions.extend(pair_set_transpositions)
    
    if return_parts:
        return pbs_unedited, pbs_total, set_errors_total, \
            set_transpositions_total, set_errors, transpostions
    else:
        return Decimal(pbs_unedited) / Decimal(pbs_total)


OUTPUT_NAME = 'Mean B metric'
SHORT_NAME  = 'B'


def values_b_detailed(dataset_masses, n_t=DEFAULT_N_T, weight=DEFAULT_WEIGHT):
    '''
    Produces a TSV for this metric
    '''
    # pylint: disable=C0103
    header = list(['coder1', 'coder2', 'error', 'edits', 'boundaries', 'n'])
    def wrapper(segment_masses_a, segment_masses_b, return_parts):
        '''
        Wrapper to provide parameters.
        '''
        return boundary_similarity(segment_masses_a, segment_masses_b, n_t=n_t,
                                   weight=weight, return_parts=return_parts)
    # Get values
    values = compute_pairwise_values(dataset_masses, wrapper, return_parts=True)
    adjusted_values = dict()
    for label, value in values.items():
        subvalues = list()
        additions, substitutions, transpositions = value[2:5]
        # For addition errors
        for addition in additions:
            subvalues.append(['a', 1, addition[2], 1])
        # For addition errors
        for substitution in substitutions:
            # TODO: Fix
            subvalues.append(['s', None, None, None])
        # For transposition errors
        for transposition in transpositions:
            subvalues.append(['t', 1, transposition[2],
                             abs(transposition[1] - transposition[0])])
        adjusted_values[label] = subvalues
    return create_tsv_rows(header, adjusted_values, expand=True)


def values_b(dataset_masses, n_t=DEFAULT_N_T, weight=DEFAULT_WEIGHT):
    '''
    Produces a TSV for this metric
    '''
    # pylint: disable=C0103
    header = list(['coder1', 'coder2', 'numerator', 'denominator', \
                   'additions', 'substitutions', 'transpositions', SHORT_NAME])
    def wrapper(segment_masses_a, segment_masses_b, return_parts):
        '''
        Wrapper to provide parameters.
        '''
        return boundary_similarity(segment_masses_a, segment_masses_b, n_t=n_t,
                                   weight=weight, return_parts=return_parts)
    # Get values
    values = compute_pairwise_values(dataset_masses, wrapper, return_parts=True)
    adjusted_values = dict()
    for label, value in values.items():
        # Get values
        numerator, denominator, additions, substitutions, transpositions = value
        similarity = Decimal(numerator) / Decimal(denominator)
        # Store values
        adjusted_values[label] = [numerator, denominator, len(additions), 
                                  len(substitutions), len(transpositions),
                                  similarity]
    return create_tsv_rows(header, adjusted_values)


def parse(args):
    '''
    Parse this module's metric arguments and perform requested actions.
    '''
    # pylint: disable=C0103,R0914
    output = None
    values = load_file(args)
    # Parse args
    n_t  = args['nt']
    wt = args['wt']
    ws = args['ws']
    weight = DEFAULT_WEIGHT
    micro = args['micro']
    if wt != 1.0 or ws != 1.0:
        weight = (ws, wt)
    # Is a TSV requested?
    if args['output'] != None:
        # Create a TSV
        output_file = args['output'][0]
        if args['detailed']:
            header, rows = values_b_detailed(values, n_t, weight)
        else:
            header, rows = values_b(values, n_t, weight)
        write_tsv(output_file, header, rows)
    elif micro:
        # Create a string to output
        mean = pairwise_similarity_micro(values, n_t, weight)
        output = render_mean_micro_values(SHORT_NAME, mean)
    else:
        # Create a string to output
        mean, std, var, stderr, n = pairwise_similarity(values, n_t, weight)
        output = render_mean_values(SHORT_NAME, mean, std, var, stderr, n)
    # Return
    return output


def parser_b_support(parser):
    '''
    Add support for B parameters
    
    :param parser: Argument parser
    :type parser: argparse.ArgumentParser
    '''
    parser.add_argument('-nt',
                        type=int,
                        default=DEFAULT_N_T,
                        help='The maximum number of PBs that boundaries can '+\
                              'span to be considered transpositions (nt<2 '+\
                              ('means no transpositions); default is %i.' \
                                    % DEFAULT_N_T))


def create_parser(subparsers):
    '''
    Setup a command line parser for this module's metric.
    '''
    from ..data import parser_add_file_support
    from .. import parser_micro_support
    parser = subparsers.add_parser('b',
                                   help=OUTPUT_NAME)
    parser_add_file_support(parser)
    parser_b_support(parser)
    parser_micro_support(parser)
    parser.add_argument('-de', '--detailed',
                        action='store_true',
                        default=False,
                        help='When specifying an output TSV file, specify '+\
                            'this to obtain a detailed error breakdown per '+\
                            'edit')
    parser.set_defaults(func=parse)