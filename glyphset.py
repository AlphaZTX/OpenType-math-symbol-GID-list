import os, re

OUTPUT_SEP = "\n"

CURR_ABS_PATH = os.path.dirname(__file__)
UM_TABLE_NAME = os.path.join(CURR_ABS_PATH, "unicode-math-table.tex")
OUTPUT_NANE_0 = os.path.join(CURR_ABS_PATH, "glyphset_base.log")
OUTPUT_NANE_1 = os.path.join(CURR_ABS_PATH, "glyphset_GSUB.log")
OUTPUT_NANE_2 = os.path.join(CURR_ABS_PATH, "glyphset_MATH.log")

LINE_PATTERN = re.compile(r"\\UnicodeMathSymbol{\"(.+)}{\\([^\s]+)\s*}{\\(.+)}{.*}")

if __name__ == '__main__':
    with open(OUTPUT_NANE_0, 'w', encoding='utf-8') as output_glyphset:
        # unicode-math-table 缺少 ASCII 中的字母和数字
        for i in range(0x20, 0x7f):
            output_glyphset.write("uni00%s" % hex(i)[2:].upper() + OUTPUT_SEP)
        with open(OUTPUT_NANE_1, 'w', encoding='utf-8') as output_glyphset_gsub:
            with open(OUTPUT_NANE_2, 'w', encoding='utf-8') as output_glyphset_math:
                with open(UM_TABLE_NAME, 'r', encoding='utf-8') as unicode_math_table:
                    # last_gid: 后面会用到
                    last_gid = None
                    # unicode-math-table 缺少 ASCII 中的字母和数字
                    output_glyphset_write_bool = False
                    output_glyphset_gsub_add_bool = True
                    while True:
                        line = unicode_math_table.readline()
                        if not line:
                            break
                        match_object = re.match(LINE_PATTERN, line)
                        if match_object:
                            # tex_cs: csname of math symbol, NOT important in this script
                            # gid: Glyph ID
                            # math_class_str: csname of math class
                            gid = match_object.group(1)
                            if gid[0] == "0":
                                gid = "uni" + gid[1:]
                            else:
                                gid = "u" + gid
                            tex_cs = match_object.group(2)
                            math_class_str = match_object.group(3)
                            # 基本的 glyphset，每个 glyph 都是有对应 Unicode 码位的
                            # 注意 unicode-math-table 里面有重复的编码，它们指向的 math class 不同
                            if output_glyphset_write_bool:
                                if gid != last_gid:
                                    output_glyphset.write(gid + OUTPUT_SEP)
                                    last_gid = gid
                            else:
                                if gid[5] == 'A':
                                    output_glyphset_write_bool = True
                                    if gid != last_gid:
                                        output_glyphset.write(gid + OUTPUT_SEP)
                                        last_gid = gid
                            if output_glyphset_gsub_add_bool:
                                if gid == 'uni003A':
                                    for i in range(0x30, 0x3a):
                                        curr_gid = "uni00%s" % hex(i)[2:].upper()
                                        output_glyphset_gsub.write("%s=%s.st%s%s=%s.sts%s" % (curr_gid, curr_gid, OUTPUT_SEP, curr_gid, curr_gid, OUTPUT_SEP))
                                elif gid == 'uni005B':
                                    for i in range(0x41, 0x5b):
                                        curr_gid = "uni00%s" % hex(i)[2:].upper()
                                        output_glyphset_gsub.write("%s=%s.st%s%s=%s.sts%s" % (curr_gid, curr_gid, OUTPUT_SEP, curr_gid, curr_gid, OUTPUT_SEP))
                                elif gid == 'uni007B':
                                    output_glyphset_gsub_add_bool = False
                                    for i in range(0x61, 0x7b):
                                        curr_gid = "uni00%s" % hex(i)[2:].upper()
                                        output_glyphset_gsub.write("%s=%s.st%s%s=%s.sts%s" % (curr_gid, curr_gid, OUTPUT_SEP, curr_gid, curr_gid, OUTPUT_SEP))
                            # 用来支持数学排版的 glyphset，用于 GSUB 或 MATH 表
                            write_gsub = output_glyphset_gsub.write("%s=%s.st%s%s=%s.sts%s" % (gid, gid, OUTPUT_SEP, gid, gid, OUTPUT_SEP))
                            match math_class_str:
                                case "mathord":
                                    write_gsub
                                case "mathalpha":
                                    write_gsub
                                case "mathbin":
                                    pass
                                case "mathrel":
                                    # \propto，字符形来源于 \infty，也要加上 ssty 特性
                                    if gid == "uni221D":
                                        write_gsub
                                    # 一些箭头类型的关系符可以延长，.lt, .rt, .tp, .bt 和 .ex 组件建议手动添加
                                case "mathpunct":
                                    write_gsub
                                case "mathop":
                                    output_glyphset_math.write("%s.dsp%s" % (gid, OUTPUT_SEP))
                                    # 一些积分号可以使用更长的形式，这部分可以通过 delimiter 调用，建议手动添加
                                case "mathopen":
                                    match gid:
                                        # 根号只预备 4 种更高的形式
                                        case "uni221A":
                                            for i in range(1, 5):
                                                output_glyphset_math.write("%s.v%d%s" % (gid, i, OUTPUT_SEP))
                                        case "uni221B":
                                            for i in range(1, 5):
                                                output_glyphset_math.write("%s.v%d%s" % (gid, i, OUTPUT_SEP))
                                        case "uni221C":
                                            for i in range(1, 5):
                                                output_glyphset_math.write("%s.v%d%s" % (gid, i, OUTPUT_SEP))
                                        # 两种 corner 不需要做更高的形式
                                        case "uni231C":
                                            pass
                                        case "uni321E":
                                            pass
                                        # 其余的都视为括号类型，做 7 种更高的形式
                                        case _:
                                            for i in range(1, 8):
                                                output_glyphset_math.write("%s.v%d%s" % (gid, i, OUTPUT_SEP))
                                case "mathclose":
                                    match gid:
                                        # 感叹号，do nothing
                                        case "uni0021":
                                            pass
                                        # 两种 corner 不需要做更高的形式
                                        case "uni231D":
                                            pass
                                        case "uni321F":
                                            pass
                                        # 其余的都视为括号类型，做 7 种更高的形式
                                        case _:
                                            for i in range(1, 8):
                                                output_glyphset_math.write("%s.v%d%s" % (gid, i, OUTPUT_SEP))
                                case "mathfence":
                                    for i in range(1, 8):
                                        output_glyphset_math.write("%s.v%d%s" % (gid, i, OUTPUT_SEP))
                                case "mathover":
                                    for i in range(1, 8):
                                        output_glyphset_math.write("%s.v%d%s" % (gid, i, OUTPUT_SEP))
                                case "mathunder":
                                    for i in range(1, 8):
                                        output_glyphset_math.write("%s.v%d%s" % (gid, i, OUTPUT_SEP))
                                case "mathaccent":
                                    pass
                                    # 不需要 ssty
                                case "mathaccentoverlay":
                                    pass
                                    # 不需要 ssty
                                case "mathbotaccent":
                                    pass
                                    # 不需要 ssty
                                case "mathaccentwide":
                                    pass
                                    # 无需制作延长的版本，拉伸 glyph 的功能由 XeTeX 完成
                                case "mathbotaccentwide":
                                    pass
                                    # 无需制作延长的版本，拉伸 glyph 的功能由 XeTeX 完成
                                case _:
                                    pass
