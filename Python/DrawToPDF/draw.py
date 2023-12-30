import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from compute import calculate_r_squared

def linear_img(savefoder, df0, df1, dfsc, corrname, item, dict1):
    plt.close()
    plt.xlabel(corrname[0])
    plt.ylabel(corrname[1])

    dff0 = df0.loc[:, [dict1["Serial_Number"], item]][~df0.loc[:, item].isna()]
    dff1 = df1.loc[:, [dict1["Serial_Number"], item]][~df1.loc[:, item].isna()]

    dff = pd.merge(dff0, dff1, left_on=dict1["Serial_Number"], right_on=dict1["Serial_Number"], how='inner')

    xArr = dff.iloc[:, 1]
    yArr = dff.iloc[:, 2]
    l1 = min(xArr.min(), yArr.min())
    l2 = max(xArr.max(), yArr.max())
    if (dff.empty):
        print('no data in ' + item)
        return 0
    if item in dfsc.index:
        if (dfsc.loc[item, dict1["LSL"]] != '-' and dfsc.loc[item, dict1["USL"]] != '-'):
            if (dfsc.loc[item, dict1["LSL"]] < l1):
                l1 = dfsc.loc[item, dict1["LSL"]]
            if (dfsc.loc[item, dict1["USL"]] > l2):
                l2 = dfsc.loc[item, dict1["USL"]]
            # l1 = dfsc.loc[item, dict1["LSL"]]
            # l2 = dfsc.loc[item, dict1["USL"]]
            plt.xlim(l1 - (l2 - l1) / 8, l2 + (l2 - l1) / 8)
            plt.ylim(l1 - (l2 - l1) / 8, l2 + (l2 - l1) / 8)
        else:
            if (l1 != l2):
                if(dfsc.loc[item, dict1["LSL"]] != '-'):
                    if(dfsc.loc[item, dict1["LSL"]] < l1):
                        l1 = dfsc.loc[item, dict1["LSL"]]
                    if(dfsc.loc[item, dict1["LSL"]] > l2):
                        l2 = dfsc.loc[item, dict1["LSL"]]
                if(dfsc.loc[item, dict1["USL"]] != '-'):
                    if(dfsc.loc[item, dict1["USL"]] > l2):
                        l2 = dfsc.loc[item, dict1["USL"]]
                    if(dfsc.loc[item, dict1["USL"]] < l1):
                        l1 = dfsc.loc[item, dict1["USL"]]
                plt.xlim(l1 - (l2 - l1) / 8, l2 + (l2 - l1) / 8)
                plt.ylim(l1 - (l2 - l1) / 8, l2 + (l2 - l1) / 8)

        set_spec(dfsc, item, dict1)
    else:
        # print("specs csv doesn't has "+item)
        if (l1 != l2):
            plt.xlim(l1 - (l2 - l1) / 8, l2 + (l2 - l1) / 8)
            plt.ylim(l1 - (l2 - l1) / 8, l2 + (l2 - l1) / 8)

    x = dff.iloc[:, 1].values
    y = dff.iloc[:, 2].values

    r2, a, b = calculate_r_squared(x, y)
    draw_scatter(dff, x, r2, a, b, plt, dict1)

    if (l1 == l2):
        if (l1 > 0):
            line = plt.plot([0.5 * l1, 2 * l2], [0.5 * l1, 2 * l2], linestyle='--', color='#cfcfc4')
        elif (l1 == 0):
            line = plt.plot([-1, 1], [-1, 1], linestyle='--', color='#cfcfc4')
        else:
            line = plt.plot([2 * l1, 2 * l2], [2 * l1, 2 * l2], linestyle='--', color='#cfcfc4')
    else:
        line = plt.plot([-100000, 100000], [-100000, 100000], linestyle='--', color='#cfcfc4')
    # 将线条的层级顺序设置为最高
    plt.gca().set_zorder(line[0].get_zorder() + 1)

    if(dict1["axis_range"] == "on"):
        if item in dfsc.index:
            if (pd.notna(dfsc.loc[item, dict1["axis_x1"]]) and pd.notna(dfsc.loc[item, dict1["axis_x2"]])):
                plt.xlim(float(dfsc.loc[item, dict1["axis_x1"]]), float(dfsc.loc[item, dict1["axis_x2"]]))
            if (pd.notna(dfsc.loc[item, dict1["axis_y1"]]) and pd.notna(dfsc.loc[item, dict1["axis_y2"]])):
                plt.ylim(float(dfsc.loc[item, dict1["axis_y1"]]), float(dfsc.loc[item, dict1["axis_y2"]]))

    if(dict1["xy_grid"] == "on"):
        plt.grid(color='gray', linestyle='-', linewidth=dict1["xy_grid_linewidth"])

    plt.savefig(savefoder + '/' + item.replace('/', '') + '1.png')
    return 1

def set_spec(dfsc, item, dict1):
    if (dict1["xy_spec_set_y"] == "on"):
        if (pd.notna(dfsc.loc[item, dict1["LSL"]]) and dfsc.loc[item, dict1["LSL"]] != '-'):
            plt.axvline(x=dfsc.loc[item, dict1["LSL"]], color='y', linestyle='dashed')
        if (pd.notna(dfsc.loc[item, dict1["USL"]]) and dfsc.loc[item, dict1["USL"]] != '-'):
            plt.axvline(x=dfsc.loc[item, dict1["USL"]], color='r', linestyle='dashed')

        if (pd.notna(dfsc.loc[item, dict1["xy_spec_y_lsl"]]) and dfsc.loc[item, dict1["xy_spec_y_lsl"]] != '-'):
            plt.axhline(y=dfsc.loc[item, dict1["xy_spec_y_lsl"]], color='y', linestyle='dashed')
        if (pd.notna(dfsc.loc[item, dict1["xy_spec_y_usl"]]) and dfsc.loc[item, dict1["xy_spec_y_usl"]] != '-'):
            plt.axhline(y=dfsc.loc[item, dict1["xy_spec_y_usl"]], color='r', linestyle='dashed')
    else:
        if (pd.notna(dfsc.loc[item, dict1["LSL"]]) and dfsc.loc[item, dict1["LSL"]] != '-'):
            plt.axhline(y=dfsc.loc[item, dict1["LSL"]], color='y', linestyle='dashed')
            plt.axvline(x=dfsc.loc[item, dict1["LSL"]], color='y', linestyle='dashed')
        if (pd.notna(dfsc.loc[item, dict1["USL"]]) and dfsc.loc[item, dict1["USL"]] != '-'):
            plt.axhline(y=dfsc.loc[item, dict1["USL"]], color='r', linestyle='dashed')
            plt.axvline(x=dfsc.loc[item, dict1["USL"]], color='r', linestyle='dashed')

def dot_img(savefoder, df0, df1, dfsc, corrname, item, order, dict1):
    plt.close()

    dff0 = df0.loc[:, [dict1["Serial_Number"], item]][~df0.loc[:, item].isna()]
    dff1 = df1.loc[:, [dict1["Serial_Number"], item]][~df1.loc[:, item].isna()]

    try:
        y1 = dff0.iloc[:, 1].values
        y2 = dff1.iloc[:, 1].values

        # 为两组数据手动设置x轴坐标
        x1 = np.linspace(20, 40, len(y1))  # 创建一个从1到4的等间隔数组，长度与y1相同
        x2 = np.linspace(60, 80, len(y2))  # 创建一个从6到9的等间隔数组，长度与y2相同

        # 计算均值和方差
        mean1, std1 = np.mean(y1), np.std(y1)
        mean2, std2 = np.mean(y2), np.std(y2)

        # 绘制散点图
        plt.scatter(x1, y1, label=f'Mean: {mean1:.2f}, Std Dev: {std1:.2f}', s=dict1["dot_size"])
        plt.scatter(x2, y2, label=f'Mean: {mean2:.2f}, Std Dev: {std2:.2f}', s=dict1["dot_size"])

        plt.xlim(0, 100)

        l1 = min(y1.min(), y2.min())
        l2 = max(y1.max(), y2.max())

        try:
            if (pd.notna(dfsc.loc[item, dict1["LSL"]]) and dfsc.loc[item, dict1["LSL"]] != '-'):
                plt.axhline(y=dfsc.loc[item, dict1["LSL"]], color='y', linestyle='dashed')
                if (l1 > dfsc.loc[item, dict1["LSL"]]):
                    l1 = dfsc.loc[item, dict1["LSL"]]
            if (pd.notna(dfsc.loc[item, dict1["USL"]]) and dfsc.loc[item, dict1["USL"]] != '-'):
                plt.axhline(y=dfsc.loc[item, dict1["USL"]], color='r', linestyle='dashed')
                if (l2 < dfsc.loc[item, dict1["USL"]]):
                    l2 = dfsc.loc[item, dict1["USL"]]
        except:
            # print(item + " has no spec")
            pass

        if (l1 != l2):
            plt.ylim(l1 - (l2 - l1) / 4, l2 + (l2 - l1) / 4)

        # 添加图例
        plt.legend()

    except:
        print(item + " can't scatter")
        return 0

    # 设置x轴刻度和标签
    plt.xticks([30, 70], [corrname[0], corrname[1]])
    # 去除x轴刻度
    plt.tick_params(axis='x', which='both', bottom=False, top=False)

    plt.savefig(savefoder + '/' + item.replace('/', '') + str(order) + '.png')
    return 1

def box_img(savefolder, dfdata, dfsc, item, order, dict1):
    corrname = dfdata[dict1["corr"]].unique().tolist()
    data = []

    plt.close()

    for name in corrname:
        df_temp = dfdata[dfdata.loc[:, dict1["corr"]] == name]
        dff_temp = df_temp.loc[:, [dict1["Serial_Number"], item]][~df_temp.loc[:, item].isna()]

        try:
            y_temp = dff_temp.iloc[:, 1].values
            data.append(y_temp)
        except:
            print(f"Error processing {name}")
            continue

    if len(data) == 0:
        print(item + " can't scatter")
        return 0

    plt.figure(figsize=(dict1["box_img_w"]/100.0, 4.8))

    # 绘制箱型图
    boxplots = plt.boxplot(data, positions=range(1, len(corrname) + 1), widths=0.6)

    l1 = min(min(d) for d in data)
    l2 = max(max(d) for d in data)

    if item in dfsc.index:
        if (dfsc.loc[item, dict1["LSL"]] != '-' and dfsc.loc[item, dict1["USL"]] != '-'):
            if (dfsc.loc[item, dict1["LSL"]] < l1):
                l1 = dfsc.loc[item, dict1["LSL"]]
            if (dfsc.loc[item, dict1["USL"]] > l2):
                l2 = dfsc.loc[item, dict1["USL"]]
            plt.ylim(l1 - (l2 - l1) / 4, l2 + (l2 - l1) / 4)
        else:
            if (l1 != l2):
                if(dfsc.loc[item, dict1["LSL"]] != '-'):
                    if(dfsc.loc[item, dict1["LSL"]] < l1):
                        l1 = dfsc.loc[item, dict1["LSL"]]
                    if(dfsc.loc[item, dict1["LSL"]] > l2):
                        l2 = dfsc.loc[item, dict1["LSL"]]
                if(dfsc.loc[item, dict1["USL"]] != '-'):
                    if(dfsc.loc[item, dict1["USL"]] > l2):
                        l2 = dfsc.loc[item, dict1["USL"]]
                    if(dfsc.loc[item, dict1["USL"]] < l1):
                        l1 = dfsc.loc[item, dict1["USL"]]
                plt.ylim(l1 - (l2 - l1) / 4, l2 + (l2 - l1) / 4)
            else:
                plt.ylim(l1 - 1, l1 + 1)  # 用于所有数据相等时提供一些空间
        if (pd.notna(dfsc.loc[item, dict1["LSL"]]) and dfsc.loc[item, dict1["LSL"]] != '-'):
            plt.axhline(y=dfsc.loc[item, dict1["LSL"]], color='y', linestyle='dashed')
        if (pd.notna(dfsc.loc[item, dict1["USL"]]) and dfsc.loc[item, dict1["USL"]] != '-'):
            plt.axhline(y=dfsc.loc[item, dict1["USL"]], color='r', linestyle='dashed')
    else:
        if (l1 != l2):
            plt.ylim(l1 - (l2 - l1) / 4, l2 + (l2 - l1) / 4)
        else:
            plt.ylim(l1 - 1, l1 + 1)  # 用于所有数据相等时提供一些空间

    # 设置 x 轴刻度标签
    plt.xticks(range(1, len(corrname) + 1), corrname)

    # 定义统一的格式
    decimal_format = "." + str(dict1["box_decimal_format"]) + "f"  # 保留两位小数的格式

    # 添加均值标签
    for i, d in enumerate(data):
        mean_val = sum(d) / len(d)
        std_val = np.std(d)
        upper_whisker = boxplots['whiskers'][2*i+1].get_ydata()[1]  # 获取上边缘的值
        if mean_val == upper_whisker or l1 == l2:
            y_position = upper_whisker + abs(l2 - l1) * 0.2 + mean_val * 0.1 # 当所有数据相等时, 按比例上移并增加均值的一部分
        else:
            y_position = l2 + (l2 - l1) / 20

        # 微调文本位置，使其垂直方向上稍微往上移
        y_position += (l2 - l1) * 0.05  # 这里的0.05是调整因子
        # plt.text(i + 1, y_position, f"Mean: {mean_val:.2f}",
        #          ha='center', va='center', fontsize=8)
        plt.text(i + 1, y_position, f"Mean: {mean_val:{decimal_format}}\nStD: {std_val:{decimal_format}}",
                 ha='center', va='center', fontsize=dict1["box_font_size"])

    plt.savefig(savefolder + '/' + item.replace('/', '') + str(order) + '.png', dpi=dict1["box_img_dpi"])
    return 1

def draw_scatter(dff, x, r2, a, b, plt, dict1):
    # 定义统一的格式
    decimal_format = "." + str(dict1["xy_decimal_format"]) + "f"  # 保留小数的格式

    if (dict1["r2_position"] != "inside"):
        if (r2 == 1):
            plt.title('R2_score=' + str(r2))
        else:
            if (b > 0):
                plt.title('R2_score = ' + str(round(r2, dict1["xy_decimal_format"])) + '   ' + 'Y = ' + str(round(a[0], dict1["xy_decimal_format"])) + 'x + ' + str(
                    round(b, dict1["xy_decimal_format"])))
            else:
                plt.title('R2_score = ' + str(round(r2, dict1["xy_decimal_format"])) + '   ' + 'Y = ' + str(round(a[0], dict1["xy_decimal_format"])) + 'x - ' + str(
                    abs(round(b, dict1["xy_decimal_format"]))))
            plt.plot(x, a * x + b, color='#5b4756')
        plt.scatter(dff.iloc[:, 1], dff.iloc[:, 2], color='black', s=dict1["dot_size"])
    else:
        if(r2 == 1):
            plt.scatter(dff.iloc[:, 1], dff.iloc[:, 2], color='black', s=dict1["dot_size"], label=f'R2_score = {r2:{decimal_format}}')
        else:
            equal = ""
            if (b >= 0):
                equal = 'Y = ' + str(round(a[0], dict1["xy_decimal_format"])) + 'x + ' + str(round(b, dict1["xy_decimal_format"]))
            else:
                equal = 'Y = ' + str(round(a[0], dict1["xy_decimal_format"])) + 'x - ' + str(abs(round(b, dict1["xy_decimal_format"])))
            plt.plot(x, a * x + b, color='#5b4756')
            plt.scatter(dff.iloc[:, 1], dff.iloc[:, 2], color='black', s=dict1["dot_size"], label=f'R2_score = {r2:{decimal_format}}\n' + equal)
        plt.legend()

def hist_img(savefoder, df0, df1, dfsc, corrname, item, order, dict1):
    plt.close()

    dff0 = df0.loc[:, [dict1["Serial_Number"], item]][~df0.loc[:, item].isna()]
    dff1 = df1.loc[:, [dict1["Serial_Number"], item]][~df1.loc[:, item].isna()]

    try:
        y1 = dff0.iloc[:, 1].values
        y2 = dff1.iloc[:, 1].values

        # 计算均值和方差
        mean1, std1 = np.mean(y1), np.std(y1)
        mean2, std2 = np.mean(y2), np.std(y2)

        plt.hist(y1, bins=dict1["hist_quantity"], density=True, alpha=dict1["hist_alpha"], label=corrname[0]) # 创建直方图，柱子高度表示频率
        plt.hist(y2, bins=dict1["hist_quantity"], density=True, alpha=dict1["hist_alpha"], label=corrname[1]) # 创建直方图，柱子高度表示频率

        # 添加图例
        if(dict1["hist_label_position_auto"] == 'off'):
            plt.legend(loc='upper right')
        else:
            plt.legend()

        l1 = min(y1.min(), y2.min())
        l2 = max(y1.max(), y2.max())

        if item in dfsc.index:
            if (dfsc.loc[item, dict1["LSL"]] != '-' and dfsc.loc[item, dict1["USL"]] != '-'):
                if (dfsc.loc[item, dict1["LSL"]] < l1):
                    l1 = dfsc.loc[item, dict1["LSL"]]
                if (dfsc.loc[item, dict1["USL"]] > l2):
                    l2 = dfsc.loc[item, dict1["USL"]]
                plt.xlim(l1 - (l2 - l1) / 9, l2 + (l2 - l1) / 9)
            else:
                if (l1 != l2):
                    if (dfsc.loc[item, dict1["LSL"]] != '-'):
                        if (dfsc.loc[item, dict1["LSL"]] < l1):
                            l1 = dfsc.loc[item, dict1["LSL"]]
                        if (dfsc.loc[item, dict1["LSL"]] > l2):
                            l2 = dfsc.loc[item, dict1["LSL"]]
                    if (dfsc.loc[item, dict1["USL"]] != '-'):
                        if (dfsc.loc[item, dict1["USL"]] > l2):
                            l2 = dfsc.loc[item, dict1["USL"]]
                        if (dfsc.loc[item, dict1["USL"]] < l1):
                            l1 = dfsc.loc[item, dict1["USL"]]
                    plt.xlim(l1 - (l2 - l1) / 9, l2 + (l2 - l1) / 9)

            if (pd.notna(dfsc.loc[item, dict1["LSL"]]) and dfsc.loc[item, dict1["LSL"]] != '-'):
                plt.axvline(x=dfsc.loc[item, dict1["LSL"]], color='y', linestyle='dashed')
            if (pd.notna(dfsc.loc[item, dict1["USL"]]) and dfsc.loc[item, dict1["USL"]] != '-'):
                plt.axvline(x=dfsc.loc[item, dict1["USL"]], color='r', linestyle='dashed')

    except:
        print(item + " can't draw_bar")
        return 0

    # 定义统一的格式
    decimal_format = "." + str(dict1["hist_decimal_format"]) + "f"  # 保留两位小数的格式

    # 使用定义的格式来格式化字符串
    plt.title(f"{corrname[0]}: N = {len(y1)}, Mean = {mean1:{decimal_format}}, Std = {std1:{decimal_format}}",
              fontsize=dict1["hist_label_size"])
    plt.xlabel(f"{corrname[1]}: N = {len(y2)}, Mean = {mean2:{decimal_format}}, Std = {std2:{decimal_format}}",
               fontsize=dict1["hist_label_size"])

    if(dict1["hist_grid"] == "on"):
        plt.grid(color='gray', linestyle='-', linewidth=dict1["hist_grid_linewidth"])

    plt.savefig(savefoder + '/' + item.replace('/', '') + str(order) + '.png')
    return 1

def hist_img1(savefoder, df0, df1, dfsc, corrname, item, order, dict1):
    plt.close()

    dff0 = df0.loc[:, [dict1["Serial_Number"], item]][~df0.loc[:, item].isna()]
    dff1 = df1.loc[:, [dict1["Serial_Number"], item]][~df1.loc[:, item].isna()]

    try:
        y1 = dff0.iloc[:, 1].values
        y2 = dff1.iloc[:, 1].values

        # 计算均值和方差
        mean1, std1 = np.mean(y1), np.std(y1)
        mean2, std2 = np.mean(y2), np.std(y2)

        plt.hist(y1, bins=dict1["hist_quantity"], density=True, alpha=dict1["hist_alpha"], label=corrname[0]) # 创建直方图，柱子高度表示频率
        plt.hist(y2, bins=dict1["hist_quantity"], density=True, alpha=dict1["hist_alpha"], label=corrname[1]) # 创建直方图，柱子高度表示频率

        # 添加图例
        if(dict1["hist_label_position_auto"] == 'off'):
            plt.legend(loc='upper right')
        else:
            plt.legend()

        l1 = min(y1.min(), y2.min())
        l2 = max(y1.max(), y2.max())

        if item in dfsc.index:
            if (dfsc.loc[item, dict1["LSL"]] != '-' and dfsc.loc[item, dict1["USL"]] != '-'):
                if (dfsc.loc[item, dict1["LSL"]] < l1):
                    l1 = dfsc.loc[item, dict1["LSL"]]
                if (dfsc.loc[item, dict1["USL"]] > l2):
                    l2 = dfsc.loc[item, dict1["USL"]]
                plt.xlim(l1 - (l2 - l1) / 9, l2 + (l2 - l1) / 9)
            else:
                if (l1 != l2):
                    if (dfsc.loc[item, dict1["LSL"]] != '-'):
                        if (dfsc.loc[item, dict1["LSL"]] < l1):
                            l1 = dfsc.loc[item, dict1["LSL"]]
                        if (dfsc.loc[item, dict1["LSL"]] > l2):
                            l2 = dfsc.loc[item, dict1["LSL"]]
                    if (dfsc.loc[item, dict1["USL"]] != '-'):
                        if (dfsc.loc[item, dict1["USL"]] > l2):
                            l2 = dfsc.loc[item, dict1["USL"]]
                        if (dfsc.loc[item, dict1["USL"]] < l1):
                            l1 = dfsc.loc[item, dict1["USL"]]
                    plt.xlim(l1 - (l2 - l1) / 9, l2 + (l2 - l1) / 9)

            if (pd.notna(dfsc.loc[item, dict1["LSL"]]) and dfsc.loc[item, dict1["LSL"]] != '-'):
                plt.axvline(x=dfsc.loc[item, dict1["LSL"]], color='y', linestyle='dashed')
            if (pd.notna(dfsc.loc[item, dict1["USL"]]) and dfsc.loc[item, dict1["USL"]] != '-'):
                plt.axvline(x=dfsc.loc[item, dict1["USL"]], color='r', linestyle='dashed')

    except:
        print(item + " can't draw_bar")
        return 0

    # 定义统一的格式
    decimal_format = "." + str(dict1["hist_decimal_format"]) + "f"  # 保留两位小数的格式

    dict1["title_text"] = f"{corrname[0]}: N = {len(y1)}, Mean = {mean1:{decimal_format}}, Std = {std1:{decimal_format}}"
    dict1["xlabel_text"] = f"{corrname[1]}: N = {len(y2)}, Mean = {mean2:{decimal_format}}, Std = {std2:{decimal_format}}"

    # 使用定义的格式来格式化字符串
    # plt.title(f"{corrname[0]}: N = {len(y1)}, Mean = {mean1:{decimal_format}}, Std = {std1:{decimal_format}}",
    #           fontsize=dict1["hist_label_size"])
    # plt.xlabel(f"{corrname[1]}: N = {len(y2)}, Mean = {mean2:{decimal_format}}, Std = {std2:{decimal_format}}",
    #            fontsize=dict1["hist_label_size"])

    if(dict1["hist_grid"] == "on"):
        plt.grid(color='gray', linestyle='-', linewidth=dict1["hist_grid_linewidth"])

    plt.savefig(savefoder + '/' + item.replace('/', '') + str(order) + '.png')
    return 1