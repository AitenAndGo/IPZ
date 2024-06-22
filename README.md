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
+ samochód
Wszystkie potrzebne kody i modele znajdują się na [tutaj](https://github.com/AitenAndGo/IPZ "tutaj!"). Teraz opiszę każdy z etapów, aby przybliżyć sposób w jaki projekt został zrealizowany.
Zaczynajmy!

##  Makieta
Makieta miała składać się ze skrzyżowania, które posiada 4 drogi wejściowe i wszystkie z dróg łączą się ze sobą tworząc zewnętrzy prostokątny pierścień. Na skrzyżowaniu są 4 światła drogowe, każde z nich osobne do kierowania ruchem przy danej drodze wejściowej. przed wjazdem na środek skrzyżowania na każdej z dróg jest również ustawiony czytnik RFID. Czytnik ten za każdym razem, gdy przejeżdza auto ze swoją kartą RFID zczytuje ją i informuje server o tym że dane auto znalazło się właśnie na danej drodze. Aby wszystko mogło działać potrzebny był mikrokontroler do sterowania światłąmi i RFID. Wybraliśmy esp32, które posiada modół bluetooth oraz wifi co ułatwi komunikację z samochodem. Wszystkie światła i czujniki trzebabyło połączyć z mikrokontrolerem co nie jest lada zadaniem. Ze względu na wielkość makiety i ilość potrzebnych połączeń (tutaj warto dodać że czujniki RFID było zkomunikowane za pomocą protokołu SPI), wykorzystaliśmy płytkę prototypową do dzięki której uzyskaliśmy uporządkowany i zchludny układ elektryczny makiety.
Poniżej pewne zdjęcia i filmy przedstawiające proces powstawania makiety:
![makieta](https://github.com/AitenAndGo/IPZ/assets/87769038/0e3b4f39-4487-42d9-8e41-d7d6547c3677)
![435650640_2062892654094104_2510210449119449921_n](https://github.com/AitenAndGo/IPZ/assets/87769038/0c56d28a-5559-4d9f-a41f-ff719faac495)
![440818486_815108286667908_91705931173108030_n](https://github.com/AitenAndGo/IPZ/assets/87769038/62c4538c-78fc-437b-b8d0-fb5394633261)
![IMG_20240619_123124](https://github.com/AitenAndGo/IPZ/assets/87769038/04248355-eb58-4fc6-bdc6-8384c063734c)

## Program sterujący makietą
Makieta zwana przez nas "miastem" pełni w tym projekcie wiele aspektów. Odpowiada ona za odpowiednie przełączanie świateł, komunikuje się z serverem i przesyła informacje o odczytanych przejazdach samochodu, oraz musi komunikować się z samochodem aby informować go w momencie gdy przejeżdża on przez skrzyżowanie czy aktualne światło mu na to zezwala. Wszelkie kody można znaleźć w katalogu projektu i powinny one wyjaśnić wszelkie niepewności.

## Strona internetowa
Projekt miał być tak zrobiony, że w teorii można by było wiele samochodów puścić po podobnej makiecie, tylko większej. W związku z tym na serwerze python-anywhere postawiono bardzo prostą stronę internetową (Flask + HTML) oraz podłączono do niej relacyjną bazę danych (MySQL). Baza ta ma 3 tabele: Car, Server oraz City_Trafic. W pierwszej tabeli są wszystkie samochody, które mogą jeździć po makiecie - każdy ma swoje ID oraz status isDriving (czy aktualnie ejst w trakcie jazdy). Dodatkowo przy każdy są przyciski START i STOP - samochody maja być autonomiczne i można nimi sterowac z poziomu strony internetowej, klikając w przycisk Start samochód o danym ID startuje. Druga tabela Server przechowuje informacje o tym, o której godzinie zaczął i skończył jazdę samochód o danym ID w mieście o danym ID. Trzecia tabela to jest kontrola, o której godzinie samochód o danym ID przejechał przez światła (w naszym projekcie były 4: Północ, Południe, Wschód i Zachód).

![image](https://github.com/AitenAndGo/IPZ/assets/162838502/638bd2ca-8b7d-4f4d-9859-aacf12b32e23)

![Screenshot 2024-06-22 20-27-15](https://github.com/AitenAndGo/IPZ/assets/162838502/014e0569-f480-4ba3-9c5f-1529e88d7c2f)

## Samochód
Na samochód składają się w sumie 4 części:
+ model 3D
+ elektronika
+ model do rozpoznawania znaków
+ program sterujący
Pliki .stl do wydrukowania modelu samochodu można znaleźć w repozytrium projektu. Składa się z dwóch warst, pomiędze znajduje się powerbank, który głównie determinuje wymiary samochodu. Zawera specjalny uchwyt na kamerę a sterowanie kołami przednimi odbywa się przy pomocy micro-serva. W kontekście elektroniki samochód jest napędzany dwoma silnikami na tylnej osi. Silniki są kontrolowane sygnałąmi PWM z drivera LN289. Zasilanie silników jest z pakietu Li-Po 3s i przetwornicy zmniejszającej napięcie do 6V. Głównym komponentem jest RaspberryPi 4 które pełni funkcję sterowania całym samochodem. Złożony samohchód wygląda następująco:
![IMG20240527121051](https://github.com/AitenAndGo/IPZ/assets/87769038/6ef540e5-8917-44ee-bb5c-4f660c7397ce)
Do rozpoznawania znaków użyto biblioteki fastAi, która kożysta z PyTorch. Zostało zrobione łącznie 400 zdjęć o 4 różnych etykietach tj. prawo, lewo, prosto i bez znaku. Następnie wytrenowano model zgodnie z kodem dostępnym w repozytorium projektu. Całość została wykonany w google colab więc w łatwy sposób można prześledzić tok postępowania. Gotowy model posiadał błąd w wysokości 1%.
Najtrudniejszym zadaniem było stworzenie programu do sterowania. Aby przygotować program jeszcze przed stworzeniem samochodu i dostępem do mikrokomputera została stworzona symulacja w środowisu Unity. Symulacja pozwalała na przygotowanie podstaw skryptu. Działanie skryptu i symulacji przedstawia poniższe nagranie:
### SIMULATION VIDEO:
[kliknij aby obejrzeć](https://github.com/AitenAndGo/IPZ/assets/87769038/a0adc0f1-8832-4500-9a60-e44e0641514c "tutaj!")

Następnie gdy samochód był gotowy należało przygotować środowisko na raspberry. W celu instalacji wszystkich bibliotek zaleca się skorzystanie z minicondy i następnie na stworzonym wirtualnym środowisku zainstalować wszystkie wszystkie biblioteki. Ważne jest również aby system był odpowiedi do zainstalowania PyTorch (potrzebny system 64-bitowy). Program składa się z lokalnej strony na której można mieć podgląd na żywo z widoku kamery co jest bardzo pomocne do debugowania błędów. 
### REMOTLY CONTROLLED CAMERA TEST

[kliknij aby obejrzeć](https://github.com/AitenAndGo/IPZ/assets/87769038/37e9659a-60ab-4ea5-bf75-93e4743b6fed "tutaj!")

Gdy wszystko było przygotowane możnabyło przetestować kod na stowrzonym testowtm torze. Po wielu próbach osiągnięto pozytywne rezultaly co prezentuje poniższy film:

[kliknij aby obejrzeć](https://github.com/AitenAndGo/IPZ/assets/87769038/8e6763ad-770e-4cb4-8f08-51653d83972e "tutaj!")

Całość już połączonego systmu wszytskich elementó można zobaczyć na głównym filmie przedstawiającym cały projekt!. 









