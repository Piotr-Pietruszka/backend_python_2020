import sqlite3
import json
from datetime import date
import re
from peewee import *




# connection to database
persons_db = SqliteDatabase('persons.db')


class Login(Model):
    uuid = CharField()
    username = CharField()
    password = CharField()
    salt = CharField()
    md5 = CharField()
    sha1 = CharField()
    sha256 = CharField()

    class Meta:
        database = persons_db


class Location(Model):
    # Street
    street_number = IntegerField()
    street_name = CharField()

    city = CharField()
    state = CharField()
    country = CharField()
    postcode = IntegerField()

    # coordinates
    latitude = FloatField()
    longitude = FloatField()

    # timezone
    timezone_offset = CharField()
    timezone_description = CharField()

    class Meta:
        database = persons_db


class Person(Model):
    gender = CharField()

    # Name
    title = CharField()
    first_name = CharField()
    last_name = CharField()

    # location
    location = ForeignKeyField(Location)

    # dob
    date_of_birth = DateTimeField()
    age = IntegerField()

    # registered
    register_date = DateTimeField()
    register_age = IntegerField()

    email = CharField()

    # login
    login = ForeignKeyField(Login)

    phone = IntegerField()
    cell = IntegerField()

    # id
    id_name = CharField()
    id_value = CharField(null=True)

    nat = CharField()
    day_to_birthday = IntegerField()

    class Meta:
        database = persons_db


def gender_percentage():
    # Tweet.select().where(Tweet.id > 50).count()
    female_count = Person.select().where(Person.gender == ['female']).count()
    male_count = Person.select().where(Person.gender == ['male']).count()
    all_count = Person.select().count()
    return 100.0*female_count/all_count, 100.0*male_count/all_count


persons_db.connect()
persons_db.create_tables([Person, Location, Login])


with open('persons.json', encoding='utf-8') as f:
    persons_data = json.load(f)
    for key, value in persons_data.items():
        if key == 'results':
            for person in value:

                # Changes before saving to database
                del person['picture']
                person['day_to_birthday'] = 9
                person['phone'] = re.sub('[^0-9]', '', person['phone'])
                person['cell'] = re.sub('[^0-9]', '', person['phone'])

                # Checking if person already exists (by username)
                query = Login.select().where(Login.username == person['login']['username'])


                for key_1, value_1 in person.items():
                    print(key_1, value_1)#DEL

                if not query.exists():

                    # Adding person, login and location to database
                    login_temp_db = Login(uuid=person['login']['uuid'], username=person['login']['username'],
                                           password=person['login']['password'], salt=person['login']['salt'],
                                           md5=person['login']['md5'], sha1=person['login']['sha1'],
                                           sha256=person['login']['sha256'])
                    login_temp_db.save()

                    loc_temp_db = Location(street_number=person['location']['street']['number'],
                                           street_name=person['location']['street']['name'],
                                           city=person['location']['city'], state=person['location']['state'],
                                           country=person['location']['country'],
                                           postcode=person['location']['postcode'],
                                           latitude=person['location']['coordinates']['latitude'],
                                           longitude=person['location']['coordinates']['longitude'],
                                           timezone_offset=person['location']['timezone']['offset'],
                                           timezone_description=person['location']['timezone']['description'])
                    loc_temp_db.save()
                    p_temp_db = Person(gender=person['gender'], title=person['name']['title'],
                                          first_name=person['name']['first'], last_name=person['name']['last'], location=loc_temp_db,
                                          email=person['email'], login=loc_temp_db, date_of_birth=person['dob']['date'],
                                          age=person['dob']['age'], register_date=person['registered']['date'],
                                          register_age=person['registered']['age'], phone=person['phone'],
                                          cell=person['cell'], id_name=person['id']['name'],
                                          id_value=person['id']['value'],
                                          nat=person['nat'], day_to_birthday=person['day_to_birthday'])
                    p_temp_db.save()


female_percentage, male_percentage = gender_percentage()


persons_db.close()


















