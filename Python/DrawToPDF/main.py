import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import time
from utils import read_file_with_progress
from utils import print_version
from utils import getConfig
from generate import generate_pdf1
from generate import generate_pdf2
from generate import generate_pdf3
from generate import generate_pdf4
from generate import generate_pdf5
from generate import generate_pdf5_1

dict1 = {}

def main(mode):
    my_dict = read_file_with_progress(dict1["pathspec"])
    # 获取第一个键
    first_key = next(iter(my_dict))
    # 通过第一个键获取对应的值
    dfspec = my_dict[first_key]
    # 过滤掉全为None的列
    dfspec = dfspec.dropna(axis=1, how='all')
    #以第一列元素作为索引
    dfspec = dfspec.set_index(dfspec.columns[0])

    os.makedirs('outputpdf/', exist_ok=True)

    total = 0
    dfdatasheets = read_file_with_progress(dict1["pathdata"], all_sheets=True)
    for sheetname, dfdata in dfdatasheets.items():
        # 过滤掉全为None的列
        dfdata = dfdata.dropna(axis=1, how='all')

        savefoder = 'images/' + sheetname
        os.makedirs(savefoder, exist_ok=True)

        pdf = canvas.Canvas('outputpdf/' + sheetname + "_" + mode + '.pdf')
        dict1["sheetname"] = sheetname
        if (mode == "0"):
            total += generate_pdf2(pdf=pdf, savefoder=savefoder, dfdata=dfdata, dfsc=dfspec, dict1=dict1)
        elif(mode == "3"):
            if(dict1["box_picture"] == "1"):
                total += generate_pdf3(pdf=pdf, savefoder=savefoder, dfdata=dfdata, dfsc=dfspec, dict1=dict1,
                                       mode=mode)
            else:
                total += generate_pdf4(pdf=pdf, savefoder=savefoder, dfdata=dfdata, dfsc=dfspec, dict1=dict1,
                                       mode=mode)
        elif(mode == "4"):
            if(dict1["type4_xlabel"] == 2):
                total += generate_pdf5_1(pdf=pdf, savefoder=savefoder, dfdata=dfdata, dfsc=dfspec, dict1=dict1)
            else:
                total += generate_pdf5(pdf=pdf, savefoder=savefoder, dfdata=dfdata, dfsc=dfspec, dict1=dict1)
        else:
            total += generate_pdf1(pdf=pdf, savefoder=savefoder, dfdata=dfdata, dfsc=dfspec, dict1=dict1,
                            mode=mode)
        pdf.save()
    print("total:", total, "items")

if __name__ == '__main__':
    print_version()
    while(1):
        mode = input("input: ")
        dict1 = getConfig()
        pdfmetrics.registerFont(TTFont(dict1["font"], dict1["font_path"]))

        print("=======================START============================")
        print("start generating pdf, please wait...")
        # 记录开始时间点
        start_time = time.time()
        main(mode)
        # 记录结束时间点
        end_time = time.time()

        print("cost time：", round(end_time - start_time, 1), "s")
        print("The task is complete, please click exit or continue")
        print("========================END=============================")