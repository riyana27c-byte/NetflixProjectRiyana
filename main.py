# API_KEY = "c8a093f4"
 
# sample 750 from df_ml with a fixed seed so you get the same sample every run
# sample = df_ml.sample(n=750, random_state=42).copy()
 
# results = []
 
# for i, row in enumerate(sample.itertuples(), 1):
#     title = row.title
#     year  = int(row.release_year) if pd.notna(row.release_year) else ""
#  
#     params = {
#         "apikey": API_KEY,
#         "t":      title,
#         "y":      year,
#         "type":   "movie" if row.type == "Movie" else "series"
#     }
#  
#         if data.get("Response") == "True":
#             results.append({
#                 "title":       title,
#                 "imdb_rating": data.get("imdbRating"),
#                 "imdb_votes":  data.get("imdbVotes"),
#                 "metascore":   data.get("Metascore"),
#                 "awards":      data.get("Awards"),
#                 "runtime":     data.get("Runtime"),
#                 "language":    data.get("Language"),
#             })
#         else:
#             # OMDb couldn't find it — still keep the row, just with nulls
#             results.append({
#                 "title":       title,
#                 "imdb_rating": None,
#                 "imdb_votes":  None,
#                 "metascore":   None,
#                 "awards":      None,
#                 "runtime":     None,
#                 "language":    None,
#             })
#            })
#             })
# 
#             })

# merge back onto the sample
# omdb_df = pd.DataFrame(results)
# df_enriched = sample.merge(omdb_df, on="title", how="left")
# clean up numeric columns
# df_enriched["imdb_rating"] = pd.to_numeric(df_enriched["imdb_rating"], errors="coerce")
# df_enriched["imdb_votes"]  = (df_enriched["imdb_votes"]
 #                               .str.replace(",", "", regex=False)
 #                               .pipe(pd.to_numeric, errors="coerce"))
# df_enriched["metascore"]   = pd.to_numeric(df_enriched["metascore"], errors="coerce")
# save so you never have to hit the API again
# df_enriched.to_csv("df_enriched.csv", index=False)
# print(f"\ndone — {df_enriched['imdb_rating'].notna().sum()} / 750 titles matched")
# print(df_enriched[["title", "imdb_rating", "imdb_votes", "metascore", "awards"]].head(10))
# API_KEY = "c8a093f4"

# existing_sample = pd.read_csv("df_enriched.csv")
# remaining = df_ml[~df_ml["title"].isin(existing_sample["title"])]
# new_sample = remaining.sample(n=1000, random_state=99).copy()

# results = []

# for i, row in enumerate(new_sample.itertuples(), 1):
#     title = row.title
#     year  = int(row.release_year) if pd.notna(row.release_year) else ""

#     params = {
#         "apikey": API_KEY,
#         "t":      title,
#         "y":      year,
#         "type":   "movie" if row.type == "Movie" else "series"
#     }

# # merge new batch and combine with existing
# new_omdb = pd.DataFrame(results)
# new_enriched = new_sample.merge(new_omdb, on="title", how="left")

# # combine old and new and save
# df_enriched_combined = pd.concat([existing_sample, new_enriched], ignore_index=True)
# df_enriched_combined.to_csv("df_enriched.csv", index=False)

# print(f"\ndone — total rows: {len(df_enriched_combined)}")
# print(f"new matches: {new_enriched['imdb_rating'].notna().sum()} / 1000")

# df_enriched = pd.read_csv("df_enriched.csv")
# df_enriched["imdb_rating"] = pd.to_numeric(df_enriched["imdb_rating"], errors="coerce")
# df_enriched["imdb_votes"] = pd.to_numeric(df_enriched["imdb_votes"].astype(str).str.replace(",", "", regex=False), errors="coerce")

# existing_sample = pd.read_csv("df_enriched.csv")
# remaining = df_ml[~df_ml["title"].isin(existing_sample["title"])]
# print(len(remaining))
# print(df_ml_final["has_awards"].value_counts())
# print(df_ml_final["trending"].value_counts())



# df_ml_final = df_ml_final.drop(columns=["awards", "has_awards", "runtime", "language"])
# print(df_ml_final.columns.tolist())

# conn = sqlite3.connect("netflix.db")
# df_ml_final.to_sql("ml_ready", conn, if_exists="replace", index=False)
# conn.close()

