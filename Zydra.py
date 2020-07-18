#!/usr/bin/env python

import optparse
import zipfile
import rarfile  # need unrar tools
import itertools
import string
import os
import crypt
import pyfiglet
from termcolor import cprint, colored
import time
import term  # py-term
from datetime import timedelta
import sys
import threading
import shutil
import subprocess
from multiprocessing import Process, BoundedSemaphore, Queue, current_process, cpu_count

class Zydra():
    def __init__(self):
        self.start_time = time.monotonic()
        self.process_lock = BoundedSemaphore(value=cpu_count())
        self.counter_lock = threading.BoundedSemaphore(value=1)
        self.banner()
        self.stop = Queue(maxsize=1)
        self.stop.put(False)
        self.count = Queue(maxsize=1)
        self.threads = []
        self.name = Queue(maxsize=1)
        self.name.put(str("a"))
        self.process_count = 0
        self.limit_process = 500
        self.shot = 5000

    def fun(self, string):
        list = []
        fer = ['-', "\\", "|", '/']
        for char in string:
            list.append(char)
        timer = 0
        pointer = 0
        fer_pointer = 0
        while timer < 20:
            list[pointer] = list[pointer].upper()
            print("\r" + self.blue("".join(str(x) for x in list) + " " + fer[fer_pointer]), end="")
            list[pointer] = list[pointer].lower()
            max_fer = len(fer) - 1
            if fer_pointer == max_fer:
                fer_pointer = -1
            max = len(list) - 1
            if pointer == max:
                pointer = -1
            pointer += 1
            fer_pointer += 1
            timer += 1
            time.sleep(0.1)
            if timer == 20:
                print("\r" + self.blue(string) + "\n", end="")
                return

    def blue(self, string):
        return colored(string, "blue", attrs=['bold'])

    def green(self, string):
        return colored(string, "green", attrs=['bold'])

    def yellow(self, string):
        return colored(string, "yellow", attrs=['bold'])

    def red(self, string):
        return colored(string, "red", attrs=['bold'])

    def bwhite(self, string):
        return colored(string, "white", attrs=['bold'])

    def white(self, string):
        return colored(string, "white")

    def detect_file_type(self, file):
        if str(file).split(".")[-1] == "rar":
            return "rar"
        elif str(file).split(".")[-1] == "zip":
            return "zip"
        elif str(file).split(".")[-1] == "pdf":
            return "pdf"
        else:
            return "text"

    def count_word(self, dict_file):
        count = 0
        with open(dict_file, "r") as wordlist:
            for line in wordlist:
                count += 1
        return count

    def count_possible_com(self, chars, min, max):
        x = min
        possible_com = 0
        while x <= max:
            possible_com += len(chars) ** x
            x += 1
        return possible_com

    def counter(self, max_words):
        self.counter_lock.acquire()
        num = self.count.get()
        # print(self.count)
        # print(num)
        if num != 0:
            self.count.put(num - 1)
            current_word = max_words - int(num) + 1
            percent = (100 * current_word) / max_words
            width = (current_word + 1) / (max_words / 42)  # 100 / 25
            bar = "\t" + self.white("Progress : [") + "#" * int(width) + " " * (42 - int(width)) \
                  + "] " + self.yellow(str("%.3f" % percent) + " %")
            # time.sleep(1)
            sys.stdout.write(u"\t\u001b[1000D" + bar)
            sys.stdout.flush()
        self.counter_lock.release()

    def handling_too_many_open_files_error(self):
        if self.process_count == self.limit_process:
            for x in self.threads:
                x.join()
            self.threads = []
            self.limit_process += 500

    def search_zip_pass(self, passwords_list, compress_file, max_words):
        try:
            temp_file = self.create_temporary_copy(compress_file, passwords_list[1])
            for word in passwords_list:
                password = word.strip('\r').strip('\n')
                stop = self.stop.get()
                self.stop.put(stop)
                if stop is False:  # if find password dont doing more
                    self.counter(max_words)
                    try:
                        with zipfile.ZipFile(temp_file, "r") as zfile:
                            zfile.extractall(pwd=bytes(password, encoding='utf-8'))
                            self.stop.get()
                            self.stop.put(True)
                            time.sleep(3)
                            print("\n\t" + self.green("[+] Password Found: " + password) + "\n")
                            break
                    except Exception as e:
                        # print(e)
                        pass
                else:
                    break
            if os.path.isfile(temp_file):
                os.remove(os.path.abspath(temp_file))
            # last_process_number = int(max_words / self.shot) + (max_words % self.shot > 0)
            if str(self.last_process_number) in str(current_process().name):
                time.sleep(20)
                stop = self.stop.get()
                self.stop.put(stop)
                if stop is False:
                    print("\n\t" + self.red("[-] password not found") + "\n")
                else:
                    pass
            self.process_lock.release()
        except KeyboardInterrupt:
            self.process_lock.release()

    def create_temporary_copy(self, file, word):
        name = self.name.get()
        name2 = str(word)
        self.name.put(name2)
        directory_path = "temp_directory"
        try:
            os.mkdir(directory_path)
        except FileExistsError:
            pass
        temp_file_name = "temp" + name + "." + self.file_type
        temp_file_path = directory_path + '/' + temp_file_name  # linux path
        shutil.copy2(file, temp_file_path)
        return temp_file_path

    def delete_temporary_directory(self):
        if os.path.exists("temp_directory"):
            shutil.rmtree("temp_directory")

    def search_rar_pass(self, passwords_list, compress_file, max_words):
        try:
            temp_file = self.create_temporary_copy(compress_file, passwords_list[1])
            for word in passwords_list:
                password = word.strip('\r').strip('\n')
                stop = self.stop.get()
                self.stop.put(stop)
                if stop is False:  # if find password dont doing more
                    self.counter(max_words)
                    try:
                        with rarfile.RarFile(temp_file, "r") as rfile:
                            # print(password)  very useful for trouble shooting
                            rfile.extractall(pwd=password)
                            self.stop.get()
                            self.stop.put(True)
                            time.sleep(3)
                            print("\n\t" + self.green("[+] Password Found: " + password + '\n'))
                            break
                    except Exception as e:
                        # print(e)
                        pass
                else:
                    break
            if os.path.isfile(temp_file):
                os.remove(os.path.abspath(temp_file))
            # last_process_number = int(max_words / 500) + (max_words % 500 > 0)
            if str(self.last_process_number) in str(current_process().name):
                time.sleep(20)
                stop = self.stop.get()
                self.stop.put(stop)
                if stop is False:
                    print("\n\t" + self.red("[-] password not found") + "\n")
                else:
                    pass
            self.process_lock.release()
        except KeyboardInterrupt:
            self.process_lock.release()

    def search_pdf_pass(self, passwords_list, file, max_words):
        try:
            temp_file = self.create_temporary_copy(file, passwords_list[1])
            for word in passwords_list:
                password = word.strip('\r').strip('\n')
                stop = self.stop.get()
                self.stop.put(stop)
                if stop is False:  # if find password dont doing more
                    self.counter(max_words)
                    proc = subprocess.Popen(['qpdf', "--password=" + password, '--decrypt', temp_file, self.decrypted_file_name], stderr=subprocess.PIPE)
                    proc.wait()
                    # output, error = proc.communicate()
                    status = proc.returncode
                    if status == 0:
                        self.stop.get()
                        self.stop.put(True)
                        time.sleep(3)
                        print("\n\t" + self.green("[+] Password Found: " + password))
                        print("\t" + self.blue("[*]") + self.white(" Your decrypted file is ") + self.bwhite(self.decrypted_file_name) + "\n")
                        # self.end_time()
                        break
                    elif status == 2:
                        pass
                else:
                    break
            # for thread in self.threads:
            #     print(thread)
            # last_process_number = int(max_words / 500) + (max_words % 500 > 0)
            if str(self.last_process_number) in str(current_process().name):
                time.sleep(20)
                stop = self.stop.get()
                self.stop.put(stop)
                if stop is False:
                    print("\n\t" + self.red("[-] password not found") + "\n")
                else:
                    pass
            self.process_lock.release()
        except KeyboardInterrupt:
            self.process_lock.release()

    def search_shadow_pass(self, passwords_list, salt_for_crypt, crypt_pass, max_words, user):
        try:
            for word in passwords_list:
                password = word.strip('\r').strip('\n')
                stop = self.stop.get()
                self.stop.put(stop)
                if stop is False:  # if find password dont doing more
                    self.counter(max_words)
                    cryptword = crypt.crypt(password, salt_for_crypt)
                    if cryptword == crypt_pass:
                        self.stop.get()
                        self.stop.put(True)
                        time.sleep(4)
                        print("\n\t" + self.green("[+] Password Found: " + password) + "\n")
                        break
                    else:
                        pass
                else:
                    break
            # print(last_process_number)
            # print(str(current_process().name))
            if str(self.last_process_number) in str(current_process().name):
                time.sleep(20)
                stop = self.stop.get()
                self.stop.put(stop)
                if stop is False:
                    print("\n\t" + self.red("[-] password not found") + "\n")
                else:
                    pass
            self.process_lock.release()
        except KeyboardInterrupt:
            self.process_lock.release()

    def last_words_check(self, max_words, passwords_list, file):
        while True:
            if self.stop is True:
                exit(0)
            elif self.count == len(passwords_list):# self_cont kam mishe
                if self.file_type is "rar":
                    self.search_rar_pass(passwords_list, file, max_words)
                if self.stop is False:
                    print("\n\t" + self.red("[-] Password not found") + "\n")
                    self.delete_temporary_directory()
                    self.end_time()
                return
            else:
                pass

    def dict_guess_password(self, dict_file, file):
        last_check = 0
        passwords_group = []
        possible_words = self.count_word(dict_file)
        self.last_process_number = int(possible_words / self.shot) + (possible_words % self.shot > 0)
        self.count.put(possible_words)
        self.file_type = self.detect_file_type(file)
        self.fun("Starting password cracking for " + file)
        print("\n " + self.blue("[*]") + self.white(" Count of possible passwords: ") + self.bwhite(str(possible_words)))
        if self.file_type == "text":
            file = open(file)
            for line in file.readlines():
                self.count.get()
                self.count.put(possible_words)
                crypt_pass = line.split(':')[1].strip(' ')
                if crypt_pass not in ['*', '!', '!!']:
                    user = line.split(':')[0]
                    print("  " + self.blue("[**]") + self.white(" cracking Password for: ") + self.bwhite(user))
                    algorythm = crypt_pass.split('$')[1].strip(' ')
                    salt = crypt_pass.split('$')[2].strip(' ')
                    salt_for_crypt = '$' + algorythm + '$' + salt + '$'
                    with open(dict_file, "r") as wordlist:
                        for word in wordlist:
                            passwords_group.append(word)
                            last_check += 1
                            self.handling_too_many_open_files_error()
                            if (len(passwords_group) == self.shot) or (possible_words - last_check == 0):
                                passwords = passwords_group
                                passwords_group = []
                                self.process_lock.acquire()
                                stop = self.stop.get()
                                self.stop.put(stop)
                                if stop is False:
                                    t = Process(target=self.search_shadow_pass,
                                                args=(passwords, salt_for_crypt, crypt_pass, possible_words, user))
                                    self.threads.append(t)
                                    self.process_count += 1
                                    t.start()
                                else:
                                    self.process_lock.release()
                            else:
                                continue
                        for x in self.threads:
                            x.join()
                        self.last_process_number *= 2
            self.end_time()
        elif self.file_type == "zip":
            with open(dict_file, "r") as wordlist:
                for word in wordlist:
                    passwords_group.append(word)
                    last_check += 1
                    self.handling_too_many_open_files_error()
                    if (len(passwords_group) == self.shot) or (possible_words - last_check == 0):
                        passwords = passwords_group
                        passwords_group = []
                        self.process_lock.acquire()
                        stop = self.stop.get()
                        self.stop.put(stop)
                        if stop is False:
                            t = Process(target=self.search_zip_pass, args=(passwords, file, possible_words))
                            self.threads.append(t)
                            self.process_count += 1
                            t.start()
                        else:
                            self.process_lock.release()
                    else:
                        continue
                for x in self.threads:
                    x.join()
                self.delete_temporary_directory()
                self.end_time()
        elif self.file_type == "pdf":
            self.decrypted_file_name = "decrypted_" + file.split('/')[-1]
            with open(dict_file, "r") as wordlist:
                for word in wordlist:
                    passwords_group.append(word)
                    last_check += 1
                    self.handling_too_many_open_files_error()
                    if (len(passwords_group) == self.shot) or (possible_words - last_check == 0):
                        passwords = passwords_group
                        passwords_group = []
                        self.process_lock.acquire()
                        stop = self.stop.get()
                        self.stop.put(stop)
                        if stop is False:
                            t = Process(target=self.search_pdf_pass, args=(passwords, file, possible_words))
                            self.threads.append(t)
                            self.process_count += 1
                            t.start()
                        else:
                            self.process_lock.release()
                    else:
                        continue
                for x in self.threads:
                    x.join()
                self.delete_temporary_directory()
                self.end_time()
        elif self.file_type == "rar":
            with open(dict_file, "r") as wordlist:
                for word in wordlist:
                    passwords_group.append(word)
                    last_check += 1
                    self.handling_too_many_open_files_error()
                    if (len(passwords_group) == self.shot) or (possible_words - last_check == 0):
                        passwords = passwords_group
                        passwords_group = []
                        self.process_lock.acquire()
                        stop = self.stop.get()
                        self.stop.put(stop)
                        if stop is False:  # ok finishing all process after finding password
                            t = Process(target=self.search_rar_pass, args=(passwords, file, possible_words))
                            self.threads.append(t)
                            self.process_count += 1
                            t.start()
                        else:
                            self.process_lock.release()
                    else:
                        continue
                for x in self.threads:
                    x.join()
                self.delete_temporary_directory()
                self.end_time()

    def bruteforce_guess_password(self, chars, min, max, file):
        last_check = 0
        passwords_group = []
        possible_com = self.count_possible_com(chars, int(min), int(max))
        self.last_process_number = int(possible_com / self.shot) + (possible_com % self.shot > 0)
        self.count.put(possible_com)
        self.file_type = self.detect_file_type(file)
        self.fun("Starting password cracking for " + file)
        print("\n " + self.blue("[*]") + self.white(" Count of possible passwords: ") + self.bwhite(str(possible_com)))
        if self.file_type == "text":
            file = open(file)
            for line in file.readlines():
                self.count.get()
                self.count.put(possible_com)
                crypt_pass = line.split(':')[1].strip(' ')
                if crypt_pass not in ['*', '!', '!!']:
                    user = line.split(':')[0]
                    print("  " + self.blue("[**]") + self.white(" cracking Password for: ") + self.bwhite(user))
                    algorythm = crypt_pass.split('$')[1].strip(' ')
                    salt = crypt_pass.split('$')[2].strip(' ')
                    salt_for_crypt = '$' + algorythm + '$' + salt + '$'
                    for password_length in range(int(min), int(max) + 1):
                        for guess in itertools.product(chars, repeat=password_length):
                            guess = ''.join(guess)
                            passwords_group.append(guess)
                            last_check += 1
                            self.handling_too_many_open_files_error()
                            if (len(passwords_group) == self.shot) or (possible_com - last_check == 0):
                                passwords = passwords_group
                                passwords_group = []
                                self.process_lock.acquire()
                                stop = self.stop.get()
                                self.stop.put(stop)
                                if stop is False:
                                    t = Process(target=self.search_shadow_pass, args=(passwords, salt_for_crypt, crypt_pass, possible_com, user))
                                    self.threads.append(t)
                                    self.process_count += 1
                                    t.start()
                                else:
                                    self.process_lock.release()
                            else:
                                continue
                    for x in self.threads:
                        x.join()
                    self.last_process_number *= 2
            self.end_time()
        elif self.file_type == "zip":
            for password_length in range(int(min), int(max) + 1):
                for guess in itertools.product(chars, repeat=password_length):
                    guess = ''.join(guess)
                    passwords_group.append(guess)
                    last_check += 1
                    self.handling_too_many_open_files_error()
                    if (len(passwords_group) == self.shot) or (possible_com - last_check == 0):
                        passwords = passwords_group
                        passwords_group = []
                        self.process_lock.acquire()
                        stop = self.stop.get()
                        self.stop.put(stop)
                        if stop is False:
                            t = Process(target=self.search_zip_pass, args=(passwords, file, possible_com))
                            self.threads.append(t)
                            self.process_count += 1
                            t.start()
                        else:
                            self.process_lock.release()
                    else:
                        continue
            for x in self.threads:
                x.join()
            self.delete_temporary_directory()
            self.end_time()
        elif self.file_type == "pdf":
            self.decrypted_file_name = "decrypted_" + file.split('/')[-1]
            for password_length in range(int(min), int(max) + 1):
                for guess in itertools.product(chars, repeat=password_length):
                    guess = ''.join(guess)
                    passwords_group.append(guess)
                    last_check += 1
                    self.handling_too_many_open_files_error()
                    if (len(passwords_group) == self.shot) or (possible_com - last_check == 0):
                        passwords = passwords_group
                        passwords_group = []
                        self.process_lock.acquire()
                        stop = self.stop.get()
                        self.stop.put(stop)
                        if stop is False:
                            t = Process(target=self.search_pdf_pass, args=(passwords, file, possible_com))
                            self.threads.append(t)
                            self.process_count += 1
                            t.start()
                        else:
                            self.process_lock.release()
                    else:
                        continue
            for x in self.threads:
                x.join()
            self.delete_temporary_directory()
            self.end_time()
        elif self.file_type == "rar":
            for password_length in range(int(min), int(max) + 1):
                for guess in itertools.product(chars, repeat=password_length):
                    guess = ''.join(guess)
                    passwords_group.append(guess)
                    last_check += 1
                    self.handling_too_many_open_files_error()
                    if (len(passwords_group) == self.shot) or (possible_com - last_check == 0):
                        passwords = passwords_group
                        passwords_group = []
                        self.process_lock.acquire()
                        stop = self.stop.get()
                        self.stop.put(stop)
                        if stop is False:  # ok finishing all process after finding password
                            t = Process(target=self.search_rar_pass, args=(passwords, file, possible_com))
                            self.threads.append(t)
                            self.process_count += 1
                            t.start()
                        else:
                            self.process_lock.release()
                    else:
                        continue
            for x in self.threads:
                x.join()
            self.delete_temporary_directory()
            self.end_time()

    def make_chars(self, char_type):
        chartype_list = char_type.split(",")
        chars = ""
        for chartype in chartype_list:
            if chartype == "lowercase":
                chars += string.ascii_lowercase
            elif chartype == "uppercase":
                chars += string.ascii_uppercase
            elif chartype == "letters":
                chars += string.ascii_letters
            elif chartype == "digits":
                chars += string.digits
            elif chartype == "symbols":
                chars += string.punctuation
            elif chartype == "space":
                chars += " "
            else:
                return False
        return chars

    def banner(self):
        term.clear()
        term.pos(1, 1)
		# check if font "epic" exists on this system
        # sudo wget http://www.figlet.org/fonts/epic.flf -O /usr/share/figlet/epic.flf
        bannerfont = "epic" if os.path.exists('/usr/share/figlet/epic.flf') else "banner"
        banner = pyfiglet.figlet_format("ZYDRA", font=bannerfont).replace("\n", "\n\t\t", 7)
		
        cprint("\r\n\t" + "@" * 61, "blue", end="")
        cprint("\n\t\t" + banner + "\t\tAuthor : Hamed Hosseini", "blue", attrs=['bold'])
        cprint("\t" + "@" * 61 + "\n", "blue")

    def end_time(self):
        self.stop = True
        end_time_show = time.asctime()
        end_time = time.monotonic()
        execution_time = (timedelta(seconds=end_time - self.start_time))
        print(self.blue("End time ==> ") + self.white(end_time_show))
        print(self.blue("Execution time ==> ") + self.white(str(execution_time)) + "\n")
        term.saveCursor()
        term.pos(7, 15)
        term.writeLine("ok", term.green, term.blink)
        term.restoreCursor()
        exit(0)

    def main(self):
        start_time_show = time.asctime()
        usage = "%prog [options] [args]" \
                "\n\nDictionary Mode:" \
                "\n   %prog -f <file> -d <wordlist>" \
                "\n\nBrute force Mode:" \
                "\n   %prog -f <file> -b <char_type> -m <min_length> -x <max_length>" \
                "\n\n   Available char_type:" \
                "\n\t<lowercase>  The lowercase letters abcdefghijklmnopqrstuvwxyz" \
                "\n\t<uppercase>  The uppercase letters ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                "\n\t<letters>    The concatenation of the lowercase and uppercase"\
                "\n\t<digits>     numbers 0123456789" \
                "\n\t<symbols>    punctuation characters !#$%&'()*+,-./:;<=>?@[\]^_`{|}~'" + '"' \
                "\n\t<space>      space character" \
                "\n   You can select multiple character types." \
                "\n\tExample: %prog -f <file> -b <space,digits> -m 1 -x 8"

        parser = optparse.OptionParser(usage)
        parser.add_option("-d", dest="dictfile", type='string', help="Specifies dictionary file")
        parser.add_option("-f", dest="file", type='string', help="Specifies the file")
        parser.add_option("-b", dest="chartype", type='string', help="Specifies the character type")
        parser.add_option("-m", dest="minlength", type='string', help="Specifies minimum length of password")
        parser.add_option("-x", dest="maxlength", type='string', help="Specifies maximum length of password")

        (options, args) = parser.parse_args()
        try:
            if options.file:
                if os.path.isfile(options.file):
                    file = os.path.abspath(options.file)
                    if options.dictfile:
                        if os.path.isfile(options.dictfile):
                            dictfile = os.path.abspath(options.dictfile)
                            print(self.blue("Start time ==> ") + self.white(start_time_show) + "\n")
                            self.dict_guess_password(dictfile, file)
                        else:
                            parser.error(" " + options.dictfile + " dictionary file does not exist")
                            exit(0)
                    elif options.chartype:
                        chars = self.make_chars(options.chartype)
                        if chars is False:
                            parser.error(" " + options.chartype + " character type is not valid, Use --help for more info")
                        if options.minlength is None:
                            parser.error(" Enter minimum length of password")
                            exit(0)
                        if options.maxlength is None:
                            parser.error(" Enter maximum length of password")
                            exit(0)
                        if options.minlength > options.maxlength:
                            parser.error(" Min and Max must be numbers and Min must be \nless than Max or be the same"
                                         ", Use --help for more info")
                            exit(0)
                        else:
                            print(self.blue("Start time ==> ") + self.white(start_time_show) + "\n")
                            self.bruteforce_guess_password(chars, options.minlength, options.maxlength, file)

                    else:
                        parser.error(" Choose a wordlist or bruteforce method, Use --help for more info")
                        exit(0)
                else:
                    parser.error("" + options.file + " file does not exist")
                    exit(0)
            else:
                parser.error(" Choose a file, Use --help for more info")
                exit(0)

        except KeyboardInterrupt:
            time.sleep(1)
            self.delete_temporary_directory()
            print(self.red("\n\n [-] Detected CTRL+C") + self.white("\n closing app...\n Finish\n"))
            # self.end_time()
            exit(0)


if __name__ == "__main__":
    cracker = Zydra()
    cracker.main()
