# PROJEKT AUTONOMICZENGO SAMOCHODU:
[kliknij aby obejrzeć](url_do_filmu)


# Projekt autonomicznego samochodu 

Celem projektu będzie stworzenie autonomicznego modelu samochodu potrafiącego poruszać się po makiecie miasta ze skrzyżowaniem i światłami, samochód będzie w stanie sam poruszać się po drodze, odpowiednio reagować na światła drogowe, oraz podejmować decyzje o swojej trasie.

___
## 1. Wprowadzenie
W ramach kursu *Interdyscyplinarny projekt zespołowy* przez 15 tygodni w grupie 4 osób będziemy pracować nad stworzeniem automocznego pojazdu, potrafiącego poruszać się na stworzonej drodze i reagować na światła drogowe. Cały projekt jest udokumentowany a pliki będą dostępne [tutaj](https://github.com/AitenAndGo/IPZ "tutaj!"). Rownież poniżej będzie dostępny i pokazany cały proces tworzenia projektu, więc chętne osoby będą mogły spróbować odtworzyć tą koncepcję. Samo stowrzenie takiego pojazdu wraz z całym systemem i makietą jest zadaniem wymagającym dużej wiedzy z zakresu programowania, elektroniki i mechaniki. Do dzieła!

## 2. Cele projektu
+ zbudowanie pojazdu mobilnego
+ stworzenie środowiska po którym będzie poruszał się pojazd
+ stowrzenie systemu świateł drogowych na skrzyżowaniu
+ implementacja oprogramowania z systemem wizyjnym
+ stworzenie bazy danych
+ stworzenie strony internetowej

## 3. Plan projektu
Szczegółowy plan projektu dostępny jest [tutaj](https://github.com/AitenAndGo/IPZ/blob/main/Documentation/Plan.txt "tutaj!")

    
___
# Realizacja
Realizacja projektu skłądała się na 4 główne etapy:
+ Makieta skrzyżowania
+ Strona internetowa
+ Program strujący makietą miasta
+ program sterujący samochodem
Wszystkie potrzebne kody i modele znajdują się na [tutaj](https://github.com/AitenAndGo/IPZ "tutaj!"). Teraz opiszę każdy z etapów, aby przybliżyć sposób w jaki projekt został zrealizowany.
Zaczynajmy!

##  Makieta
Makieta miała składać się ze skrzyżowania, które posiada 4 drogi wejściowe i wszystkie z dróg łączą się ze sobą tworząc zewnętrzy prostokątny pierścień. Na skrzyżowaniu są 4 światła drogowe, każde z nich osobne do kierowania ruchem przy danej drodze wejściowej. przed wjazdem na środek skrzyżowania na każdej z dróg jest również ustawiony czytnik RFID. Czytnik ten za każdym razem, gdy przejeżdza auto ze swoją kartą RFID zczytuje ją i informuje server o tym że dane auto znalazło się właśnie na danej drodze. Aby wszystko mogło działać potrzebny był mikrokontroler do sterowania światłąmi i RFID. Wybraliśmy esp32, które posiada modół bluetooth oraz wifi co ułatwi komunikację z samochodem. Wszystkie światła i czujniki trzebabyło połączyć z mikrokontrolerem co nie jest lada zadaniem. Ze względu na wielkość makiety i ilość potrzebnych połączeń (tutaj warto dodać że czujniki RFID było zkomunikowane za pomocą protokołu SPI), wykorzystaliśmy płytkę prototypową do dzięki której uzyskaliśmy uporządkowany i zchludny układ elektryczny makiety.

# SIMULATION VIDEO:
[kliknij aby obejrzeć](https://github.com/AitenAndGo/IPZ/assets/87769038/a0adc0f1-8832-4500-9a60-e44e0641514c "tutaj!")

# REMOTLY CONTROLLED CAMERA TEST
https://github.com/AitenAndGo/IPZ/assets/87769038/37e9659a-60ab-4ea5-bf75-93e4743b6fed





