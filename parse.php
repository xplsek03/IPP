#!/usr/local/bin/php7.3
<?php

/* tokenize() = natokenizuj radek kodu
@param count = (int) pocet argumentu operace + 1 (operacni kod)
@param line = (str) zpracovavany radek kodu
@return tokens = (arr) radek kodu rozsekany na tokeny pomoci mezer
*/
function tokenize($count,$line) { // natokenizuj radek
    $tokens = preg_split("/#/",$line); // odstran komentar
	$tokens = preg_split("/\s+/",$tokens[0]); // nasekej podle mezer
    $tokens = array_slice($tokens,0,$count); // pouze pocet prvku ktere potrebujes, duvodem je mozna prebytecna mezera pred komentarem
    return $tokens;
}

/* 
check_function_name() = zkontroluj jestli je nazev operacni kod ok
@param tokens = (arr) radek rozdeleny na tokeny
@param count = (int) pocet argumentu operace + operacni kod
@return (STR) = nazev funkce
@return (str) "" = pokud chyba vrat prazdny retezec
*/
function check_function_name($tokens,$count) {
    $accept_1 = array("CREATEFRAME","PUSHFRAME","POPFRAME","RETURN","BREAK");
    $accept_2 = array("DEFVAR","CALL","PUSHS","POPS","WRITE","LABEL","JUMP","EXIT","DPRINT");
    $accept_3 = array("MOVE","INT2CHAR","READ","STRLEN","TYPE");
    $accept_4 = array("ADD","SUB","MUL","IDIV","LT","GT","EQ","AND","OR","NOT","STRI2INT","CONCAT","GETCHAR","SETCHAR","JUMPIFEQ","JUMPIFNEQ");
    foreach(${"accept_" . $count} as $acc) { // dynamicky vytvor nazev pole podle ktereho budes testovat
        if(strtoupper($tokens[0]) == $acc) // prevod na upper aby se dal nazev funkce porovnat
            return strtoupper($tokens[0]); // nazev funkce nalezen, je ok
    }
    return ''; // vrat chybu, nenaslo to nazev fce
}

/*
test_type() = otestuj argument typu TYP
@param token = (str) retezec s nazvem typu
@return "" = pokud chyba vrat pr retezec
@return (arr) = pokud ok vrat pole s typem TYP a nazvem typu
*/
function test_type($token) {
    if($token == "int" || $token == "string" || $token == "bool")
        return array("type",$token);
    else
        return "";    
}

/*
test_symb() = otestuj argument typu SYMBOL
@param token = (str) retezec s argumentem
@return (arr) = pokud chyba vrat prazdne pole
@return (arr) = pokud ok vrat pole s typem CONST/VAR a nazvem promenne/obsahem konstanty
*/
function test_symb($token) { // otestuj jestli vyhovuje symbolu
    $t = test_var($token);
    if(!count($t)) { // pokud nesedi na var
        $c = test_const($token);
        if(!count($c)) {
            return array(); // nesedela na konstantu 
        }
        else // na konstantu sedela
            return $c; 
    }
    else // sedi na promennou
        return $t;
}


/*
test_var() = otestuj argument typu VAR - promenna
@param token = (str) retezec s argumentem
@return "" = pokud chyba vrat pr retezec
@return (arr) = pokud ok vrat pole s typem VAR a vlastni promennou
*/
function test_var($token) {
    if(preg_match("/^(LF|TF|GF)\@[a-zA-Z\_\-$&%\*!\?][\da-zA-Z\_\-$&%\*!\?]*$/",$token))
        return array("var",$token);
    else
        return array();
}

/*
test_const() = otestuj argument typu CONST - konstanta
@param token = (str) retezec s argumentem
@return "" = pokud chyba vrat pr retezec
@return token_parts = (arr) pokud ok vrat pole s typem CONST a obsahem konstanty
*/
function test_const($token) {
    $token_parts = preg_split("/@/",$token); // rozdel podle @ uprostred
    if(count($token_parts) !== 2) // bylo tam vic @ nez 1 uprostred
        return array();
    if($token_parts[0] == "int") {
        if(!preg_match("/^[\+\-]?\d+$/",$token_parts[1])) // nesedi sablone integeru: cislo
            return array();
    }
    else if($token_parts[0] == "bool") {
        if($token_parts[1] !== "true" && $token_parts[1] !== "false")
            return array();
    }
    else if($token_parts[0] == "string") {
        preg_match("/\\\D|\\\d\D|\\\d\d\D|#/",$token_parts[1],$incomplete_numbers); // test na \d, \da, # a \aad, kde d = cislo a a = neco jineho nez cislo
        if($incomplete_numbers)
            return array(); // existuji nejaka chybna cisla nebo znak #, vrat chybu
        preg_match("/\\\d\d\d/",$token_parts[1],$numbers); // kontrola jestli cisla za \ jsou spravna
        if($numbers) {
            foreach($numbers as $number) {
                $num = str_replace('\\','',"$number"); // odstran lomitka od cisel znaku, kvuli testu
                $num = (int)$num;
                if($num > 32 && $num !== 35 && $num !== 92)
                    return array();            
            }                    
        }
    }
    else if($token_parts[0] == "nil") {
        if($token_parts[1] !== "nil")
            return array();
    }
    else // spatny typ
        return array();

    return $token_parts;
}

/*
test_label() = otestuj argument typu LABEL
@param token = (str) retezec s argumentem
@return "" = pokud chyba vrat pr retezec
@return (arr) = pokud ok vrat pole s typem LABEL a vlastnim nazvem navesti
*/
function test_label($token) { // otestuj navesti
    if(preg_match("/[a-zA-Z\_\-$&%\*!\?][\da-zA-Z\_\-$&%\*!\?]*$/",$token))
        return array("label",$token);
    else
        return "";
}

/*
xml_escape() = zbav se problemovych XML znaku, nahrazenim
@param str = (str) retezec se string/label/var
@return str = (str) upraveny retezec
*/
function xml_escape($str) { // pro label, var, string se zbav problematickych XML znaku
    $str = str_replace("&", "&amp;",$str);
    $str = str_replace("<", "&lt;",$str);
    $str = str_replace(">", "&gt;",$str);
    $str = str_replace("'", "&apos;",$str);
    $str = str_replace("\"", "&quot;",$str);
    return $str;
}

// START

// zpracovani argumentu --help
if(count($argv) > 1) { // jsou tam nejake argumenty
    if(count($argv) == 2 && $argv[1] == "--help") {
        $help = "IPPcode19 parser\n****************\nSkript parse.php nacita ze STDIN kod ve formatu IPPcode19, zkontroluje jeho syntaktickou a lexikalni spravnost a vrati na STDOUT zpracovany kod IPPcode19 ve formatu XML 1.0 . Chybova hlaseni jsou odesilana na STDERR.\nRozsireni implementovano neni, protoze neni cas.";
        fwrite(STDOUT, $help . PHP_EOL);
        exit(0);    
    }
    else { // spatne argumenty
        fwrite(STDERR, "Spatne argumenty programu." . PHP_EOL);
        exit(10);
    }
}

$file = fopen("php://stdin","r");
$counter = 1; // globalni citac instrukci
$FirstLine = True; // nacteni prvniho radku
$SomeContent = False; // existuje alespon jeden radek - validni - ve stdin

if($file) {
	while(($line = fgets($file)) !== false) {
       $SomeContent = True; // na stdin je alespon jeden radek
        if($FirstLine) { // test na hlavicku kodu probehne prave jednou
            if(!preg_match("/^\.IPPCODE19\s*(#.*)?$/",strtoupper($line))) {
                fwrite(STDERR, "Spatna hlavicka IPPcode19." . PHP_EOL);
                exit(21); // vytiskni neco na stderr a vrat 21
            }
            $FirstLine = False; // vypni analyzu prvniho radku

            // ZAHAJ XML
            $writer = new XMLWriter();  
            $writer->openMemory();  // ujladani do bufferu v pameti
            $writer->startDocument('1.0','UTF-8');  
            $writer->setIndent(4);
            $writer->startElement('program');  
            $writer->writeAttribute('language', 'IPPcode19'); 

            continue;        
        }

		if(preg_match("/^\s*$/",$line) || preg_match("/^\s*#.*$/",$line)) // cokoliv pri cem radek preskocis
			continue;
		else if(preg_match("/^\S+\s+\S+\s+\S+\s*(#.*)?$/",$line)) // 2arg + opcode 
            		$instruction = 3;
		else if(preg_match("/^\S+\s+\S+\s*(#.*)?$/",$line)) // 1arg + opcode
			$instruction = 2;
		else if(preg_match("/^\S+\s*(#.*)?$/",$line)) // pouze opcode
			$instruction = 1;	
		else if(preg_match("/^\S+\s+\S+\s+\S+\s+\S+\s*(#.*)?$/",$line)) // 3arg + opcode	
		    $instruction = 4;
		else { // jinak se jedna o syntaktickou chybu
            fwrite(STDERR, "Nejaky radek je cely spatne, syntakticka chyba." . PHP_EOL);
            exit(23);
		}

        // PROCESSING INSTRUKCE

        $tokens = tokenize($instruction,$line); // natokenizuj
        $func_name = check_function_name($tokens,$instruction); // zkontroluj nazev funkce, podle nej pak rozhodnes o dalsich testech
        if($func_name == '') { // '' == chyba v syntaxi, v nazvu funkce
            fwrite(STDERR, "Chybny operacni kod." . PHP_EOL);
            exit(22);
        }

        // tady zacina kontrola argumentu, uz vime ze vyhovuje nazvu funkce a muzeme na ne bezpecne testovat
        // do promennych se nahraje obsah naparsovanych argumentu
        $arg1 = array();
        $arg2 = array();
        $arg3 = array();

        if($instruction == 3) { // 2arg + opcode
            if($func_name == "READ") {
                $arg1 = test_var($tokens[1]);
                $arg2 = test_type($tokens[2]);
                if(!count($arg1) || !count($arg2)) {
                    goto arg_error; // jdi na chybu operandu
                }                               
            }
            else {
                $arg1 = test_var($tokens[1]);
                $arg2 = test_symb($tokens[2]);
                if(!count($arg1) || !count($arg2)) {
                    goto arg_error; // jdi na chybu operandu
                }     
            }
        }

        else if($instruction == 2) { // 1arg + opcode
            if($func_name == "DEFVAR" || $func_name == "POPS") {
                $arg1 = test_var($tokens[1]);
                if(!count($arg1)) {
                    goto arg_error; // jdi na chybu operandu
                }          
            }
            else if($func_name == "PUSHS" || $func_name == "WRITE" || $func_name == "EXIT" || $func_name == "DPRINT") {
                $arg1 = test_symb($tokens[1]);
                if(!count($arg1)) {
                    goto arg_error; // jdi na chybu operandu
                }             
            }  
            else {
                $arg1 = test_label($tokens[1]);
                if(!count($arg1)) {
                    goto arg_error; // jdi na chybu operandu
                }             
            }        
        }

        else if($instruction == 4) { // 3arg + opcode
            if($func_name == "JUMPIFEQ" || $func_name == "JUMPIFNEQ") {
                $arg1 = test_label($tokens[1]);
                $arg2 = test_symb($tokens[2]);
                $arg3 = test_symb($tokens[3]);
                if(!count($arg1) || !count($arg2) || !count($arg3)) {
                    goto arg_error; // jdi na chybu operandu
                }     
            }
            else {
                $arg1 = test_var($tokens[1]);
                $arg2 = test_symb($tokens[2]);
                $arg3 = test_symb($tokens[3]);
                if(!count($arg1) || !count($arg2) || !count($arg3)) {
                    goto arg_error; // jdi na chybu operandu
                }             
            }     
        }

            // TADY DOJDE K PREVEDENI DO DOCASNEHO XML, KTERE SE PAK MOZNA POUZIJE
            $writer->startElement('instruction');  
            $writer->writeAttribute('order', $counter);
            $counter++; // zvys citac instrukce
            $writer->writeAttribute('opcode', $func_name);

            for($i = 1; $i < $instruction; $i++) { // postupne zpracovani dynamickeho poctu argumentu operace
                $writer->startElement('arg' . $i);
                $writer->writeAttribute('type', ${'arg' . $i}[0]);
                if(${'arg' . $i}[0] == "var" || ${'arg' . $i}[0] == "string" || ${'arg' . $i}[0] == "label") // pro var|string|label se zbav XML specialnich znaku        
                    $writer->writeRaw(xml_escape(${'arg' . $i}[1]));
                else
                    $writer->text(${'arg' . $i}[1]);
                $writer->endElement();                
            }      
            $writer->endElement();
	}
	fclose($file);

    if($SomeContent) { // stdin nebyl prazdny
        // DOKONCI XML A VYTISKNI HO
        $writer->endElement();  
        $writer->endDocument();
        fwrite(STDOUT, $writer->outputMemory()); // vypis na STDout obsah bufferu, sam se pak flushne
        exit(0);
    }
    else { // stdin byl prazdny
        fwrite(STDERR, "Prazdny vstup." . PHP_EOL);
        exit(21);    
    }
}
else { // fopen error
    fwrite(STDERR, "Nelze otevrit vstupni soubor." . PHP_EOL);
    exit(11);
}

arg_error: // syntakticka chyba operandu
    fwrite(STDERR, "Syntakticka chyba operandu." . PHP_EOL);
    exit(23);

?>

