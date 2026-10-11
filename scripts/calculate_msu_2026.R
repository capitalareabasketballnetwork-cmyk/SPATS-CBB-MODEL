# National 2025-26 player ratings and Michigan State team shares
suppressPackageStartupMessages(library(hoopR))
d <- as.data.frame(load_mbb_player_box(seasons=2026))
names(d) <- tolower(names(d))
cat("Available columns:", paste(names(d), collapse=", "), "\n")
pick <- function(...) {
  candidates <- c(...)
  hit <- candidates[candidates %in% names(d)]
  if (!length(hit)) stop("Required column absent; tried: ",paste(candidates,collapse=", "))
  hit[[1]]
}
num <- function(x) {
  x <- as.character(x)
  time <- grepl("^[0-9]+:[0-9][0-9]$",x)
  x[time] <- vapply(strsplit(x[time],":"),function(t) as.character(as.numeric(t[1])+as.numeric(t[2])/60),character(1))
  suppressWarnings(as.numeric(x))
}
team_col <- pick("team_id","teamid")
player_col <- pick("athlete_id","player_id","athleteid")
name_col <- pick("athlete_display_name","athlete_name","player_name","athlete_short_name")
teamname_col <- pick("team_display_name","team_name","team_short_display_name")
game_col <- pick("game_id","gameid")
stat_names <- list(
  pts=c("points","pts"), ast=c("assists","ast"),
  orb=c("offensive_rebounds","offensive_rebounds_total","off_rebounds"),
  drb=c("defensive_rebounds","defensive_rebounds_total","def_rebounds"),
  stl=c("steals","stl"),blk=c("blocks","blk"),tov=c("turnovers","to"),
  fga=c("field_goals_attempted","field_goals_attempts","fga"),
  fta=c("free_throws_attempted","free_throws_attempts","fta"),
  minutes=c("minutes","minutes_played","min")
)
cols <- vapply(stat_names,function(x) do.call(pick,as.list(x)),character(1))
x <- data.frame(team_id=as.character(d[[team_col]]),player_id=as.character(d[[player_col]]),
  player=as.character(d[[name_col]]),team=as.character(d[[teamname_col]]),
  game=as.character(d[[game_col]]),stringsAsFactors=FALSE)
for (nm in names(cols)) x[[nm]] <- num(d[[cols[[nm]]]])
x <- x[!is.na(x$team_id)&!is.na(x$player_id)&!is.na(x$game),]
x <- x[!duplicated(x[c("team_id","player_id","game")]),]
# Ignore rows without box score minutes or core scoring data
x <- x[!is.na(x$minutes)&!is.na(x$pts),]
stats <- names(cols)
totals <- aggregate(x[stats],by=x[c("team_id","player_id")],FUN=function(v) sum(v,na.rm=TRUE))
games <- aggregate(x$game,by=x[c("team_id","player_id")],FUN=function(v) length(unique(v)))
names(games)[3] <- "games"
totals <- merge(totals,games,by=c("team_id","player_id"))
labels <- unique(x[c("team_id","player_id","player","team")])
labels <- labels[!duplicated(labels[c("team_id","player_id")]),]
totals <- merge(totals,labels,by=c("team_id","player_id"),all.x=TRUE)
g <- pmax(totals$games,1)
totals$ppg <- totals$pts/g; totals$apg <- totals$ast/g
totals$orb_pg <- totals$orb/g; totals$drb_pg <- totals$drb/g
totals$spg <- totals$stl/g; totals$bpg <- totals$blk/g
totals$to_pg <- totals$tov/g; totals$mpg <- totals$minutes/g
den <- 2*(totals$fga+0.44*totals$fta)
totals$ts_pct <- ifelse(den>0,100*totals$pts/den,NA_real_)
weights <- c(ppg=.25,apg=.15,ts_pct=.15,orb_pg=.08,drb_pg=.07,spg=.10,bpg=.05,to_pg=.10,mpg=.05)
# Same midrank percentile convention as src/model.py, eligibility >= 5 games.
for (s in names(weights)) {
  ref <- totals[[s]][totals$games>=5 & !is.na(totals[[s]])]
  if (length(ref)<2) stop("Insufficient national reference for ",s)
  v <- totals[[s]]
  pct <- vapply(v,function(a) if(is.na(a)) NA_real_ else
    100*(sum(ref<a)+0.5*sum(ref==a))/length(ref),numeric(1))
  if(s=="to_pg") pct <- 100-pct
  totals[[paste0(s,"_pctile")]] <- pct
}
pctcols <- paste0(names(weights),"_pctile")
totals$rating <- as.vector(as.matrix(totals[pctcols])%*%weights)
totals$rating[!complete.cases(totals[pctcols])] <- NA_real_
totals$value_units <- totals$rating*totals$mpg*totals$games
denom <- ave(totals$value_units,totals$team_id,FUN=function(v) sum(v,na.rm=TRUE))
totals$team_value_pct <- 100*totals$value_units/denom
msu <- totals[grepl("michigan state",totals$team,ignore.case=TRUE),]
msu <- msu[order(-msu$team_value_pct),]
if(!nrow(msu)) stop("Michigan State team not found; inspect team names")
dir.create("output",showWarnings=FALSE)
write.csv(msu,"output/michigan_state_2026_player_values.csv",row.names=FALSE)
cat("\nMICHIGAN STATE 2025-26 PLAYER VALUE\n")
print(msu[c("player","games","ppg","apg","ts_pct","mpg","rating","team_value_pct")],row.names=FALSE)
cat("TOTAL:",sum(msu$team_value_pct,na.rm=TRUE),"\n")
