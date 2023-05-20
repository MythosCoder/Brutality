import pickle, argparse, requests
from webbrowser import open_new_tab
import pyfiglet
import sys,os
import threading
from random import choice

#colors
class colors:
	blue = '\033[94m'
	cyan = '\033[96m'
	green = '\033[92m'
	yellow = '\033[93m'
	red = '\033[91m'
	end = '\033[0m'


#displays the banner
banner = pyfiglet.figlet_format("Brutality")
print(banner)


#Arguments Parser, and program options
class argsManagement:
	BrutusDescription = "Brutality is a tool made for brute forcing web logins"
	parser = argparse.ArgumentParser(description = BrutusDescription, prog = "Brutality", add_help = False, epilog = "I'm not responsible for the ilegal uses of this tool")
	group = parser.add_mutually_exclusive_group()

	parser.add_argument('-h', "--help", help = "displays help", action = "help")
	group.add_argument('-f', "--fuzz", action = "store_true", help = "directory enumeration mode")
	parser.add_argument('-m', "--method", required = False, choices = ("get", "post"), help = "Specifies METHOD used be it POST or GET")

	group.add_argument('-p', "--param", help = "Specifies parameters used")

	parser.add_argument('-w', "--wordlist", action = "store", required=True, help = "Specifies the WORDLIST used for the attack")
	parser.add_argument("-u", '--url', required = True, help = "Specifies the target URL")
	parser.add_argument("-t", "--threads", type = int, default = 10, help = "sets threads", nargs = "?")
	#parser.add_argument("-t", '--tor', help = "uses tor socks for the requests")

args = argsManagement.parser.parse_args()

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
	print(colors.red + "ERROR" + colors.end,"\n[!] please check file path ->", colors.blue + "\"" + args.wordlist + "\"" + colors.end)
	sys.exit(0)

#randomize User-Agent
def randomAgent():
	user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
	'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.3',
	'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.',

	]

	return choice(user_agents)

#directory enumeration mode
def FuzzingMode():
	agent = {'User-Agent': randomAgent()}
	try:
		print("Ignoring",colors.red,"404",colors.end,"status")
		ask = input("would you like to open a browser tab for found directories?(Y/N)")
		print("fuzzing web directories")
		for i in lines:
			byte2str = i.decode("utf-8")
			if(byte2str.startswith('/')):
				reqGET = requests.head(args.url + byte2str, timeout = 3, headers = agent)
				if(reqGET.status_code < 404):
					print(colors.blue + args.url + byte2str + colors.end, "<-----> status code:", statusCode(reqGET))
			else:
				reqGET = requests.head(args.url + "/" + byte2str, timeout = 3, headers = agent)
				if(reqGET.status_code < 404):
					print(colors.blue + args.url + "/" + byte2str + colors.end, "<----> status code:", statusCode(reqGET))

			if((ask == 'y' or ask == 'Y') and (reqGET.status_code >= 200 and reqGET.status_code < 400)):
				open_new_tab(args.url + '/' + byte2str)

	except requests.exceptions.ConnectionError:
		print(colors.red + "Connection ERROR" + colors.end)

	except requests.exceptions.InvalidURL:
		print(colors.red + "Invalid URL" + colors.end)

	except requests.exceptions.MissingSchema:
		print(colors.red + "Error" + colors.end,"\nMissing Schema, did you mean?: http(s)://" + args.url)

	else:
		print(colors.red + "error" + colors.end)

def POST_Req():
	pass

#changing the color depending on the status code
def statusCode(code):
	if(code.status_code >= 200 and code.status_code < 300):
		return colors.green + str(code.status_code) + colors.end

	elif(code.status_code >= 300 and code.status_code < 400):
		return colors.yellow + str(code.status_code) + colors.end

#implementing threading
def runBrute(Request):
	for i in range(args.threads):
			t = threading.Thread(target=Request)
			t.start

def GET_Req():
	try:
		if(args.param == None):
			sys.exit(0)
			print("No Get variable name inputed exiting...")
		print("Sending GET Request")
		for i in range(len(lines)):
			values = {args.param : lines[i]}
			reqGET = requests.head(args.url, params = values)
			print(colors.blue + reqGET.url + colors.end, "<------> status code:", statusCode(reqGET))

	except requests.exceptions.MissingSchema:
		print(colors.red + "Error" + colors.end,"\nMissing Schema, did you mean?: http(s)://" + args.url)

	except requests.exceptions.ConnectionError:
		print(colors.red + "Connection ERROR" + colors.end)

	else:
		print(colors.red + "Connection Error" + colors.end)

#check command line options and check if user has privileges
def main():
	if(os.getuid() != 0):
		print("You must have privileges to use Brutus!")
		sys.exit(0)

	if(args.fuzz == True):
		print(colors.green + "running on", args.threads, "threads" + colors.end)
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

#run the program
main()
