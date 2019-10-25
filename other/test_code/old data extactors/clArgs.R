

args <- commandArgs(TRUE)

print(paste('length of args is:', length(args)))

r <- as.integer(args[1])
s <- as.character(args[2])

print(paste('r is:', r))
print(paste('s is:', s))


for (i in 1:r) { 
	print (i)
}

of1 <- paste(s, sep = '')
cat('$Parameters', file = of1, append = FALSE, sep = '\n')


for (i in 1:r) {
    cat(i, file = of1, append = TRUE, sep = '\n')
}

