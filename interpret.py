#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-

from variables import *
from functions import *

import sys
import xml.etree.ElementTree as ET
import re
import copy
#import xml.sax.xmlreader as SAX
    
######## ################# ######
####### ##### START ##### #######
###### ################# ########


# PARSOVANI ARGUMENTU
if len(sys.argv) > 3:
    ArgError('Spatny pocet argumentu.')
if len(sys.argv) == 3:
    sys.argv.pop(0)
    for arg in sys.argv:
        if arg.startswith('--source='):
            arg_source = arg.split('--source=')[1]
            arg_src = True
        if arg.startswith('--input='):
            arg_input = arg.split('--input=')[1]
            arg_inp = True
    if not arg_src or not arg_inp:
        ArgError('Spatne argumenty.')
elif len(sys.argv) == 2:    
    if sys.argv[1] == '--help':
        print('Napoveda k intepret.py. Interpret jazyka IPPcode19, vstupni format XML. --source: zdrojovy soubor ve formatu XML (jinak stdin), --input: vstupni soubor (jinak stdin). Musi byt zadan alespon jeden z techto argumentu.')
        sys.exit(0)
    elif sys.argv[1].startswith('--source='):
        arg_source = sys.argv[1].split('--source=')[1]
        arg_input = sys.stdin
    elif sys.argv[1].startswith('--input='):
        arg_input = sys.argv[1].split('--input=')[1]
        arg_source = sys.stdin
    else:
        ArgError('Spatny argument.')
else:
    ArgError('Spatny pocet argumentu.')
     
try:
    tree = ET.parse(arg_source) 
    program = tree.getroot() # KORENOVY ELEMENT

    #xmlLang = False # NALEZEN ATRIBUT LANGUAGE
    #for capt in program.attrib:
    #    if capt == 'language':
    #        if program.get(capt) == 'IPPcode19':
    #            xmlLang = True
    #        else:
    #            XmlStructError('Uveden jiny jazyk v XML tagu Program.')
    #    elif capt == 'name' or capt == 'description':
    #        pass
    #    else:
    #        XmlStructError('Uveden spatny atribut v XML tagu Program.')
    #if not capt:
    #    XmlStructError('Neuveden atribut language v XML tagu Program.')     

    program_len = len(list(program)) # POCET INSTRUKCI

    ## NULTY PRUBEH - srovnani XML polozek podle cisla a argumenty podle nazvu (arg1,arg2 atd.)

    #if program.text is not None:
    #    XmlStructError('Korenovy tag XML obsahuje text.')

    if program.tag != 'program':
        XmlStructError('Ve vstupnim XML chybi je spatny korenovy tag.')
    if 0 < len(program.attrib) < 4:
        if 'language' in program.attrib and program.attrib['language'] == 'IPPcode19':
            if len(program.attrib) == 2:
                if not 'description' in program.attrib or not 'name' in program.attrib:
                    XmlStructError('Ve vstupnim XML jsou v korenovem tagu nespravne atributy.')
            elif len(program.attrib) == 3:
                if not 'description' in program.attrib and not 'name' in program.attrib:
                    XmlStructError('Ve vstupnim XML jsou v korenovem tagu nespravne atributy.')                
        else:
            XmlStructError('Ve vstupnim XML chybi u korenoveho tagu atribut language nebo ma spatnou hodnotu.')
    else:
        XmlStructError('Prilis mnoho atributu u korenoveho XML tagu.')

    program[:] = sorted(program, key=lambda a: int(a.get('order'))) # SETRID OPERACE PODLE PORADI
    for child in program:
        child[:] = sorted(child, key=lambda a: a.tag) # SETRID TAGY PODLE PORADI

    ## PRVNI PRUBEH - SYNTAXE/GLOBALNI PROMENNE/NAVESTI
   
    for i in range(0,program_len):
        
        # ANALYZA XML, PROVADI SE PROTOZE UZIVATEL MUZE TESTOVAT SOUBOR KTERY NEVYPADL Z PARSE.PHP 
        if len(program[i].attrib) > 2:
            XmlStructError('V XML jsou u instrukce atributy navic.')    
        if program[i].tag != 'instruction':
            XmlStructError('Ve vstupnim XML chybi tag instruction.')
        if not 'opcode' in program[i].attrib or not 'order' in program[i].attrib:
            XmlStructError('Ve vstupnim XML chybi atribut order nebo opcode.')
        if int(program[i].attrib['order']) != (i+1):
            XmlStructError('Spatne ocislovani order ve vstupnim XML.')
        opcode = program[i].attrib['opcode'].upper() # kod operace
        if len(list(program[i])) == 0:
            if not opcode in availableOps_0:
                XmlStructError('Neznamy operacni kod instrukce.') 
        elif len(list(program[i])) == 1:
            if program[i][0].tag != 'arg1' or len(program[i][0].attrib) != 1 or 'type' not in program[i][0].attrib:
                XmlStructError('Chybny format atributu instrukce v XML.')
            typ = program[i][0].attrib['type'] # typ argumentu
            value = program[i][0].text # hodnota argumentu
            if opcode in availableOps_1:
                if opcode == 'DEFVAR' or opcode == 'POPS':
                    if testForVar(typ,value):
                        XmlStructError('Chybny format instrukce v XML.')
                elif opcode == 'LABEL' or opcode == 'JUMP' or opcode == 'CALL':
                    if testForLabel(typ,value):
                        XmlStructError('Chybny format instrukce v XML.')
                elif opcode == 'PUSHS' or opcode == 'DPRINT' or opcode == 'EXIT' or opcode == 'WRITE':
                    if testForSymb(typ,value):
                        XmlStructError('Chybny format instrukce v XML.') 
            else:
                XmlStructError('Neznamy operacni kod instrukce.')    
        elif len(list(program[i])) == 2:
            if program[i][0].tag != 'arg1' or len(program[i][0].attrib) != 1 or 'type' not in program[i][0].attrib:
                XmlStructError('Chybny format atributu instrukce v XML.')
            if program[i][1].tag != 'arg2' or len(program[i][1].attrib) != 1 or 'type' not in program[i][1].attrib:
                XmlStructError('Chybny format atributu instrukce v XML.')
            typ1 = program[i][0].attrib['type'] # typ argumentu 1
            value1 = program[i][0].text # hodnota argumentu 1
            typ2 = program[i][1].attrib['type'] # typ argumentu 2
            value2 = program[i][1].text # hodnota argumentu 2
            if opcode in availableOps_2:
                if opcode == 'READ':
                    if testForVar(typ1,value1) or testForType(typ2,value2):
                        XmlStructError('Chybny format instrukce v XML.')   
                elif opcode == 'MOVE' or opcode == 'INT2CHAR' or opcode == 'STRLEN' or opcode == 'TYPE' or opcode == 'NOT':
                    if testForVar(typ1,value1) or testForSymb(typ2,value2):
                        XmlStructError('Chybny format instrukce v XML.')  
            else:
                XmlStructError('Neznamy operacni kod instrukce.')
        elif len(list(program[i])) == 3:
            if program[i][0].tag != 'arg1' or len(program[i][0].attrib) != 1 or 'type' not in program[i][0].attrib:
                XmlStructError('Chybny format atributu instrukce v XML.')
            if program[i][1].tag != 'arg2' or len(program[i][1].attrib) != 1 or 'type' not in program[i][1].attrib:
                XmlStructError('Chybny format atributu instrukce v XML.') 
            if program[i][2].tag != 'arg3' or len(program[i][2].attrib) != 1 or 'type' not in program[i][2].attrib:
                XmlStructError('Chybny format atributu instrukce v XML.')  
            if opcode in availableOps_3:
                typ1 = program[i][0].attrib['type'] # typ argumentu 1
                value1 = program[i][0].text # hodnota argumentu 1
                typ2 = program[i][1].attrib['type'] # typ argumentu 2
                value2 = program[i][1].text # hodnota argumentu 2
                typ3 = program[i][2].attrib['type'] # typ argumentu 3
                value3 = program[i][2].text # hodnota argumentu 3
                if opcode == 'JUMPIFEQ' or opcode == 'JUMPIFNEQ':
                    if testForLabel(typ1,value1) or testForSymb(typ2,value2) or testForSymb(typ3,value3):
                        XmlStructError('Chybny format instrukce v XML.')
                else:  
                    if testForVar(typ1,value1) or testForSymb(typ2,value2) or testForSymb(typ3,value3):
                        XmlStructError('Chybny format instrukce v XML.')
            else:
                XmlStructError('Neznamy operacni kod instrukce.') 
        else:
            XmlStructError('Spatny pocet argumentu instrukce v XML.')
        # GF a Labels        
        if opcode == 'LABEL':
            if program[i][0].text not in Labels:
                Labels[program[i][0].text] = i # ULOZ NAVESTI DO SEZNAMU NAVESTI
            else:
                SemanticError('Redefinice navesti.')    
        elif opcode == 'DEFVAR':
            var = stripName(program[i][0].text)
            if var[0] == 'GF':
                if GF.addVar(Variable(var[1],None,None)): # ULOZ GLOBALNI PROMENNOU
                    SemanticError('Redefinice promenne.')

    ## DRUHY PRUBEH, ZPRACOVANI TOKU PODLE INSTRUKCI   
    ## obsah xml je syntakticky spravny, pristupujes k argumentum pomoci program[i][0/1/2]
    
    frameStack = FrameStack() # zasobnik ramcu, defaultne prazdny
    lilStack = FrameStack() # maly stack
    callStack = FrameStack() # zasobnik volani

    finished = False # dokud se nedostaneme na konec programu, porad budeme preskakovat z jednoho for cyklu do druheho, akorat se bude menit hodnotu radku kde zaciname

    start = 0 # defaultne zaciname v cyklu od 0, muze se kvuli JUMP/CALL zmenit
    if arg_input != sys.stdin:
        inp_file = open(arg_input)
        inp = inp_file.read().splitlines()
        read = 0 # pocitadlo instrukci READ v pripade ze se cte ze souboru   

    while not finished:
        cycle = False # defaultne necykli, ale snaz se ukoncit co nejdriv
        for i in range(start,program_len): # start je cislo radku kde se ma zacinat, defaultne 0, pokud naskakujeme zpet kvuli cyklu nebo neco tak jina hodnota => pozice toho labelu      
            opcode = program[i].attrib['opcode'].upper() # kod operace

            # SEMANTIC START

            if opcode == 'MOVE':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb = parseSymbol(program[i][1],TF,frameStack)
                
                if symb[0] == 'string':
                    if symb[1] is None:
                        symb[1] = ''
                frame.updConst(var,symb[0],symb[1])
                
            elif opcode == 'EXIT':
                symb = parseSymbol(program[i][0],TF,frameStack)
                if symb[0] == 'int':
                    if 0 <= int(symb[1]) <= 49:
                        sys.exit(int(symb[1]))
                    else:
                        RunError('Spatna ciselna hodnota instrukce EXIT.')
                else:
                    OperandTypeError('Spatny typ operandu u instrukce EXIT.')
                               
            elif opcode == 'TYPE':
                frame1,var1 = processVarArgument(program[i][0],TF,frameStack)
                if program[i][1].attrib['type'] == 'var': # je li symbol neinicializovana promenna
                    frame2,var2 = processVarArgument(program[i][1],TF,frameStack)
                    if var2.typ == None:
                        frame1.updConst(var1,'',None)
                    else:
                        frame1.updConst(var1,'string',var2.typ)
                else:    
                    symb = parseSymbol(program[i][1],TF,frameStack)
                    frame1.updConst(var1,'string',symb[0])

            elif opcode == 'CREATEFRAME':
                TF = Frame()
            
            elif opcode == 'PUSHFRAME':
                try:
                    TF
                    if TF is not None:
                        frameStack.pushStack(copy.deepcopy(TF)) # je to nezbytny? Nefungovalo by to bez toho?
                    else:
                        NoFrame('Ramec neexistuje.')
                    TF = None
                except NameError:
                    NoFrame('Neexistujici ramec TF.')

            elif opcode == 'POPFRAME':
                TF = Frame()
                if frameStack.stackSize() > 0:    
                    TF = frameStack.popStack()
                else:
                    NoFrame('Zasobnik ramcu je prazdny.')

            elif opcode == 'DEFVAR':
                var = stripName(program[i][0].text) # LF@jmeno
                if var[0] != 'GF': # GF jsme vyresili v prvnim pruchodu
                    frame = testFrame(var[0],TF,frameStack) # ramec var
                    if frame is None:
                        NoFrame('Ramec neexistuje.')
                    if frame.addVar(Variable(var[1],None,None)):
                        SemanticError('Redefinice promenne.') 

            elif opcode == 'CALL':
                if program[i][0].text not in Labels:
                    SemanticError('Nedefinovane navesti.')
                cycle = True
                start = Labels[program[i][0].text] + 1 # + 1 aby neanalyzoval to navesti ale jel rovnou dal v kodu
                callStack.pushStack(i+1) # budes se pomoci RETURN vracet na call, tj dalsi radek od toho kde byl umisten tenhle CALL
                break
            
            elif opcode == 'RETURN':
                if callStack.stackSize() == 0:
                    MissValError('V zasobniku volani instrukci chybi hodnota.')
                if callStack.getLocalFrame() >= program_len: # skaces nekam za konec: ukoncit cyklus                  
                    break
                cycle = True
                start = callStack.popStack()
                break

            elif opcode == 'JUMP':
                if program[i][0].text not in Labels:
                    SemanticError('Nedefinovane navesti.')
                cycle = True
                start = Labels[program[i][0].text] + 1 # + 1 aby neanalyzoval to navesti ale jel rovnou dal v kodu
                break 

            elif opcode == 'WRITE':
                symb1 = parseSymbol(program[i][0],TF,frameStack) 
                if symb1[0] == 'bool':
                    if symb1[1] == 'false':
                        print('false', end='')
                    else:
                        print('true', end='')
                elif symb1[0] == 'int':
                    print(int(symb1[1]),end='')
                elif symb1[0] == 'string':
                    print(translateString(symb1[1]),end='')
                        
            elif opcode == 'DPRINT':
                symb1 = parseSymbol(program[i][0],TF,frameStack)
                if symb[0] == 'bool':
                    if symb[1] == 'false':
                        sys.stderr.write(False)
                    else:
                        sys.stderr.write(True)
                elif symb[0] == 'int':
                    sys.stderr.write(int(symb[1]))
                elif symb[0] == 'string':
                    sys.stderr.write(translateString(symb1[1]))
                        
            elif opcode == 'BREAK':
                try:
                    TF
                    sys.stderr.write('TF: ' + str(TF.var))
                except NameError:
                    sys.stderr.write('TF: -')
                sys.stderr.write('GF: ' + str(GF.var))
                sys.stderr.write('Instrukce: ' + program[i].attrib['opcode'])
                sys.stderr.write('Pozice: ' + str(i) + ' / ' + str(program_len))
                
            elif opcode == 'READ':
                frame,old = processVarArgument(program[i][0],TF,frameStack)  
    
                if arg_input == sys.stdin: # nacitej pomoci input()
                    try:
                        line = input()
                    except EOFError:
                        if program[i][1].text == 'bool':
                            frame.updConst(old,'bool','false')
                        elif program[i][1].text == 'int':
                            frame.updConst(old,'int',0)
                        else:
                            frame.updConst(old,'string','')
                        continue
                else: # nacitej jeden radek ze souboru
                    line = ""
                    for a, l in enumerate(inp):
                        if a == read:
                            line = l.rstrip()
                    read = read + 1
                    if len(line) == 0:
                        if program[i][1].text == 'bool':
                            frame.updConst(old,'bool','false')
                        elif program[i][1].text == 'int':
                            frame.updConst(old,'int',0)
                        else:
                            frame.updConst(old,'string','') 
                        continue                       
                if program[i][1].text == 'bool':
                    if line.lower() == 'true':
                        frame.updConst(old,'bool','true')
                    else:
                        frame.updConst(old,'bool','false')
                elif program[i][1].text == 'int':
                    if re.match(re_int,line):
                        frame.updConst(old,'int',int(line))
                    else:
                        frame.updConst(old,'int',0)
                else:
                    frame.updConst(old,'string',line)
              
            if opcode == 'JUMPIFEQ' or opcode == 'JUMPIFNEQ':
                if program[i][0].text not in Labels:
                    SemanticError('Nedefinovane navesti.')
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)            

                if symb1[0] == symb2[0]:
                    if opcode == 'JUMPIFEQ':
                        if symb1[1] == symb2[1]:
                            cycle = True
                            start = Labels[program[i][0].text] + 1 # + 1 aby neanalyzoval to navesti ale jel rovnou dal v kodu
                            break
                    else:
                        if symb1[1] != symb2[1]:
                            cycle = True
                            start = Labels[program[i][0].text] + 1 # + 1 aby neanalyzoval to navesti ale jel rovnou dal v kodu
                            break                        
                else:
                    OperandTypeError('Jine typy pri porovnani JUMPIFEQ.')
                    
            elif opcode == 'CONCAT':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)                
                if symb1[0] == 'string' and symb2[0] == 'string':
                    var.value = symb1[1] + symb2[1]
                    var.typ = 'string'
                else:
                    OperandTypeError('Spatne typy symbolu pri CONCAT.')    
            
            elif opcode == 'STRLEN':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb = parseSymbol(program[i][1],TF,frameStack)
                if symb[0] == 'string':
                    minus = re.findall(re_right_numbers,symb[1])                   
                    frame.updConst(var,'int',int(len(symb[1]))-(3*len(minus)))
                else:
                    OperandTypeError('Spatny typ symbolu pri STRLEN.')
                    
            elif opcode == 'GETCHAR':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)
                if symb1[0] == 'string' and symb2[0] == 'int':
                    if 0 <= int(symb2[1]) < len(symb1[1]):
                        var.typ = 'string'
                        var.value = symb1[1][int(symb2[1])]
                    else:
                        StrError('Pozice v GETCHAR mimo rozsah retezce.')
                else:
                    OperandTypeError('Spatny typ symbolu pri GETCHAR.')

            elif opcode == 'SETCHAR':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)
                if var.typ == 'string' and symb1[0] == 'int' and symb2[0] == 'string':
                    if len(symb2[1]) == 0:
                        StrError('Prazdny retezec u SETCHAR.')
                    replace = symb2[1][0]
                    if 0 <= int(symb1[1]) < len(var.value):

                        var.value = var.value[0:int(symb1[1]):] + replace + var.value[int(symb1[1])+1::]
                        
                    else:
                        StrError('Pozice v SETCHAR mimo rozsah retezce.')
                else:
                    OperandTypeError('Spatny typ symbolu pri SETCHAR.')
                    
            elif opcode == 'STRI2INT':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)
                if symb1[0] == 'string' and symb2[0] == 'int':
                    if 0 <= int(symb2[1]) < len(symb1[1]):
                        var.typ = 'int'
                        var.value = ord(symb1[1][int(symb2[1])])
                    else:
                        StrError('Pozice v STRI2INT mimo rozsah retezce.')
                else:
                    OperandTypeError('Spatny typ symbolu pri STRI2INT.')        
                    
            elif opcode == 'INT2CHAR':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                if symb1[0] == 'int':
                    if 0 <= int(symb1[1]) < 128:
                        var.typ = 'string'
                        var.value = chr(int(symb1[1]))
                    else:
                        StrError('Pozice v INT2CHAR mimo rozsah retezce.')
                else:
                    OperandTypeError('Spatny typ symbolu pri INT2CHAR.')  
                    
            elif opcode == 'ADD' or opcode == 'SUB' or opcode == 'MUL' or opcode == 'IDIV':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)                

                if symb1[0] == 'int' and symb2[0] == 'int':
                    var.typ = 'int'
                    if opcode == 'ADD':
                        var.value = int(symb1[1]) + int(symb2[1])
                    elif opcode == 'SUB':
                        var.value = int(symb1[1]) - int(symb2[1]) 
                    elif opcode == 'MUL':
                        var.value = int(symb1[1]) * int(symb2[1])
                    elif opcode == 'IDIV':
                        if int(symb2[1]) == 0:
                            RunError('Deleni nulou u IDIV.')
                        var.value = int(symb1[1]) // int(symb2[1]) 
                else:
                    OperandTypeError('Spatny typ symbolu pri ADD.')  
            
            elif opcode == 'NOT':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                if symb1[0] == 'bool':
                    var.typ = 'bool'
                    if symb1[1] == 'true':
                        var.value = 'false'
                    else:
                        var.value = 'true'
                else:
                    OperandTypeError('Spatny typ symbolu pri NOT.')
                    
            elif opcode == 'AND' or opcode == 'OR':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)
                if symb1[0] == 'bool' and symb2[0] == 'bool':
                    var.typ = 'bool'
                    if opcode == 'AND':
                        if symb1[1] == 'true' and symb2[1] == 'true':
                            var.value = 'true'
                        else:
                            var.value = 'false'                        
                    else:
                        if symb1[1] == 'false' and symb2[1] == 'false':
                            var.value = 'false'
                        else:
                            var.value = 'true' 
                else:
                    OperandTypeError('Spatny typ symbolu pri AND nebo OR.') 

            elif opcode == 'AND' or opcode == 'OR':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)
                if symb1[0] == 'bool' and symb2[0] == 'bool':
                    var.typ = 'bool'
                    if opcode == 'AND':
                        if symb1[1] == 'true' and symb2[1] == 'true':
                            var.value = 'true'
                        else:
                            var.value = 'false'                        
                    else:
                        if symb1[1] == 'false' and symb2[1] == 'false':
                            var.value = 'false'
                        else:
                            var.value = 'true' 
                else:
                    OperandTypeError('Spatny typ symbolu pri AND nebo OR.')
                    
            elif opcode == 'EQ':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)
                var.typ = 'bool'
                if symb1[0] == 'nil' or symb[1] == 'nil': # jeden z nich je nil, porovnej cokoliv
                    if symb1[0] == symb2[0]:
                        if symb1[1] == symb2[1]:
                            var.value = 'true'
                        else:
                            var.value = 'false'
                    else:
                        var.value = 'false'
                else: # ani jeden z nich neni nil, porovnavej jen stejny typ
                    if symb1[0] == symb2[0]:
                        if symb1[1] == symb2[1]:
                            var.value = 'true'
                        else:
                            var.value = 'false'
                    else:
                        OperandTypeError('Porovnavani jinych typu u EQ.')                    
                    
            elif opcode == 'LT' or opcode == 'GT':
                frame,var = processVarArgument(program[i][0],TF,frameStack)
                symb1 = parseSymbol(program[i][1],TF,frameStack)
                symb2 = parseSymbol(program[i][2],TF,frameStack)
                if symb1[0] == 'nil' or symb2[0] == 'nil':
                    OperandTypeError('Porovnani nil u LT nebo GT.')
                if symb1[0] != symb2[0]:
                    OperandTypeError('U LT nebo GT porovnani jinych typu.')
                else:
                    var.typ = 'bool'
                    if symb1[1] != symb2[1]:
                        if symb1[0] == 'bool':
                            if opcode == 'LT':
                                if symb1[1] == 'false':
                                    var.value = 'true'
                                else:
                                    var.value = 'false'
                            else:
                                if symb1[1] == 'false':
                                    var.value = 'false'
                                else:
                                    var.value = 'true'                                
                        elif symb1[0] == 'int':
                            if opcode == 'LT':
                                if int(symb1[1]) < int(symb2[1]):
                                    var.value = 'true'
                                else:
                                    var.value = 'false'
                            else:
                                if int(symb1[1]) < int(symb2[1]):
                                    var.value = 'false'
                                else:
                                    var.value = 'true'                                
                        else:
                            if opcode == 'LT':
                                if symb1[1] < symb2[1]:
                                    var.value = 'true'
                                else:
                                    var.value = 'false'
                            else:
                                if symb1[1] < symb2[1]:
                                    var.value = 'false'
                                else:
                                    var.value = 'true'
                    else:
                        var.value = 'false'
            
            elif opcode == 'PUSHS':
                symb = parseSymbol(program[i][0],TF,frameStack)
                if symb[0] == '' or symb[0] == None:
                    MissValError('Pri PUSHS vkladame na zasobnik neco s chybejicim typem.')
                item = StackItem(symb[0],symb[1])
                lilStack.pushStack(copy.deepcopy(item))
                
            elif opcode == 'POPS':
                if lilStack.stackSize() > 0:
                    frame,var = processVarArgument(program[i][0],TF,frameStack)
                    item = lilStack.popStack()
                    frame.updConst(var,item.typ,item.value)
                    del item
                else:
                    MissValError('Pri POPS byl zasobnik prazdny.')
                
            # SEMANTIC END            
            
        if not cycle: # pokud to dojelo a neskocili jsme ven kvuli cyklu       
            finished = True # dostal ses za posledni radek kodu, vyskocit z cyklu            

except IOError:
    sys.stderr.write('Chyba vstupniho souboru.')
    sys.exit(11)
except ET.ParseError as err:
    sys.stderr.write('Spatny format XML souboru. Kod: '+str(err.code)+' / pozice: '+str(err.position)+'.')
    sys.exit(31)
#except ET.ParserError as err:
#    sys.stderr.write('Chyba pri parsovani.')
#    sys.exit(31)   
#except:
#    print('Obecna chyba.')
#    sys.exit(99)
    
