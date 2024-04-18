import argparse
import json

class CLIHandler:
	def __init__(self, parser: argparse.ArgumentParser):
		self.parser: argparse.ArgumentParser = parser

	def parseArgs(self):
		self.parser.add_argument("url", help="Web page URL to collect image (ignored if a configuration file applied)", type=str, nargs="?")
		self.parser.add_argument("-b", "--headless", "--background", help="Hide browser UI to run in background (i.e. headless mode)", action="store_true")
		self.parser.add_argument("-w", "--wired", help="Collect images captured during network connections, NOT IN HTML DOM.", action="store_true")
		self.parser.add_argument("-s", "--silent", help="Hide image URL output", action="store_true")
		self.parser.add_argument("-d", "--download", dest="DownloadPath", help="Download listed images to a destinated directory (relative path available)", type=str)
		self.parser.add_argument("-o", "--out", dest="OutputFilePath", help="Write image URL list to a destinated JSON file", type=str)
		self.parser.add_argument("-c", "--config", dest="ConfigPath", help="Configuration file path (shortens CLI inputs)", type=str)

		argInput: dict = vars(self.parser.parse_args())

		if "ConfigPath" in argInput:
			configFile = open(argInput["ConfigPath"])
			self.args = json.load(configFile)
			configFile.close()
		else:
			if "url" in argInput and str(argInput["url"]).strip() != "None":
				self.args = argInput
			else:
				self.parser.error("the following arguments are required: url")
				exit(-1)

	def getArg(self, argName: str) -> any:
		if argName in self.args:
			return self.args[argName]
		return None