import itertools
import random
from sys import path

from pygame.constants import PREALLOC
from pygame.event import peek


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True
 

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        #prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue
           
                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    #print("Sentence")
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):

        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        # raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        # raise NotImplementedError
    def mark_mine(self, cell):
        #print("mark_mine", self.cells, cell)
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """   
        if cell in self.cells:  
            self.cells.remove(cell)       
            self.count -= 1     
            
            # raise NotImplementedError
    def mark_safe(self, cell):
        #print("mark_safe", self.cells)
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """  
        if cell in self.cells:            
            self.cells.remove(cell)      
        # raise NotImplementedError


class MinesweeperAI():
    """
    Minesweeper game player
    """
    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()
   
        # List of sentences about the game known to be true
        self.knowledge = []
        self.new_kb = []
  
    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)
    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """ 
        self.mark_safe(cell)
        #self.safes.add(cell)
        self.moves_made.add(cell)    
        #print("self.moves_made", self.moves_made)
        new_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < 8 and 0 <= j < 8:     
                    if (i, j) == cell:
                        continue
                    if (i, j) in self.safes or (i, j) in self.moves_made:
                        continue
                    if (i, j) in self.mines:
                        count -= 1
                        continue
                    new_cells.add((i, j)) 
        
        #s = Sentence(cells, count)
        self.knowledge.append(Sentence(cells=new_cells, count =count) )
        new_kb = self.new_kb
        mixed_cells = []
        for item in self.knowledge:            
            for item1 in self.knowledge:          
                if item == item1 or not item1.cells.issubset(item.cells):
                    continue
                sen_count = 0 
                if item.count > 0:
                    sen_count = sorted((item.count, item1.count), reverse= True)[0] - sorted((item.count, item1.count), reverse= True)[1]                       
                intern_count = sorted((item.count, item1.count), reverse= True)[0] - sen_count  
                
                diff_cells = item.cells.difference(item1.cells) 
                s_cells_copy = item.cells.intersection(item1.cells)     
                if diff_cells and Sentence(diff_cells, sen_count) not in new_kb and Sentence(diff_cells, sen_count) not in mixed_cells:
                        new_kb.append(Sentence(diff_cells, sen_count)) 
                if s_cells_copy and Sentence(s_cells_copy, intern_count) not in mixed_cells and Sentence(s_cells_copy, intern_count) not in new_kb :
                    mixed_cells.append( Sentence(s_cells_copy, intern_count) )
                self.knowledge = mixed_cells + new_kb   
        
        self.detector()
        print(self.safes)
             
            
    def detector(self):
            knowledge = self.knowledge  
            can1 = [] 
            can = []            
            for sen in knowledge:
                sent = sen
                if sent.known_mines():
                    
                    for mine in sent.known_mines():
                        can.append(mine)
                    print("s.known_mines()", sent.known_mines() )         
                   
                elif sent.known_safes():
                    print("knownsafes", sent.known_safes() )
                    for safe in sent.known_safes():
                        can1.append(safe)
                              
            for mine in can:
                self.mark_mine(mine)
            for safe in can1:
                self.mark_safe(safe)

    def make_safe_move(self):
        print("make safe move")
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        pure_cells  = self.safes - self.moves_made


        for i in pure_cells:
            return random.choice(list(pure_cells))
        




        # raise NotImplementedError

    def make_random_move(self):
        #print("make_random_move")
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        
        free = []
        for i in range(self.height):
                for j in range(self.width):
                    cell = (i, j)
                    if cell not in self.moves_made and cell not in self.mines:
                        free.append(cell)
            # BUG: if there are no free moves return None
            # fixed with below "if statement"
        if len(free) == 0:
            return None
        else:
            i = random.randrange(len(free))
            return free[i]

