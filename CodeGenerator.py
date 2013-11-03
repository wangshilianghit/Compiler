#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
# CodeGenerator.py  - This module will performs storage allocation for 
#                  all variables in the ST and generates instructions 
#                  during a post-order-style traversal of the AST.
#########################################################################

from SymbolTable import Variable

class CodeGenerator:
    def __init__(self, symbol_table, ast_root):
        self.__symbol_table = symbol_table
        self.__ast_root = ast_root
        self.__output_code = ''
        self.__false_label_number = 0
        self.__end_label_number = 0
        self.__repeat_label_number = 0
        
    """
        This function is called by the generate_code function 
        It will perform storage allocation for all variables 
        in the ST
    """
    def __storage_allocation(self):
        offset = 0
        for key, value in sorted(self.__symbol_table.items()):
            #it will perform storage allocation for all variables in the ST
            if isinstance(value, Variable):
                #print 'perform storage allocation for the ' + str(key)
                #set the address offset for each variable
                value.set_address_offset(offset)
                
                variable_type = value.get_type()
                variable_type.accept(self)
                variable_type.to_storage_allocation()
                size = variable_type.get_size()
                offset += size
                
                #print 'storage allocation for the ' + str(key) + ' completed. size = ' + str(variable_type.get_size()) \
                #+ ' start address = ' + str(value.get_address_offset())
                
        self.add_code('.data\n')
        self.add_code('variable:\n')
        self.add_code('\t.space\t' + str(offset) + ', ' + str(0) + '\n')
        self.add_code('\t.align\t' + str(2) + '\n')
        self.add_code('printformat:\n')
        self.add_code('\t.ascii\t\"%d\\n\\000\"\n')
        self.add_code('\t.text\n')
        self.add_code('\t.align\t2\n')
        self.add_code('scanformat:\n')
        self.add_code('\t.ascii\t\"%d\\000\"\n')
        self.add_code('\t.text\n')
        self.add_code('\t.align\t2\n')
        self.add_code('diverrorformat:\n')
        self.add_code('\t.ascii\t\"error: the expression on the right-hand side of the DIV cannot evaluate to zero at line %d, position: (\
%d, %d)\\n\\000\"\n')
        self.add_code('\t.text\n')
        self.add_code('\t.align\t2\n')
        self.add_code('moderrorformat:\n')
        self.add_code('\t.ascii\t\"error: the expression on the right-hand side of the MOD cannot evaluate to zero at line %d, position: (\
%d, %d)\\n\\000\"\n')
        self.add_code('\t.text\n')
        self.add_code('\t.align\t2\n')
        self.add_code('indexerrorformat:\n')
        self.add_code('\t.ascii\t\"error: the index value %d is out of bounds at line %d, position: (\
%d, %d)\\n\\000\"\n')
        self.add_code('\t.text\n')
        self.add_code('\t.align\t2\n')
        self.add_code('\t.global\tmain\n')
        
    """
        This function is called by the driver program
        It will perform storage allocation for all variables in the ST and 
        generates instructions during a post-order-style traversal of the 
        AST
    """
    def generate_code(self):
        #print 'start perform storage allocation'
        self.__storage_allocation()
        #print 'storage allocation success'
        #print 'start generates instructions of this program'
        self.add_code('main:\n')
        self.add_code('\tstmfd\tsp!, {fp, lr}\n')
        self.add_code('\tadd\tfp, sp, #4\n')
        
        if self.__ast_root:
            #r7 is used to store the base address
            self.add_code('\tldr\tr7, variablepointer\n')
            self.__ast_root.accept(self)
            self.__ast_root.to_code_generation()
        self.add_code('\tsub\tsp, fp, #4\n')
        self.add_code('\tldmfd\tsp!, {fp, lr}\n')
        self.add_code('\tbx\tlr\n')
        
        self.add_code('\t.ltorg\n')
        self.add_code('\nprintformatpointer:\n')
        self.add_code('\t.word\tprintformat\n')
        self.add_code('\nscanformatpointer:\n')
        self.add_code('\t.word\tscanformat\n')
        self.add_code('\ndiverrorformatpointer:\n')
        self.add_code('\t.word\tdiverrorformat\n')
        self.add_code('\nmoderrorformatpointer:\n')
        self.add_code('\t.word\tmoderrorformat\n')
        self.add_code('\nindexerrorformatpointer:\n')
        self.add_code('\t.word\tindexerrorformat\n')
        self.add_code('\nvariablepointer:\n')
        self.add_code('\t.word\tvariable\n')
        #print 'Generate the instructions of the program finished'
        
    def add_code(self, code):
        self.__output_code += code
        
    def generate_false_label(self):
        self.__false_label_number += 1
        label_name = '.false' + str(self.__false_label_number)
        return label_name
    
    def generate_end_label(self):
        self.__end_label_number += 1
        label_name = '.end' + str(self.__end_label_number)
        return label_name
    
    def generate_repeat_label(self):
        self.__repeat_label_number += 1
        label_name = '.repeat' + str(self.__repeat_label_number)
        return label_name
    
    def print_code(self):
        print self.__output_code
        
        
        