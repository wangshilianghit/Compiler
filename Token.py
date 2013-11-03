#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
##   Token  - This class accepts the token name, the token value, the 
##            current line number and the 
##            start position, end position for it's constructor
##
## ######################################################################

class Token:
    def __init__(self, token_name, value, line, start_index, end_index):
        self.__token_name = token_name
        self.__value = value
        self.__line_number = line
        self.__start_index = start_index
        self.__end_index = end_index
        
    def display(self):
        display_string = self.__token_name 
        if str(self.__value) != '':
            display_string += '<' + str(self.__value) + '>'
        display_string += '@(' + str(self.__start_index) + ', ' + str(self.__end_index) + ')'
        print display_string
        
    def get_display_string(self):
        display_string = self.__token_name 
        if str(self.__value) != '':
            display_string += '<' + str(self.__value) + '>'
        display_string += '@(' + str(self.__start_index) + ', ' + str(self.__end_index) + ')'
        return display_string

    def get_line_number(self):
        return self.__line_number

    def get_token_name(self):
        return self.__token_name

    def get_token_value(self):
        return self.__value
    
    def get_token_start_index(self):
        return self.__start_index
    
    def get_token_end_index(self):
        return self.__end_index
    

        
