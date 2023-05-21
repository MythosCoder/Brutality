import pickle, argparse, requests
from webbrowser import open_new_tab
import pyfiglet
import sys,os
import threading
from random import choice

#displayed colors
class Colors:
	BLUE = '\033[94m'
	CYAN = '\033[96m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	END = '\033[0m'

#alternative to "colors.blue + string + colors.end"
def colored(string, color):
	return getattr(Colors, color.upper()) + string + Colors.END

#displays the banner
banner = pyfiglet.figlet_format("Brutality")
print(banner)

def run_discovery_mode():
	if(args.discover == True):
		print(colored(f"[i] running on {args.threads} threads", "cyan"))
		print(f"[i] Ignoring", colored("404", "red"), "status")
		ask = input("[i] would you like to open a browser tab for found content?(Y/N)")
		print("[i] Looking for web directories")
		try:
			runThreads(DiscoveryMode)
		except KeyboardInterrupt:
			SaveTask()

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
	parser.add_argument("--hc", "--hidecode", type = int, help = "hide status code", nargs = "?")

	#grouped args
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-d', "--discover", action = "store_true", help = "directory enumeration mode")
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
	print(colored("ERROR\n", "red") + "[!] Could not read file, please check file path ->", colored(f"\"{args.wordlist}\"","yellow"))
	sys.exit(0)

#save current progress then exit
def SaveTask():
	with open(".brutalSave", "wb") as saveFile:
		saveFile.write(pickle.dumps("text"))
		print(colored("\n[i] saving current progress...", "cyan"))
		print(colored("[i] exiting...", "yellow"))
		saveFile.close()
		sys.exit(0)

#randomize User-Agent
def randomAgent():
	user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
	'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.3',
	'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.',

	]

	return choice(user_agents)

#found matches
found = []

#directory enumeration mode
def DiscoveryMode():
	agent = {'User-Agent': randomAgent()}
	try:
		for i in lines:
			byte2str = i.decode("utf-8")
			if(byte2str.startswith('/')):
				reqGET = requests.get(args.url + byte2str, headers = agent)
				if(reqGET.status_code < 404):
					found.append(i)
					print(colored(f"{args.url + '/'  + byte2str}", "blue"), "<----> Status code:", statusCode(reqGET), colored(f"size[{len(reqGET.content)}]", "cyan"))
			else:
				reqGET = requests.get(args.url + "/" + byte2str, headers = agent)
				if(reqGET.status_code < 404):
					found.append(i)
					print(colored(f"{args.url + '/' + byte2str}", "blue"), "<----> Status code:", statusCode(reqGET), colored(f"size[{len(reqGET.content)}]", "cyan"))

	except requests.exceptions.ConnectionError:
		print(colored("[!] Connection ERROR", "red"))

	except requests.exceptions.InvalidURL:

		print(colored("[!] Invalid URL", "red"))

	except requests.exceptions.MissingSchema:
		print(colored("Error", "red"),"\n[!] Missing Schema, did you mean?: http(s)://" + args.url)


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
	t1 = threading.Thread(target=Request)
	t1.start()

def GET_Req():
	try:
		if(args.param == None):
			print(colored("[!] No Get variable name inputed exiting...", "red"))
			sys.exit(0)
		print("Sending GET Request")
		for i in range(len(lines)):
			values = {args.param : lines[i]}
			reqGET = requests.get(args.url, params = values)
			print(colored(f"{reqGET.url}","blue"), "<------> status code:", statusCode(reqGET), colored(f"size[{len(reqGET.content)}]", "cyan"))

	except requests.exceptions.MissingSchema:
		print(colored("Error", "red"),"\nMissing Schema, did you mean?: http(s)://" + args.url)

	except requests.exceptions.ConnectionError:
		print(colored("Connection ERROR", "red"))

	else:
		print(colored("Connection Error", "red"))

#check if running python version is not lower than version 3
def check_python_version():
	PYTHON_VERSION = 3

	if(sys.version_info[0] < PYTHON_VERSION):
		print("[!] python version lower than version 3, not supported")
		sys.exit(1)

def run_discovery_mode():
	if(args.discover == True):
		print(colored(f"[i] running on {args.threads} threads", "cyan"))
		print(f"[i] Ignoring", colored("404", "red"), "status")
		ask = input("[i] would you like to open a browser tab for found content?(Y/N)")
		print("[i] Looking for web directories")
		try:
			runThreads(DiscoveryMode)
		except KeyboardInterrupt:
			SaveTask()

def check_method():
	if(args.method == "post"):
		try:
			runThreads(POST_Req)
		except KeyboardInterrupt:
			SaveTask()

	elif(args.method == "get"):
		try:
			runThreads(GET_Req)
		except KeyboardInterrupt:
			SaveTask()

#check user privileges
def check_privileges():
	if(os.getuid() != 0):
		print("[!] you must have privileges to use Brutality!")


if __name__ == "__main__":
	check_python_version()
	check_privileges()
	run_discovery_mode()
	check_method()
