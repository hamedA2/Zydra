Zydra
Zydra is a file password recovery tool and Linux shadow file cracker 
It uses the dictionary search or Brute force method for cracking passwords.
Supported files:
•	RAR Files
•	Legacy ZIP Files
•	PDF Files
•	Linux shadow files (zydra can find all the user’s password in the linux shadow file one after the other)
Requirements:
To run the app, minimal requirements are:
•	Python 3.3 or higher
•	debian-based linux distro, preferably Kali linux 2
•	qpdf and unrar packages : Installing these packages on kali is as easy as running the following commands on terminal:
o	sudo apt-get update
o	sudo apt-get install qpdf unrar
•	some python modules in this program need to be installed manually, like:
zipfile, rarfile, crypt, pyfiglet, py-term(for term module) and so on.
you can use pip3 for install them
example: pip3 install py-term 
notice: rar,zip and pdf files must have an extension, shadow files does not need an extension.
Disclaimer:
This tool is only for testing and academic purposes Do not use it for illegal purposes!
features:
•	Cracking files password using two methods:  1.dictionary method 2.brute force method
•	In the brute force method, you can specify the min length and max length of the passwords.
•	 In the brute force method, you can specify the type of characters that may be used in the password.
•	There is a percent progress bar showing how much of the process has been performed.
•	Error handling.
•	One of the most important features of Zydra is the multiprocessing feature that speeds up the program. For example if you have 8 CPU cores, Zydra will use all of them for processing at the same time.
Installation:
Download Zydra by cloning the Git repository:
  $ git clone https://github.com/wafpassproject/wafpass.git
Usage:
To get a list of all options and learn how to use this app, enter the following command:

  $ python3 Zydra.py -h

 
Examples:
1 - Dictionary search to find the password for a zip file:
In this example I use rockyou.txt dictionary
$ python3 Zydra.py –f file.zip –d rockyou.txt
 
2 - Brute force search to find the password for the users in the shadow file:
Minimum length of password is 4 and maximum length is 4 and we try to find passwords that are composed of numbers and symbols letters.
$ python3 Zydra.py –f shadow –b digits,symbols –m 4 –x 4
 		
