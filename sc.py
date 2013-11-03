#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
##  sc.py  - This file implements the driver program.
##            The option "-s" is to run the scanner by itself and to produce
##            a list of recognized tokens.
##            start position, end position for it's constructor
##            
##            If a second argument is given, it will process the file name 
##            of a simple program
##            If no filename is given, you should read the program from 
##            standard input instead.
#########################################################################

import sys
import os
from Scanner import Scanner
from Parser import Parser
from Visitor import Output
from Visitor import ParserAscOutput
from Visitor import ParserDotOutput
from Visitor import SemanticAscOutput
from Visitor import SemanticDotOutput
from Visitor import AstAscOutput
from Visitor import AstDotOutput
from Factory import ParserFactory
from Factory import SemanticFactory
from Factory import AstFactory
from Interpreter import Interpreter
from CodeGenerator import CodeGenerator
from ImprovedCodeGenerator import ImprovedCodeGenerator

try:
    #if the argument is not 1 or 2 or 3 then abort the program
    if len(sys.argv) < 1 or len(sys.argv) > 4:
        print 'error: the drier program should be invoked as follows: Invocation = \"./sc\" [\"-\" (\"-\" (\"s\"|\"c\"|\"t\"|\"a\"|\"i\")] [filename]'
        exit (-1)
    
    #if there are no argument except for the name of the program, the driver is supposed to generate code for an input program
    elif len(sys.argv) == 1:
        input_string = ''
        new_line = ''
        while new_line != 'stop\n':
            try:
                input_string += new_line
                new_line = raw_input() + '\n'
            except (EOFError, KeyboardInterrupt):
                break
        
        #construct the object of Scanner by it's constructor
        scanner = Scanner(input_string)
        #produce a list of tokens by calling it's function
        token_array = scanner.all()
        #if produces the error message, then display it
        if scanner.have_error() == True:
            print scanner.get_error_message()

        else:
            output = Output()
            factory = AstFactory(output)
            parser = Parser(token_array, output, factory)
            #print 'parse start'
            parser.parse()
            print 'parse success'
            if parser.get_error_message() != '':
                print parser.get_error_message()
                exit()
                
            symbol_table = factory.get_symbol_table()
            ast_root = factory.get_ast_root()
            #print 'code generation start'
            if symbol_table:
                code_generation = CodeGenerator(symbol_table, ast_root)
                code_generation.generate_code()
                code_generation.print_code()
        
    else:
        #if the option is -s, it will run the scanner and produce a list of tokens
        if  sys.argv[1] == '-s':
            input_string = '';
            #if the second argument exist, it means read from file
            if len(sys.argv) == 3:
                #Read the file
                if os.path.exists(sys.argv[2]):
                    f = open(sys.argv[2])
                    input_string = f.read()
                #if the directory of the file does not exist
                else:
                    print 'error: The directory of the file does not exist'
            #if the second argument does not exist, it will read from standard input
            elif len(sys.argv) == 2:
                while True:
                    try:
                        input_string += raw_input() + '\n'
                    except (EOFError, KeyboardInterrupt):
                        break
            #construct the object of Scanner by it's constructor
            scanner = Scanner(input_string)
            #produce a list of tokens by calling it's function
            token_array = scanner.all()
            #display all the tokens
            for token in token_array:
                token.display()
            #if produces the error message, then display it
            if scanner.have_error()== True:
                print scanner.get_error_message()
        
        #if the option is -c, it will run the Parser and produce the syntax tree
        elif sys.argv[1] == '-c':
            input_string = '';
            #if the second argument doesn't exist.
            if len(sys.argv) == 2:
                while True:
                    try:
                        input_string += raw_input() + '\n'
                    except (EOFError, KeyboardInterrupt):
                        break
                
                #construct the object of Scanner by it's constructor
                scanner = Scanner(input_string)
                #produce a list of tokens by calling it's function
                token_array = scanner.all()
            
                output = ParserAscOutput()
                factory = ParserFactory(output)
                parser = Parser(token_array, output, factory)     
                print 'parse begin'
                parser.parse()  
                print 'parse success'
                output.print_output()
                print parser.get_error_message()
                        
            #if the second argument exist, it means either to read from file or produce a graphic output.
            elif len(sys.argv) == 3:
                #if the second argument is -g, it means to produce a graphic output. 
                if sys.argv[2] == '-g': 
                    while True:
                        try:
                            input_string += raw_input() + '\n'
                        except (EOFError, KeyboardInterrupt):
                            break
                    #construct the object of Scanner by it's constructor
                    scanner = Scanner(input_string)
                    #produce a list of tokens by calling it's function
                    token_array = scanner.all()
                    output = ParserDotOutput()
                    factory = ParserFactory(output)
                    parser = Parser(token_array, output, factory)
                    #print 'parser begin'
                    parser.parse()
                    #print 'parser success'
                    output.print_output()
                        
                #Otherwise, it means to read from the file
                elif os.path.exists(sys.argv[2]):
                    f = open(sys.argv[2])
                    input_string = f.read()
                    #construct the object of Scanner by it's constructor
                    scanner = Scanner(input_string)
                    #produce a list of tokens by calling it's function
                    token_array = scanner.all()
                    output = ParserAscOutput()
                    factory = ParserFactory(output)
                    parser = Parser(token_array, output, factory)
                    parser.parse()
                    output.print_output()
                    print parser.get_error_message()
                        
                #if the directory of the file does not exist
                else:
                    print 'error: The directory of the file does not exist'
            
            #if the third argument exist, it means both to read from file and produce a graphic output.
            elif len(sys.argv) == 4:
                #if the second argument is -g, it means to produce a graphic output. 
                if sys.argv[2] == '-g':
                    #judge whether the filename in the third argument is exist
                    if os.path.exists(sys.argv[3]):
                        f = open(sys.argv[3])
                        input_string = f.read()
                        #construct the object of Scanner by it's constructor
                        scanner = Scanner(input_string)
                        token_array = scanner.all()
                        output = ParserDotOutput()
                        factory = ParserFactory(output)
                        parser = Parser(token_array, output, factory)
                        parser.parse()
                        output.print_output()
                    else:
                        print 'error: The directory of the file does not exist'
                        
                else :
                    print 'error: need -g to produce a graphic output'
                    
        #if the argument is -t, it will build and display the symbol table for the given input program.
        elif sys.argv[1] == '-t':
            input_string = '';
            #if the second argument doesn't exist.
            if len(sys.argv) == 2:
                while input_string != 'stop':
                    try:
                        input_string += raw_input() + '\n'
                    except (EOFError, KeyboardInterrupt):
                        break
                
                #construct the object of Scanner by it's constructor
                scanner = Scanner(input_string)
                #produce a list of tokens by calling it's function
                token_array = scanner.all()
                #if produces the error message, then display it
                if scanner.have_error() == True:
                    print scanner.get_error_message()
    
                else:
                    #print 'scanner complete'
                    output = SemanticAscOutput()
                    factory = SemanticFactory(output)
                    parser = Parser(token_array, output, factory)
                    parser.parse()
                    output.print_output()
                    print parser.get_error_message()
                    
            #if the second argument exist, it means either to read from file or produce a graphic output.
            elif len(sys.argv) == 3:
                #if the second argument is -g, it means to produce a graphic output. 
                if sys.argv[2] == '-g': 
                    while True:
                        try:
                            input_string += raw_input() + '\n'
                        except (EOFError, KeyboardInterrupt):
                            break
                    #construct the object of Scanner by it's constructor
                    scanner = Scanner(input_string)
                    #produce a list of tokens by calling it's function
        
                    token_array = scanner.all()
                    #if produces the error message, then display it
                    if scanner.have_error() == True:
                        print scanner.get_error_message()
                    else:
                        output = SemanticDotOutput()
                        factory = SemanticFactory(output)
                        parser = Parser(token_array, output, factory)
                        parser.parse()
                        output.print_output()
                        
                #Otherwise, it means to read from the file
                elif os.path.exists(sys.argv[2]):
                    f = open(sys.argv[2])
                    input_string = f.read()
                    #construct the object of Scanner by it's constructor
                    scanner = Scanner(input_string)
                    #produce a list of tokens by calling it's function
                    
                    token_array = scanner.all()
                    #if produces the error message, then display it
                    if scanner.have_error() == True:
                        print scanner.get_error_message()
                    else:
                        output = SemanticAscOutput()
                        factory = SemanticFactory(output)
                        parser = Parser(token_array, output, factory)
                        parser.parse()
                        output.print_output()
                        print parser.get_error_message()
                        
                #if the directory of the file does not exist
                else:
                    print 'error: The directory of the file does not exist'
            
            #if the third argument exist, it means both to read from file and produce a graphic output.
            elif len(sys.argv) == 4:
                #if the second argument is -g, it means to produce a graphic output. 
                if sys.argv[2] == '-g':
                    #judge whether the filename in the third argument is exist
                    if os.path.exists(sys.argv[3]):
                        f = open(sys.argv[3])
                        input_string = f.read()
                        #construct the object of Scanner by it's constructor
                        scanner = Scanner(input_string)
                        #produce a list of tokens by calling it's function
                        
                        token_array = scanner.all()
                        #if produces the error message, then display it
                        if scanner.have_error() == True:
                            print scanner.get_error_message()
                        else:
                            output = SemanticDotOutput()
                            factory = SemanticFactory(output)
                            parser = Parser(token_array, output, factory)
                            parser.parse()
                            output.print_output()
                    else:
                        print 'error: The directory of the file does not exist'
                        
                else :
                    print 'error: need -g to produce a graphic output'
                    
        #if the argument is -a, it will build the AST
        elif sys.argv[1] == '-a':
            input_string = '';
            #if the second argument doesn't exist.
            new_line = ''
            if len(sys.argv) == 2:
                while new_line != 'stop\n':
                    try:
                        input_string += new_line
                        new_line = raw_input() + '\n'
                    except (EOFError, KeyboardInterrupt):
                        break
                
                #construct the object of Scanner by it's constructor
                scanner = Scanner(input_string)
                #produce a list of tokens by calling it's function
                token_array = scanner.all()
                #if produces the error message, then display it
                if scanner.have_error() == True:
                    print scanner.get_error_message()
    
                else:
                    #print 'scanner complete'
                    output = AstAscOutput()
                    factory = AstFactory(output)
                    parser = Parser(token_array, output, factory)
                    parser.parse()
                    output.print_output()
                    print parser.get_error_message()
                    
                    
            #if the second argument exist, it means either to read from file or produce a graphic output.
            elif len(sys.argv) == 3:
                #if the second argument is -g, it means to produce a graphic output. 
                new_line = ''
                if sys.argv[2] == '-g': 
                    while new_line != 'stop\n':
                        try:
                            input_string += new_line
                            new_line = raw_input() + '\n'
                        except (EOFError, KeyboardInterrupt):
                            break
                    #construct the object of Scanner by it's constructor
                    scanner = Scanner(input_string)
                    #produce a list of tokens by calling it's function
        
                    token_array = scanner.all()
                    #if produces the error message, then display it
                    if scanner.have_error() == True:
                        print scanner.get_error_message()
                    else:
                        #print 'scanner complete'
                        output = AstDotOutput()
                        factory = AstFactory(output)
                        parser = Parser(token_array, output, factory)
                        parser.parse()
                        output.print_output()
                        
                #Otherwise, it means to read from the file
                elif os.path.exists(sys.argv[2]):
                    f = open(sys.argv[2])
                    input_string = f.read()
                    #construct the object of Scanner by it's constructor
                    scanner = Scanner(input_string)
                    #produce a list of tokens by calling it's function
                    
                    token_array = scanner.all()
                    #if produces the error message, then display it
                    if scanner.have_error() == True:
                        print scanner.get_error_message()
                    else:
                        #print 'scanner complete'
                        output = AstAscOutput()
                        factory = AstFactory(output)
                        parser = Parser(token_array, output, factory)
                        parser.parse()
                        print 'parse complete'
                        output.print_output()
                        print parser.get_error_message()
                        
                #if the directory of the file does not exist
                else:
                    print 'error: The directory of the file does not exist'
            
            #if the third argument exist, it means both to read from file and produce a graphic output.
            elif len(sys.argv) == 4:
                #if the second argument is -g, it means to produce a graphic output. 
                if sys.argv[2] == '-g':
                    #judge whether the filename in the third argument is exist
                    if os.path.exists(sys.argv[3]):
                        f = open(sys.argv[3])
                        input_string = f.read()
                        #construct the object of Scanner by it's constructor
                        scanner = Scanner(input_string)
                        #produce a list of tokens by calling it's function
                        
                        token_array = scanner.all()
                        #if produces the error message, then display it
                        if scanner.have_error() == True:
                            print scanner.get_error_message()
                        else:
                            #print 'scanner complete'
                            output = AstDotOutput()
                            factory = AstFactory(output)
                            parser = Parser(token_array, output, factory)
                            parser.parse()
                            output.print_output()
                    else:
                        print 'error: The directory of the file does not exist'
                        
                else :
                    print 'error: need -g to produce a graphic output'
                    
            
        #if the argument is -i, it will build and display the symbol table for the given input program.
        elif sys.argv[1] == '-i':
            input_string = ''
            new_line = ''
            #if the second argument doesn't exist.
            if len(sys.argv) == 2:
                while new_line != 'stop\n':
                    try:
                        input_string += new_line
                        new_line = raw_input() + '\n'
                    except (EOFError, KeyboardInterrupt):
                        break
                
                #print input_string
                #construct the object of Scanner by it's constructor
                scanner = Scanner(input_string)
                #produce a list of tokens by calling it's function
                token_array = scanner.all()
                #if produces the error message, then display it
                if scanner.have_error() == True:
                    print scanner.get_error_message()
    
                else:
                    #print 'scanner complete'
                    output = Output()
                    factory = AstFactory(output)
                    parser = Parser(token_array, output, factory)
                    #print 'parse start'
                    parser.parse()
                    #print 'parse success'
                    if parser.get_error_message() != '':
                        print parser.get_error_message()
                        exit()
                        
                    symbol_table = factory.get_symbol_table()
                    ast_root = factory.get_ast_root()
                    #print 'interpret start'
                    if symbol_table and ast_root:
                        interpreter = Interpreter(symbol_table, ast_root)
                        interpreter.interpret()
                        
        #if the argument is -x, it will run the improved code generator 
        elif sys.argv[1] == '-x':
            input_string = ''
            new_line = ''
            #if the second argument doesn't exist.
            if len(sys.argv) == 2:
                while new_line != 'stop\n':
                    try:
                        input_string += new_line
                        new_line = raw_input() + '\n'
                    except (EOFError, KeyboardInterrupt):
                        break
                
                #print input_string
                #construct the object of Scanner by it's constructor
                scanner = Scanner(input_string)
                #produce a list of tokens by calling it's function
                token_array = scanner.all()
                #if produces the error message, then display it
                if scanner.have_error() == True:
                    print scanner.get_error_message()
    
                else:
                    #print 'scanner complete'
                    output = Output()
                    factory = AstFactory(output)
                    parser = Parser(token_array, output, factory)
                    #print 'parse start'
                    parser.parse()
                    #print 'parse success'
                    if parser.get_error_message() != '':
                        print parser.get_error_message()
                        exit()
                        
                    symbol_table = factory.get_symbol_table()
                    ast_root = factory.get_ast_root()
                    #print 'improved code generator start'
                    if symbol_table:
                        improvedCodeGenerator = ImprovedCodeGenerator(symbol_table, ast_root)
                        improvedCodeGenerator.generate_code()
                        improvedCodeGenerator.print_code()
                    
            #if the second argument exist, it means to read from file
            elif len(sys.argv) == 3:
                if os.path.exists(sys.argv[2]):
                    f = open(sys.argv[2])
                    input_string = f.read()
                    input_string += '\n'
                    #construct the object of Scanner by it's constructor
                    scanner = Scanner(input_string)
                    #produce a list of tokens by calling it's function
                    token_array = scanner.all()
                    #if produces the error message, then display it
                    if scanner.have_error() == True:
                        print scanner.get_error_message()
                    else:
                        #print 'scanner complete'
                        output = Output()
                        factory = AstFactory(output)
                        parser = Parser(token_array, output, factory)
                        #print 'parse start'
                        parser.parse()
                        #print 'parse success'
                        if parser.get_error_message() != '':
                            print parser.get_error_message()
                            exit()
                            
                        symbol_table = factory.get_symbol_table()
                        ast_root = factory.get_ast_root()
                        #print 'interpret start'
                        if symbol_table:
                            improvedCodeGenerator = ImprovedCodeGenerator(symbol_table, ast_root)
                            improvedCodeGenerator.generate_code()
                            improvedCodeGenerator.print_code()
                        
                #if the directory of the file does not exist
                else:
                    print 'error: The directory of the file does not exist'
            
        else:
            #if other argument is given, the driver is supposed to generate an file based on the argument
            if os.path.exists(sys.argv[1]):
                f = open(sys.argv[1])
                input_string = f.read()
                input_string += '\n'
                #construct the object of Scanner by it's constructor
                scanner = Scanner(input_string)
                #produce a list of tokens by calling it's function
                token_array = scanner.all()
                #if produces the error message, then display it
                if scanner.have_error() == True:
                    print scanner.get_error_message()
        
                else:
                    output = Output()
                    factory = AstFactory(output)
                    parser = Parser(token_array, output, factory)
                    #print 'parse start'
                    parser.parse()
                    #print 'parse success'
                    if parser.get_error_message() != '':
                        print parser.get_error_message()
                        exit()
                        
                    symbol_table = factory.get_symbol_table()
                    ast_root = factory.get_ast_root()
                    #print 'code generation start'
                    if symbol_table and ast_root:
                        code_generation = CodeGenerator(symbol_table, ast_root)
                        code_generation.generate_code()
                        code_generation.print_code()
            else:
                print 'error: The directory of the file does not exist' 
        
except Exception:
    print 'error: error exist'
    
