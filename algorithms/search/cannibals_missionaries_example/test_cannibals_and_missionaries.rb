#!/usr/bin/env ruby

require 'test/unit'
require './base_solve_treesearch'
require './prob_cannibals_and_missionaries'

$init_state = [3,3,-1]
$goal_state = [0,0,1]
$states =     [[3,3,-1]]
$actions =    [[0,1], [0,2], [1,1], [1,0],[2,0]] 

class TestCannibalsAndMissionaries < Test::Unit::TestCase

  def setup
    @pr = CanAndMis.new( $init_state, $goal_state, $states, $actions )
  end

  def test_problem_goal
    assert_equal(  true, @pr.isGoal?($goal_state) )
    assert_equal( false, @pr.isGoal?($init_state) )
  end

  def test_states 
    assert_equal( $states, @pr.states )
  end

  def test_initial_state
    @pr.setInitialState($init_state)
    assert_equal( $init_state, @pr.init_state )
  end
  
  def test_goal_state
    assert_equal( false, @pr.isGoal?([3,3,-1]) )
    assert_equal( true,  @pr.isGoal?([0,0, 1]) )
  end

  def test_valid__state
    assert_equal( true,  @pr.isStateValid?([3,3,-1]) )
    assert_equal( true,  @pr.isStateValid?([2,3,-1]) )
    assert_equal( false, @pr.isStateValid?([3,2,-1]) )
    assert_equal( false, @pr.isStateValid?([0,1,-1]) )
  end

  def test_valid_set
    @pr.setInitialState [2,3,-1]
    assert_equal( [2, 3, -1], @pr.init_state )
  end

  def test_invalid_init_state
    begin 
     @pr.setInitialState "junk"
    rescue
     puts "Exception caught"
    end
    assert_equal( [3,3,-1], @pr.init_state )
  end

  def test_successorFunction

    next_set = @pr.successorFn [3,3,-1]
    assert_equal({[2,0]=>[1,3,1],[1,1]=>[2,2,1],[1,0]=>[2,3,1]}, next_set)

    next_set = @pr.successorFn [1,1,1]
    assert_equal({[0,2]=>[1,3,-1],[1,1]=>[2,2,-1]}, next_set)

  end

  def test_node_structure
    depth = 0
    zeroNode = Node.new(   [3,3,-1], nil,       nil,   0, depth += 1)
    firstNode = Node.new(  [2,2,1],  zeroNode,  [1,1], 1, depth += 1)
    secondNode = Node.new( [3,2,-1], firstNode, [1,1], 1, depth += 1)
    lastNode = secondNode
    while lastNode.parent != nil do
      lastNode = lastNode.parent
    end
      
  end

  def test_insert
    fringe = []
    solve = Solve.new
    solve.deja_vu = []
    fringe = solve.insert([3,3,-1], fringe)
    assert_equal([3,3,-1], fringe[0].state)
    assert_equal(nil, fringe[0].parent)
    assert_equal(nil, fringe[0].action)
    assert_equal(0, fringe[0].path_cost)
    assert_equal(0, fringe[0].depth)
  end

  def test_tree_search
    solve = Solve.new
    fringe = []
    @pr.setInitialState($init_state)
    solve.TreeSearch(@pr, fringe) 
  end

end


