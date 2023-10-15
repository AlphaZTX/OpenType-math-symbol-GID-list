import os, re

CURR_ABS_PATH = os.path.dirname(__file__)
UM_TABLE_NAME = os.path.join(CURR_ABS_PATH, "unicode-math-table.tex")
OUTPUT_NANE_0 = os.path.join(CURR_ABS_PATH, "glyphset.log")
OUTPUT_NANE_1 = os.path.join(CURR_ABS_PATH, "glyphset_math.log")

LINE_PATTERN = re.compile(r"\\UnicodeMathSymbol{\"(.+)}{\\([^\s]+)\s*}{\\(.+)}{.*}")

if __name__ == '__main__':
    with open(OUTPUT_NANE_0, 'w', encoding='utf-8') as output_glyphset:
        with open(OUTPUT_NANE_1, 'w', encoding='utf-8') as output_glyphset_gsub:
            with open(UM_TABLE_NAME, 'r', encoding='utf-8') as unicode_math_table:
                # last_gid: 后面会用到
                last_gid = None
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
                        if gid != last_gid:
                            output_glyphset.write(gid + " ")
                            last_gid = gid
                        # 用来支持数学排版的 glyphset，用于 GSUB 或 MATH 表
                        match math_class_str:
                            case "mathord":
                                output_glyphset_gsub.write(gid + ".s " + gid + ".ss ")
                            case "mathalpha":
                                output_glyphset_gsub.write(gid + ".s " + gid + ".ss ")
                            case "mathbin":
                                pass
                            case "mathrel":
                                # \propto，字符形来源于 \infty，也要加上 ssty 特性
                                if gid == "uni221D":
                                    output_glyphset_gsub.write(gid + ".s " + gid + ".ss ")
                                # 一些箭头类型的关系符可以延长，.lt, .rt, .tp, .bt 和 .ex 组件建议手动添加
                            case "mathpunct":
                                output_glyphset_gsub.write(gid + ".s " + gid + ".ss ")
                            case "mathop":
                                output_glyphset_gsub.write(gid + ".dsp ")
                                # 一些积分号可以使用更长的形式，这部分可以通过 delimiter 调用，建议手动添加
                            case "mathopen":
                                match gid:
                                    # 根号只预备 4 种更高的形式
                                    case "uni221A":
                                        for i in range(1, 5):
                                            output_glyphset_gsub.write(gid + ".v%d " % i)
                                    case "uni221B":
                                        for i in range(1, 5):
                                            output_glyphset_gsub.write(gid + ".v%d " % i)
                                    case "uni221C":
                                        for i in range(1, 5):
                                            output_glyphset_gsub.write(gid + ".v%d " % i)
                                    # 两种 corner 不需要做更高的形式
                                    case "uni231C":
                                        pass
                                    case "uni321E":
                                        pass
                                    # 其余的都视为括号类型，做 7 种更高的形式
                                    case _:
                                        for i in range(1, 8):
                                            output_glyphset_gsub.write(gid + ".v%d " % i)
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
                                            output_glyphset_gsub.write(gid + ".v%d " % i)
                            case "mathfence":
                                for i in range(1, 8):
                                    output_glyphset_gsub.write(gid + ".v%d " % i)
                            case "mathover":
                                for i in range(1, 8):
                                    output_glyphset_gsub.write(gid + ".h%d " % i)
                            case "mathunder":
                                for i in range(1, 8):
                                    output_glyphset_gsub.write(gid + ".h%d " % i)
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
