#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-

from variables import *

import re
# preloz escape sekvence v retezci na znaky
# arg@string - vstupni retezec
# @return - prelozeny retezec
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

# otestuj jestli je promenna promenna
# arg@typ - typ promenne
# arg@string - nazev promenne
def testForVar(typ,string):
    if string is None or typ != 'var':
        return 1
    if not re.match(re_var,string):
        return 1
    return 0

# otestuj jestli je navesti navesti
# arg@typ - typ navesti
# arg@string - nazev navesti
def testForLabel(typ,string):
    if string is None or typ != 'label':
        return 1
    if not re.match(re_label,string):
        return 1
    return 0

# otestuj jestli je symbol konstanta nebo promenna
# arg@typ - typ symbolu
# arg@string - nazev symbolu
def testForSymb(typ,string):
    if not testForConst(typ,string):
        return 0
    if not testForVar(typ,string):
        return 0
    return 1

# otestuj jestli je typ typ
# arg@typ - typ typu
# arg@string - nazev typu
def testForType(typ,string):
    if typ != 'type':
        return 1
    if string != 'string' and string != 'int' and string!= 'bool':
        return 1
    return 0

# otestuj jestli je konstanta konstanta
# arg@typ - typ konstanty
# arg@string - nazev konstanty
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

# otestuj jestli ramec je ramec a jestli existuje
# arg@string - nazev typu ramce
# arg@TF - objekt: temporaryframe TF
# arg@frameStack - objekt: frameStack zasobnik ramcu
# return - konkretni ramec, jinak None
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

# vrat promennou z ramce
# arg@instrukction - text instrukce, kde je ulozena promenna co chceme vratit
# arg@TF - objekt: temporaryframe TF
# arg@frameStack - objekt: frameStack zasobnik ramcu
# return - [ramec, objekt promenne]
def processVarArgument(instruction,TF,frameStack):
    arg = stripName(instruction.text) # dostan promennou ven z textu instrukce
    frame = testFrame(arg[0],TF,frameStack) # otestuj ramec
    old = frame.retVar(arg[1]) # vrat promennou z ramce
    if old is None:
        NoVarError('Neexistujici promenna (ramec existuje).')
    return frame,old

# vrat promennou z ramce nebo konstantu, pouziva se pri parsovani symbolu
# arg@instrukction - text instrukce, kde je ulozena promenna co chceme vratit
# arg@TF - objekt: temporaryframe TF
# arg@frameStack - objekt: frameStack zasobnik ramcu
# return - [typ symbolu, hodnota symbolu]   
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
        if symbol.attrib['type'] == 'int': # pozor, u konstanty je i int v podobe stringu! Proto to tu prevadim.
            return [symbol.attrib['type'],int(symbol.text)] # vracej int, kvuli pozdejsimu porovnani napriklad v rekurzi
        else:
            return [symbol.attrib['type'],symbol.text] # jinak vracej string
