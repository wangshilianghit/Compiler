#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
## Environment.py - This module is used for building the environment 
##             
#########################################################################

import copy

#########################################################################
## Box - This class is the base class for environment box
##
#########################################################################
class Box( object ):
    def __init__(self):
        pass
    
    
#########################################################################
## IntegerBox - This class derived from Box to hold the integer
##              value
##
#########################################################################
class IntegerBox( object ):
    def __init__(self):
        self.__value = 0
        
    def get_value(self):
        return self.__value
    
    def set_value(self, value):
        self.__value = value
        
    """
        This function will copy another box to itself
    """
    def copy(self, value_box):
        self.set_value(value_box.get_value())


#########################################################################
## ArrayBox - This class derived from Box to make up the value of an array
##
#########################################################################
class ArrayBox( object ):
    """
        This function will initialize a number of new boxes
    """
    def __init__(self, element_box, element_number):
        self.__array = []
        self.__max_index = element_number - 1
        for i in range(0, element_number):
            self.__array.append(copy.copy(element_box))
    
    def is_valid_index(self, index):
        if index >= 0 and index <= self.__max_index:
            return True
        return False
    
    """
        This function will return the new box based on the array index
    """
    def get_element(self, index):
        return self.__array[index]
    
    """
        This function will set the new box based on the array index
    """
    def set_element(self, index, value):
        self.__array[index] = value
        
    """
        This function will copy another box to itself
    """
    def copy(self, value_box):
        for i in range(0, self.__max_index):
            self.__array[i].copy(value_box.get_element(i))
        

#########################################################################
## RecordBox - This class derived from Box to hold the boxes that make up 
##          the value of a record
##
#########################################################################
class RecordBox( object ):
    """
        This constructor did nothing, the initialization has to be finished with
        the add_element_box function
     """
    def __init__(self):
        self.__record = {}
        
    
    def get_environment(self):
        return self.__record
    
    """
        This function will add the new element box
    """ 
    def add_element_box(self, key, element_box):
        self.__record[key] = element_box
    
    """
        This function will get the box based on the value name
    """
    def get_element_box(self, key):
        return self.__record[key]
    
    """
        This function will copy another box to itself
    """
    def copy(self, value_box):
        for key, value in self.__record.items():
            self.__record[key].copy(value_box.get_element_box(key))
        
#########################################################################
## DereferenceBox - This class derived from Box to hold the boxes that make up 
##          the value of a record
##
#########################################################################
class DereferenceBox( object ):
    def __init__(self, reference_box):
        self.__reference_box = reference_box
        
    def get_reference_box(self):
        return self.__reference_box
    
        
