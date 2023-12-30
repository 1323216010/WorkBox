def replace_iguana(input_string):
    # 替换所有出现的IGUANA为Iguana
    return input_string.replace("IGUANA", "Iguana")

# 测试函数
example_string = "This is an IGUANA, and here is another IGUANA!"
result = replace_iguana(example_string)
print(result)
