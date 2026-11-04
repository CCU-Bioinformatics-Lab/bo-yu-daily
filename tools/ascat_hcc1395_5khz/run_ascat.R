# ASCAT on HCC1395 ONT 5kHz tumour/normal (long read), rerun of the 2026-08 analysis.
# Settings follow the 2026-08 run (git f489437 data.md §3): hg38, min_base_qual 10, alleleCounter -f 0.
# Added for CRAM input: alleleCounter -r REF, and loci files with a "chr" prefix (the CRAMs use chr names).
#
# Usage: Rscript tools/ascat_hcc1395_5khz/run_ascat.R WORK_DIR NTHREADS
library(ASCAT)
args <- commandArgs(trailingOnly = TRUE)
work <- args[1]
nthreads <- as.integer(args[2])
ref_dir <- file.path(work, "ref")
d5 <- "/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG"
fasta <- "/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta"
counter <- "/bip8_disk/boyu114/miniforge3/envs/ascat/bin/alleleCounter"

# loci files with "chr" prefix, same SNPs as the official G1000 hg38 set
chr_loci <- file.path(ref_dir, "loci_chr")
dir.create(chr_loci, showWarnings = FALSE)
for (c in c(1:22, "X")) {
  out <- file.path(chr_loci, paste0("G1000_loci_hg38_chr", c, ".txt"))
  if (!file.exists(out)) {
    # the official chr20 file writes one position as "8e+06"; read as numeric, write as integer
    x <- read.table(file.path(ref_dir, paste0("G1000_loci_hg38_chr", c, ".txt")), colClasses = c("character", "numeric"))
    x[[1]] <- paste0("chr", x[[1]])
    x[[2]] <- sprintf("%d", as.integer(round(x[[2]])))
    write.table(x, out, sep = "\t", quote = FALSE, row.names = FALSE, col.names = FALSE)
  }
}

setwd(work)
ascat.prepareHTS(
  tumourseqfile = file.path(d5, "HCC1395.cram"),
  normalseqfile = file.path(d5, "HCC1395BL.cram"),
  tumourname = "HCC1395_5khz", normalname = "HCC1395BL_5khz",
  allelecounter_exe = counter,
  alleles.prefix = file.path(ref_dir, "G1000_alleles_hg38_chr"),
  loci.prefix = file.path(chr_loci, "G1000_loci_hg38_chr"),
  gender = "XX", genomeVersion = "hg38", nthreads = nthreads,
  tumourLogR_file = "Tumor_LogR.txt", tumourBAF_file = "Tumor_BAF.txt",
  normalLogR_file = "Germline_LogR.txt", normalBAF_file = "Germline_BAF.txt",
  min_base_qual = 10,
  additional_allelecounter_flags = paste("-f 0 -r", fasta),
  seed = 42)

ascat.bc <- ascat.loadData(Tumor_LogR_file = "Tumor_LogR.txt", Tumor_BAF_file = "Tumor_BAF.txt",
                           Germline_LogR_file = "Germline_LogR.txt", Germline_BAF_file = "Germline_BAF.txt",
                           gender = "XX", genomeVersion = "hg38")
ascat.plotRawData(ascat.bc, img.prefix = "Before_correction_")
ascat.bc <- ascat.correctLogR(ascat.bc, GCcontentfile = file.path(ref_dir, "GC_G1000_hg38.txt"),
                              replictimingfile = file.path(ref_dir, "RT_G1000_hg38.txt"))
ascat.plotRawData(ascat.bc, img.prefix = "After_correction_")
ascat.bc <- ascat.aspcf(ascat.bc, seed = 42)
ascat.plotSegmentedData(ascat.bc)
ascat.output <- ascat.runAscat(ascat.bc, gamma = 1, write_segments = TRUE)
qc <- ascat.metrics(ascat.bc, ascat.output)
write.table(qc, "QC_metrics.tsv", sep = "\t", quote = FALSE, row.names = FALSE)
write.table(data.frame(sample = names(ascat.output$purity), purity = ascat.output$purity,
                       ploidy = ascat.output$ploidy, goodnessOfFit = ascat.output$goodnessOfFit),
            "purity_ploidy.txt", sep = "\t", quote = FALSE, row.names = FALSE)
save(ascat.bc, ascat.output, qc, file = "ASCAT_objects.Rdata")
