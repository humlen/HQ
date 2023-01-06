# Import Libraries
library(cluster)
library(tidyverse)
library(factoextra)

# Basic Prep
data <- user_metrics	  	# Imports dataset
data <- na.omit(data)   	# Omits missing values
data <- scale(data)		    # Scales the dataset to correct for outliers
# data <- data[-c(x),-c(Y)] # Deletes the Xth row(s) and Yth column(s) of a dataset


# Euclidian distance for number of groups
d <- dist(data,method="euclidian")

# Perform hierarchical cluster analysis on a set of dissimilarities
fit <- hclust(d,method="ward")

# Plot the dendrogram
plot(fit) 

# Create n groups to cut the branches into
groups <- cutree(fit,k=n) 

# Create colored borders around n groups
rect.hclust(fit,k=5,border="color")


# ALTERNATIVELY USE LINE METHOD
# wss <- (nrow(data)-1)*sum(apply(data,2,var))
# for (i in 2:20) wss[i] <- sum(kmeans(data,centers=i)$withinss)
# plot(1:20,wss,type='b',xlab='Number of Clusters',)


# Analysis
fit <- kmeans(data,4)  							
aggregate(data,by=list(fit$cluster),FUN=mean)
data <- data.frame(data,fit$cluster)			
fit <- kmeans(data,4)

# Creates scatterplot with clusters
clusplot(data,fit$cluster,color=TRUE,shade=TRUE,labels=2,lines=0)