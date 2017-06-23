# Base file for search problems.
# Problem class contains the basics, extended by successorFn
# Node struct should be generic enough for most cases
require 'tco'
class Problem
  attr_accessor :init_state
  attr_accessor :goal_state
  attr_accessor :states
  attr_accessor :actions

  def initialize( init_state, goal_state, states, actions )
    @init_state = init_state
    @goal_state = goal_state
    @states     = states
    @actions    = actions
    raise "Init state not included in initial set" unless states.include? init_state
  end
  
  def setInitialState( state )
    raise "State is not valid" unless isStateValid?( state )
    @init_state = state
  end

  def isGoal?( state )
    (goal_state == state) ? true : false
  end
  
  def successorFn( _state)
    next_states = {} 
    @actions.each do |action|
      state = _state.dup
      next_state = method(action).call(state)
      if isStateValid? next_state
        next_states[action] = next_state.dup
      end
    end
    return next_states
  end
 
  def isStateValid?( state )
    raise "THIS NEEDS TO BE OVERRIDEN" 
  end

  def getNextNode( fringe )
    fringe.pop
  end
 
  def pathCost( start_state, action, end_state )
    raise "THIS NEEDS TO BE OVERRIDEN"
  end
end

Node = Struct.new(:state, :parent, :action, :path_cost, :depth, :hval)

