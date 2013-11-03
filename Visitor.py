#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
##   Visitor.py  - This module store all the output class. The output will use
##              the visitor pattern
##              
## ######################################################################


#########################################################################
##   Output  - This class is the base class of Observers. Observers can be
##             hooked up to parsers to trace the progress made so far. 
##             Useful for producing concrete syntax trees.
## ######################################################################

from Myfunc import *

class Output( object ):
    def __init__(self):
        pass
    
    def add_output(self, output_string, level):
        pass

    def print_output(self):
        pass

    def add_semantic_output(self, output_string):
        pass
    
    def get_table(self, symbol_table):
        pass
    
    def get_indentation(self):
        pass
    
    def set_indentation(self, value):
        pass
    
    def get_output(self):
        pass
    
    def set_root(self, root_node):
        pass
    
    
#########################################################################
##ParserAscOutput  - This class is to produce the output in characters
##                When object of the Parser changes state, it will be notified 
##                by the methods and updated automatically
## ######################################################################

class ParserAscOutput(Output):
    def __init__(self):
        self.__output_array = [];
    
    """
        This function is called by Parser when essential info is needed
    """
    def add_output(self, output_string, level):
        self.__output_array.append([output_string, level])

    """
        This function will print the textual output for parser analysis
    """
    def print_output(self):
        for element in self.__output_array:
            output_string = ''
            cnt = 0
            while cnt < element[1]:
                output_string += '  '
                cnt += 1
            output_string += element[0]
            print output_string
            
            
#########################################################################
##ParserDotOutput  - This class is to produce the output in diagrams
##                When object of the Parser changes state, it will be notified 
##                by the methods and updated automatically
## ######################################################################

class ParserDotOutput(Output):
    def __init__(self):
        self.__output_array = [];
        self.__output_string = ''
    
    def add_output(self, output_string, level):
        self.__output_array.append([output_string, level])

    def print_output(self):
        self.__output_string =  'digraph G {' + '\n'
        #character_list = [';','=',':','+','-','*','(',')','<','>','[',']','.',',',':=','<=','>=']
        #input each label's attributes
        cnt = 0
        for element in self.__output_array:
            #if the current token is a terminal
            if element[0].find('@') != -1:
                element[0] = element[0].split('@',1)[0]
                element[0] = text_wrap('<','>',element[0])
                self.__output_string += '    ' + 'struct' + str(cnt) + ' [shape=diamond, label=\"' + str(element[0]) + '\",' + '];\n'
                
            #if the current token is a non-terminal
            else:
                self.__output_string += '    ' + 'struct' + str(cnt) + ' [shape=box, label=\"' + str(element[0]) + '\",' + '];\n'
            cnt += 1
                
        #input the relationship between each label
        for index in range(len(self.__output_array)):
            if index > 0:
                if self.__output_array[index][1] > self.__output_array[index-1][1]:
                    self.__output_string += '    ' + 'struct' + str(index-1) + ' -> ' + 'struct' + str(index) + ';\n'
                    
                elif self.__output_array[index][1] <= self.__output_array[index-1][1]:
                    #find the parent of such node
                    cnt = index - 2
                    while cnt >= 0:
                        if self.__output_array[cnt][1] < self.__output_array[index][1]:
                            break
                        cnt -= 1
                    self.__output_string += '    ' + 'struct' + str(cnt) + ' -> ' + 'struct' + str(index) + ';\n'
        self.__output_string += '}'
        print self.__output_string
        
#########################################################################
##SemanticAscOutput  - This class is to produce the output in characters
##                When object of the Parser changes state, it will be notified 
##                by the methods and updated automatically
## ######################################################################

class SemanticAscOutput(Output):
    def __init__(self):
        self.__symbol_table = {};
        self.__output_string = ''
        self.__indentation = 0
        
    """
        This function is called by factory after one scope is being deleted. 
        The essential information will be printed in a sorted way
    """
    def get_table(self, symbol_table):
        self.__symbol_table = symbol_table
        self.__output_string += 'SCOPE BEGIN\n'
        for key, value in sorted(self.__symbol_table.items()):
            self.__indentation = 1
            self.__output_string += '  ' * self.__indentation + key + ' =>\n'
            self.visit(value)
            self.__indentation -= 1
        self.__indentation = 0
        self.__output_string += 'END SCOPE'
        
    def visit(self, entry):
        entry.accept(self)
        entry.to_asc_output()
    
    def get_indentation(self):
        return self.__indentation
    
    def set_indentation(self, value):
        self.__indentation = value
        
    def get_output(self):
        return self.__output_string
    
    def add_semantic_output(self, output_string):
        self.__output_string += output_string
        
    """
        This function will print the textual output for semantic analysis
    """
    def print_output(self):
        print self.__output_string
        
        
#########################################################################
##SemanticDotOutput  - This class is to produce the output in diagrams
##                When object of the Parser changes state, it will be notified 
##                by the methods and updated automatically
## ######################################################################

class SemanticDotOutput(Output):
    def __init__(self):
        self.__symbol_table = {};
        self.__output_string = ''
        self.__visited_id = []
    
    """
        This function is called by factory after the last program scope is being deleted. 
        It will use the deep first algorithm to traverse the tree and print the dot output.
    """
    def get_table(self, symbol_table):
        self.__symbol_table = symbol_table
        self.add_semantic_output('digraph X {\n')
        for key, value in sorted(self.__symbol_table.items()):
            self.visit(value)
        
        self.add_semantic_output('subgraph cluster_' + str(id(self)) + ' {\n')
        for key, value in sorted(self.__symbol_table.items()):
            self.add_semantic_output(key + '_' + str(id(self)) + ' [label=\"' + key + '\",shape=box,color=white,fontcolor=black]\n')
        self.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"\",style=invis]\n}\n')
        #print 'current scope completed'
        
        for key, value in sorted(self.__symbol_table.items()):
            self.add_semantic_output(key + '_' + str(id(self)) + ' -> _anchor_' + str(id(value)) + '\n') 
        self.add_semantic_output('}\n')
        #print 'totally finished'

    def visit(self, entry):
        entry.accept(self)
        entry.to_dot_output()
    
    def is_idnumber_exist(self, id_number):
        if id_number in self.__visited_id:
            return True
        return False
    
    def add_idnumber(self, id_number):
        self.__visited_id.append(id_number)
    
    def add_semantic_output(self, output_string):
        self.__output_string += output_string
        
    def print_output(self):
        print self.__output_string
        
    
#########################################################################
##AstAscOutput  - This class is to produce the abstract syntax tree 
##                in characters.
##                When object of the Parser changes state, it will be notified 
##                by the methods and updated automatically
#########################################################################

class AstAscOutput(Output):
    def __init__(self):
        self.__root = None
        self.__output_string = ""
        self.__indentation = 0
    
    def set_root(self, root_node):
        self.__root = root_node
        self.__current_node = self.__root
        self.visit(self.__current_node)
        
    def visit(self, node):
        node.accept(self)
        node.to_asc_output()
        
    def get_indentation(self):
        return self.__indentation
    
    def set_indentation(self, value):
        self.__indentation = value
        
    def get_output(self):
        return self.__output_string
    
    def add_semantic_output(self, output_string):
        self.__output_string += output_string
        
    def get_table(self, symbol_table):
        pass
    
    def print_output(self):
        print self.__output_string
        
        
#########################################################################
##AstDotOutput  - This class is to produce the abstract syntax tree 
##                in dot diagram.
##                When object of the Parser changes state, it will be notified 
##                by the methods and updated automatically
## ######################################################################

class AstDotOutput(Output):
    def __init__(self):
        self.__root = None
        self.__output_string = ''
        
    def set_root(self, root_node):
        self.__root = root_node
        self.__current_node = self.__root
        self.add_semantic_output('digraph X{\n')
        self.visit(self.__current_node) 
        self.add_semantic_output('}\n')
            
    def visit(self, node):
        node.accept(self)
        node.to_dot_output()
        
    def add_semantic_output(self, output_string):
        self.__output_string += output_string
        
    def get_table(self, symbol_table):
        pass
            
    def print_output(self):
        print self.__output_string
        
        
        