class PrintUtil:
	isPrintable: bool

	@staticmethod
	def printLog(message: str):
		if PrintUtil.isPrintable:
			print(message)