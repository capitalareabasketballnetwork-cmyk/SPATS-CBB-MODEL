# Data acquisition for available 2003–2026 men's D-I box scores
# Requires R and hoopR: install.packages("hoopR")
# This downloads RAW player-game box scores, NOT validated player-season totals.
# Run: Rscript scripts/download_hoopr.R 2003 2026
args <- commandArgs(trailingOnly = TRUE)
first <- if (length(args) >= 1) as.integer(args[[1]]) else 2003L
last <- if (length(args) >= 2) as.integer(args[[2]]) else 2026L
stopifnot(first >= 2003, last <= 2026, first <= last)
if (!requireNamespace("hoopR", quietly=TRUE)) stop("Install hoopR first")
dir.create("data/raw/hoopr", recursive=TRUE, showWarnings=FALSE)
rows <- list()
for (year in seq.int(first,last)) {
  path <- sprintf("data/raw/hoopr/player_box_%d.rds",year)
  if (file.exists(path)) {
    rows[[length(rows)+1]] <- data.frame(season=year,status="exists",rows=NA_integer_)
    next
  }
  message("Downloading season ",year)
  tryCatch({
    data <- hoopR::load_mbb_player_box(seasons=year)
    if (nrow(data)==0) stop("No rows")
    saveRDS(data,path)
    rows[[length(rows)+1]] <- data.frame(season=year,status="downloaded",rows=nrow(data))
  },error=function(e) {
    rows[[length(rows)+1]] <<- data.frame(season=year,status=paste0("error: ",conditionMessage(e)),rows=NA_integer_)
  })
}
manifest <- do.call(rbind,rows)
write.csv(manifest,"data/raw/hoopr/download_manifest.csv",row.names=FALSE)
print(manifest)
if (any(grepl("^error",manifest$status))) quit(status=1)
