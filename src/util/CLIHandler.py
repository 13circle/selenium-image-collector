import argparse
import json

class CLIHandler:
	"""
	CLI 인터페이스 매개변수 관리 핸들러
	"""
	def __init__(self, parser: argparse.ArgumentParser):
		"""
		:param parser: ArgumentParser 클래스 (argparse)
		"""
		self.parser: argparse.ArgumentParser = parser

	def parseArgs(self):
		"""
		CLI 도움말 생성 및 매개변수 파싱
		"""
		# 매개변수별 도움말 생성
		self.parser.add_argument("url", help="Web page URL to collect image (ignored if a configuration file applied)", type=str, nargs="?")
		self.parser.add_argument("-b", "--headless", "--background", help="Hide browser UI to run in background (i.e. headless mode)", action="store_true")
		self.parser.add_argument("-w", "--wired", help="Collect images captured during network connections, NOT IN HTML DOM.", action="store_true")
		self.parser.add_argument("-s", "--silent", help="Hide image URL output", action="store_true")
		self.parser.add_argument("-d", "--download", dest="DownloadPath", help="Download listed images to a destinated directory (relative path available)", type=str)
		self.parser.add_argument("-o", "--out", dest="OutputFilePath", help="Write image URL list to a destinated JSON file", type=str)
		self.parser.add_argument("-c", "--config", dest="ConfigPath", help="Configuration file path (shortens CLI inputs)", type=str)

		# CLI 매개변수 파싱 수행
		# 파싱된 매개변수명과 값을 사전으로 저장
		argInput: dict = vars(self.parser.parse_args())

		# CLI 매개변수를 JSON 설정 파일로 일괄 입력할 경우 url을 필수 매개변수에서 제외
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
		"""
		설정된 CLI 매개변수의 값을 반환
		
		:param argName: 매개변수명
		:return: 매개변수값
		"""
		if argName in self.args:
			return self.args[argName]
		return None