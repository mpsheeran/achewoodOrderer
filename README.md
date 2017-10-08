# README #

### What is this repository for? ###

Retrieving a chronologically-sorted list of achewood comics and blog posts.

### How do I get set up? ###

`virtualenv --no-site-packages env
source ./env/bin/activate
pip install -r "requirements.txt"
cp base_config.json config.json`
Then populate config.json with your API key and a list of blogger urls.