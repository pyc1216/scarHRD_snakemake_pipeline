from pathlib import Path
import os
import time

sequenza  = snakemake.config['sequenza-utils']
pigz = snakemake.config['pigz']
parallel = snakemake.config['parallel']
gc = snakemake.config["gc50Base"]
genome = snakemake.config["genome"]
tumor = snakemake.input[0]
normal = snakemake.input[1]
Chr = snakemake.params[0]
prefix = snakemake.params[1]
log = snakemake.log
temfile = snakemake.params[1]
output = snakemake.output
pwd = Path.cwd()

def bam2seqz():
    (pwd/"bam2seqz").mkdir(exist_ok=True)
    if not Path("bam2seqz/sample.seqz.successfully").exists():
        shell = f"{sequenza} bam2seqz -gc {gc} --fasta {genome} -t {tumor} -n {normal} -C {Chr} --parallel 25 -o {prefix} 2>{log}"
        print(shell)
        shell = os.system(shell)
        if shell == 0:
            os.system("touch bam2seqz/sample.seqz.successfully")

def seqz_binning():
    if not Path("seqz_binning/seqz_binning.successfully").exists():
        shell = f"find {temfile}_chr*|{parallel} -j 24 '{sequenza} seqz_binning -w 50 -s {{}} -o seqz_binning/{{/}}_seqz_binning 2>logs/{{/}}_seqz_binning.logs'"
        print(shell)
        shell = os.system(shell)
        #print(shell)
        if shell == 0:
            os.system("touch seqz_binning/seqz_binning.successfully")

def remove_duplicate_headers():
    shell_head1 = f"head -1 `find seqz_binning/*chr*|head -1` >{output}"
    print(shell_head1)
    head = os.system(shell_head1)
    shell_combine = f"find seqz_binning/*chr*|sort -V|{parallel} -j 1 'cat {{}}|sed '1d' >>{output}'"
    print(shell_combine)
    os.system(shell_combine)
    
def pigz():
    shell_bam2seqz = f"find bam2seqz/*chr*|{parallel} -j 8 '{pigz} {{}}'&"    
    print(shell_bam2seqz)
    os.system(shell_bam2seqz)
    shell_seqzbin = f"find seqz_binning/*chr*|{parallel} -j 8 '{pigz} {{}}'&"
    print(shell_seqzbin)
    os.system(shell_seqzbin)

bam2seqz()
seqz_binning()
remove_duplicate_headers()
pigz()
