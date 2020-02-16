cd ../server/
sudo apt install virtualenv
pip install --upgrade virtualenv

rm -rf venv
virtualenv -p python3 venv

. venv/bin/activate

pip install -r requirements.txt

pip install django
