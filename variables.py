#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-

import re
import sys
import copy

def stripName(string): # vrati list rozseknute promenne/konstanty - podle @
    return string.split('@')

def NoFrame(err):
    sys.stderr.write(err)
    sys.exit(55)

def NoVarError(err):
    sys.stderr.write(err)
    sys.exit(54)

def MissValError(err):
    sys.stderr.write(err)
    sys.exit(56)
    
def StrError(err):
    sys.stderr.write(err)
    sys.exit(58)
    
def SemanticError(err):
    sys.stderr.write(err)
    sys.exit(52)   
    
def ArgError(err):
    sys.stderr.write(err)
    sys.exit(10)
    
def XmlStructError(err):
    sys.stderr.write(err)
    sys.exit(32)
    
def RunError(err):
    sys.stderr.write(err)
    sys.exit(57)
    
def OperandTypeError(err):
    sys.stderr.write(err)
    sys.exit(53)

class Variable: # jednotliva promenna
    def __init__(self,name,typ,value): # inicializuj pri DEFVAR
        self.name = name
        self.typ = typ
        self.value = value
        
class StackItem: # jednotliva promenna
    def __init__(self,typ,value): # inicializuj pri pridavani na datovy zasobnik
        self.typ = typ
        self.value = value
 
class FrameStack: # trida pro zasobnik ramcu a datovy zasobnik a zasobnik volani
    def __init__(self):
        self.stack = []
        self.size = 0
        
    def popStack(self): # popni ven prvni prvek
        self.size = self.size - 1 
        pop = copy.deepcopy(self.stack[0])
        self.stack.pop(0)
        return pop
        
    def pushStack(self,F): # strc prvek na vrchol zasobniku
        self.stack.insert(0,F)
        self.size = self.size + 1
        
    def stackSize(self): # vrat pocet ramcu v zasobniku pro kontrolu
        return self.size
    
    def getLocalFrame(self): # vrat odkaz na vrchol zasobniku => LF
        return self.stack[0]       
        
class Frame: # samostatny ramec, vychazi z nej GF a TF, LF je jen odkaz na prvni prvek v zasobniku ramcu. TF bude vzdy vytvoren a znicen!
    def __init__(self):
        self.var = {} # struktura slovniku: {'jmeno_promenne' : Variable_objekt}
    
    def addVar(self,V): # pridej promennou do slovniku
        if V.name not in self.var:
            self.var[V.name] = V
            return 0
        return 1
        
    def retVar(self,name): # vrat promennou ze slovniku
        if name not in self.var:
            return None
        else:
            return self.var[name]
        
    def updConst(self,old,typ,value): # updatuj promenou ve slovniku ramce pomoci konstanty
        self.var[old.name].typ = typ
        self.var[old.name].value = value
    
TF = None # globalni promenna TF, na zacatku nedefinovana   
Labels = {} # slovnik navesti, analyza v prvnim behu
GF = Frame() # globalni ramec promennych
re_right_numbers = re.compile('\\\d\d\d')
re_bad_numbers = re.compile('\\\D|\\\d\D|\\\d\d\D|#')
re_int = re.compile('^[\+\-]?\d+$')
re_label = re.compile('^[a-zA-Zá-žÁ-Ž\_\-$&%\*!\?][\da-zA-Zá-žÁ-Ž\_\-$&%\*!\?]*$')
re_var = re.compile('^(LF|TF|GF)\@[a-zA-Zá-žÁ-Ž\_\-$&%\*!\?][\da-zA-Zá-žÁ-Ž\_\-$&%\*!\?]*$')
availableOps_0 = ['CREATEFRAME','PUSHFRAME','POPFRAME','RETURN','BREAK']
availableOps_1 = ['DEFVAR','CALL','PUSHS','POPS','WRITE','LABEL','JUMP','EXIT','DPRINT']
availableOps_2 = ['MOVE','INT2CHAR','READ','STRLEN','TYPE']
availableOps_3 = ['ADD','SUB','MUL','IDIV','LT','GT','EQ','AND','OR','NOT','STR2INT','CONCAT','GETCHAR','SETCHAR','JUMPIFEQ','JUMPIFNEQ']
availableFrames = ['TF','GF','LF']
