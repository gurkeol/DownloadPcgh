from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import datetime
from pyquery import PyQuery
from os import path
from sys import exit
from requests import Session

# Seite zur Anmeldung des Benutzers
LOGIN_URL = "https://shop.computec.de/gujsso/auth/upstream/sst/1/module/customer-login"
# Zielseite für das Login-Formular
FORM_URL = "https://sso.guj.de/computec_shop/auth/login_check"
# Geschützte Seite mit den PCGH-Pdfs
PCGH_PDFS_URL = "https://shop.computec.de/customer/products/list/?vdz=70551"

parser = ArgumentParser()
parser.add_argument("config_file", help="Pfad zur Konfigurationsdatei")
args = parser.parse_args()

if not path.isfile(args.config_file):
    raise ValueError("Kann die Konfigurationsdatei nicht finden. Ist der Pfad korrekt?")

config = ConfigParser()
config.read(args.config_file)

# Logindaten
login_data = {
    "_login[email]": config["shop.computec.de"]["email"],
    "_login[password]": config["shop.computec.de"]["password"],
}

# Zieldaten
target_data = {
    "edition": "Ausgabe {}".format(datetime.now().strftime("%-m / %Y")),
    "file": config["DEFAULT"]["directory"] + "/PC_Games_Hardware_{}.pdf".format(datetime.now().strftime("%Y_0%m")),
}

if path.isfile(target_data['file']):
    print("Die Zieldatei \"{}\" existiert bereits. Beende Skript.".format(target_data["file"]))
    exit(0)

session = Session()

session.get(LOGIN_URL)
session.post(FORM_URL, data=login_data, allow_redirects=True)

query = PyQuery(session.get(PCGH_PDFS_URL).content)
url = query("div[class='product-issue']") \
    .filter(lambda i: PyQuery(this).text() == target_data["edition"]) \
    .siblings("div[class='product-actions']") \
    .children("a[class='download-select']") \
    .attr("href")

with open(target_data["file"], "wb+") as file:
    file.write(session.get(url).content)
    file.close()

session.close()
