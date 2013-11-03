#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
##   Scanner  - This class accepts a string(representing the source text)
##              in its constructor.   
##
#########################################################################

### Sets of characters ###############################################

# all characters that are considered whitespace
eol = "\n\r"
blanks = " \t\f" + eol

# all characters that are (or start) special symbols
symbols = ";:,.+-*=#()[]<>"

# first(identifier), i.e. all character that start an identifier
letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# first(number), i.e. all characters that start a number
digits = "0123456789"

### Sets of strings ##################################################

# all identifiers that are in fact keywords
keywords = ["ARRAY", "BEGIN", "CONST", "DIV", "DO", "ELSE", "END", \
            "IF", "MOD", "OF", "PROGRAM", "READ", "RECORD", "REPEAT", \
            "THEN", "TYPE", "UNTIL", "VAR", "WHILE", "WRITE", "PROCEDURE", "RETURN"]


from Token import *


class Scanner:
    def __init__(self, source):
        # source text and cached length
        self.__src = source
        self.__len = len(source)
        # current position in source text
        self.__pos = 0
        self.__line = 1
        self.__have_error = False
        # position current token started at
        self.__start = 0
        # next() was not called yet
        self.__clean = True
        self.__error_message = ''
    
    """
    Are we still inside the source text?
    """
    def __valid( self ):
        return self.__pos < self.__len
    
    """
    Character at current position in source text.
    """
    def __char( self ):
        return self.__src[self.__pos]
    
        
    """
    Advance the current position in the source text!
    """
    def __tick( self ):
        assert self.__valid() 
        self.__pos += 1
        
        
    """
    Judge whether it is a start of a potential comment
    """
    def __is_start_comment( self ):
        #Find the start of comment by searching (*
        if self.__pos + 1 < self.__len and self.__src[self.__pos] == '(' and self.__src[self.__pos + 1]=='*':
            self.__pos += 2
            return True
        return False
    
    """
    We found a potential comment, process it in some way.
    """
    def __comment( self ):
        #Find the end of comment by searching *)
        while self.__pos + 1 < self.__len and not(self.__src[self.__pos]=='*' and self.__src[self.__pos + 1]==')'):
            self.__tick()
        
        #if the whole source text has been processed. It will return a EOF token
        if self.__pos + 1 == self.__len:
            self.__error('error: ' + 'Unfinished comment statement' + ' Line:' + str(self.__line) + ' Position:' + str(self.__pos))
        self.__pos += 2

    """
    Process an identifier or a keyword.
    """
    def __identifierOrKeyword( self ):
        current_string = ""
         
        while self.__valid() and self.__char() in letters+digits:
            current_string += self.__char()
            self.__tick()
            
        if current_string in keywords:
            token = Token(current_string, '', self.__line, self.__start, self.__pos - 1)
        else:
            token = Token('identifier', current_string, self.__line, self.__start, self.__pos - 1)
            
        return token

    """
      Process a number.
    """
    def __number( self ):
        current_string  = ""
        
        while self.__valid() and self.__char() in digits:
            current_string += self.__char()
            self.__tick()
        
        # TODO: check for floating point here...
        
        token = Token( "integer", int(current_string), self.__line, self.__start, self.__pos - 1 )
        
        return token
    
    """
        Process a symbol.
    """
    def __symbol( self ):
        current_string = ""
        
        if self.__valid() and self.__char() in symbols:
            current_string += self.__char()
            self.__tick()
            if current_string in ":<>":
                if self.__valid() and self.__char() in "=":
                    current_string += self.__char()
                    self.__tick()
        
        token = Token( current_string, '', self.__line, self.__start, self.__pos - 1 )
        
        return token

    """
        Return the next token in the source text, or an "eof"
        token if the input is exhausted. Raises an exception
        for illegal characters.
    """
    def next(self):
        # mark it "dirty," can't call "all()" anymore
        self.__clean = False
        
        # skip leading whitespace and comments (if any)
        while self.__valid():
            if self.__char() in blanks:
                if self.__char() in eol:
                    self.__line += 1
                self.__tick()
            #Find the start of comment by searching (*
            elif self.__is_start_comment():
                self.__comment()
            else:
                break

        # reset token start position
        self.__start = self.__pos
        
        # recognize an actual token now (we hope)
        if self.__valid():
            if self.__char() in letters:
                token = self.__identifierOrKeyword()
            elif self.__char() in digits:
                token = self.__number()
            elif self.__char() in symbols:
                token = self.__symbol()
            else:
                # nope, something we can't handle...
                self.__have_error = True
                self.__error('error: ' + 'Unexpected symbol: ' +  self.__char() + ' Line:' + str(self.__line) + ' Position:' + str(self.__pos))
                self.__tick()
                token =  Token('eof','', self.__line, self.__pos, self.__pos)

        if not self.__valid():
            token =  Token('eof','', self.__line, self.__pos, self.__pos)
            
        return token
            
    
    """
        Return the list of token objects for the complete source
        text, including the trailing "eof" token. Only works if
        next() has not been called yet.
    """
    def all(self):
        #it will call function next() repeatedly to implement
        assert self.__clean
        token_array = []
        while self.__valid():
            token = self.next()
            if token.get_token_name() != 'eof':
                token_array.append( token )
                
        token_array.append(Token('eof','', self.__line,self.__pos,self.__pos))
        return token_array
        
    """
        Return whether the scanner part has errors
    """
    def have_error(self):
        return self.__have_error
    
    """
        Set the error if it detects the error
    """
    def __error(self, error_message):
        self.__have_error = True
        self.__error_message += error_message + '\n'
        
    """
        Return all the errors in Scanner part
    """
    def get_error_message(self):
        return self.__error_message
    
