To run the app on localhost:\
1)Clone this repo\
2)On terminal: sudo docker compose down\
3)On terminal: sudo docker compose up\
4)Open http://localhost:5174/ on browser\
\
To rebuild the processed csv files and tfidf matrices and vectorizers run all python scripts under /data-processing-scripts in the following order:\
1)stem.py\
2)preprocess.py\
3)tfidf.py\
4)similarities.py\
5)lsi.py\
6)kmeans.py\
