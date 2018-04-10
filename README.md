https://dash.plot.ly/installation

https://dash.plot.ly/deployment

https://dash.plot.ly/sharing-data-between-callbacks

## Deploy

conda create -n venv

conda install pip

pip install dash dash-renderer dash-core-components dash-html-components dash_table_experiments plotly gunicorn numpy tqdm pandas

pip freeze > requirements.txt

git add .
git commit -m 'first commit'
git push heroku master

echo 'pandas' >> requirements.txt

git add .
git commit -m 'added pandas'
git push heroku master

heroku ps:scale web=1 

