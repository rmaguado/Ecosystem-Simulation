l<-read.delim("log_out-2020.08.07-14.15.02.tsv")

summary(l)
Table(l$random) # 1%
Table(l$q_val==0) # 26%

Table(l$action)

rep<-l[l$action=="repro",] # 440
Table(rep$reward) # 15%
