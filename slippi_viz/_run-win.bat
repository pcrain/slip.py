SET PATH=%PATH%;"%HOMEDRIVE%%HOMEPATH%\AppData\Roaming\Python\Python38\Scripts"
SET FLASK_APP=slippi_viz
SET FLASK_DEBUG=1	
chdir /d C:\Users\Patrick\AppData\Roaming\Python\Python38\site-packages\slippi_viz
start "" http://127.0.0.1:5000
flask run
