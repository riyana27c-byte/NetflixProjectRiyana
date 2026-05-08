README — Netflix Trending Predictor
CS 210 | Riyana Chaudhary

HOW TO RUN
Pull the GitHub repository linked in the final report.
Make sure netflix_titles.csv and df_enriched.csv are in the same folder.
Run the files in this order from the terminal:

python3 datacleaning.py
python3 databasework.py
python3 chartandvisual.py
python3 mlwork.py

The IPython notebook submitted through the course portal is not functional because the data files are too large to upload there.

WHAT EACH FILE DOES

datacleaning.py    cleans the raw Netflix CSV, merges IMDb data, saves df_ml_final.csv
databasework.py    builds the SQLite relational database and runs SQL queries
chartandvisual.py  generates the 10 charts saved to the charts/ folder
mlwork.py          trains both models, prints results, runs the interactive predictor

NOTES
At the end of mlwork.py the program will ask you to enter details about a Netflix title and predict whether it will trend using both models.
