# Overview

In efforts to take my coding experience to be more applicable and useful, I decided to dive into a data analysis project. My primary goal was to work with a large, real-world dataset,  and apply fundamental  data science techniques to get some  kind of meaningful insights. Well, as a long-time PC gamer, I felt that analyzing data from the most popular game distribution system on the planet, Steam Games, would be a great way to showcase my ability to analyze and extract meaning from a large data set. I would also demonstrate a solid ability to clean semi-formatted data to an analaysis ready form, use statistical analysis, and demonstrate it visually with rendered graphs.

The dataset used is the "All Steam Games" dataset found [here on Kaggle](https://www.kaggle.com/datasets/joebeachcapital/top-1000-steam-games?resource=download&select=93182_steam_games.csv). This dataset contained information on over 90,000 games on Steam, including 39 columns of individual data points on each game, including the cost, user reviews, ratings, name, developer name, title, release date, and so on. The data focused on was the review data, the cost, and the ratings.

The data was cleaned of games that had incomplete critical data, or of adult content games.

The main purpose of the software is to answer specific, data-driven questions about trends in the video game market using the Pandas library for data manipulation.

[Software Demo Video](http://youtube.link.goes.here)

# Data Analysis Results

**QUESTION 1:** What are the 5 most common genres among top-rated games?

Games analyzed based on the following criteria:
* 90% Positive Reviews
* 100 Total Reviews

*Result*

    Genre       # Games
    --------------------
    Adventure     443
    Action        392
    Simulation    185
    RPG           180
    Strategy      143

# Development Environment

{Describe the tools that you used to develop the software}

{Describe the programming language that you used and any libraries.}

# Useful Websites

{Make a list of websites that you found helpful in this project}
* [Web Site Name](http://url.link.goes.here)
* [Web Site Name](http://url.link.goes.here)

# Future Work

{Make a list of things that you need to fix, improve, and add in the future.}
* Item 1
* Item 2
* Item 3