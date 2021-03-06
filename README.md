# house-scraping 

As I am starting to search a new house, I thought I would optimize my search by creating this tool.

## scrape_immoweb.py

I run this script (1 times per hour) to scrape Immoweb website, so I am informed when there is new or updated houses on their website. 

**scrape_immoweb.py** launches a chrome browser with *Selenium*, and then I use *BeautifulSoup* to find the info needed. Then it saves all in a csv file

Here is the format of the scrape_immoweb.py's json config file :
```json
{
  "url": "url to scrape",
  "log_full_path": "self-explanatory",
  "annonces_root_path": "folder where the generated csv files will be stored"
}
```
## immo/annonces_importer.py
Inside *Django* project ***immo***, I created an app ***annonce***. The script **annonces_importer.py** imports the info scraped from the csv generated by **scrape_immoweb.py** to the database. 
I can see the new houses and updates in the django admin.
It sends a mail to a list of emails.

Here is the format of the immo/annonces_importer.py's json config file :
```json
{
  "smtp": "",
  "port": "",
  "email_sender": "account from which you send your mail",
  "email_password": "password of the account",
  "email_dest": [
    "user1@gmail.com",
    "user2@hotmail.com"
  ],
  "root_path_annonces": "path where the csv annonces are stored"
}
```

## Environment settings

#### Django immo structure ####
I have separated environments so I can test without interfering with production data.

```
immo
|──settings
    |-- base.py
    |-- dev.py
    |-- prod.py
```
In base.py, I put everything from the old settings.py. Then in dev.py and prod.py, you add :
```
from .base import *
```
Now, you can override each variables from the base.py settings.


In manage.py, you have to comment 
```
def main():
    #os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'immo.settings')
```
 
To use one environment, in the terminal, specify which setting you want to use :
```
set DJANGO_SETTINGS_MODULE=immo.settings.prod
```

Then you can *makemigrations*, *migrate*, *launch* your app as usual.