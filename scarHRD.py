from pathlib import Path
import os

Rscript = snakemake.config["Rscript"]
input_file = snakemake.input
out_dir = Path(f"{snakemake.output}").parent
#chromosome = ",".join([f"'chr{i}'" for i in range(1,23)] + ["'chrX'","'chrY'","'chrM'"])
chromosome = ",".join([f"'{i}'" for i in snakemake.params[0]])
print(chromosome)
with open("sampleHRD/scarHRD.R","w") as out:
    out.write("library('sequenza')\n")
    out.write("library('scarHRD')\n")
    out.write(f"test <- sequenza.extract('{input_file}',assembly='hg19',chromosome.list=c({chromosome}))\n")
    out.write("names(test)\n")
    out.write("chromosome.view(mut.tab = test$mutations[[1]],baf.windows = test$BAF[[1]],ratio.windows = test$ratio[[1]],min.N.ratio = 1,segments =test$segments[[1]], main = test$chromosomes[1])\n")
    out.write("CP.example <- sequenza.fit(test)\n")
    out.write(f"sequenza.results(sequenza.extract = test, cp.table = CP.example, sample.id='sample',out.dir='{out_dir}')\n")
    out.write(f"scar_score('{input_file}',reference = 'grch37',seqz=TRUE,outputdir='{out_dir}')\n")

print(f"{Rscript} sampleHRD/scarHRD.R 2>{snakemake.log}")
shell = os.system(f"export RHOME=/home/whsong/R-3.5.1;{Rscript} sampleHRD/scarHRD.R 2>{snakemake.log}")
if shell == 0:
    os.system("touch sampleHRD/sampleHRD.successfully")
#os.system("touch sampleHRD/sampleHRD.successfully")