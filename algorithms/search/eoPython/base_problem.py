#!/usr/bin/env python
"""
    Base class for defining a problem to be solved by tree search
"""

class Problem:
    def __init__(self, initial_state, goal_state, states, actions):
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.states = states
        self.actions = actions

    def setInitialState(state):
        self.initial_state = state

    def is_goal(self, state):
        if self._is_same_state(self.goal_state, state):
            return True
        else:
            return False
    
    def successorFunction(self, state):
        next_states = [] 
        for action in self.actions:
            next_state = self._get_next_state(action, state)
            if self.is_valid(next_state):
                next_states.append(next_state)
        
        return next_states

    def is_valid(self, state):
        raise "Override this function"       

    def _is_same_state(self, state1, state2):
        raise "Override this fucntion"
    def _get_next_state(self, action):
        raise "Override this function"

class CannibalsMissionaries(Problem):
    """
       Representation: array of length 3 representing
       1. Number of missionaries on left bank
       2. Number of cannibals on left bank
       3. location of boat, -1 for left, +1 for right
       The number of missionaries or cannibals on the right
       is taken to be the difference of left, for example
       if there are 2 missionaries on the left, then there are
       3 - 2 = 1 on the right
    """
    def __init__(self, initial_state, goal_state, states, actions):
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.states = states
        self.actions = actions
    
    def _is_same_state(self, state1, state2):
        """States are 'equal' if they contain the same values"""
        assert len(state1) == len(state2)
        return state1 == state2

    def is_valid(self, state):
        """From wikipedia....https://en.wikipedia.org/wiki/Missionaries_and_cannibals_problem
         ...boat which can carry at most two people, under the constraint that,
         for both banks, if there are missionaries present on the bank,
         they cannot be outnumbered by cannibals...
         From which we get 3 rules
         1. only 2 people can be on the boat
         2. num of cannibals must be = or < missionaries
         3. Boat doesn't move by itself
        """
        n_missionaries = state[0]
        n_cannibals = state[1]
        boat_position = state[2]
        # Basic number counting for cannibals, missionaries and boat
        if n_cannibals < 0 or n_cannibals > 3:
            print "invalid number of cannibals"
            return False
        if n_missionaries < 0 or n_missionaries > 3:
            print "invalid number of missionaries"
            return False
        if not (boat_position == -1 or boat_position == 1):
            print "invalid boat position"
            return False

        # Check rule 2...for left bank
        if n_cannibals > n_missionaries:
            print "Cannibals outnumber missionaries on left bank", state
            return False
        # for the right bank, ...
        # if there are 3 missionaries on the left we're ok, all missionaries are safe
        # if there are 2 missinoaries, then we need at least 2 cannibals to keep right missionary safe
        if n_missionaries == 2 and n_cannibals < 2:
            print "cannibals outnumber missionaries on right bank case 1"
            return False
        # if there is only one missionary, we need at least on missionary to keep the right 2 safe
        if n_missionaries == 1 and n_cannibals < 1:
            print "cannibals outnumber missionaries on right bank case 2"
            return False
        # if none of the bad conditions exist, then we're good
        return True
    
    def _get_next_state(self, action, state):
        """Don't try to calculate all states, this function simply calculates
        what end_state belongs to this combination of start_state + action
        """
        boat_position = state[2]
        # If boat position is on left (-1) subtract people from left...
        if boat_position == -1:
            miss = state[0] - action[0]
            cans = state[1] - action[1]
        # otherwise add them to the left it's coming back
        else:
            miss = state[0] + action[0]
            cans = state[1] + action[1]
        # flip boat position
        boat_position = boat_position * -1
        # return the end_state
        return [miss, cans, boat_position]


########################
# Test the class

prob_can_n_mis = CannibalsMissionaries(
    initial_state = [3,3,-1],
    goal_state = [0,0,1],
    states = [],
    # since we can only put 2 people on boat these are the valid combinations...
    # of who we can put on the boat, we can worry about direction later.
    actions = [[0,1],[1,0],[1,1],[2,0],[0,2]]
)

# we must be able to identify goal state, distiguish from non-goal state
assert prob_can_n_mis.is_goal([0,0,1]) == True 
assert prob_can_n_mis.is_goal([1,1,-1]) == False

# we must be able to distinguish valid from invalid states
assert prob_can_n_mis.is_valid([0,0,1]) == True
assert prob_can_n_mis.is_valid([2,3,1]) == False

print prob_can_n_mis.successorFunction([3,3,-1])

# Test that we get all the valid states from an initial state
# given the very first state we can...
# move one missionary XXX not, because it would imbalance left side
# move one cannibale to right, this is valid
# move one missionary and one cannibale,  valid because sides are balanced
# move two missionaries, XXX not, because it imbalances left side
# move two cannibals, valid 
# so that's three states that are valid....
assert len(prob_can_n_mis.successorFunction([3,3,-1])) == 3