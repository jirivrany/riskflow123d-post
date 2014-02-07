#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append('../flowIni/')

import transport

data_sub = '''
$ElementData
1
"A_mobile_[M/L^3]"
1
100
1
1
1
1444
1 2
2 3
$EndElementData
$ElementData
1
"B_mobile_[M/L^3]"
1
100
1
0
1
1444
1 5
2 11
$EndElementData
'''

data_class = '''
$ElementData
1
"Concentration of RN"
1
10.000000
3
0
1
37068
1 1.000000
2 1.000000
3 1.000000
$EndElementData
$ElementData
1
"Concentration of RN"
1
20.000000
3
0
1
37068
1 2.000000
2 2.000000
3 2.000000
$EndElementData
'''

def test_read_single_subs():
    data = data_class.split('\n')
    result = transport.parse_single_substances(data, True)
    print result
    assert result[0] == [10.0, 20.0]
    assert result[1] == {1: {10.0: 1.0, 20.0: 2.0}, 2: {10.0: 1.0, 20.0: 2.0}, 3: {10.0: 1.0, 20.0: 2.0}} 
    assert result[2] == {1: 3.0, 2: 3.0, 3: 3.0}
    

    
def test_read_multiple_subs():
    data = data_sub.split('\n')
    result = transport.parse_multiple_substances(data, True) 
    assert result[0] == [100.0]
    assert result[1] == {
                         'A_mobile_[M/L^3]': {1: {100.0: 2.0}, 2: {100.0: 3.0}},
                         'B_mobile_[M/L^3]': {1: {100.0: 5.0}, 2: {100.0: 11.0}}
                         }
    
    assert result[2] == {
                         'A_mobile_[M/L^3]': {1: 2.0, 2: 3.0},
                         'B_mobile_[M/L^3]': {1: 5.0, 2: 11.0}
                         }
    
def test_change_ini_file():
    ininame = '/home/albert/data/risk_flow/test_data/2substance/flow.ini'
    transport.create_ini_file_for_substance(ininame, 'A')
    ininame2 = '/home/albert/data/risk_flow/test_data/2substance/A/A_flow.ini'
    assert transport.get_name_from_ini_file(ininame2) == '../krychle_t.pos'
    
def test_parse_dir():
    ininame = '/home/albert/data/risk_flow/substance/pokus_ndir'
    soubory = transport.get_result_files(ininame, True)
    transport.read_process_substances(soubory, 'json')
    
if __name__ == '__main__':
    test_parse_dir()

    