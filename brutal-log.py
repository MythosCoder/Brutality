import argparse
from webbrowser import open_new_tab
import requests
import pyfiglet
import sys,os
import threading

#colors
class colors:
	blue = '\033[94m'
	cyan = '\033[96m'
	green = '\033[92m'
	yellow = '\033[93m'
	red = '\033[91m'
	end = '\033[0m'

#shows the banner
result = pyfiglet.figlet_format("Brutal-Log")
print(result)

#Arguments Parser, and program options
BrutusDescription = "Brutal-log is a tool made for brute forcing web logins"
parser = argparse.ArgumentParser(description = BrutusDescription, prog = "Brutal-Log", add_help = False, epilog = "We are not responsible for the ilegal uses of this tool")
group = parser.add_mutually_exclusive_group()

parser.add_argument('-h', "--help", help = "displays help", action = "help")
group.add_argument('-f', "--fuzz", action = "store_true", help = "directory enumeration mode")
parser.add_argument('-m', "--method", required = False, choices = ("get", "post"), help = "Specifies METHOD used be it POST or GET")
group.add_argument('-p', "--param", help = "Specifies parameters used")
parser.add_argument('-w', "--wordlist", action = "store", required=True, help = "Specifies the WORDLIST used for the attack")
parser.add_argument("-u", '--url', required = True, help = "Specifies the target URL")
parser.add_argument("-t", "--threads", type = int, default = 10, help = "sets threads", nargs = "?")
#parser.add_argument("-t", '--tor', help = "uses tor socks for the requests")

args = parser.parse_args()

#store every wordlist value inside lines
lines = []

#check if the path the user inputed is valid
if(os.path.isfile(args.wordlist)):
	try:
		with open(args.wordlist, 'rb') as wordL:
			for line in wordL:
				line = line.strip()
				lines.append(line)
	finally:
		wordL.close()

else:
	print(colors.red + "ERROR" + colors.end,"\nplease check file path -->", "\"" + args.wordlist + "\"")
	sys.exit(0)

#directory enumeration mode
def FuzzingMode():
	try:
		ask = input("would you like to open browser tab for found directories?(Y/N)")
		print("fuzzing web directories")
		for i in lines:
			byte2str = i.decode("utf-8")
			reqGET = requests.head(args.url + "/" + byte2str, timeout = 5)
			print(colors.blue + args.url + "/" + byte2str + colors.end, "<-----> status code:", statusCode(reqGET))

			if((ask == 'y' or ask == 'Y') and (reqGET.status_code >= 200 and reqGET.status_code < 400)):
				open_new_tab(args.url + "/" + byte2str)

	except requests.exceptions.ConnectionError:
		print(colors.red + "Connection ERROR" + colors.end)

	except requests.exceptions.InvalidURL:
		print(colors.red + "Invalid URL" + colors.end)

	except requests.exceptions.MissingSchema:
		print(colors.red + "Error" + colors.end,"\nMissing Schema, did you mean?: http(s)://" + args.url)

	else:
		print(colors.red + "error" + colors.end)

#sends the POST request 
def POST_Req():
	pass

#changing the color depending on the status code
def statusCode(code):
	if(code.status_code >= 400 and code.status_code < 500):
		return colors.red + str(code.status_code) + colors.end

	elif(code.status_code >= 200 and code.status_code < 300):
		return colors.green + str(code.status_code) + colors.end

	elif(code.status_code >= 300 and code.status_code < 400):
		return colors.yellow + str(code.status_code) + colors.end

#implementing threading
def runBrute(Request):
	#check if valid integer range of threads
	if(args.threads >= 1 and args.threads <= 50):
		for i in range(args.threads):
			t = threading.Thread(target=Request)
			t.start
	else:
		print(colors.red + "Invalid thread number" + colors.end)

#sends the GET Request
def GET_Req():
	try:
		print("Sending GET Request")
		for i in range(len(lines)):
			payload = {args.param : lines[i]}
			reqGET = requests.head(args.url, params = payload)
			print(colors.blue + reqGET.url + colors.end, "<------> status code:", statusCode(reqGET))

	except requests.exceptions.MissingSchema:
		print(colors.red + "Error" + colors.end,"\nMissing Schema, did you mean?: http(s)://" + args.url)

	except requests.exceptions.ConnectionError:
		print(colors.red + "Connection ERROR" + colors.end)

	else:
		print(colors.red + "Connection Error" + colors.end)

#check command line options and check if user has privileges
def run():
	if(os.getuid() != 0):
		print("You must have privileges to use Brutus!")
		sys.exit(0)

	if(args.fuzz == True):
		try:
			runBrute(FuzzingMode())
		except KeyboardInterrupt:
			print(colors.yellow + "\nexiting..." + colors.end)
			sys.exit(0)

	if(args.method == "post"):
		POST_Req()

	if(args.method == "get"):
		try:
			runBrute(GET_Req())
		except KeyboardInterrupt:
			print(colors.yellow + "\nexiting..." + colors.end)
			sys.exit(0)

run()
