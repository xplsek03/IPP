#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-

from variables import *

import re

def translateString(string):
    i = 0
    sc = 0
    string2 = ''
    skip = False  
    for s in string:
        if skip:
            if sc == 2:
                sc = 0
                skip = False
            else:
                sc = sc+1
            i = i+1
            continue        
        if s == '\\':
            number = string[i+1:i+4]
            number = int(number)
            string2 = string2 + chr(number)
            skip = True
        else:
            string2 = string2 + s
        i = i+1     
    return string2            

def testForVar(typ,string):
    if string is None or typ != 'var':
        return 1
    if not re.match(re_var,string):
        return 1
    return 0

def testForLabel(typ,string):
    if string is None or typ != 'label':
        return 1
    if not re.match(re_label,string):
        return 1
    return 0

def testForSymb(typ,string):
    if not testForConst(typ,string):
        return 0
    if not testForVar(typ,string):
        return 0
    return 1

def testForType(typ,string):
    if typ != 'type':
        return 1
    if string != 'string' and string != 'int' and string!= 'bool':
        return 1
    return 0

def testForConst(typ,string):
    if typ != 'string' and string is None: # jedine co muze byt prazdne je retezec, v otm pripade netestovat na findall, viz dale
        return 1
    if typ == 'int':
        if not re.match(re_int,string):
            return 1
    elif typ == 'bool':
        if string != 'true' and string != 'false':
            return 1
    elif typ == 'nil':
        if string != 'nil':
            return 1
    elif typ == 'string':
        if string is None:
            return 0
        else:
            bad = re.findall(re_bad_numbers,string)
            if len(bad) > 0:
                return 1
            all_nums = re.findall(re_right_numbers,string)
            if len(all_nums) > 0:
                for n in all_nums:
                    n = n.replace('\\','')
                    n = int(n)
                    if n > 32 and n != 35 and n != 92:
                        return 1        
    else:
        return 1
    return 0    

def testFrame(string,TF,frameStack):
    if string == 'GF':
        return GF
    elif string == 'TF':
        try:
            TF
            return TF
        except NameError:
            NoFrame('Ramec neexistuje.')

    else:
        if frameStack.stackSize() > 0:
            return frameStack.getLocalFrame()
    return None    

def processVarArgument(instruction,TF,frameStack):
    arg = stripName(instruction.text) # LF@jmeno
    frame = testFrame(arg[0],TF,frameStack) # ramec arg
    old = frame.retVar(arg[1])
    if old is None:
        NoVarError('Neexistujici promenna (ramec existuje).')
    return frame,old
    
def parseSymbol(symbol,TF,frameStack):
    if symbol.attrib['type'] == 'var':
        var = stripName(symbol.text) # LF@jmeno
        frame = testFrame(var[0],TF,frameStack) # ramec arg
        symb = frame.retVar(var[1])
        if symb is None:
            NoVarError('Neexistujici promenna (ramec existuje).')
        if symb.typ == None:
            MissValError('Chybi hodnota promenne.')
        return [symb.typ,symb.value]
    else:
        if symbol.attrib['type'] == 'int':  
            return [symbol.attrib['type'],int(symbol.text)]
        else:
            return [symbol.attrib['type'],symbol.text]
