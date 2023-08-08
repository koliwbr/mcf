
def process_file(infile_path: str,outfile_path: str):
    infile = open(infile_path,'r')
    outfile = open(outfile_path,'w')

    varables = []
    line_num = 0

    for line in infile.read().splitlines():
        line_num+=1
        line = normalize_line(line)
        outline = line

        if not line: continue
        if line.startswith("#"): continue #komętaże usuń!
        if line.startswith(";"): continue #komętaże usuń!

        if line.startswith("let ") and line.endswith("Selector()"):
            assert line.count('=') == 1
            # print(f"error in line {-1}: too many = ")

            line = line.replace('=',' = ')
            outline = line.split()
            assert len(outline) == 4
            assert outline[0] == 'let' and outline[2] == '=' and outline[3] == 'Selector()'

            if outline[1] in varables:
                raise Exception(f'line {line_num}: Varable {outline[1]} created twice!')
            varables.append(outline[1])
            continue

        for var in varables:
            if line.startswith(f'{var}.'):
                operation = line.split()[0].split('.',1)[1].split('(')[0]
                assert len(line.split()[0].split('.',1)[1].split('(',1)) == 2 #mayby space after operation? before "(" 
                line = line.removesuffix(')') # raise Exception(f'missing ) at line {line_num}')
                selector = line.split('.',1)[1].split('(',1)[1].strip()
                #TODO check if selector is valid
                match operation:
                    case 'add':
                        outline = f'tag add {selector} mcfVar_{var}'
                    case 'remove' | 'rm':
                        outline = f'tag remove {selector} mcfVar_{var}'
                    case 'free':
                        outline = f'tag remove @e mcfVar_{var}'
                        varables.remove(var)


                    case _:
                        raise Exception(f'command "{operation}" at line {line_num} not found')
            if line.startswith(f'{var}$'):
                outline = f"execute as @e[tag=mcfVar_{var}] at @s run {line.split('$',1)[1]}"
                continue

            # tag remove @e[gamemode=!creative] smplVar_ulubionyGracz
            
        outfile.write(outline+'\n')

    if len(varables) > 0:
        outfile.write(f"\n# {len(varables)} left allocated after compiling file. {varables}")

    infile.close()
    outfile.close()


def normalize_line(text):
    text = text.strip()
    while "  " in text:
        text = text.replace("  "," ")
    return text


if __name__ == "__main__":
    process_file('input.mcf','out.mcfunction')