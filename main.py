import sqlite3
import json
from datetime import datetime, timedelta
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


def most_popular_cities(n):
    query = Location.select(Location.city, fn.COUNT(Location.city).alias('city_count')).group_by(Location.city).order_by(fn.COUNT(Location).desc()).limit(n)
    for result in query:
        print(result.city, result.city_count)


def most_popular_passwords(n):
    query = Login.select(Login.password, fn.COUNT(Login.password).alias('pass_count')).group_by(Login.password).order_by(fn.COUNT(Login).desc()).limit(n)
    for result in query:
        print(result.password, result.pass_count)


def date_range(date_1, date_2):
    date_time_1 = datetime.strptime(date_1, '%Y-%m-%d')
    date_time_2 = datetime.strptime(date_2, '%Y-%m-%d')

    print(f"{date_time_1} - {date_time_2}")
    query = Person.select().where(Person.date_of_birth > date_time_1, Person.date_of_birth < date_time_2)
    for result in query:
        print(result.login.username)



persons_db.connect()
persons_db.create_tables([Person, Location, Login])


with open('persons.json', encoding='utf-8') as f:
    persons_data = json.load(f)
    for key, value in persons_data.items():
        if key == 'results':
            for person in value:

                # Changes before saving to database
                del person['picture']
                person['phone'] = re.sub('[^0-9]', '', person['phone'])
                person['cell'] = re.sub('[^0-9]', '', person['phone'])

                # Changing dates to datetime type from string
                dob_date_time = datetime.strptime(person['dob']['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                registered_date_time = datetime.strptime(person['registered']['date'], '%Y-%m-%dT%H:%M:%S.%fZ')

                # Calculating days to birthday
                current_datetime = datetime.now()
                birthday_date_time_temp = dob_date_time
                try:
                    birthday_date_time_temp = birthday_date_time_temp.replace(year=current_datetime.year)
                except ValueError:
                    # In case od leap year
                    birthday_date_time_temp = birthday_date_time_temp.replace(year=current_datetime.year,
                                                                              day=birthday_date_time_temp.day+1)
                days_to_birthday = (birthday_date_time_temp.date() - current_datetime.date()).days
                if days_to_birthday < 0:
                    try:
                        birthday_date_time_temp = birthday_date_time_temp.replace(year=current_datetime.year + 1)
                    except ValueError:
                        # In case od leap year
                        birthday_date_time_temp = birthday_date_time_temp + timedelta(days=1)
                        birthday_date_time_temp = birthday_date_time_temp.replace(year=current_datetime.year + 1)

                    days_to_birthday = (birthday_date_time_temp.date() - current_datetime.date()).days

                person['day_to_birthday'] = days_to_birthday


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
                                          email=person['email'], login=loc_temp_db, date_of_birth=dob_date_time,
                                          age=person['dob']['age'], register_date=registered_date_time,
                                          register_age=person['registered']['age'], phone=person['phone'],
                                          cell=person['cell'], id_name=person['id']['name'],
                                          id_value=person['id']['value'],
                                          nat=person['nat'], day_to_birthday=person['day_to_birthday'])
                    p_temp_db.save()


female_percentage, male_percentage = gender_percentage()

print("\nCititees: ")#DEL
most_popular_cities(5)
print("\nPAsswords: ")#DEL
most_popular_passwords(7)


print("\nDAte range: ")#DEL
date_range('1997-01-30', '1998-02-04')

persons_db.close()




















