import os
import requests
import shutil
import filetype
import re
import json

from typing import List

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from urllib.parse import urlparse, urljoin

from .BrowserManager import BrowserManager
from util.PrintUtil import PrintUtil

class ImageScraper:
	def __init__(self, browser: BrowserManager):
		self.browser = browser
		self.imgUrlList = list()
		self.imgSerial = 0

	def scrapeImageOfCurrentPage(self, parentElement: EC.WebDriverOrWebElement, downloadRootPath: str):
		elements: List[WebElement] = None
		if type(parentElement) == WebElement:
			elements = self.browser.querySelectorAll(parentElement, "img")
			elements.extend(self.browser.querySelectorAll(parentElement, "picture > source"))
		else:
			elements = self.browser.waitUntil("img", 30)
			elements.extend(self.browser.waitUntil("picture > source", 30))
		for element in elements:
			src: str = self.browser.getAttribute(element, "srcset")
			if src is None:
				src = self.browser.getAttribute(element, "src")
			else:
				src = src.split(" ")[0]

			if src is not None:
				if src.startswith("data:"):
					continue
				elif not src.startswith("http") or src.startswith("/") and not src.startswith("//"):
					src = urljoin(self.browser.getCurrentLocation(), src)
				self.imgUrlList.append(src)

				if downloadRootPath is not None:
					fileName: str = os.path.join(downloadRootPath, os.path.basename(urlparse(src).path))
					if fileName.endswith("/"):
						fileName = fileName + str(self.imgSerial)
						self.imgSerial = self.imgSerial + 1
					PrintUtil.printLog("Start download file : " + src)

					if not self.downloadImage(src, fileName):
						self.saveScreenshot(element, fileName)
					if not re.compile(r"\....$").search(fileName) and not re.compile(r"\.....$").search(fileName):
						fileExt: str = filetype.guess_extension(fileName)
						if fileExt is not None:
							os.rename(fileName, fileName + "." + fileExt)
			else:
				PrintUtil.printLog("scrapeImageOfCurrentPage : src/srcset attribute is not available")

	def scrape(self, url: str, downloadRootPath: str, outputFilePath: str):
		self.browser.goTo(url)

		collectedRequests = self.browser.getCollectedRequests()
		if collectedRequests is None:
			self.scrapeImageOfCurrentPage(self.browser.getWebDriver(), downloadRootPath)
			self.browser.forEachIframes(None, self.scrapeImageOfCurrentPage, [downloadRootPath])
		else:
			if len(collectedRequests) > 0:
				PrintUtil.printLog("Start collecting images... ({reqLen})".format(reqLen=str(len(collectedRequests))))
			else:
				PrintUtil.printLog("No wired requests")

			for request in collectedRequests:
				mimeType = filetype.guess_mime(request.response.body)
				if mimeType is None or not str(mimeType).startswith("image"):
					continue

				self.imgUrlList.append(request.url)

				if downloadRootPath is not None:
					fileExt = filetype.guess_extension(request.response.body)
					fileName = os.path.join(downloadRootPath, str(self.imgSerial) + "." + fileExt)
					try:
						with open(fileName, "wb") as outFile:
							outFile.write(request.response.body)
							outFile.close()
							self.imgSerial = self.imgSerial + 1
							PrintUtil.printLog("Image saved successfully : " + fileName)
					except:
						PrintUtil.printLog("Failed to save image : " + str(request.path))
			self.browser.initCollectedRequests()

		if outputFilePath is not None and len(self.imgUrlList) > 0:
			with open(outputFilePath, "w") as outFile:
				json.dump(self.imgUrlList, outFile, indent=4)
				outFile.close()

		for imgUrl in self.imgUrlList:
			PrintUtil.printLog(imgUrl)

	def downloadImage(self, imgUrl: str, savePath: str):
		isSuccess = False

		requests_cookies = {}
		cookies = self.browser.getWebDriver().get_cookies()
		for cookie in cookies:
			requests_cookies[cookie["name"]] = cookie["value"]

		response = requests.get(imgUrl, cookies=requests_cookies, stream=True)
		if response.status_code < 300:
			with open(savePath, "wb") as outFile:
				response.raw.decode_content = True
				shutil.copyfileobj(response.raw, outFile)
				outFile.close()
				isSuccess = True
				PrintUtil.printLog("Image downloaded successfully : " + savePath)
		else:
			self.browser.goToNewTab(imgUrl)
			imgElementList = self.browser.waitUntil("img", 20)
			if len(imgElementList) > 0:
				self.saveScreenshot(imgElementList[0], savePath)
				PrintUtil.printLog("downloadImage : " + savePath)
			else:
				PrintUtil.printLog("Failed to download file : code=" + str(response.status_code) + ", " + response.reason)
			self.browser.closeTab()

		return isSuccess

	def saveScreenshot(self, element: WebElement, savePath: str):
		if self.browser.saveElementPNGScreenshot(element, savePath):
			PrintUtil.printLog("Image saved successfully : " + savePath)
		else:
			PrintUtil.printLog("Unable to save image : " + savePath)