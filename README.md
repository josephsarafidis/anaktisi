To run the app on localhost:\
\
1)Clone this repo\
2)On terminal: sudo docker compose up --build\
3)Open http://localhost:5174/ on browser\

Note: this repo is using a sample with 10.000 speeches from the parliament dataset due to filesize limitations. Please follow the steps below to build using the complete dataset.\
\
To rebuild the processed csv files and tfidf matrices and vectorizers make sure that INPUT_FILE in preprocess.py is equal to your datafile and then run all python scripts under /data-processing-scripts in the following order:\
\
1)stem.py\
2)preprocess.py\
3)tfidf.py\
4)similarities.py\
5)lsi.py\
6)kmeans.py\
7)sentiments.py\
\
Now you can run "sudo docker compose up --build" again

