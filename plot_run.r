library(tidyverse)

setwd("/home/mastermind/magnapress")
exp_data_1 <- as.tibble(read.csv(file = 'Donor-7365-39m.csv'))
exp_data_2 <- as.tibble(read.csv(file = 'Donor-7366-69m.csv'))
exp_data_3 <- as.tibble(read.csv(file = 'AM7381 76M G-2-static.csv'))


strain_p <- ggplot( ) +
  geom_point(data= exp_data_1, aes(x= time, y= strain), color = 'blue') + 
  geom_point(data= exp_data_2, aes(x= time, y= strain),color = 'red') + 
  geom_point(data= exp_data_3, aes(x= time, y= strain),color = 'green') + 
  scale_y_continuous(name = "Strain", limits = c(0, 100)) + 
  scale_colour_manual("", 
                      breaks = c("Donor-7365", "Donor-7366"),
                      values = c("blue", "red")) + 
  theme_classic() +
  theme(text = element_text(size = 20))

show(strain_p)

  