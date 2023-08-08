import os
from pathlib import Path
import shutil

class Selector:
    '''
    Pseudo-wirtual class to document how it works on MCF side.
    '''
    def add(selector):
        '''
        add player/entity by UUID, name or standard minecraft selector. Do NOT put selector in ", just type .add(@a[level=..5])
        '''
        pass
    def remove(selector):
        '''
        remowe player/entity by UUID, name or standard minecraft selector. Do NOT put selector in ", just type .remove(@a[level=..5])
        '''
        pass
    def free():
        '''
        remove all players from selector and remove it from memory
        '''
        pass

def process_file(infile_path: str,outfile_path: str):
    '''
    Read mcf file, compile it, and write it to file.

    First draft available at https://docs.google.com/document/d/1LTOjGk4AVTAzR0z8PaZW3r4xKW2ZM5OCgNI_hK8JVeU/

    > let varablename = Selector()
    create new var named varablename. Don't produce any lines to outfile

    > varablename.add(@a)
    add @a to varablename, support all Minecraft selector

    > varablename$ say example
    run "say example" as all entity forom var 'varablename'

    > varablename.remove(@e[gamemode=!creative])
    removes from varable

    > varablename.free()
    removes all entity form varable AND remove it from memory

    ''' 
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
        outfile.write(outline+'\n')

    if len(varables) > 0:
        outfile.write(f"\n# {len(varables)} left allocated after compiling file. {varables}")

    infile.close()
    outfile.close()


def normalize_line(text: str):
    """
    Removes spaces from begining and end. Cheanes multiple spaces to single space.
    """
    text = text.strip()
    while "  " in text:
        text = text.replace("  "," ")
    return text

def process_dir(input_dirname: str,outdir:str):
    '''
    Read mcf files, compile it, and write it to files.
    input_dirname - directory recursivly reads all files and directoris
    outdir - copy all files, compile files, see process_file()
    If file is NOT .mcf simply copy it to outdir
    '''
    for dir_path, _, file_list in os.walk(input_dirname):
        for file in file_list:
            file_base_name, file_ext = os.path.splitext(os.path.join(dir_path,file))
            if not os.path.exists(outdir / Path(*Path(file_base_name).parts[1:-1])):
                os.mkdir(outdir / Path(*Path(file_base_name).parts[1:-1]))
            if file_ext != '.mcf':
                shutil.copy2(file_base_name+file_ext,str(outdir / Path(*Path(file_base_name).parts[1:])) + file_ext)
                continue
            process_file(file_base_name+'.mcf',str(outdir / Path(*Path(file_base_name).parts[1:])) + '.mcfunction' )



if __name__ == "__main__":
    # process_file('input.mcf','out.mcfunction')
    process_dir('src','datapack')