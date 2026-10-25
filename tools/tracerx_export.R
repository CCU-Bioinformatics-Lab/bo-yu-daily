# tracerx_export.R
# 把 Frankell 2023（TRACERx 421，Zenodo 7822002）的 .fst/.rds 轉成 TSV，給 tracerx_event_stats.py 讀。
# 用法：
#   Rscript --vanilla tools/tracerx_export.R <figurecode/data 目錄> <輸出目錄>
# 需要 R 套件 fst（本機裝在 ~/Rlib）與 data.table。
.libPaths(c(path.expand("~/Rlib"), .libPaths()))
suppressMessages({library(fst); library(data.table)})

args <- commandArgs(TRUE)
D <- args[1]; O <- args[2]
dir.create(O, showWarnings = FALSE, recursive = TRUE)

# 1. SCNA（每區域、各 tumour 共用 segmentation、已跨區域 phasing 的 nAraw/nBraw）
s <- as.data.table(read_fst(file.path(D, "20221109_TRACERx421_scna_table.fst")))
fwrite(s, file.path(O, "scna_region.tsv"), sep = "\t")

# 2. 每 tumour 的 evolutionary metrics 直接複製（已是 TSV，不需轉）

# 3. 樹：edge、cluster CCF（每區域）、trunk、被移除的 cluster
tr <- readRDS(file.path(D, "20221109_TRACERx421_phylogenetic_trees.rds"))
edges <- list(); ccf <- list(); meta <- list(); muts <- list()
for (tid in names(tr)) {
  x <- tr[[tid]]
  g <- x$graph_pyclone
  if (is.null(g$Corrected_tree)) next
  e <- g$Corrected_tree
  edges[[tid]] <- data.table(tumour_id = tid, parent = e[, 1], child = e[, 2])
  cc <- x$nested_pyclone$ccf_cluster_table
  if (!is.null(cc)) {
    m <- as.data.table(cc, keep.rownames = "cluster")
    ccf[[tid]] <- melt(m, id.vars = "cluster", variable.name = "region", value.name = "ccf_pct")[, tumour_id := tid]
  }
  meta[[tid]] <- data.table(tumour_id = tid, trunk = paste(g$trunk, collapse = ","),
    n_alt_trees = length(g$alt_trees),
    cpn_removed = paste(x$cpn_removed_clusters, collapse = ","),
    tree_removed = paste(x$tree_removed_clusters, collapse = ","),
    merged = paste(x$merged_clusters, collapse = ","))
  # mutation 層級（每區域）：cov、var_count、PhyloCCF、nAraw、nBraw、cluster
  t <- as.data.table(x$ccf_table_pyclone_clean, keep.rownames = "mutation_id")
  if (nrow(t) > 0) {
    regs <- unique(sub("_cov$", "", grep("_cov$", names(t), value = TRUE)))
    for (r in regs) {
      muts[[paste(tid, r)]] <- data.table(tumour_id = tid, region = r, mutation_id = t$mutation_id,
        cluster = t$PycloneCluster, cov = t[[paste0(r, "_cov")]], var_count = t[[paste0(r, "_var_count")]],
        phylo_ccf = t[[paste0(r, "_PhyloCCF")]], cpn_copies = t[[paste0(r, "_cpn.copies")]],
        mut_cpn = t[[paste0(r, "_mut.cpn.num")]], nAraw = t[[paste0(r, "_nAraw")]], nBraw = t[[paste0(r, "_nBraw")]])
    }
  }
}
fwrite(rbindlist(edges), file.path(O, "tree_edges.tsv"), sep = "\t")
fwrite(rbindlist(ccf), file.path(O, "cluster_ccf_region.tsv"), sep = "\t")
fwrite(rbindlist(meta), file.path(O, "tree_meta.tsv"), sep = "\t")
fwrite(rbindlist(muts), file.path(O, "mutation_region_tree.tsv"), sep = "\t")

# 4. mutation table（tumour 層級，含 PyClone cluster、clonal 標記、timing）
mt <- as.data.table(read_fst(file.path(D, "20221109_TRACERx421_mutation_table.fst")))
fwrite(mt[, .(mutation_id, tumour_id, chr, start, ref, var, ITHState, PyCloneClonal_SC, PyCloneCluster_SC,
             cleanCluster_SC, combTiming_SC, DriverMut)], file.path(O, "mutation_table.tsv"), sep = "\t")

# 5. tumour 臨床（只取 histology）
a <- readRDS(file.path(D, "20221109_TRACERx421_all_tumour_df.rds"))
fwrite(as.data.table(a)[, .(tumour_id = tumour_id_muttable_cruk, histology_3)], file.path(O, "tumour_histology.tsv"), sep = "\t")
cat("done\n")
