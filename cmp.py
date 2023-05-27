#TJD4のアセンブラ
#Author : masuda
#Date   : 2023/4/17

import os
import re
import csv

#アセンブリの正規表現と対応表のアドレス
ASM = []
BIN = []
RAN = []
TABLE_ADRS = "table.txt"

#アセンブリ対応表の読み込み
def import_table(_adrs):
    _f = open(_adrs, "r")
    _table = _f.readlines()
    for i in range(len(_table)):
        _t0 = _table[i].replace("\n", "")
        _t1 = " ".join(_t0.split())
        _t2 = _t1.split()
        ASM.append(_t2[0])
        BIN.append(int(_t2[1], 0))
        RAN.append(int(_t2[2]))

#ファイルの読み込み
def import_file():
    _pwd = os.getcwd()
    os.chdir(_pwd + "/source")
    print("Directory :", os.getcwd())

    _iext  = input("Extension? (t/c)  : ")
    _ipass = input("Source file name? : ")
    _epass = input("Export file name? : ")

    if(_iext == "t"):
        _f = open(_ipass + ".tjd4", "r")
        _text_list = _f.readlines()
        _f.close()
    if(_iext == "c"):
        with open(_ipass + ".csv", "r") as f:
            _r = csv.reader(f)
            _l = [row for row in _r]
        _text_list = []
        for i in range(len(_l)):
            _t = " ".join(_l[i])
            _text_list.append(_t)
        f.close()

    return _text_list, _epass

#テキストが，命令かコメントかを判定する
def check_text_type(_text):
    _type = 2

    pattern1 = r"^\s*;.*" #コメント行
    pattern2 = r"^\s*[\r\n]?$" #空白行
    pattern3 = r"^\s*0x[0123456789abcdef]{2}\s+[A-Z]{3}" #オペランドなし
    pattern4 = r"^\s*0x[0123456789abcdef]{2}\s+[A-Z]{3},\s*[ABXY]" #レジスタオペランド
    pattern5 = r"^\s*0x[0123456789abcdef]{2}\s+[A-Z]{3},\s*[0123456789abcdef]" #アドレスオペランド

    if re.search(pattern1, _text):
        _type = 0
    elif re.search(pattern2, _text):
        _type = 0
    elif re.search(pattern3, _text):
        _type = 1
    elif re.search(pattern4, _text):
        _type = 1
    elif re.search(pattern5, _text):
        _type = 1
    else:
        _type = 2

    return _type


#書き込みアドレスの指定
def search_address(_text):
    _pattern = r"[0123456789abcdef]{2}"
    _matches = re.findall(_pattern, _text)
    _address = int(_matches[0], 16)
    return _address #コメントなどで複数マッチしてしまった場合，一番最初のアドレスを返す

#アセンブリ -> 機械語 変換
def assemble(_text):
    for i in range(len(ASM)):
        if re.match(ASM[i], _text):
            match_matrix = re.findall(ASM[i], _text)
            if(RAN[i] == 1):
                _operand = re.search(r"(?<=.)\S$", match_matrix[0])
                _rand =  _operand.group(0)
            else:
                _rand = 0
            return BIN[i], _rand, match_matrix[0]
    return None, None, None

#アドレス消去
def remove_hex(_text):
    _match = re.match(r"^0x[0-9a-fA-F]+\s", _text)
    if _match:
        remaining_text = _text[_match.end():].strip()
        return remaining_text
    else:
        return _text

#アセンブリ表示
def dump_assembly(_code, _rand, _asm):
    print("")
    print("adrs", "\t", "code", "\t", "asm")
    print("-----------------------")
    for i in range(16):
        _i = "0x" + str(hex(i).replace("0x", "")).zfill(2)
        _c = str(hex(_code[i])).replace("0x", "").zfill(2)
        _r = str(_rand[i])
        _a = _asm[i]
        _cr = _c + _r
        print(_i, "\t", _cr, "\t", _a)
    _disp = input("...\nPrint all? (y/n) : ")
    if(_disp == "Y" or _disp == "y"):
        print("")
        print("adrs", "\t", "code", "\t", "asm")
        print("-----------------------")
        for i in range(256):
            _i = "0x" + str(hex(i).replace("0x", "")).zfill(2)
            _c = str(hex(_code[i])).replace("0x", "").zfill(2)
            _r = str(_rand[i])
            _a = _asm[i]
            _cr = _c + _r
            print(_i, "\t", _cr, "\t", _a)

#ファイル書き込み
def create_file(_code, _rand, _asm, _pass):
    os.chdir("../output")
    _teasm = ["" for mi in range(259)] 
    _teasm[0] = _pass + ".txt"
    _teasm[1] = "adrs    code    asm"
    _teasm[2] = "---------------------"
    _usage = 0
    for i in range(256):
        _i = "0x" + str(hex(i).replace("0x", "")).zfill(2)
        _c = str(hex(_code[i])).replace("0x", "").zfill(2)
        _r = str(_rand[i])
        _a = _asm[i]
        _cr = _c + _r
        if(_a == "NOP"):
            _teasm[i+3] = _i
        else:
            _teasm[i+3] = _i + "    " + _cr + "    " + _a
            _usage += 1
    _easm = "\n".join(_teasm)
    
    _temcn = ["" for mj in range(19)]
    _temcn[0] = "const int ROM[] = {"
    _temcn[1] = "  /* LSB         0,     1,     2,     3,     4,     5,     6,     7,     8,     9,     a,     b,     c,     d,     e,     f */"
    _temcn[18] = "};"
    for i in range(16):
        if(i == 0):
            _temcn[i+2] = "  /* MSB 0 */"
        else:
            _temcn[i+2] = "      /* " + str(hex(i)).replace("0x", "") + " */" 
        for j in range(16):
            _c = str(hex(_code[i*16+j])).replace("0x", "").zfill(2)
            _r = str(_rand[i*16+j])
            _temcn[i+2] += "0x" + _c + _r + ", "
    _emcn = "\n".join(_temcn)

    _tecsv = ["" for mi in range(259)] 
    _tecsv[0] = _pass + ".csv"
    _tecsv[1] = "adrs,code,asm"
    for i in range(256):
        _i = "0x" + str(hex(i).replace("0x", "")).zfill(2)
        _c = str(hex(_code[i])).replace("0x", "").zfill(2)
        _r = str(_rand[i])
        _a = _asm[i]
        _cr = _c + _r
        if(_a == "NOP"):
            _teasm[i+2] = _i
        else:
            _tecsv[i+2] = _i + "," + _cr + "," + _a
    _ecsv = "\n".join(_tecsv)

    return _easm, _emcn, _ecsv, _usage

#ファイルの書き出し
def export_file(_asm, _code, _csv, _usage, _pass):
    _a = input("Export txt file? (y/n) : ")
    _d = input("Export dat file? (y/n) : ")
    _c = input("Export csv file? (y/n) : ")

    if(_a == "Y" or _a == "y"):
        with open(_pass + ".txt", "w", encoding = "utf-8") as f:
            f.write(_asm)
            f.close()
        _asm_size = round((os.path.getsize(_pass + ".txt") / 1000), 1)
        print("asm file size : " + str(_asm_size) + "KB")

    if(_d == "Y" or _d == "y"):
        with open(_pass + ".dat", "w", encoding = "utf-8") as f:
            f.write(_code)
            f.close()
        _code_size = round((os.path.getsize(_pass + ".dat") / 1000), 1)
        print("dat file size : " + str(_code_size) + "KB")

    if(_c == "Y" or _c == "y"):
        with open(_pass + ".csv", "w", encoding = "utf-8") as f:
            f.write(_csv)
            f.close()
        _csv_size = round((os.path.getsize(_pass + ".csv") / 1000), 1)    
        print("csv file size : " + str(_csv_size) + "KB")
    
    print("\nSaved.")

    _usage_rate = round(100 * _usage / 256)
    print("Data usage    : " + str(_usage) + " / 256words (" + str(_usage_rate) + "%)")

#テキストが誤っている場合の警告，プログラムの終了
def syntax_error(_i, _t):
    print("Detect a syntax error in line", _i)
    print("error text : ", _t)

#メイン関数ここから
import_table(TABLE_ADRS)
assembly_text_list, epass = import_file()

list_length = len(assembly_text_list)
data_c = [0x20  for mi in range(256)] #256の静的配列確保
data_r = [0     for mj in range(256)] 
data_a = ["NOP" for mk in range(256)] 

for i in range(list_length):
    text_type = check_text_type(assembly_text_list[i]) #text_typeが0ならコメント，1なら命令，2ならエラー
    if(text_type == 1):
        address_value = search_address(assembly_text_list[i]) #書き込みアドレス
        machine_code, machine_rand, assembly = assemble(assembly_text_list[i]) #書き込みコード
        data_c[address_value] = machine_code
        data_r[address_value] = machine_rand
        data_a[address_value] = remove_hex(assembly)
        #print(hex(address_value), hex(data_c[address_value]), data_r[address_value])
    elif(text_type == 2):
        syntax_error(i, assembly_text_list[i])

dump_assembly(data_c, data_r, data_a)
asm_text, code_text, csv_text, usage = create_file(data_c, data_r, data_a, epass)
export_file(asm_text, code_text, csv_text, usage, epass)
