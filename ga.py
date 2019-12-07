#-------------------------------------------------------------------------------------
#-----------------------Importing Modules

import maze
import maze_samples
from random import *



#-------------------------------------------------------------------------------------
#-----------------------Classes

class ga: #Main prog Class
  def __init__(self):
    test_case = select_maze() #choosing the maze
    Mutation=Mutate() #choosing Mutation chance
    M = maze.Maze(maze_samples.maze[test_case])
    Generation_number=choose_generation_number()

    #start with a random generation of X mice
    old_mouse_pop=population(test_case)
    print("Running Generation 0")
    #choosing the most fit mouse in this generation to run
    best_mouse=select_best_mouse(old_mouse_pop.population_list,M)
    M.RunMaze(best_mouse.dna_strand)
    if best_mouse.fitness(M)>1000: #if mouse finds the cheese
      print ('The experiment is over.')
      Generation_number=0 #stop running future generations

    #Creating new generations
    if Generation_number>1:
      for i in range(Generation_number-1):
        print('Running Generation ',i+1)
        #generating a new population
        new_mouse_pop=new_population(len(old_mouse_pop.population_list),old_mouse_pop.population_list,Mutation,M)
        #the old population is replaced with the new one
        old_mouse_pop=new_mouse_pop
        M.ResetMouse()
        #the best mouse in this population is selected and runs through the maze
        best_mouse=select_best_mouse(old_mouse_pop.population_list,M)
        M.RunMaze(best_mouse.dna_strand)
        if best_mouse.fitness(M)>1000: #if mouse finds the cheese
          print ('The experiment is over.')
          break #stop running future geenrations


          
          



class individual: #Class of the mouse
  def __init__(self,test_case,set_moves=None):
    if set_moves==None: #randomizes the strand if nothing is present
      self.dna_strand=''
      moves = ['U','D','R','L']
      limit=33
      if test_case==1:
        limit=15
      for i in range(limit): #the mouse will have 9 or 60 moves depending on maze size
        self.dna_strand+=moves[randint(0,3)]
    else:  #allows custom dna strand when making children from other individuals
      self.dna_strand=set_moves
    fitness=1 #mouse initially starts with 1 fitness
  def runMaze(self,M):
    #mouse runs through the mase based on his DNA strand
    M.RunMaze(self.dna_strand)
  def ResetMouse(self,M):
    M.ResetMouse()
    
  #check the mouse's final position on the grid
  #def Mouse_Position(self,M):
    #x1,y1=M.Convert(M.mouse.pos.r,M.mouse.pos.c)
    #return x1,y1
  
  def fitness(self,M):
    fitness=0 #
    continuous=True
    mouseC,mouseR=M.mouse.pos.c,M.mouse.pos.r
    old_direction=None #initializing the previous direction
    for direction in self.dna_strand:
      new_mouseC,new_mouseR=mouseC,mouseR
      if direction=='U':
        new_mouseR += 1
        if old_direction!='D' and old_direction!=None:
          fitness+=2 #extra points for not back tracking
      elif direction=='D':
        new_mouseR -= 1
        if old_direction!='U' and old_direction!=None:
          fitness+=2
      elif direction=='R':
        new_mouseC += 1
        if old_direction!='L' and old_direction!=None:
          fitness+=2
      elif direction=='L':
        new_mouseC -= 1
        if old_direction!='R' and old_direction!=None:
          fitness+=2
          
      if 0 <= new_mouseR and new_mouseR < M.row_dim \
      and 0 <= new_mouseC and new_mouseC < M.col_dim:
        if M.values[new_mouseR][new_mouseC] in ['M', '-', 'C']:
          fitness=+2
          old_direction=direction
          mouseC,mouseR=new_mouseC,new_mouseR
        else:
          continuous=False #Lose the extra points for hitting an obstacle
        if continuous: #extra points for not hitting a wall
          fitness+=2

    #check how close the mouse was to the cheese
    cheeseR,cheeseC=M.cheese_pos.r,M.cheese_pos.c
    close=abs(cheeseR-mouseR)+abs(cheeseC-mouseR)
    GainPoints=15*(close+1)/(2^close) #exponentially more points the closer to cheese
    fitness+=GainPoints
    if fitness<=0:
      fitness=1
    if cheeseR==mouseR and cheeseC==mouseC:
      return 1500 #if cheese is found fitness is set to 1500
    return(fitness)

  


class population: #initial population
  def __init__(self,test_case):
    self.population_list=[]
    M = maze.Maze(maze_samples.maze[1])
    while True:
      population_size=input('Input the population size (2 or above): ')
      if population_size.isnumeric():
        population_size=int(population_size)
        if population_size>1:
          break
    for i in range(population_size):
      mouse=individual(test_case)
      self.population_list.append(mouse)




class new_population: 
  def __init__(self,pop_size,old_population_list,Mutation,M):
    self.population_list=[]
    #crossbreeding the parents
    Monte_weights=SetWeightsForMonteCarloSelection(old_population_list,M)
    for i in range(len(old_population_list)//2):
      child1,child2=Make_a_baby(old_population_list,1,M,Mutation.state,Monte_weights)
      self.population_list.append(child1) #child 1 added to new population
      self.population_list.append(child2)




class Mutate:
  def __init__(self):
    while True:
      mutate_rate=input('Choose Mutate chance for this generation: any integer from 0=0% 10=100%: ')
      if mutate_rate.isnumeric():
        mutate_rate=int(mutate_rate)
        if mutate_rate in range(11):
          print('Mutation chance is ',mutate_rate*10,'%')
          break
    if mutate_rate>randint(1,9):
      
      self.state=True  #generation is mutates
    else:
      self.state=False #no mutation




#-------------------------------------------------------------------------------------
#-----------------------Functions

def SetWeightsForMonteCarloSelection(values,M):
  fitness_total=0
  for current_mouse in values:
    fitness_total+=current_mouse.fitness(M)
  normalized_values = [int(v.fitness(M)/fitness_total*100+.5) for v in values]
  accum = 0
  selection_weights = []
  for w in normalized_values:
    accum += w
    selection_weights.append(accum)
  return selection_weights

def MonteCarloSelection(selection_weights):
  selection = randint(0,selection_weights[-1])
  for i,w in enumerate(selection_weights):
    if selection <= w:
      return i


def Make_a_baby(population_list,test_case,M,Mutation,weights):
  #choosing the parents using the montecarlo selection based on fitness
  for i in range(len(population_list)//2):
    p1 = MonteCarloSelection(weights)
    p2 = MonteCarloSelection(weights)
    p1=population_list[p1]
    p2=population_list[p2]
    
  #Making the child
  child=''
  for i in range((len(population_list)//2)):
    cut=randint(0,len(population_list[0].dna_strand)) #random cut in the parent's DNA
    #children are a random combination of parents' DNA strand
    child1_dna_strand=list(p1.dna_strand[:cut]+p2.dna_strand[cut:]) 
    child2_dna_strand=list(p2.dna_strand[:cut]+p1.dna_strand[cut:])
  if Mutation: #if Mutation happens by chance (changeable by the user)
    moves = ['U','D','R','L']
    child1_dna_strand[randint(0,len(child1_dna_strand)-1)]=moves[randint(0,3)] #random Gene changed to a random direction
  child1_dna_strand=''.join(child1_dna_strand)
  child1=individual(test_case,child1_dna_strand) #child is now an individual(mouse)
  #Making child 2
  if Mutation:
    moves = ['U','D','R','L']
    child2_dna_strand[randint(0,8)]=moves[randint(0,3)]
  child2_dna_strand=''.join(child2_dna_strand)
  child2=individual(test_case,child2_dna_strand)
  return child1,child2




def select_maze():
  while True:
    test_case=input('Input 0 for big maze, 1 for small maze : ')
    if test_case.isnumeric():
      test_case=int(test_case)
      if test_case in range (2):
        return test_case

  
def select_best_mouse(population_list,M):
  #If only 1 mouse in the whole population
  if len(population_list)==1:
      return population_list[0]  
  #If more than 1 mouse in the population
  for mouse_number in range (len(population_list)-1):
    if population_list[mouse_number].fitness(M)>population_list[mouse_number+1].fitness(M):
      best_mouse=population_list[mouse_number]
    else:
      best_mouse=population_list[mouse_number+1]
    return(best_mouse)
    


def choose_generation_number():
  #choose the number of generations to be produced after the initial one
    while True:
      generation_number=input('Choose the number of NEW generations (0 or more): ')
      if generation_number.isnumeric():
        generation_number=int(generation_number)
        if generation_number>=0:
          return generation_number

#-------------------------------------------------------------------------------------
#-----------------------Program Body


def main():
  repeat=True
  while repeat:
    Expermient=ga()
    while True:
      repeat_choice=input("Do you want to repeat the experiment? (Y/N) ")
      if repeat_choice.upper()=='Y': #repeat the simulation if Y is input
        break
      if repeat_choice.upper()=='N': #Close the simulation if N is input
        quit()



#-------------------------------------------------------------------------------------
#-----------------------Executing the program

if __name__=='__main__' :
  main()

  

