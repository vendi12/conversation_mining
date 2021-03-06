import itertools
from itertools import chain, combinations

# switch on this library only to get the stats on memorty usage for debug
# from pympler.tracker import SummaryTracker

# The program depends on the tree search, nodes of which are described below
class Node:
    def __init__(self, pattern, pattern_composed_now = '', father_node = None, siblings = None, depth = 0, score_pattern = -1000000, score_composed_now = -1000000):
        self.pattern = pattern
        self.pattern_composed_now = pattern_composed_now
        self.loop = ''
        self.depth = depth
        self.score_pattern = score_pattern
        self.score_composed_now = score_composed_now # the more the better
        self.father_node = father_node
        self.siblings = siblings


# separating patterns in the ones the we can start the serach with and others
def findPatternsWithStartSymbol(patterns):
    patterns_with_start = set()
    patterns_without = set()
    total_score = 0
    for i in patterns:
        if i[0][0] == '<': patterns_with_start.add(i)
        else: patterns_without.add(i)
        total_score += i[1]
    return patterns_with_start, patterns_without, total_score

# The main function to find composed patterns from the list of input patterns 
# Input example:
# patterns: <class 'list'>: [('>', 2199), ('<', 2199), ('Q', 2137), ('<Q', 2073), ('A', 1988), ('QA', 1714), ('<QA', 1588)]
# patterns: is a list of tuples where first element is a pattern:
# patterns: A-Z - are the activities
# patterns: 1-9 - are the loops
# patterns: <, > are the start and end symbol
def composePattern(patterns, max_pattern_len = 6, number_of_patterns_out = 5, max_loops_number = 1):
    print ("---looking for patterns with a max pattern len: " + str(max_pattern_len))
    print ("---max loops allowed: " + str(max_loops_number))
    print ("---number of patterns we are looking for: " + str(number_of_patterns_out))

    # first we find starting points of our tree search
    start_points, all_others, total_score = findPatternsWithStartSymbol(patterns)

    # out of the patterns with starting symbol we create
    # the roots of the search trees
    roots = [Node(i[0],i[0], score_pattern=i[1], score_composed_now=i[1]) for i in start_points]
    for root in roots:
        siblings_of_root = set()
        for other in all_others:
            siblings_of_root.add(Node(other[0], father_node=root, depth=1, score_pattern=other[1]))

        root.siblings = siblings_of_root
    all_others.clear()

    # in this variable we keep all sub-result patterns 
    global best_composed
    best_composed = []

    # check if there are less or equal of loops than allowed
    def find_loops(s1, s2):
        a = set()
        for i in s1 + s2:
            if i.isdigit():
                a.add(i)
        # if not len(a) <= max_loops_number:
        #     print (s1 + s2)
        return len(a) > max_loops_number

    # core recursive function to find patterns by building the search tree
    def search(root):
        global best_composed
        for i in root.siblings:

            elements_to_compare = min(len(root.pattern_composed_now)-1, len(i.pattern))

            if not find_loops(root.pattern_composed_now, i.pattern):
                while elements_to_compare > 0:
                    if root.pattern_composed_now[-elements_to_compare:] == i.pattern[:elements_to_compare]:
                        #print (root.pattern_composed_now + i.pattern[elements_to_compare:] + "  " + str(len(root.pattern_composed_now + i.pattern[elements_to_compare:])))
                        if max_pattern_len < len(root.pattern_composed_now + i.pattern[elements_to_compare:]) :
                            pass
                        else:
                            #print ("number of siblings: " + str(len(root.siblings)))
                            # found a match! write it to the patterns_composed_now!
                            i.pattern_composed_now = root.pattern_composed_now + i.pattern[elements_to_compare:]

                            # here we calculate scores
                            i.score_composed_now = root.score_composed_now + i.score_pattern
                            if i.pattern_composed_now[-1] == ">":
                                best_composed.append(i)
                                #print (i.pattern_composed_now + "  depth: " + str(i.depth) + ' ' + str(i.score))
                            else:
                                siblings_set = set()
                                for rs in root.siblings:
                                    if not rs.pattern == i.pattern:
                                        new_rs = Node(rs.pattern, depth=root.depth + 1, father_node= i, score_pattern=rs.score_pattern)
                                        siblings_set.add(new_rs)
                                i.siblings = siblings_set
                                search(i)
                            break
                    elements_to_compare -= 1


    # uncommend next to get the stats on memorty usage for debug
    # tracker = SummaryTracker()

    # this is the main loop where we search for each initial state 
    for rn in range(len(roots)):
        print("root number " + str(rn + 1) + "/" + str(len(roots)))
        search(roots[rn])
        roots[rn].siblings.clear()
        
        # uncommend next to get the stats on memorty usage for debug
        # tracker.print_diff()

    # greedy algo to search for best patterns with non repeatable composing patterns
    def sort_out_pattern(best_composed):
        best_composed = sorted(best_composed, key=lambda x: -x.score_composed_now)
        best_patterns_out = list()
        # greedy algorithm to find best #number_of_patterns_out number
        set_used = set()

        checking_ind = 0

        while len(best_patterns_out) < number_of_patterns_out and checking_ind < len(best_composed):
            pat_check = best_composed[checking_ind]
            # check if pattern is already in the set

            candidate_is_good = True
            while pat_check:
                if pat_check.pattern in set_used:
                    candidate_is_good = False
                    break
                pat_check = pat_check.father_node

            # if no, then add its parts fully to the set
            if candidate_is_good:
                pat_check = best_composed[checking_ind]
                while pat_check:
                    set_used.add(pat_check.pattern)
                    pat_check = pat_check.father_node
                best_patterns_out.append(best_composed[checking_ind])
            checking_ind += 1

        return best_patterns_out

    # now the optimization on how to choose number_of_patterns_out
    # that have biggest score, and non repeating composing patterns
    sor = sort_out_pattern(best_composed)

    total_score_patternalized = 0

    # nice output of the results
    for i in sor:
        pat_check = i
        list_used = list()
        while pat_check:
            list_used.append(pat_check.pattern)
            pat_check = pat_check.father_node

        print (i.pattern_composed_now, i.score_composed_now, list_used[::-1])
        total_score_patternalized += i.score_composed_now

    print ("Total score patternalized: " + str(total_score_patternalized) +" / "+ str(total_score))

    return None if sor == [] else sor
