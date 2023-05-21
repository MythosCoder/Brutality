import pickle, argparse, requests
from webbrowser import open_new_tab
import pyfiglet
import sys,os
import threading
from random import choice

#displayed colors
class colors:
	blue = '\033[94m'
	cyan = '\033[96m'
	green = '\033[92m'
	yellow = '\033[93m'
	red = '\033[91m'
	end = '\033[0m'

#alternative to "colors.blue + string + colors.end"
def colored(string, color):
	return getattr(colors, color) + string + colors.end

#displays the banner
banner = pyfiglet.figlet_format("Brutality")
print(banner)

#Arguments Parser, and program options
class argsManagement:
	BrutusDescription = "Brutality is a tool made for brute forcing web logins"
	
	#some args
	parser = argparse.ArgumentParser(description = BrutusDescription, prog = "Brutality", add_help = False, epilog = "I'm not responsible for the ilegal uses of this tool")
	parser.add_argument('-h', "--help", help = "displays help", action = "help")
	parser.add_argument('-m', "--method", required = False, choices = ("get", "post"), help = "Specifies METHOD used be it POST or GET")
	parser.add_argument('-w', "--wordlist", action = "store", required=True, help = "Specifies the WORDLIST used for the attack")
	parser.add_argument("-u", '--url', required = True, help = "Specifies the target URL")
	parser.add_argument("-t", "--threads", type = int, default = 10, help = "sets threads", nargs = "?")
	
	#grouped args
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-f', "--fuzz", action = "store_true", help = "directory enumeration mode")
	group.add_argument('-p', "--param", help = "Specifies parameters used")

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
	print(colored("ERROR\n", "red") + "[!] please check file path ->", colored(f"\"{args.wordlist}\"","yellow"))
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
def DiscoveryMode():
	agent = {'User-Agent': randomAgent()}
	try:
		print(f"[i] Ignoring", colored("404", "red"), "status")
		ask = input("[i] would you like to open a browser tab for found content?(Y/N)")
		print("[i] Looking for web directories")
		for i in lines:			
			byte2str = i.decode("utf-8")
			if(byte2str.startswith('/')):
				reqGET = requests.get(args.url + byte2str, headers = agent)
				if(reqGET.status_code < 404):
					print(colors.blue + args.url + byte2str + colors.end, "<----> Status code:", statusCode(reqGET), colored(f"size[{len(reqGET.content)}]", "cyan"))
			else:
				reqGET = requests.get(args.url + "/" + byte2str, headers = agent)
				if(reqGET.status_code < 404):
					print(colors.blue + args.url + "/" + byte2str + colors.end, "<----> Status code:", statusCode(reqGET), colored(f"size[{len(reqGET.content)}]", "cyan"))

			if((ask == 'y' or ask == 'Y') and (reqGET.status_code >= 200 and reqGET.status_code < 400)):
				open_new_tab(args.url + '/' + byte2str)

	except requests.exceptions.ConnectionError:
		print(colored("[!] Connection ERROR", "red"))

	except requests.exceptions.InvalidURL:

		print(colored("[!] Invalid URL", "red"))

	except requests.exceptions.MissingSchema:
		print(colored("Error", "red"),"\n[!] Missing Schema, did you mean?: http(s)://" + args.url)

	else:
		print(colored("[!] Error", "red"))

def POST_Req():
	pass

#changing the color depending on the status code
def statusCode(code):
	if(code.status_code >= 200 and code.status_code < 300):
		return colored(f"({str(code.status_code)})", "green")

	elif(code.status_code >= 300 and code.status_code < 400):
		return colored(f"({str(code.status_code)})", "yellow")

#implementing threading
def runThreads(Request):
	for i in range(args.threads):
			t = threading.Thread(target=Request)
			t.start

def GET_Req():
	try:
		if(args.param == None):
			sys.exit(0)
			print("[!] No Get variable name inputed exiting...")
		print("Sending GET Request")
		for i in range(len(lines)):
			values = {args.param : lines[i]}
			reqGET = requests.get(args.url, params = values)
			print(colors.blue + reqGET.url + colors.end, "<------> status code:", statusCode(reqGET))

	except requests.exceptions.MissingSchema:
		print(colored("Error", "red"),"\nMissing Schema, did you mean?: http(s)://" + args.url)

	except requests.exceptions.ConnectionError:
		print(colored("Connection ERROR", "red"))

	else:
		print(colored("Connection Error", "red"))

#check command line options and check if user has privileges
def main():
	if(sys.version_info[0] < 3):
		print("[!] python version lower than version 3, not supported")
		sys.exit(1)

	if(os.getuid() != 0):
		print("[!] You must have privileges to use Brutus!")
		sys.exit(0)

	if(args.fuzz == True):
		print(colored(f"[i] running on {args.threads} threads", "cyan"))
		try:
			runThreads(DiscoveryMode())

		except KeyboardInterrupt:
			print(colored("\n[i] exiting...", "yellow"))
			sys.exit(0)

	if(args.method == "post"):
		runThreads(POST_Req())

	if(args.method == "get"):
		try:
			runThreads(GET_Req())
		except KeyboardInterrupt:
			print(colored("\n[i] exiting...", "yellow"))
			sys.exit(0)

#run the program
main()
