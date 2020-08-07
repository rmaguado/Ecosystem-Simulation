l<-read.delim("log_out-2020.08.07-14.34.06.tsv", na.strings = ".")

summary(l)
Table(l$random) #  ~ 1000
Table(is.na(l$q_val)) # ~ 25%

summary(l$q_val)

Table(l$action)
Table(l$action, l$reward)

