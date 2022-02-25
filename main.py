import argparse, datetime, os, pathlib, zipfile

def check_today_argument(zipf, tempzipf): #funkcja sprawdzająca czy został podany trzeci parametr 
    if args.today:
        if 'updated.txt' in zf.namelist(): #sprawdzenie czy plik updated.txt znajduje się w archiwum
            try:
                with zipf.open('updated.txt', 'r') as updated_file: #otworzenie pliku updated.txt oraz skopiowanie jego zawartości
                    content = updated_file.read()
                    content = content.decode('utf-8')
                    content = content + f"\n{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
                    tempzipf.writestr('updated.txt', content)  #dodanie aktualnej daty do pliku updated.txt
            except IOError as e:
                print(e) 
        else:
            tempzipf.writestr('updated.txt', f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        return True
    else:
        if 'updated.txt' in zf.namelist():
            try:
                with zf.open('updated.txt', 'r') as updated_file:
                    content = updated_file.read()
                    content = content.decode('utf-8')
                    tempzipf.writestr('updated.txt', content)
                    return True
            except IOError as e:
                print(e)

def delete_temp_file(): #funkcja usuwająca tymczasowe archiwum służące skopiowania plików z archiwum pierwotnego
    try:
        os.remove(f'{args.name}')
        os.rename('temp.zip', f'{args.name}')
    except OSError as e:
        print(e)

parser = argparse.ArgumentParser(description="Zadanie dla XTM") #inicjalzacja CLI

parser.add_argument("name", metavar="nazwa archiwum", type=str,
                    help = "Podaj nazwę archiwum zip, które ma zostać utworzone/zaktualizowane") #dodanie argumentów do CLI

parser.add_argument("add_value", metavar="wartość do dodania", type=str,
                    help = "Podaj wartość, która ma zostać dodana do pliku VERSION.txt")

parser.add_argument('-td', '--today', action='store_true',
                    help = "Dodaj argument, jeśli chcesz dodać dzisiejszą datę do pliku updated.txt")

args = parser.parse_args()

file = pathlib.Path(f'{args.name}')

if file.exists(): #sprawdzenie czy archiwum istnieje

    try:
        with zipfile.ZipFile(f'{args.name}', 'a') as zf: #otwarcie archiwum
            zf_copied = False                            #flaga służąca do poinformowania czy zostało utworzone tymczasowe archiwum
            if 'VERSION.txt' in zf.namelist():           #sprawdzenie czy w archiwum znajduje się plik VERSION.txt
                try:
                    with zf.open('VERSION.txt', 'r') as version_file, zipfile.ZipFile('temp.zip', 'w') as temp_zf: #otwarcie pliku VERSION.txt oraz utworzenie
                                                                                                                   #tymczasowego archiwum
                        zf_copied = check_today_argument(zf, temp_zf)            #kopiowanie plików z archiwum pierwotnego do archiwum tymczasowego
                        
                        content = version_file.read() 
                        content = content.decode('utf-8')
                        content = content + f'\n{args.add_value}'
                        temp_zf.writestr('VERSION.txt', content)
                            
                        for item in zf.namelist():   
                            if item != 'VERSION.txt' and item != 'updated.txt':
                                buffer = zf.read(item)
                                temp_zf.writestr(item, buffer)
                except (IOError, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError) as e:
                    print(e)            

            else:
                if 'updated.txt' in zf.namelist():
                    try:
                        with zipfile.ZipFile('temp.zip', 'w') as temp_zf:
                            temp_zf.writestr('VERSION.txt', args.add_value)
                            zf_copied = check_today_argument(zf, temp_zf)
                    except (IOError, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError) as e:
                        print(e)
                elif 'updated.txt' not in zf.namelist() and args.today:
                    zf.writestr('VERSION.txt', args.add_value)
                    zf.writestr('updated.txt', f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            
        if zf_copied:
            delete_temp_file()
    
    except (IOError, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError) as e:
        print(e)

    print('Wykonano wszystkie operacje')

else:
    print('Archiwum nie istnieje')
