'''
Multiple-boundary edit distance.

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
'''
from __future__ import absolute_import, annotations, division

from itertools import permutations
from collections import namedtuple


Addition = namedtuple('Addition', 'type side')  # For side; a = from a, b = from b
Substitution = namedtuple('Substitution', 'type_a type_b')
Transposition = namedtuple('Transposition', 'start end type')
Difference = namedtuple('Difference', 'sim a_b b_a')


def additions_substitutions(d: set, a: set, b: set):
    '''
    Compute the number of additions and substitutions for a given pair of
    boundary string positions using:

    :param d: Symmetric difference between the pair.
    :param a: Difference between the pair; A / B.
    :param b: Difference between the pair; B / A.
    :type d: set
    :type a: set
    :type b: set

    Examples
    --------
    >>> a_i = set([1, 2, 3, 4])
    >>> b_i = set([1, 6])
    >>> a = a_i - b_i
    >>> b = b_i - a_i
    >>> d = a_i ^ b_i
    >>> segeval.similarity.distance.multipleboundary.additions_substitutions(d, a, b)
    (2, 1)
    '''

    additions = abs(len(a) - len(b))
    substitutions = (len(d) - additions) / 2
    return additions, substitutions


def additions_substitutions_sets(d: set, a: set, b: set) -> tuple[list, set]:
    '''Compute the sets of additions and substitutions for a given pair of
    boundary string positions using:

    :param d: Symmetric difference between the pair.
    :param a: Difference between the pair; A / B.
    :param b: Difference between the pair; B / A.
    :type d: set
    :type a: set
    :type b: set

    Examples
    --------
    >>> a_i = set([1, 2, 3, 4])
    >>> b_i = set([1, 6])
    >>> a = a_i - b_i
    >>> b = b_i - a_i
    >>> d = a_i ^ b_i
    >>> segeval.similarity.distance.multipleboundary.additions_substitutions_sets(d, a, b)
    ([(2, 'a'), (3, 'a')], set([(4, 6)]))
    '''

    substitutions = list()
    delta = None
    for perm_a in permutations(sorted(a)):
        for perm_b in permutations(sorted(b)):
            current_substitutions = zip(perm_a, perm_b)
            current_substitutions = set(current_substitutions)
            current_delta = sum(abs(a_i - b_i)
                                for a_i, b_i in current_substitutions)
            if delta is None or current_delta < delta:
                delta = current_delta
                substitutions = current_substitutions
    # Collect all substitutions
    substituted = list()
    added = list()
    for a_i, b_i in substitutions:
        substituted.append(a_i)
        substituted.append(b_i)
    additions = d - set(substituted)
    # Add from a
    for addition in a - set(substituted):
        added.append(Addition(addition, 'a'))
    # Add from b
    for addition in b - set(substituted):
        added.append(Addition(addition, 'b'))
    assert len(added) is len(additions)
    return added, set([Substitution(a_i, b_i) for a_i, b_i in set(substitutions)])


def __has_substitutions__(i: int, j: int, d, options_set):
    '''
    Determine whether two substitutions are present involving the boundary 'd'
    at the positions 'i' and 'j'.
    '''

    present = False
    if i in options_set and d in options_set[i][0] and j in options_set and d in options_set[j][0]:
        d_i, a_i, b_i = options_set[i]
        d_j, a_j, b_j = options_set[j]
        if (additions_substitutions(d_i, a_i, b_i)[1] > 0 and
            additions_substitutions(d_j, a_j, b_j)[1] > 0):
            present = True
    return present


def __overlaps_existing__(i: int, j: int, d, options_transp):
    '''
    Determine whether a transposition would overlap another that has been
    previously identified involving the boundary 'd' at the positions 'i' and
    'j'.
    '''

    def check_position(position):
        '''
        Check a position for an overlapping transposition
        '''
        if position in options_transp:
            for t in options_transp[position]:
                # If the transposition 't' is of the boundary type 'd'
                if t[2] is d:
                    return True
    return check_position(i) or check_position(j)


def find_transpositions(boundary_string_a: list[frozenset], boundary_string_b: list[frozenset],
                        n_t: list[int], options_set: dict[int: Difference]) -> list[Transposition]:
    '''Identify all non-overlapping minimal transpositions between two boundary
    strings while removing the additions/deletions and substitutions that they
    would overlap from the set of potential additions/deletions and
    substitutions.

    Algorithm 4.3 from Fournier 2013.
    '''

    options_transp: dict[Transposition] = dict()  # stored transitions :math:`O_T` that we check
    transpositions = list()
    for n_i in sorted(n_t):
        n_i = n_i - 1
        for i in range(0, len(boundary_string_a) - n_i):
            j = i + n_i

            # Select edge sets
            a_i: frozenset = boundary_string_a[i]
            a_j: frozenset = boundary_string_a[j]
            b_i: frozenset = boundary_string_b[i]
            b_j: frozenset = boundary_string_b[j]

            # Compute symmetric differences
            diff_i = a_i ^ b_i
            diff_j = a_j ^ b_j
            diff_a = a_i ^ a_j
            diff_b = b_i ^ b_j

            # Detect potential transposition
            t_p = diff_i & diff_j & diff_a & diff_b

            # Apply each transposition found by boundary type
            for d in t_p:
                # Create transposition representation
                option_transp = Transposition(i, j, d)

                # Check to see that it does not overlap an existing
                # transposition and that 2 substitutions are not removed
                if (not __overlaps_existing__(i, j, d, options_transp) and
                    not __has_substitutions__(i, j, d, options_set)):

                    # Add
                    transpositions.append(option_transp)

                    # Record positions covered
                    if i not in options_transp:
                        options_transp[i] = list()
                    if j not in options_transp:
                        options_transp[j] = list()
                    options_transp[i].append(option_transp)
                    options_transp[j].append(option_transp)

                    # Removing potential set errors that overlap
                    options_set[i][0].discard(d)
                    options_set[i][1].discard(d)
                    options_set[i][2].discard(d)
                    options_set[j][0].discard(d)
                    options_set[j][1].discard(d)
                    options_set[j][2].discard(d)

    return transpositions


def optional_set_edits(
        boundary_string_a: list[frozenset], boundary_string_b: list[frozenset]
) -> dict[int: Difference]:
    '''Identify all potential additions/deletions and substitutions,
    the optional set edits :math:`O_S`.

    Algorithm 4.2 from Fournier 2013.
    '''

    options_set = dict()
    for i, value in enumerate(zip(boundary_string_a, boundary_string_b)):
        a_i, b_i = value
        a = set(a_i - b_i)
        b = set(b_i - a_i)
        d = set(a_i ^ b_i)
        # Record additions/deletions
        if len(d) > 0:
            options_set[i] = Difference(d, a, b)
    return options_set



def boundary_edit_distance(boundary_string_a: list[frozenset], boundary_string_b: list[frozenset],
                           n_t: int = 2) -> tuple[list, list, list]:
    '''Computes boundary edit distance between two boundary strings.

    Identifies the minimum set of additions, substitutions, and transpositions
    that could be applied between two boundary strings for a given set
    of transpositions spanning lengths ``n_t``.

    Returns a list of Addition, Substitution, and Transposition edit sets.

    Algorithm 4.1 from Fournier 2013.

    :param boundary_string_a:
        Boundary string to compare; produced by :func:`boundary_string_from_masses`
    :param boundary_string_b:
        Boundary string to compare; produced by :func:`boundary_string_from_masses`
    :param n_t:
        Maximum distance (in potential boundary positions) that a
        transposition may span.

    :type boundary_string_a:  tuple
    :type boundary_string_b:  tuple
    :type n_t:  int
    '''
    n_t = range(2, n_t + 1)
    # Find potential addition/deletion/substitution operations
    options_set = optional_set_edits(boundary_string_a, boundary_string_b)

    # Find transpositions
    transpositions = find_transpositions(boundary_string_a, boundary_string_b, n_t, options_set)

    # Construct additions and substitutions
    additions = list()
    substitutions = list()
    for option in options_set.values():
        current_additions, current_substitutions = additions_substitutions_sets(option.sim, option.a_b, option.b_a)
        additions.extend(current_additions)
        substitutions.extend(current_substitutions)
    # Return
    return additions, substitutions, transpositions
