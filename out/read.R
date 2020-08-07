l<-read.delim("log_out-2020.08.07-17.09.59.tsv", na.strings = ".")

summary(l)
Table(is.na(l$q_val)) # ~ 25%

summary(l$q_val)

Table(l$action)
Table(l$action, l$reward)

Table(l$action[!l$random], l$reward[!l$random])

Table(l$action[500000:NROW(l)], l$reward[500000:NROW(l)])

Table(l$action[1:NROW(l)>500000 & !is.na(l$q_val)], l$reward[1:NROW(l)>500000 & !is.na(l$q_val)])
