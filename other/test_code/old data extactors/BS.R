B <- function(){
	listOne <- c(1,2,3,4,5,6)
	testString <- "Test"
	return(list('numbers' = listOne, 'letters' = testString))
}
returnlist <- B()

print(returnlist)

x <- returnlist[['numbers']]
print(x)
print(min(x))
