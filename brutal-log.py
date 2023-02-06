import argparse
from termcolor import colored
from urllib.parse import urlparse
import requests
import pyfiglet
import sys
import os

#show banner
result = pyfiglet.figlet_format("Brutal-Log")
print(result)

#Arguments Parser
BrutusDescription = "Brutal-log is a tool made for brute forcing web logins"
parser = argparse.ArgumentParser(description = BrutusDescription, prog = "Brutal-Log", add_help = False)
parser.add_argument('-h', "--help", help = "displays help", action = "help")
parser.add_argument('-f', "--fuzz", action = "store_true", help = "directory enumeration mode")
parser.add_argument('-m', "--method", required=True, choices = ("get", "post"), help = "Specifies METHOD used be it POST or GET")
parser.add_argument('-w', "--wordlist", action = "store", required=True, help = "Specifies the WORDLIST used for the attack")
parser.add_argument("-u", '--url', required = True, help = "Specifies the target URL")
args = parser.parse_args()

#wordlist
lines = []

if(os.path.isfile(args.wordlist)):
	try:
		with open(args.wordlist) as wordL:
			for line in wordL:
				line = line.strip()
				lines.append(line)
	finally:
		wordL.close()
else:
	print(colored("ERROR", "red"),"\nplease check file path -->", "\"" + args.wordlist + "\"")
	sys.exit(0)


#incase of POST request
def POST_Req():

	try:
		print("Sending POST Request")
		reqPOST = requests.post(args.url)
		print(colored(args.url, "blue"), "<--------->", "status code:", statusCode(reqPOST))
	except requests.exceptions.MissingSchema:
		print(colored("Error", "red"),"\nMissing Schema, did you mean?: http(s)://" + args.url)
	except requests.exceptions.ConnectionError:
		print(colored("Error", "red"),"\nConnection Error")
	else:
		print("error")

def statusCode(code):
	#changing color depending on status code
	if(code.status_code >= 400 and code.status_code < 500):
		return colored(code.status_code, "red")

	elif(code.status_code >= 200 and code.status_code < 300):
		return colored(code.status_code, "green")

	elif(code.status_code >= 300 and code.status_code < 400):
		return colored(code.status_code, "orange")


def FuzzingMode():
	try:
		print("using fuzzing mode")
		for i in lines:
			reqGET = requests.get(args.url + "/" + i)
			print(colored(args.url + "/" + i, "blue"), "<-------> status code:", statusCode(reqGET))
	except requests.exceptions.ConnectionError:
		print(colored("Connection ERROR", "red"))
	else:
		print("error")

#incase of GET request
def GET_Req():
	try:
		print("Sending GET Request")
		for i in lines:
			reqGET = requests.get(args.url)
			print(args.url + i)
			print(colored(args.url, "blue"), "<---------> status code:", statusCode(reqGET))
	except requests.exceptions.MissingSchema:
		print(colored("Error", "red"),"\nMissing Schema, did you mean?: http(s)://" + args.url)
	except requests.exceptions.ConnectionError:
		print(colored("Connection ERROR", "red"))
	else:
		print("Connection Error")

def run():
	if(os.getuid() != 0):
		print("You must have privileges to use Brutus!")
		sys.exit(0)
	if(args.fuzz == True):
		FuzzingMode()
	if(args.method == "post"):
		POST_Req()
	elif(args.method == "get"):
		GET_Req()
run()
