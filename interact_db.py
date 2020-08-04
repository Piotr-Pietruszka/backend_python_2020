import json
from datetime import datetime, timedelta
import re
from peewee import *
import argparse


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

    password_safety = IntegerField()

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


class DatabaseInterface:

    def gender_percentage(self):
        """
        Calculate and print percentage of female and male users
        :return: None
        """
        female_count = Person.select().where(Person.gender == ['female']).count()
        male_count = Person.select().where(Person.gender == ['male']).count()
        all_count = Person.select().count()
        print(f"Female percentage: {100.0*female_count/all_count}, Male percentage: {100.0*male_count/all_count}")

    def calculate_average_age(self, gender):
        """
        Calculate and print average age of female/male/all users
        :param gender: Specify gender: female/male/all
        :return: None
        """
        if gender != 'male' and gender != 'female':
            query = Person.select(fn.AVG(Person.age).alias('Average_age'))
        else:
            query = Person.select(fn.AVG(Person.age).alias('Average_age')).where(Person.gender == gender)

        for result in query:
            print(result.Average_age)

    def most_common_cities(self, n):
        """
        Find and print most common cities in database
        :param n: Number of cities to print
        :return: None
        """
        query = Location.select(Location.city, fn.COUNT(Location.city).alias('city_count')).group_by(Location.city).order_by(fn.COUNT(Location).desc()).limit(n)
        for result in query:
            print(result.city, result.city_count)

    def most_common_passwords(self, n):
        """
        Find and print most common passwords in database
        :param n: Number of passwords to print
        :return: None
        """
        query = Login.select(Login.password, fn.COUNT(Login.password).alias('pass_count')).group_by(Login.password).order_by(fn.COUNT(Login).desc()).limit(n)
        for result in query:
            print(result.password, result.pass_count)

    def date_range(self, dates):
        """
        Print users (their usernames) who were born between given dates
        :param dates: list of two dates
        :return: None
        """
        date_time_1 = datetime.strptime(dates[0], '%Y-%m-%d')
        date_time_2 = datetime.strptime(dates[1], '%Y-%m-%d')

        print(f"{date_time_1} - {date_time_2}")
        query = Person.select().where(Person.date_of_birth > date_time_1, Person.date_of_birth < date_time_2)
        for result in query:
            print(f"{result.login.username}")

    def safest_password(self):
        """
        Find and print safest password in database (which received most points)
        :return: None
        """
        query = Login.select(Login).order_by(Login.password_safety.desc()).limit(1)
        for result in query:
            print(f"Password: \"{result.password}\", Points: {result.password_safety}")

    def calc_pass_safety(self, password):
        """
        Calculate safety of password (points given to it)
        If password contains
        At least one small letter it receives 1 point
        At least one big letter - 2 points
        At least one digit - 1 point
        At least one special character - 3 points
        Is at least 8 char long - 5 points

        :param password: password which safety is calculated
        :return: points given to password
        """
        password_safety = 0
        if any(c.islower() for c in password):
            password_safety += 1
        if any(c.isupper() for c in password):
            password_safety += 2
        if any(c.isdigit() for c in password):
            password_safety += 2
        if any(not c.isalnum() for c in password):
            password_safety += 3
        if len(password) >= 8:
            password_safety += 5
        return password_safety

    def print_all(self):
        """
        Print all information from database
        :return: None
        """
        query = Person.select()
        for result in query:
            print(f"Title: {result.title}, First name: {result.first_name}, Last name: {result.last_name}\n"
                  f"Street number: {result.location.street_number}, Street name: {result.location.street_name}\n"
                  f"City: {result.location.city}, State: {result.location.state}, "
                  f"Country: {result.location.country}, Postcode: {result.location.postcode}\n"
                  f"Latitude: {result.location.latitude}, Longitude: {result.location.longitude}\n"
                  f"Timezone offset: {result.location.timezone_offset}, Timezone description: {result.location.timezone_description}\n"
                  f"Date of birth: {result.date_of_birth}, Age: {result.age}\n"
                  f"Register date: {result.register_date}, Register age: {result.register_age}\n"
                  f"Email: {result.email}\n"
                  f"uuid: {result.login.uuid}, username: {result.login.username}, password:{result.login.password}\n"
                  f"salt: {result.login.salt}, md5: {result.login.md5}, sha1:{result.login.sha1}\n"
                  f"sha256: {result.login.sha256}, Password safety: {result.login.password_safety}\n"
                  f"Phone: {result.phone}, Cell: {result.cell}\n"
                  f"Id name: {result.id_name}, Id value: {result.id_value}\n"
                  f"nat: {result.nat}, Day to birthday: {result.day_to_birthday}\n")

            print("\n")

    def update_database(self, drop_existing_tables=False, filename='persons.json'):
        """
        Update database. Load data from json file and safe it to persons.db.
        :param drop_existing_tables: Boolean value determining if existing tables are supposed to be dropped. If set
        True whole database is created from json file. If set to False (on default) existing database is used and only
        non existing records are added.
        :param filename: filename of json file
        :return: None
        """

        # Deleting existing tables
        if drop_existing_tables:
            persons_db.drop_tables([Person, Login, Location])
            persons_db.create_tables([Person, Login, Location])

        with open(filename, encoding='utf-8') as f:
            persons_data = json.load(f)
            for key, value in persons_data.items():
                if key == 'results':
                    for person in value:

                        # Deleting picture field and changing phone and cell to pure numbers
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
                            # In case of the leap year - then as birthday is selected 01.03
                            birthday_date_time_temp = birthday_date_time_temp.replace(year=current_datetime.year,
                                                                                      day=birthday_date_time_temp.day+1)
                        days_to_birthday = (birthday_date_time_temp.date() - current_datetime.date()).days

                        if days_to_birthday < 0:  # Next birthday is next year
                            try:
                                birthday_date_time_temp = birthday_date_time_temp.replace(year=current_datetime.year+1)
                            except ValueError:
                                # In case of the leap year - then as birthday is selected 01.03
                                birthday_date_time_temp = birthday_date_time_temp + timedelta(days=1)
                                birthday_date_time_temp = birthday_date_time_temp.replace(year=current_datetime.year+1)
                            days_to_birthday = (birthday_date_time_temp.date() - current_datetime.date()).days

                        person['day_to_birthday'] = days_to_birthday

                        # Checking if person already exists (by username)
                        query = Login.select().where(Login.username == person['login']['username'])

                        if not query.exists():
                            # Adding person, login and location to database
                            pass_safety = db_interface.calc_pass_safety(person['login']['password'])
                            login_temp_db = Login(uuid=person['login']['uuid'], username=person['login']['username'],
                                                  password=person['login']['password'], salt=person['login']['salt'],
                                                  md5=person['login']['md5'], sha1=person['login']['sha1'],
                                                  sha256=person['login']['sha256'], password_safety=pass_safety)
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
                                               first_name=person['name']['first'], last_name=person['name']['last'],
                                               location=loc_temp_db,
                                               email=person['email'], login=loc_temp_db, date_of_birth=dob_date_time,
                                               age=person['dob']['age'], register_date=registered_date_time,
                                               register_age=person['registered']['age'], phone=person['phone'],
                                               cell=person['cell'], id_name=person['id']['name'],
                                               id_value=person['id']['value'],
                                               nat=person['nat'], day_to_birthday=person['day_to_birthday'])
                            p_temp_db.save()


db_interface = DatabaseInterface()
persons_db.connect()

# Creating tables if they don't exist
if not persons_db.table_exists('Location'):
    persons_db.create_tables([Location])
if not persons_db.table_exists('Login'):
    persons_db.create_tables([Login])
if not persons_db.table_exists('Person'):
    persons_db.create_tables([Person])



# Argparse CLI
my_parser = argparse.ArgumentParser()

# Group of argumenrs
group = my_parser.add_mutually_exclusive_group()
group.add_argument("-gender-percentage", "--gender_percentage", action="store_true",
                   help="Percentage of male and female in database")

group.add_argument("-average-age", "--average_age", nargs='?', const="both", metavar='Gender',
                   help="Average age of people in database. Optional argument to specify gender (male/female)")

group.add_argument("-most-common-cities", "--most_common_cities", nargs=1, type=int, metavar='Number_of_cities',
                   help="Most common cities in database. Parameter specifies number of displayed cities.")

group.add_argument("-most-common-passwords", "--most_common_passwords", nargs=1, type=int, metavar='Number_of_passwords',
                   help="Most common passwords in database. Parameter specifies number of displayed passwords.")

group.add_argument("-date-range", "--date_range", nargs=2, type=str, metavar=('First_date', 'Second_date'),
                   help="Usernames of people born between two given dates. Format of dates: YYYY-MM-DD")

group.add_argument("-safest-password", "--safest_password", action="store_true", help="Safest password in database")

group.add_argument("-load-data", "--load_data", action="store_true",
                   help="Drop existing tables in database. Load data from json file and save them to database.")

group.add_argument("-print-all", "--print_all", action="store_true", help="Print all people from database")

args = my_parser.parse_args()

# Updating database
if args.load_data:
    # Dropping existing tables
    db_interface.update_database(drop_existing_tables=True)
else:
    # Using existing tables
    db_interface.update_database()

# Other commands
if args.gender_percentage:
    db_interface.gender_percentage()
elif args.average_age:
    db_interface.calculate_average_age(args.average_age)
elif args.most_common_cities:
    db_interface.most_common_cities(args.most_common_cities)
elif args.most_common_passwords:
    db_interface.most_common_passwords(args.most_common_passwords)
elif args.date_range:
    db_interface.date_range(args.date_range)
elif args.safest_password:
    db_interface.safest_password()
elif args.print_all:
    db_interface.print_all()

persons_db.close()




















