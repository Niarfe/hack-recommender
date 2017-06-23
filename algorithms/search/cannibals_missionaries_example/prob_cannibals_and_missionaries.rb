# Program class, following definition in AIMA
require './base_problem'

class CanAndMis < Problem

  def successorFn( state )
    start_state = state
    next_set = {}
    actions.each do |action|
      end_state = [0,0,0] 
      end_state[0] = start_state[0] + start_state[2]*action[0]
      end_state[1] = start_state[1] + start_state[2]*action[1]
      end_state[2] = start_state[2] * -1
      if isStateValid? end_state
        next_set[action] = end_state
      end
    end
    return next_set 
  end

  def isStateValid?( state )
    if ( (state[1] > 0) && (state[0] > state[1]) ) || 
                        ( (3-state[1] > 0) && (3-state[0] > 3-state[1]) ) 
      return false
    else
      if (state[0] < 0) || (state[1] < 0) || (3 - state[0] < 0) ||
                                      (3 - state[1] < 0)
        return false
      else 
        return true
      end
    end   
  end

  def pathCost( start_st, action, end_st  )
    1
  end

  def getNextNode( fringe )
    fringe.pop
  end
end

