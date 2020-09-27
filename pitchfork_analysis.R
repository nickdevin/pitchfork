library(dplyr)
library(tidyr)
library(ggplot2)

pitchfork = read.csv('pitchfork.csv', header = TRUE)

pitchfork

max_genres = max(sapply(pitchfork$genre, function(x) {
  length(strsplit(x, '\\|')[[1]])
}))
max_genres

max_labels = max(sapply(pitchfork$label, function(x) {
  length(strsplit(x, '\\|')[[1]])
}))
max_labels

genre_cols = paste(rep(c('genre'), max_genres), as.character(1:max_genres), sep = '')

label_cols = paste(rep(c('label'), max_labels), as.character(1:max_labels), sep = '')

pitchfork_sep = pitchfork %>%
  separate(., col = 'genre', sep = '\\|', into = genre_cols, fill = 'right') %>% 
  gather(., key = 'temp', value = 'genre', genre_cols) %>% 
  select(., -temp) %>%
  filter(., !is.na(genre)) %>% 
  separate(., col = 'label', sep = '\\|', into = label_cols, fill = 'right') %>% 
  gather(., key = 'temp', value = 'label', label_cols) %>% 
  select(., -temp) %>% 
  filter(., !is.na(label))

pitchfork %>%
  group_by(., genre) %>% 
  summarise(., n(), mean(score))

pitchfork_sep %>%
  group_by(., reviewer) %>% 
  summarise(., n(), mean(score))

pitchfork_sep %>% 
  group_by(., label) %>% 
  summarise(., n(), mean(score))
