#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################


#########################################################################
##   text_wrap  - get the string between the two characters
##
## ######################################################################
def text_wrap(start_str, end_str, process_string):
    start = process_string.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = process_string.find(end_str,start)
        if end >= 0:
            return process_string[start:end].strip()
        else :
            return process_string
    else :
        return process_string
        