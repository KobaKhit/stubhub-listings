https://dash.plot.ly/installation

https://dash.plot.ly/deployment

https://dash.plot.ly/sharing-data-between-callbacks

conda create -m venv

cond install pip

pip install dash dash-renderer dash-core-components dash-html-components plotly gunicorn numpy

pip freeze > requirements.txt

git add .
git commit -m 'first commit'
git push heroku master

echo 'pandas' >> requirements.txt

git add .
git commit -m 'added pandas'
git push heroku master


