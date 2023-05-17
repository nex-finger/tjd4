#TJD4のアセンブラ
#Author : masuda
#Date   : 2023/4/17

import re

#アセンブリの正規表現
ASM = [
    "^\s*0x[0123456789abcdef]{2}\s+LDA,\s*A", "^\s*0x[0123456789abcdef]{2}\s+LDA,\s*B", "^\s*0x[0123456789abcdef]{2}\s+LDA,\s*X", "^\s*0x[0123456789abcdef]{2}\s+LDA,\s*Y",
    "^\s*0x[0123456789abcdef]{2}\s+LDB,\s*A", "^\s*0x[0123456789abcdef]{2}\s+LDB,\s*B", "^\s*0x[0123456789abcdef]{2}\s+LDB,\s*X", "^\s*0x[0123456789abcdef]{2}\s+LDB,\s*Y",
    "^\s*0x[0123456789abcdef]{2}\s+LDX,\s*A", "^\s*0x[0123456789abcdef]{2}\s+LDX,\s*B", "^\s*0x[0123456789abcdef]{2}\s+LDX,\s*X", "^\s*0x[0123456789abcdef]{2}\s+LDX,\s*Y",
    "^\s*0x[0123456789abcdef]{2}\s+LDY,\s*A", "^\s*0x[0123456789abcdef]{2}\s+LDY,\s*B", "^\s*0x[0123456789abcdef]{2}\s+LDY,\s*X", "^\s*0x[0123456789abcdef]{2}\s+LDY,\s*Y",
    "^\s*0x[0123456789abcdef]{2}\s+IMA,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+IMB,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+IMX,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+IMY,\s*[0123456789abcdef]",
    "^\s*0x[0123456789abcdef]{2}\s+ABA,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+ABB,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+ABX,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+ABY,\s*[0123456789abcdef]",
    "^\s*0x[0123456789abcdef]{2}\s+INA,", "^\s*0x[0123456789abcdef]{2}\s+INB,", "^\s*0x[0123456789abcdef]{2}\s+INX,", "^\s*0x[0123456789abcdef]{2}\s+INY,",
    "^\s*0x[0123456789abcdef]{2}\s+STA,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+STB,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+STX,\s*[0123456789abcdef]", "^\s*0x[0123456789abcdef]{2}\s+STY,\s*[0123456789abcdef]",
    "^\s*0x[0123456789abcdef]{2}\s+ADD", "^\s*0x[0123456789abcdef]{2}\s+SUB", "^\s*0x[0123456789abcdef]{2}\s+ORA", "^\s*0x[0123456789abcdef]{2}\s+AND",
    "^\s*0x[0123456789abcdef]{2}\s+ROR", "^\s*0x[0123456789abcdef]{2}\s+ROL", "^\s*0x[0123456789abcdef]{2}\s+TRA", "^\s*0x[0123456789abcdef]{2}\s+TRB",
    "^\s*0x[0123456789abcdef]{2}\s+JMP", "^\s*0x[0123456789abcdef]{2}\s+JCA", "^\s*0x[0123456789abcdef]{2}\s+JEQ", "^\s*0x[0123456789abcdef]{2}\s+JCM", "^\s*0x[0123456789abcdef]{2}\s+JIN"
]

#アセンブリに対応する機械語
BIN = [
    0b100000, 0b100001, 0b100010, 0b100011, 0b100100, 0b100101, 0b100110, 0b100111, 0b101000, 0b101001, 0b101010, 0b101011, 0b101100, 0b101101, 0b101110, 0b101111,
    0b110000, 0b110001, 0b110010, 0b110011, 0b110100, 0b110101, 0b110110, 0b110111, 0b111000, 0b111001, 0b111010, 0b111011, 0b011000, 0b011001, 0b011010, 0b011011,
    0b010000, 0b010001, 0b010010, 0b010011, 0b010100, 0b010101, 0b010110, 0b010111, 0b001000, 0b001100, 0b001101, 0b001110, 0b001111
]

#オペランドの有無
RAN = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

#ファイルの読み込み
def import_file():
    _pass = input("Input assembly file pass: ")
    _f = open(_pass, 'r')
    _text_list = _f.readlines()
    _f.close()
    return _text_list

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
                _operand = re.search(r"\d+$", match_matrix[0])
                _rand =  _operand.group(0)
            else:
                _rand = 0
            return BIN[i], _rand, match_matrix[0]
    return None, None, None

#アドレス消去
def remove_hex(_text):
    match = re.match(r'^0x[0-9a-fA-F]+\s', _text)
    if match:
        remaining_text = _text[match.end():].strip()
        return remaining_text
    else:
        return _text

#アセンブリ表示
def dump_assembly(_code, _rand, _asm):
    print("adrs", "\t", "code", "\t", "asm")
    print("-----------------------")
    for i in range(16):
        _i = "0x" + str(hex(i).replace("0x", "")).zfill(2)
        _c = str(hex(_code[i])).replace("0x", "").zfill(2)
        _r = str(_rand[i])
        _a = _asm[i]
        _cr = _c + _r
        print(_i, "\t", _cr, "\t", _a)
    _disp = input("Print all? (y/n) : ")
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

#機械語表示
def create_file():
    print("dmcn")

#ファイルの書き出し
def export_file():
    print("exf")

#テキストが誤っている場合の警告，プログラムの終了
def syntax_error(_i, _t):
    print("Detect a syntax error in line", _i)
    print("error text : ", _t)

#メイン関数ここから
assembly_text_list = import_file()

list_length = len(assembly_text_list)
data_c = [0x20 for mi in range(256)] #256の静的配列確保
data_r = [0 for mi in range(256)] 
data_a = ["NOP" for mi in range(256)] 

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
create_file()
export_file()