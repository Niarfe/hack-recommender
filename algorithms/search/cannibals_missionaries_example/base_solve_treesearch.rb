#!/usr/bin/env ruby
#*-----------------------------------------------------------------------------
#    fringe <- {new searchNode(problem.init_state) }
#    loop
#      if empty(fringe) then return failure
#      node <- selectFrom(fringe, strategy)
#      if problem goalTest(node.state) then
#        return pathTo(node)
#      fringe <- fringe + expand(problem, node)
#*-----------------------------------------------------------------------------

# require 'pry' # used for debugging only


class Solve
  attr_accessor :deja_vu
  def initialize()
    @deja_vu = []
  end

  def TreeSearch( problem, fringe )
    fringe = insert(problem.init_state, fringe)
    raise "Fringe size should be 1 with init state" unless fringe.size == 1
    iter = 0
    while true do
      iter += 1
      if iter > 1000 
        puts "Iteration overflow"
        exit
      end

      if fringe.empty?
        puts "TreeSearch exiting with false" 
        return false
      end
      node = problem.getNextNode( fringe )
      if problem.isGoal?(node.state) 
        puts "Goal State Reached. Output Path:"
        pathTo(node)
        return true
      end
      fringe = expand(problem, node, fringe)
    end
  end

  def insert( init_state, fringe )
    raise "nil state passed for insert" if init_state == nil
    @deja_vu << init_state
    fringe << Node.new(init_state, nil, nil, 0, 0, 0)
  end

  def pathTo(node)
    loop do
      puts "depth: #{node.depth}\taction:#{node.action}\t-> state:#{node.state}"
      break if node.parent == nil
      node = node.parent
    end
  end

  def expand( problem, node, fringe)
    next_set = problem.successorFn(node.state)
    next_set.each do |action, state|
       new_node = Node.new(state, node, action, 0, node.depth + 1, 0)
       if !( @deja_vu.include? new_node.state )
         @deja_vu << new_node.state
         fringe << new_node
       end
    end
    fringe      
  end
end
