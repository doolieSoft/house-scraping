import argparse
import copy
import csv
import json
import os
import re
import smtplib
from email.message import EmailMessage

import django
from django.core.files import File


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_json", help="Config path to load", required=True)
    args = parser.parse_args()

    with open(args.config_json) as config_file:
        config = json.load(config_file)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", config["DJANGO_SETTINGS_MODULE"])
    django.setup()

    from annonce.models import Annonce

    path_annonces = config['root_path_annonces']
    files = [f for f in os.listdir(path_annonces) if
             re.match(r'^annonces-[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}\.csv$', f)]

    liste_new_annonce = []
    list_old_value_existing_annonce = {}
    list_new_value_existing_annonce = {}
    list_id_annonces_from_csv_file = []

    if len(files) == 0:
        print("No files to treat...")
        return

    with open(path_annonces + files[0], mode='r', encoding="UTF-8") as annonce_file:
        annonce_reader = csv.reader(annonce_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in annonce_reader:
            localisation = row[0]
            type_house = row[1]
            price = row[2]
            surface = row[3]
            description = row[4]
            lien = row[5]
            id = row[6]
            django_file = None
            if row[7] != "":
                django_file = File(open(row[7], 'rb'))

            old_price = row[8]
            try:
                list_id_annonces_from_csv_file.append(id)
                annonce = Annonce.objects.get(id=id)
                updated_annonce = annonce
                updated = False
                list_old_value_existing_annonce[id] = copy.deepcopy(annonce)
                if annonce.lien != lien:
                    updated_annonce.lien = lien
                    # updated = True
                if annonce.description != description:
                    updated_annonce.description = description
                    updated = True
                if annonce.price != price:
                    updated_annonce.price = price
                    updated = True
                if annonce.old_price != old_price:
                    updated_annonce.old_price = old_price
                    updated = True
                if annonce.surface != surface:
                    updated_annonce.surface = surface
                    updated = True
                if annonce.type_house != type_house:
                    updated_annonce.type_house = type_house
                    updated = True
                if annonce.localisation != localisation:
                    updated_annonce.localisation = localisation
                    updated = True

                if updated == True:
                    list_new_value_existing_annonce[id] = updated_annonce
                    if django_file is not None:
                        updated_annonce.image.save("image.jpg", django_file, save=True)
                    else:
                        updated_annonce.mark_as_deleted = False
                        updated_annonce.save(force_update=True)

            except Annonce.DoesNotExist:
                new_annonce = Annonce()
                new_annonce.id = id
                new_annonce.lien = lien
                new_annonce.description = description
                new_annonce.price = price
                new_annonce.old_price = old_price
                new_annonce.surface = surface
                new_annonce.type_house = type_house
                new_annonce.localisation = localisation
                if django_file is not None:
                    new_annonce.image.save("image.jpg", django_file, save=True)
                else:
                    new_annonce.save()
                liste_new_annonce.append(new_annonce)

    msg = "Hello,\nTu trouveras la liste des nouvelles maisons mises en ligne sur Immoweb\n\n"
    if len(liste_new_annonce) == 0:
        msg += "Pas de nouvelles annonces...\n"
    else:
        for a in liste_new_annonce:
            msg += "Id : " + str(a.id) + "\n" \
                   + str(a.localisation) + "\n" \
                   + str(a.type_house) + " - " + str(a.description) + "\n" \
                   + str(a.surface) + "\n" \
                   + "Prix : " + str(a.price) + " Ancien prix : " + str(a.old_price) + "\n" \
                   + str(a.lien) + "\n\n"

    msg += "\n\nIci, la liste des annonces mises à jour :\n"

    for id_annonce, new_annonce in list_new_value_existing_annonce.items():
        msg += "Id : " + str(id_annonce) + "\n" \
               + str(new_annonce.localisation) + "\n" \
               + str(new_annonce.type_house) + " - " + str(new_annonce.description) + "\n" \
               + str(new_annonce.surface) + "\n" \
               + "Prix : " + str(new_annonce.price) + " Ancien prix : " + str(new_annonce.old_price) + "\n" \
               + str(new_annonce.lien) + "\n\n"

        msg += "Anciennes valeurs :\n"
        old_annonce = list_old_value_existing_annonce[id_annonce]
        if new_annonce.localisation != old_annonce.localisation:
            msg += "Localisation : {}\n".format(old_annonce.localisation)
        if new_annonce.type_house != old_annonce.type_house:
            msg += "Type : {}\n".format(old_annonce.type_house)
        if new_annonce.description != old_annonce.description:
            msg += "Description : {}\n".format(old_annonce.description)
        if new_annonce.surface != old_annonce.surface:
            msg += "Surface : {}\n".format(old_annonce.surface)
        if new_annonce.price != old_annonce.price:
            msg += "Price : {}\n".format(old_annonce.price)
        if new_annonce.old_price != old_annonce.old_price:
            msg += "Old price : {}\n".format(old_annonce.old_price)
        # if new_annonce.lien != old_annonce.lien:
        #    msg += "Lien : {}\n\n\n".format(old_annonce.lien)
        msg += "\n\n"

    if len(list_new_value_existing_annonce) == 0:
        msg += "\nPas d'annonces mises à jour\n"

    msg += "\n\nEt ici, les biens qui ne sont plus disponibles :\n"
    nb_deleted_annonce = 0
    all_annonces = Annonce.objects.filter(mark_as_deleted=False)
    for a in all_annonces:
        if str(a.id) not in list_id_annonces_from_csv_file:
            nb_deleted_annonce += 1
            a.mark_as_deleted = True
            a.save(force_update=True)
            msg += "Id : " + str(a.id) + "\n" \
                   + str(a.localisation) + "\n" \
                   + str(a.type_house) + " - " + str(a.description) + "\n" \
                   + str(a.surface) + "\n" \
                   + "Prix : " + str(a.price) + " Ancien prix : " + str(a.old_price) + "\n" \
                   + str(a.lien) + "\n\n"
    if nb_deleted_annonce == 0:
        msg += "\nPas d'annonces supprimées\n"
    msg += "\nBisous ..."

    os.rename(path_annonces + files[0], path_annonces + files[0] + '.DONE')
    print("rename from {} to {}".format(path_annonces + files[0], path_annonces + files[0] + '.DONE'))

    print("Sending {} new annonce by mail".format(len(liste_new_annonce)))
    print("Sending {} updated annonce by mail".format(len(list_new_value_existing_annonce)))
    print("Sending {} deleted annonce by mail".format(nb_deleted_annonce))
    if len(liste_new_annonce) > 0 or len(list_new_value_existing_annonce) > 0 or nb_deleted_annonce > 0:
        server = smtplib.SMTP(config['smtp'], config['port'])
        server.ehlo()
        server.starttls()
        server.login(config['email_sender'], config['email_password'])

        # Send the mail
        for email_dest in config['email_dest']:
            my_email = EmailMessage()
            my_email.set_content(msg)
            my_email['From'] = config['email_sender']
            my_email['To'] = email_dest
            subject = ''
            if 'dev' in config["DJANGO_SETTINGS_MODULE"]:
                subject = '[ DEV ] '
            my_email['Subject'] = subject + 'Nouvelles de ScrapeImmoweb'
            server.send_message(my_email)
        server.quit()


if __name__ == "__main__":
    main()
