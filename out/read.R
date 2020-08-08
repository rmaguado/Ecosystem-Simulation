#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

l<-as.data.frame(data.table::fread(args[1], na.strings = ".", fill=T))

options(width=150)

cat("\nAll\n\n")

summary(l)
Table(l$repro == 0)
Table(l$creatures)
Table(l$action)
Table(l$action, l$reward)


cat("\nLast 25%\n\n")
l<-l[ round(NROW(l)*.75):NROW(l),]

summary(l)
Table(l$repro == 0)
Table(l$creatures)
Table(l$action)
Table(l$action, l$reward)

cat("\nLast 25% no random\n\n")
l<-l[ l$repro!=0,]

summary(l)
Table(l$creatures)
Table(l$action)
Table(l$action, l$reward)

