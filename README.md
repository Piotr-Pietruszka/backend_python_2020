# README

Plik interact_db.py należy umieścić w jednym folderze z plikiem persons.json. Baza danych jest przechowywana w pliku persons.db. Po uruchomieniu skryptu jest ona zawsze aktualizowana na podstawie pliku persons.json. Nowy rekord jest zapisywany, jeżeli nie ma jeszcze w bazie rekordu z taką samą nazwą użytkownika. Można wymusić utworzenie bazy od nowa, przy pomocy odpowiedniej komendy.

#### Spis komend:

* *python interact_db.py -gender-percentage*   - wyświetla procentowy udział kobiet i mężczyzn w bazie                                                                                                                                                
* *python interact_db.py -average-age [Gender]* - podaje średni wiek użytkowników. Opcjonalnie można wyspecyfikować płeć (*female / male*)  i wtedy podawana jest średni wieku użytkowników danej płci.
* *python interact_db.py -most-common-cities Number_of_cities* - podaje najpopularniejsze miasta oraz liczbę ich wystąpień w bazie danych. Liczba wyświetlonych miast jest określona parametrem.                                                                  
* *python interact_db.py -most-common-passwords Number_of_passwords*- podaje najpopularniejsze hasła praz liczbę ich wystąpień. Liczba wyświetlonych haseł jest określona parametrem.                                                         
* *python interact_db.py -date-range First_date Second_date* - wyświetla użytkowników urodzonych w pomiędzy danymi (określonymi parametrami) datami. Format daty: YYYY-MM-DD
* *python interact_db.py -safest-password* - podaje najbezpieczniejsze hasło w bazie oraz uzyskaną przez nie liczbę punktów
* *python interact_db.py -load-data*  - wymusza usunięcie dotychczasowej bazy i ponowne załadowanie danych z pliku persons.json                                                                                                                
* *python interact_db.py -print-all* - wyświetla dane wszystkich osób znajdujących się w bazie


#### Rozwiązania programowe:
Dane poszczególnych użytkowników oraz te dotyczące ich lokalizacji i logowania przechowywane są w oddzielnych tabelach (*Person, Location, Login*). Do komunikacji z bazą danych użyty został peewee, a do utworzenia interfejsu linii poleceń moduł argparse.
