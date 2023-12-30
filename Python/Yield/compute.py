import pandas as pd
from toGenYield import toGenYieldTable
from utils import filter_by_string
from utils import read_csv

def toDoTargetS(TargetS, data):
    stations = data['stations']
    colSelect = data['column']
    mydict = getStationDict(TargetS, stations, colSelect, data)

    # 两两连接
    dfMerge = getDfmerge(mydict, stations, colSelect, data)

    dfMerge['result'] = getResult(dfMerge, stations)

    # 要先按照测试时间排序
    dfMerge.sort_values(data['SiteTime'], ascending=True, na_position='first', inplace=True)

    testOrder, totalTestTimes = getColumn(dfMerge, data)
    dfMerge['bar_testOrder'] = testOrder
    dfMerge['bar_TotalTestTimes'] = totalTestTimes

    # 该列的值根据'bar_TotalTestTimes'和'bar_testOrder'是否相等来确定
    dfMerge['bar_isFinalTest'] = dfMerge['bar_TotalTestTimes'] == dfMerge['bar_testOrder']

    # 重新调整dfMerge数据框的列的顺序（Match_Item放在最前）
    part1 = ['Match_Item']
    part2 = [x for x in dfMerge.columns if 'Match_Item' not in x]
    dfMerge = dfMerge[part1 + part2]

    dfMerge.sort_values(by=[data['barcode'], 'bar_testOrder'], ascending=True, na_position='first', inplace=True)

    # so 一个特征目录保存一个文件
    dfYield = toGenYieldTable(dfMerge, data)

    return (dfMerge, dfYield)

def getStationDict(TargetS, stations, colSelect, data):
    mydict = {}
    for station in stations:
        # 得到当前站位的所有summary log路径
        filePaths = filter_by_string(TargetS, station)
        assert (len(filePaths) > 0)

        lst = []
        for path in filePaths:
            print(path)
            df = read_csv(path)
            try:
                df = df[df[data['barcode']] != '-']
                lst.append(df[colSelect])
            except:
                data['exception_files'].append(path)
                print("File read failure: ", path)
                continue

        #合并
        dfStation = pd.concat(lst, axis=0)
        dfStation['Match_Item'] = dfStation[data['barcode']] + '_' + dfStation[data['SiteTime']]
        dfStation.rename({data['PASS_FAIL']: station + '_PASS_FAIL'}, axis=1, inplace=True)

        mydict[station] = dfStation

    return mydict

def getDfmerge(mydict, stations, colSelect, data):
    # 两两连接
    dfMerge = mydict[stations[0]]
    # 只保留一个
    dfMerge.drop_duplicates('Match_Item', keep='last', inplace=True)

    for station in stations[1:]:
        df = mydict[station]
        df.drop([x for x in colSelect if data['PASS_FAIL'] not in x], axis=1, inplace=True)

        dfMerge = pd.merge(dfMerge, df, how='left', on='Match_Item')
        dfMerge.drop_duplicates('Match_Item', keep='last', inplace=True)
        # 看来左连接会与多个相同的item ,需要去重
    return dfMerge

def getResult(dfMerge, stations):
    names = [x + '_PASS_FAIL' for x in stations]
    # 使用列表推导式生成lstNames列表

    def process_row(row):
        # 定义一个处理单行数据的函数
        for name in names:
            if isinstance(row[name], str):
                if 'PASS' not in row[name]:
                    return row[name]
            else:
                return 'Unknown'
        return 'PASS'

    return dfMerge.apply(process_row, axis=1).tolist()
    # 使用DataFrame的apply方法应用process_row函数到每一行，然后将结果转换为列表

def getColumn(dfMerge, data):
    # 创建一个长度与dfMerge相同的列表，所有元素初始化为0
    testOrder = []

    # 创建一个空字典，用于存储每个条形码及其出现的次数
    testTimes = {}

    # 遍历dfMerge中的"barcode"列
    for i, bar in enumerate(dfMerge[data["barcode"]]):
        # 如果条形码已经在字典中，那么将其对应的次数加1
        if bar in testTimes.keys():
            testTimes[bar] += 1
        # 如果条形码不在字典中，那么将其添加到字典中，并设置其次数为1
        else:
            testTimes[bar] = 1
        # 将条形码的次数存储在lstRename列表的对应位置
        testOrder.append(testTimes[bar])

    # 创建另一个长度与dfMerge相同的列表，所有元素初始化为0
    totalTestTimes = []

    # 再次遍历dfMerge中的"barcode"列
    for i, bar in enumerate(dfMerge[data["barcode"]]):
        # 将条形码的次数存储在mylst列表的对应位置
        totalTestTimes.append(testTimes[bar])
    return testOrder, totalTestTimes