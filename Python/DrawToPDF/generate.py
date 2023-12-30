import pandas as pd
from tqdm import trange
from draw import linear_img
from draw import dot_img
from draw import box_img
from draw import hist_img
from draw import hist_img1

#生成一种类型的图
def generate_pdf1(pdf, savefoder, dfdata, dfsc, dict1, mode):
    img_w, img_h = 640, 480
    pdf_size = (1920, 1080)
    pdf.setPageSize(pdf_size)
    flag = 0
    items = []
    total = 0

    corrname = dfdata[dict1["corr"]].unique().tolist()
    df0 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[0]]
    df1 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[1]]

    if (dict1["depend_spec"] == "on"):
        combined_set = list(set(dict1["uncorrs"]) | (set(dfsc.index.tolist()) & set(df0.columns.tolist())))
        # 使用列表推导式保持原始顺序
        filtered_columns = [col for col in df0.columns if col in combined_set]

        df0 = df0.loc[:, filtered_columns]  # 通过 loc 方法过滤列
        df1 = df0.loc[:, filtered_columns]

    n = df0.columns.size

    pdf.setFont(dict1["font"], dict1["font_size"])
    for i in trange(n, desc=dict1["sheetname"] + ' Progress'):
        item=df0.columns[i]

        # 如果当前列是xy类型名或者是关联列则跳过
        if(item in dict1["uncorrs"]):
            continue

        # 如果当前列含有字符串则跳过
        if(not pd.api.types.is_numeric_dtype(df0.loc[:,item])):
            print(item+' has string, which is not compared '+'df0.loc[0,item]=', df0.loc[0,item])
            continue
        if(mode == "1"):
            if (dot_img(savefoder, df0, df1, dfsc, corrname, item, 1, dict1) == 0):
                continue
        elif(mode == "2"):
            if (linear_img(savefoder, df0, df1, dfsc, corrname, item, dict1) == 0):
                continue
        else:
            print("type error")
            break

        items.append(item)

        if(len(items) == 2):
            img_x = 320
            if(flag == 1):
                img_y = 60 + img_h
                flag = 0
            else:
                img_y = 60
                flag = 1

            pdf.drawImage(savefoder+'/'+items[0].replace('/','')+'1.png',img_x,img_y,img_w,img_h)
            text_width = pdf.stringWidth(items[0], dict1["font"], dict1["font_size"])
            pdf.drawString(320 + (img_w - text_width)/2, 480 + img_y - 25 + dict1["font_high"], items[0])
            pdf.drawImage(savefoder+'/'+items[1].replace('/','')+'1.png', img_x + img_w, img_y, img_w, img_h)

            text_width = pdf.stringWidth(items[1], dict1["font"], dict1["font_size"])
            pdf.drawString(320 + img_w + (img_w - text_width)/2, 480 + img_y -  25 + dict1["font_high"], items[1])
            items = []
            if(flag == 1):
                pdf.showPage()
                pdf.setFont(dict1["font"], dict1["font_size"])
        elif(i == df0.columns.size - 1 and len(items) == 1 ):
            img_x = 320
            if(flag == 1):
                img_y = 60 + img_h
            else:
                img_y = 60

            pdf.drawImage(savefoder + '/' + items[0].replace('/', '') + '1.png', img_x, img_y, img_w, img_h)
            text_width = pdf.stringWidth(items[0], dict1["font"], dict1["font_size"])
            pdf.drawString(320 + (img_w - text_width) / 2, 480 + img_y - 25 + dict1["font_high"], items[0])

        total = total + 1

    return total

#生成散点图和线性拟合图
def generate_pdf2(pdf, savefoder, dfdata, dfsc, dict1):
    img_w, img_h = 640, 480
    pdf_size = (1920, 1080)
    pdf.setPageSize(pdf_size)
    flag = 1
    total = 0

    corrname = dfdata[dict1["corr"]].unique().tolist()
    df0 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[0]]
    df1 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[1]]

    if (dict1["depend_spec"] == "on"):
        combined_set = list(set(dict1["uncorrs"]) | (set(dfsc.index.tolist()) & set(df0.columns.tolist())))
        # 使用列表推导式保持原始顺序
        filtered_columns = [col for col in df0.columns if col in combined_set]

        df0 = df0.loc[:, filtered_columns]  # 通过 loc 方法过滤列
        df1 = df0.loc[:, filtered_columns]

    n = df0.columns.size

    pdf.setFont(dict1["font"], dict1["font_size"])
    for i in trange(n, desc=dict1["sheetname"] + ' Progress'):
        item=df0.columns[i]

        if(item in dict1["uncorrs"]):
            continue
        if(not pd.api.types.is_numeric_dtype(df0.loc[:,item])):
            print(item+' has string, which is not compared '+'df0.loc[0,item]=', df0.loc[0,item])
            continue
        if(linear_img(savefoder,df0,df1,dfsc,corrname,item, dict1)==0 or dot_img(savefoder,df0,df1,dfsc,corrname,item, 0, dict1)==0):
            continue

        img_x = 320
        if (flag):
            img_y = 60 + img_h
            flag = 0
        else:
            img_y = 60
            flag = 1


        pdf.drawImage(savefoder + '/' + item.replace('/', '') + '0.png', img_x, img_y, img_w, img_h)
        text_width = pdf.stringWidth(item, dict1["font"], dict1["font_size"])
        pdf.drawString(320 + (img_w - text_width) / 2, img_h + img_y - 25 + dict1["font_high"], item)

        img_x = 320 + img_w
        pdf.drawImage(savefoder + '/' + item.replace('/', '') + '1.png', img_x, img_y, img_w, img_h)
        text_width = pdf.stringWidth(item, dict1["font"], dict1["font_size"])
        pdf.drawString(320 + img_w + (img_w - text_width) / 2, img_h + img_y - 25 + dict1["font_high"], item)

        if (flag == 1):
            pdf.showPage()
            pdf.setFont(dict1["font"], dict1["font_size"])
        total = total + 1

    return total

#生成一种类型的图(箱型图单排)
def generate_pdf3(pdf, savefoder, dfdata, dfsc, dict1, mode):
    img_w, img_h = dict1["box_img_w"], 480
    pdf_size = (1920, 1080)
    pdf.setPageSize(pdf_size)
    flag = 0

    total = 0

    corrname = dfdata[dict1["corr"]].unique().tolist()
    df0 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[0]]
    df1 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[1]]

    if (dict1["depend_spec"] == "on"):
        combined_set = list(set(dict1["uncorrs"]) | (set(dfsc.index.tolist()) & set(df0.columns.tolist())))
        # 使用列表推导式保持原始顺序
        filtered_columns = [col for col in df0.columns if col in combined_set]

        df0 = df0.loc[:, filtered_columns]  # 通过 loc 方法过滤列
        df1 = df0.loc[:, filtered_columns]

    n = df0.columns.size

    pdf.setFont(dict1["font"], dict1["font_size"])
    for i in trange(n, desc=dict1["sheetname"] + ' Progress'):
        item=df0.columns[i]

        # 如果当前列是xy类型名或者是关联列则跳过
        if(item in dict1["uncorrs"]):
            continue

        # 如果当前列含有字符串则跳过
        if(not pd.api.types.is_numeric_dtype(df0.loc[:,item])):
            print(item+' has string, which is not compared '+'df0.loc[0,item]=', df0.loc[0,item])
            continue
        if (box_img(savefoder, dfdata, dfsc, item, 1, dict1) == 0):
            continue

        img_x = dict1["box_img_x"]
        if (flag == 1):
            img_y = 60 + img_h
            flag = 0
        else:
            img_y = 60
            flag = 1

        pdf.drawImage(savefoder + '/' + item.replace('/', '') + '1.png', img_x, img_y, img_w, img_h)
        text_width = pdf.stringWidth(item, dict1["font"], dict1["font_size"])
        pdf.drawString(img_x + (img_w - text_width) / 2, img_h + img_y - 25 + dict1["font_high"], item)

        if (flag == 1):
            pdf.showPage()
            pdf.setFont(dict1["font"], dict1["font_size"])

        total = total + 1

    return total

#生成一种类型的图(箱型图双排)
def generate_pdf4(pdf, savefoder, dfdata, dfsc, dict1, mode):
    img_w, img_h = dict1["box_img_w"], 480
    pdf_size = (1920, 1080)
    pdf.setPageSize(pdf_size)
    flag = 0
    items = []
    total = 0

    corrname = dfdata[dict1["corr"]].unique().tolist()
    df0 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[0]]
    df1 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[1]]

    if (dict1["depend_spec"] == "on"):
        combined_set = list(set(dict1["uncorrs"]) | (set(dfsc.index.tolist()) & set(df0.columns.tolist())))
        # 使用列表推导式保持原始顺序
        filtered_columns = [col for col in df0.columns if col in combined_set]

        df0 = df0.loc[:, filtered_columns]  # 通过 loc 方法过滤列
        df1 = df0.loc[:, filtered_columns]

    n = df0.columns.size

    pdf.setFont(dict1["font"], dict1["font_size"])
    for i in trange(n, desc=dict1["sheetname"] + ' Progress'):
        item=df0.columns[i]

        # 如果当前列是xy类型名或者是关联列则跳过
        if(item in dict1["uncorrs"]):
            continue

        # 如果当前列含有字符串则跳过
        if(not pd.api.types.is_numeric_dtype(df0.loc[:,item])):
            print(item+' has string, which is not compared '+'df0.loc[0,item]=', df0.loc[0,item])
            continue
        if(mode == "1"):
            if (dot_img(savefoder, df0, df1, dfsc, corrname, item, 1, dict1) == 0):
                continue
        elif(mode == "2"):
            if (linear_img(savefoder, df0, df1, dfsc, corrname, item, dict1) == 0):
                continue
        elif(mode == "3"):
            if (box_img(savefoder, dfdata, dfsc, item, 1, dict1) == 0):
                continue
        else:
            print("type error")
            break

        items.append(item)

        if(len(items) == 2):
            img_x = dict1["box_img_x"]
            if(flag == 1):
                img_y = 60 + img_h
                flag = 0
            else:
                img_y = 60
                flag = 1

            pdf.drawImage(savefoder+'/'+items[0].replace('/','')+'1.png',img_x,img_y,img_w,img_h)
            text_width = pdf.stringWidth(items[0], dict1["font"], dict1["font_size"])
            pdf.drawString(img_x + (img_w - text_width)/2, img_h + img_y - 25 + dict1["font_high"], items[0])
            pdf.drawImage(savefoder+'/'+items[1].replace('/','')+'1.png', img_x + img_w, img_y, img_w, img_h)

            text_width = pdf.stringWidth(items[1], dict1["font"], dict1["font_size"])
            pdf.drawString(img_x + img_w + (img_w - text_width)/2, img_h + img_y -  25 + dict1["font_high"], items[1])
            items = []
            if(flag == 1):
                pdf.showPage()
                pdf.setFont(dict1["font"], dict1["font_size"])
        elif(i == df0.columns.size - 1 and len(items) == 1 ):
            img_x = dict1["box_img_x"]
            if(flag == 1):
                img_y = 60 + img_h
            else:
                img_y = 60

            pdf.drawImage(savefoder + '/' + items[0].replace('/', '') + '1.png', img_x, img_y, img_w, img_h)
            text_width = pdf.stringWidth(items[0], dict1["font"], dict1["font_size"])
            pdf.drawString(img_x + (img_w - text_width) / 2, img_h + img_y - 25 + dict1["font_high"], items[0])

        total = total + 1

    return total

#生成柱形图和线性拟合图
def generate_pdf5(pdf, savefoder, dfdata, dfsc, dict1):
    img_w, img_h = 640, 480
    pdf_size = (1920, 1080)
    pdf.setPageSize(pdf_size)
    flag = 1
    total = 0

    corrname = dfdata[dict1["corr"]].unique().tolist()
    df0 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[0]]
    df1 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[1]]

    if (dict1["depend_spec"] == "on"):
        combined_set = list(set(dict1["uncorrs"]) | (set(dfsc.index.tolist()) & set(df0.columns.tolist())))
        # 使用列表推导式保持原始顺序
        filtered_columns = [col for col in df0.columns if col in combined_set]

        df0 = df0.loc[:, filtered_columns]  # 通过 loc 方法过滤列
        df1 = df0.loc[:, filtered_columns]

    n = df0.columns.size

    pdf.setFont(dict1["font"], dict1["font_size"])
    for i in trange(n, desc=dict1["sheetname"] + ' Progress'):
        item=df0.columns[i]

        if(item in dict1["uncorrs"]):
            continue
        if(not pd.api.types.is_numeric_dtype(df0.loc[:,item])):
            print(item+' has string, which is not compared '+'df0.loc[0,item]=', df0.loc[0,item])
            continue
        if(linear_img(savefoder,df0,df1,dfsc,corrname,item, dict1)==0 or hist_img(savefoder,df0,df1,dfsc,corrname,item, 0, dict1)==0):
            continue

        img_x = 320
        if (flag):
            img_y = 60 + img_h
            flag = 0
        else:
            img_y = 60
            flag = 1


        pdf.drawImage(savefoder + '/' + item.replace('/', '') + '0.png', img_x, img_y, img_w, img_h)
        text_width = pdf.stringWidth(item, dict1["font"], dict1["font_size"])
        pdf.drawString(320 + (img_w - text_width) / 2, img_h + img_y - 25 + dict1["font_high"], item)

        img_x = 320 + img_w
        pdf.drawImage(savefoder + '/' + item.replace('/', '') + '1.png', img_x, img_y, img_w, img_h)
        text_width = pdf.stringWidth(item, dict1["font"], dict1["font_size"])
        pdf.drawString(320 + img_w + (img_w - text_width) / 2, img_h + img_y - 25 + dict1["font_high"], item)

        if (flag == 1):
            pdf.showPage()
            pdf.setFont(dict1["font"], dict1["font_size"])
        total = total + 1

    return total

#生成柱形图和线性拟合图
def generate_pdf5_1(pdf, savefoder, dfdata, dfsc, dict1):
    img_w, img_h = 640, 480
    pdf_size = (1920, 1080)
    pdf.setPageSize(pdf_size)
    flag = 1
    total = 0

    corrname = dfdata[dict1["corr"]].unique().tolist()
    df0 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[0]]
    df1 = dfdata[dfdata.loc[:, dict1["corr"]] == corrname[1]]

    if (dict1["depend_spec"] == "on"):
        combined_set = list(set(dict1["uncorrs"]) | (set(dfsc.index.tolist()) & set(df0.columns.tolist())))
        # 使用列表推导式保持原始顺序
        filtered_columns = [col for col in df0.columns if col in combined_set]

        df0 = df0.loc[:, filtered_columns]  # 通过 loc 方法过滤列
        df1 = df0.loc[:, filtered_columns]

    n = df0.columns.size

    pdf.setFont(dict1["font"], dict1["font_size"])
    for i in trange(n, desc=dict1["sheetname"] + ' Progress'):
        item=df0.columns[i]

        if(item in dict1["uncorrs"]):
            continue
        if(not pd.api.types.is_numeric_dtype(df0.loc[:,item])):
            print(item+' has string, which is not compared '+'df0.loc[0,item]=', df0.loc[0,item])
            continue
        if(linear_img(savefoder,df0,df1,dfsc,corrname,item, dict1)==0 or hist_img1(savefoder,df0,df1,dfsc,corrname,item, 0, dict1)==0):
            continue

        img_x = 320
        if (flag):
            img_y = 80 + img_h
            flag = 0
        else:
            img_y = 60
            flag = 1

        pdf.drawImage(savefoder + '/' + item.replace('/', '') + '0.png', img_x, img_y, img_w, img_h)

        img_x = 320 + img_w
        pdf.drawImage(savefoder + '/' + item.replace('/', '') + '1.png', img_x, img_y, img_w, img_h)

        text_width = pdf.stringWidth(item, dict1["font"], dict1["font_size"])
        pdf.drawString(320 + (img_w*2 - text_width) / 2, img_h + img_y - 25 + dict1["font_high"], item)

        pdf.setFont(dict1["font"], dict1["type4_xlabel_size"])
        # 计算整个字符串的宽度
        text_width_title = pdf.stringWidth(dict1["title_text"], dict1["font"], dict1["type4_xlabel_size"])
        text_width_xlabel = pdf.stringWidth(dict1["xlabel_text"], dict1["font"], dict1["type4_xlabel_size"])

        # 计算到“:”号的宽度
        colon_index_title = dict1["title_text"].find(":")
        colon_index_xlabel = dict1["xlabel_text"].find(":")

        text_width_to_colon_title = pdf.stringWidth(dict1["title_text"][:colon_index_title], dict1["font"],
                                                    dict1["type4_xlabel_size"])
        text_width_to_colon_xlabel = pdf.stringWidth(dict1["xlabel_text"][:colon_index_xlabel], dict1["font"],
                                                     dict1["type4_xlabel_size"])

        # 比较宽度并调整位置
        if text_width_to_colon_title > text_width_to_colon_xlabel:
            # 调整 xlabel_text 的位置
            adjustment = (text_width_to_colon_title - text_width_to_colon_xlabel) / 2
            pdf.drawString(320 + (img_w - text_width_title) / 2, img_y + dict1["type4_xlabel1_position"], dict1["title_text"])
            pdf.drawString(320 + (img_w - text_width_xlabel) / 2 + adjustment, img_y + dict1["type4_xlabel2_position"], dict1["xlabel_text"])
        else:
            # 调整 title_text 的位置
            adjustment = (text_width_to_colon_xlabel - text_width_to_colon_title) / 2
            pdf.drawString(320 + (img_w - text_width_title) / 2 + adjustment, img_y + dict1["type4_xlabel1_position"], dict1["title_text"])
            pdf.drawString(320 + (img_w - text_width_xlabel) / 2, img_y + dict1["type4_xlabel2_position"], dict1["xlabel_text"])

        pdf.setFont(dict1["font"], dict1["font_size"])
        if (flag == 1):
            pdf.showPage()
            pdf.setFont(dict1["font"], dict1["font_size"])
        total = total + 1

    return total