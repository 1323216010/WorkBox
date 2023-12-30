import pandas as pd
from utils import getDesc

def toGetCnt(dfA):
    if (len(dfA) < 1): return (0, 0, 0, set())
    pass_cnt = (dfA['result'] == 'PASS').sum()
    unknown_cnt = (dfA['result'] == 'Unknown').sum()
    failItems = dfA[dfA['result'].isin(['Unknown', 'PASS']) == False]
    fail_cnt = len(failItems)
    assert (len(dfA) == pass_cnt + unknown_cnt + fail_cnt)
    return (pass_cnt, unknown_cnt, fail_cnt, set(failItems['result']))

def toTwiceCheckFailCnt(dfA, lst_failcode, pass_cnt1, unknown_cnt1, fail_cnt1):
    lst_1st = [0] * len(lst_failcode)
    lst_1st[0:4] = len(dfA), pass_cnt1, fail_cnt1, unknown_cnt1
    for idx, item in enumerate(lst_failcode):
        if 'header' in item: continue
        lst_1st[idx] = (dfA['result'] == item).sum()
    assert (sum(lst_1st[4:]) == fail_cnt1)
    return lst_1st

def toGenYieldTable(df, data):
    # if len(df)<1: return None
    pass_cnt1, unknown_cnt1, fail_cnt1, failcodeSet1 = toGetCnt(df[df['bar_testOrder'] == 1])
    pass_cnt2, unknown_cnt2, fail_cnt2, failcodeSet2 = toGetCnt(df[df['bar_testOrder'] == 2])
    pass_cnt3, unknown_cnt3, fail_cnt3, failcodeSet3 = toGetCnt(df[df['bar_testOrder'] == 3])
    pass_cntF, unknown_cntF, fail_cntF, failcodeSetF = toGetCnt(df[df['bar_isFinalTest'] == True])

    failcodeAll = failcodeSet1 | failcodeSet2 | failcodeSet3 | failcodeSetF
    lst_failcode = ['header'] * 4
    lst_failcode += list(failcodeAll)

    lst_1st = toTwiceCheckFailCnt(df[df['bar_testOrder'] == 1], lst_failcode, pass_cnt1, unknown_cnt1, fail_cnt1)
    lst_2nd = toTwiceCheckFailCnt(df[df['bar_testOrder'] == 2], lst_failcode, pass_cnt2, unknown_cnt2, fail_cnt2)
    lst_3rd = toTwiceCheckFailCnt(df[df['bar_testOrder'] == 3], lst_failcode, pass_cnt3, unknown_cnt3, fail_cnt3)
    lst_final = toTwiceCheckFailCnt(df[df['bar_isFinalTest'] == True], lst_failcode, pass_cntF, unknown_cntF, fail_cntF)

    lst_desc = [""] * len(lst_failcode)
    lst_desc[0] = 'Input'
    lst_desc[1] = 'Pass'
    lst_desc[2] = 'Fail'
    lst_desc[3] = 'Unknown'
    dfres = pd.DataFrame()

    getDesc(lst_failcode, lst_desc, data)
    dfres['failcode'] = lst_failcode
    dfres['faildesc'] = lst_desc
    dfres['1st_test'] = lst_1st
    dfres['2nd_test'] = lst_2nd
    dfres['3rd_test'] = lst_3rd
    dfres['final_test'] = lst_final
    return dfres
