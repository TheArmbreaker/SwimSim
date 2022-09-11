# Introduction

Coding Project for Python for Data Science
by Markus Armbrecht.

The overall objective is to present coding skills in Python in the context of an project. Additional Data Science environments are optional but benefitial (e.g. SQL and mongoDB).

---

## Motivation

To gain knowledge in a large variaty of Data Science technologies, following bulletpoints are used as technology objectives.

* For and while loops
* Working with numpy and pandas
* Working with GeoData in GeoPandas and Geopy
* Webscrapping with BeautifulSoup
* Working with SQL databases
* Working with mongoDB
* Object oriented programming
* Plotting with Matplotlib, Folium and Plotly
* Understanding programming constrains in terms of Time Complexity

---

## Project Idea

In order to achieve the technology objectives the Use Case should not be answered by existing datasets and an adequat approch for object oriented programming had to be found.

I am a swimming enthusiast and always wanted to work in a sport analytics context. From time to time one can read about athletes not participating in competitions because of injuries or other random influences on performance.

### Background Gina Lueckenkemper

For example in an interview on the Youtube Channel from [Suttgarter Zeitung & Suttgarter Nachrichten (2018)](https://youtu.be/2HR6FPdYYMw) Gina Lueckenkemper, a German sprinter and meanwhile European Champion, speaks about unexpected long travel time to tournaments - 14 hours instead of 5 hours - and other influences on consistent performance.
Additionally following sentence once was said, according to an not very reliable source, but I know equal statements from her podcasts and other interviews.
> "Ich habe immer Probleme mit den Matratzen. Die sind weich und ziemlich durchgelegen. Mein Rücken ist da eh etwas empfindlich. Ich gehe jeden Tag zum Chiropraktiker, dann geht das wieder.“ (Gina Lueckenkemper according to [bild.de: 2022])

### Background Kathleen Baker

In terms of swimming I know about the crohn's disease background from Kathleen Baker, former world-record holder in 100m backstroke and 4x100m medley relay.

Crohn's disease is not yet fully understood by medicine. There can be triggers in the immune system as well environmental factors. Therefore the occurence of bad days due to crohn's disease can be seen as random by some degree [(webmd.com: 2022)](https://www.webmd.com/ibd-crohns-disease/crohns-disease/crohns-disease-causes). An athlete has to travel a lot and traveling could also be a trigger [(dccv.de: 2020)](https://www.dccv.de/betroffene-angehoerige/leben-mit-einer-ced/reisen/).
> "I definitely think it's challenging and most people don't have to deal with a chronic disease while trying to make an Olympic team." (Kathleen Baker according to [olympics.com: 2021])

### Monte-Carlo-Simulation

This background led to the idea of programming the structure for a **Monte-Carlo-Simulation** and to predict an athlete's probability of winning a race when injured or not. During the chapter, this question will be adapted to other scenarios like chances to get on the winners' podium. Furthermore the term *injured* is interpreted as any kind of issue at the moment of the race.

The website [www.swimrankings.net](https://www.swimrankings.net) provides data on swimming athletes all over the world and will be the data source for this project. Between webscrapping and Monte-Carlo-Simulation the Data Exploration is done to get an idea of the data, even if the structures are set when scrapping.

---

## Miscellaneous

This Readme File is planned to be the frontpage of a jupyter book. However, .py-Files are not displayed in jupyter books. To counter this, the .py-Files are separately presented in additional jupyter notebooks, while actual .py-Files are imported in the other jupyter notebooks.

Some parts used the mathematical notation with $-symbols. Unfortunately this interfers with plotly plots in jupyter-book [(jupyterbook.org: 2022)]. Therefore mathematical notation is dismissed or moved to chapters without plotly plots. This was in such short notice that some operations could seem unnecessary, because originally the Simulation was in one notebook. The code was re-run after the split and works as shown.

---

Icon by [Icons8](https://icons8.com).

[bild.de: 2022]: https://www.bild.de/sport/mehr-sport/sport-mix/leichtathletik-wm-gina-hat-ein-matratzen-problem-80738596.bild.html
[olympics.com: 2021]: https://olympics.com/en/news/kathleen-baker-crohns-disease-made-me-strong-swimming
[(jupyterbook.org: 2022)]: https://jupyterbook.org/en/stable/interactive/interactive.html
