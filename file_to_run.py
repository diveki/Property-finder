import os
import datetime as dt


date = dt.datetime.today()
html_path_name = 'Html'
filename_ipynb = 'Summary_for_flats_template.ipynb'
html_name = os.path.join(html_path_name, date.strftime('%Y%m%d') + '.html')

os.system('jupyter nbconvert --no-input --execute --output ' + html_name + ' --to html ' + filename_ipynb)
