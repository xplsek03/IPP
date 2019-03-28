<?php

// nastaveni skriptu
$parser = "parse.php"; // defaultni parser
$interpret = "interpret.py"; // defaultni interpret
$path = "."; // defaultni cesta
$recursive = false; // rekurze?
$testcount = 0; // pocet testu celkem
$passed = 0; // ok testy
$error = 0; // err testy

/* 
probehni test pro jeden src soubor ze slozky dir
arg@folders - pole s testy
arg@src - nazev src souboru s testem
arg@dir - klic pro pole folders
arg@fullpath - plna cesta k testu src
*/
function runTest($folders,$src,$dir,$fullpath) {

    global $parser,$interpret,$mode, $passed, $error, $tmp; // nastaveni skriptu

    $foundIn = false; // naslo to .in
    $foundRc = false; // naslo to .rc
    $foundOut = false; // naslo to .out

    foreach($folders[$dir] as $item) { // prohledavej obsah konkretni slozky v poli folders
        $src_parts = pathinfo($src);

        if($item == $src_parts['filename'].".rc")
            $foundRc = true;
        if($item == $src_parts['filename'].".in")
            $foundIn = true;
        if($item == $src_parts['filename'].".out")
            $foundOut = true;
    }
    // v pripade ze neexistuji, dotvor povinne soubory testu
    if(!$foundIn)
            createFile($fullpath.$src_parts['filename'].".in","");
    if(!$foundRc)
            createFile($fullpath.$src_parts['filename'].".rc","0");
    if(!$foundOut)
            createFile($fullpath.$src_parts['filename'].".out","");

    // samotne testovani: START

    $rc = file_get_contents($fullpath.$src_parts['filename'].".rc"); // nactio obsah .rc  
    $ok = 1; // 1 = test neprosel, 0 = test prosel

    if($mode == 1) { // testuj jen parser
        exec("php7.3 ".$parser." < ".$fullpath.$src." > temp_output 2>/dev/null", $out, $rc_real);
        if($rc == $rc_real) {
            if($rc_real == 21)
                $ok = 0;
            else            
                exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar temp_output ".$fullpath.$src_parts['filename'].".out options", $out, $ok);
        }
    }
    else if($mode == 2) { // testuj jen interpret
        exec("python3 ".$interpret." --source=".$fullpath.$src." --input=".$fullpath.$src_parts['filename'].".in > temp_output 2>/dev/null", $out, $rc_real);
        if($rc == $rc_real) {
            exec("diff ".$fullpath.$src_parts['filename'].".out temp_output",  $out, $ok);         
        }        
    }    
    else { // testuj oba
        exec("cat ".$fullpath.$src." | php7.3 ".$parser." > temp_both 2>/dev/null", $out, $rc_real);
        if($rc_real == 0) {
          exec("python3 ".$interpret." --input=".$fullpath.$src_parts['filename'].".in < temp_both > temp_output 2>/dev/null",  $out, $rc_real);
          if($rc == $rc_real)
              exec("diff ".$fullpath.$src_parts['filename'].".out temp_output",  $out, $ok); 
        }
    }
    // v 'ok' je ted ulozeno jak test dopadnul
    
    if($ok == 0) { // test prosel
        $passed++;
        echo "<a class=\"tab passed\">
        ".$dir."/<strong>".$src_parts['filename']."</strong>   
        </a>";
    }
    
    else { // test neprosel
        $error++;
        echo "<a class=\"tab error\">
        ".$dir."/<strong>".$src_parts['filename']."</strong>";
        if($rc != $rc_real)
            echo " (ocekaval ".$rc." dostal ".$rc_real.")";
        else
            echo " (selhalo porovnani vystupu)";
        echo "</a>";
    }
    
   // vynuluj docasne soubory, pro jistotu
   file_put_contents("temp_output","");
   file_put_contents("temp_both","");             
}

/*
vytvor novy soubor.
arg@name - nazev noveho souboru
arg@content - obsah noveho souboru
*/
function createFile($name,$content) {
    $file = fopen($name,"wb");
    if($file == false){
        fwrite(STDERR, "Nelze vytvorit soubor." . PHP_EOL);
        exit(11); 
    }
    else{
        fwrite($file,$content);
        fclose($file);
    }
}

// kontroly argumentu
if($argc == 2 && $argv[1] == "--help") {
    echo("Skript test.php spousti automatizovane testovani skriptu interpret.php a / nebo parse.php. Parametry: [--directory] [--recursive] [--parse-script | --int-only] [--int-script | --parse-only].");
}
$args = getopt("",array("help","directory:","recursive","parse-script","int-script","parse-only","int-only"));
if(isset($args["directory"]))
    $path = rtrim($args["directory"],"/")."/"; // vyresi problem toho jestli cesta obsahuje '/' nebo ne
if(isset($args["recursive"]))
    $recursive = true;
if(isset($args["parse-script"]))
    $parser = $args["parse-script"];
if(isset($args["int-script"]))
    $interpret = $args["int-script"];

if(!is_dir($path)) {
    fwrite(STDERR, "Zadany adresar neni adresar." . PHP_EOL);
    exit(11);    
}

// test modu. 1 = parse only, 2 = int only, 3 = both
if((isset($args["int-only"]) && isset($args["parse-only"])) || (isset($args["int-only"]) && isset($args["parse-script"])) || (isset($args["parse-only"]) && isset($args["int-script"]))) {
    fwrite(STDERR, "Spatne argumenty programu." . PHP_EOL);
    exit(10);
}
else {
    if(isset($args["parse-only"]))
        $mode = 1; // PARSER
    else if(isset($args["int-only"]))
        $mode = 2; // INTERPRET
    else
        $mode = 3; // BOTH
}

// kontroly souboru
if(!file_exists($interpret)) {
    echo "Vstupni soubor interpret.py neexistuje.";
    exit(11);
}
if(!file_exists($parser)) {
    echo "Vstupni soubor parser.php neexistuje.";
    exit(11);
}

// zacatek html generovani
echo "<html>
<head>
<style>
  body {
  font-size: 12px;
  padding-top: 8%;
  text-align: center;
  font-family: 'Open Sans', monospace;
}
h1, h2 {
  display: inline-block;
}
h1 {
  font-size: 30px;
}
h2 {
  font-size: 20px;
}
span {
  background: #fd0;
  padding: 0 5px;
}

.tab {
  width: 100%;
  display: block;
  float: left;
  padding: 5px 0;
  color: #2f2f2f;
  transition: 1s;
  text-decoration: none;
}

.info {
  width: 100%;
  text-align: left;
  float: left;
  padding: 5px 0;  
  color: #2f2f2f;
    }

.tab:hover {
  transition: 1s;
  color: #000;
  opacity: 0.8;
  }

.passed {
  background: #89e2a0;  
  }
  
.error {
  background: #f2777a;   
  }

.table {
  width: 75%;
  margin: 0 auto;
}

.green {
  color: #89e2a0;
  }
  
  .red {
  color: #f2777a;  
}

</style>
</head>
<body>
<h1>Testovaci skript IPP <span>xplsek03</span></h1><br>
<div class=\"table\">";

$tmp = fopen('temp_output','w+'); // docasny soubor pro mode 1/2
$bothtmp = fopen('temp_both', 'w+'); // docasny soubor pro mode 3
if(!$tmp || !$bothtmp) {
    fwrite(STDERR, "Nelze otevrit docasny soubor." . PHP_EOL);
    exit(12);    
}

// generovani pole souboru 'folders'
$folders = array(); // seznam vseho v adresari
if($recursive) { // projdi adresar $path rekurzivne
    // vygeneruj pole se seznamem vsech adresaru
    foreach($iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path,RecursiveDirectoryIterator::SKIP_DOTS)) as $item) {
        $subPath = $iterator->getSubPathName(); // nazev souboru 
        $folders[dirname($subPath)][] = basename($subPath); // do pole s klicem DIR => zaznam o souboru v tomto DIR
    }
}
else { // vyhledej testy jen v adresari $path
    foreach($iterator = new DirectoryIterator($path) as $item) {
            if(!is_dir($item)) {
                $subPath = $iterator->getFileName(); // nazev souboru 
                $folders[$path][] = basename($subPath); // do pole s klicem DIR => zaznam o souboru v tomto DIR
            }
    }
}

$foundsome = false; // oddelovac slozek ve vystupnim html

// testuj pole souboru
foreach($folders as $dir => $items) { // spust testy nad polem testu
    foreach($items as $item) {
        if(preg_match('/\S*\.src/', $item)) { // naslo to .src test soubor  
            $foundsome = true;          
            $testcount++; 
            if($path == ".")
                runTest($folders,$item,$dir,$dir."/"); // spust test na vybranem src souboru
            else                 
                runTest($folders,$item,$dir,$path.$dir."/"); // spust test na vybranem src souboru
        }
    }
    if($foundsome) // oddel slozky ve vystupnim html, kvuli prehlednosti
        echo "<a class=\"tab\">&nbsp;</a>";
    $foundsome = false;
}

// uzavreni html a generovani souhrnu
echo "
<div class=\"info\"></div> 
<div class=\"info\">
   Celkem: <strong>".$testcount."</strong>   
  </div>
    <div class=\"info\">
   Passed: <strong class=\"green\">".$passed."</strong>&nbsp;&nbsp;Error: <strong class=\"red\">".$error."</strong>   
  </div> 
</div>
</body>
</html>";

// zavri a smaz docasne soubory
fclose($bothtmp);
fclose($tmp);
exec("rm temp_output temp_both");

?>
