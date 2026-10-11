suppressPackageStartupMessages(library(hoopR))
args <- commandArgs(trailingOnly=TRUE)
first <- if(length(args)>0) as.integer(args[1]) else 2003L
last <- if(length(args)>1) as.integer(args[2]) else 2026L
stopifnot(first>=2003,first<=last,last<=2026)
root <- "data/processed/player_percentiles"
dir.create(root,recursive=TRUE,showWarnings=FALSE)
num <- function(v) suppressWarnings(as.numeric(v))
weights <- c(ppg=.25,apg=.15,ts_pct=.15,orb_pg=.08,drb_pg=.07,spg=.10,bpg=.05,to_pg=.10,mpg=.05)
manifest <- list()
for(yr in seq.int(first,last)) {
 message("Processing season ",yr)
 outfile <- file.path(root,sprintf("player_percentiles_%d.csv",yr))
 tryCatch({
  d <- as.data.frame(hoopR::load_mbb_player_box(seasons=yr))
  required <- c("game_id","athlete_id","athlete_display_name","team_id","team_display_name","minutes","points","assists","offensive_rebounds","defensive_rebounds","steals","blocks","turnovers","field_goals_attempted","free_throws_attempted")
  if(length(setdiff(required,names(d)))) stop("Missing fields: ",paste(setdiff(required,names(d)),collapse=","))
  raw_rows <- nrow(d)
  d <- d[!is.na(d$game_id)&!is.na(d$athlete_id)&!is.na(d$team_id),]
  d <- d[!duplicated(d[c("game_id","athlete_id","team_id")]),]
  d <- d[!is.na(d$minutes)&!is.na(d$points),]
  statmap <- c(minutes="minutes",pts="points",ast="assists",orb="offensive_rebounds",drb="defensive_rebounds",stl="steals",blk="blocks",tov="turnovers",fga="field_goals_attempted",fta="free_throws_attempted")
  for(k in names(statmap)) d[[k]] <- num(d[[statmap[[k]]]])
  d <- d[is.finite(d$minutes)&is.finite(d$pts)&d$minutes>=0,]
  key <- interaction(d$team_id,d$athlete_id,drop=TRUE)
  idx <- split(seq_len(nrow(d)),key)
  out <- do.call(rbind,lapply(idx,function(ii){
   x <- d[ii,,drop=FALSE]
   totals <- vapply(names(statmap),function(k) sum(x[[k]],na.rm=TRUE),numeric(1))
   c(team_id=as.character(x$team_id[1]),player_id=as.character(x$athlete_id[1]),player_name=as.character(tail(x$athlete_display_name[!is.na(x$athlete_display_name)],1)),team_name=as.character(tail(x$team_display_name[!is.na(x$team_display_name)],1)),games=as.character(length(unique(x$game_id))),as.character(totals))
  }))
  out <- as.data.frame(out,stringsAsFactors=FALSE)
  names(out) <- c("team_id","player_id","player_name","team_name","games",names(statmap))
  for(k in c("games",names(statmap))) out[[k]] <- num(out[[k]])
  g <- pmax(out$games,1)
  out$ppg <- out$pts/g;out$apg <- out$ast/g
  out$orb_pg <- out$orb/g;out$drb_pg <- out$drb/g
  out$spg <- out$stl/g;out$bpg <- out$blk/g
  out$to_pg <- out$tov/g;out$mpg <- out$minutes/g
  den <- 2*(out$fga+.44*out$fta)
  out$ts_pct <- ifelse(den>0,100*out$pts/den,NA_real_)
  for(k in names(weights)) {
   ref <- sort(out[[k]][out$games>=5 & is.finite(out[[k]])])
   if(length(ref)<2) {out[[paste0(k,"_pctile")]] <- NA_real_;next}
   v <- out[[k]]
   less <- findInterval(v,ref,left.open=TRUE)
   leq <- findInterval(v,ref)
   pct <- 100*(less+.5*(leq-less))/length(ref)
   pct[!is.finite(v)] <- NA_real_
   if(k=="to_pg") pct <- 100-pct
   out[[paste0(k,"_pctile")]] <- pct
  }
  pctcols <- paste0(names(weights),"_pctile")
  out$spats_rating <- as.vector(as.matrix(out[pctcols]) %*% weights)
  out$spats_rating[!complete.cases(out[pctcols])] <- NA_real_
  out$value_units <- out$spats_rating*out$mpg*out$games
  totals <- ave(out$value_units,out$team_id,FUN=function(v)sum(v,na.rm=TRUE))
  out$team_value_pct <- ifelse(totals>0,100*out$value_units/totals,NA_real_)
  out$season <- yr
  out <- out[c("season","team_id","team_name","player_id","player_name","games",names(statmap),names(weights),pctcols,"spats_rating","value_units","team_value_pct")]
  out <- out[order(out$team_name,-out$team_value_pct,out$player_name),]
  write.csv(out,outfile,row.names=FALSE,na="")
  manifest[[length(manifest)+1]] <- data.frame(season=yr,status=if(raw_rows<1000)"INCOMPLETE_EARLY_COVERAGE" else "processed",raw_rows=raw_rows,player_seasons=nrow(out),teams=length(unique(out$team_id)),missing_ratings=sum(is.na(out$spats_rating)),file=outfile)
  message("Saved ",outfile,": ",nrow(out)," player-teams; ",length(unique(out$team_id))," teams")
 },error=function(e){
  message("FAILED ",yr,": ",conditionMessage(e))
  manifest[[length(manifest)+1]] <<- data.frame(season=yr,status=paste0("ERROR: ",conditionMessage(e)),raw_rows=NA_integer_,player_seasons=NA_integer_,teams=NA_integer_,missing_ratings=NA_integer_,file=outfile)
 })
}
m <- do.call(rbind,manifest)
write.csv(m,file.path(root,"manifest.csv"),row.names=FALSE,na="")
print(m)
if(any(grepl("^ERROR",m$status))) quit(status=1)
