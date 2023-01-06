# install prereq packages
install.packages(
	"aws.s3",repos = c(getOption("repos"),
	"http://cloudyr.github.io/drat")
)

library("aws.s3")
Sys.setenv(
    "AWS_ACCESS_KEY_ID" = "<your aws access key",
    "AWS_SECRET_ACCESS_KEY" = "<your aws secret acces key>"
)



# Create a data frame "export" with the rownames and cluster ID
export <- data.frame(fit[["cluster"]])

# make the export file a temp file that unlinks upon exiting RStudio. This will
# allow easy uploading without creating additional tables or vectors

tmp <- tempfile()
on.exit(unlink(tmp))
utils::write.csv(export,file=tmp)

# Export the file
put_object(

# File to upload, where object gives the file a name
  tmp, 
  object = "name.csv", 

# Select bucket to add the file to (no closing / needed)
  bucket = "jrg-business-intelligence/eirik",

# Create a progress bar
  show_progress = TRUE  
)