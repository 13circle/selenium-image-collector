import os
import requests
import shutil
import filetype
import re
import json

from typing import List

from urllib.parse import urlparse, urljoin

from .BrowserManager import BrowserManager, EC, WebElement, Request
from util.PrintUtil import PrintUtil

class ImageScraper:
	"""
	셀레니움 기반 브라우저 내 이미지 스크래퍼
	"""
	def __init__(self, browser: BrowserManager):
		"""
		:param browser: 셀레니움 브라우저 관리자 클래스
		"""
		self.browser: BrowserManager = browser
		self.imgUrlList: List[str] = list()
		self.imgSerial: int = 0

	def scrapeImageOfCurrentPage(self, parentElement: EC.WebDriverOrWebElement, cssSelector: str, downloadRootPath: str) -> None:
		"""
		해당 URL의 웹페이지 내 모든 이미지들을 스크래핑 및 다운로드하는 핵심 로직 (iframe 전수 탐색 시 callback으로 사용됨)

		:param parentElement: 탐색의 기준이 되는 부모 웹페이지 요소 (iframe 전수 탐색 시 iframe 요소가 여기에 해당함)
		:param cssSelector: 이미지 요소의 CSS Selector (미지정 시 None)
		:param downloadRootPath: 이미지 다운로드 디렉터리 경로
		"""
		elements: List[WebElement] = None
		if cssSelector is None:
			elements = self.browser.querySelectorAll("img", parentElement, 30)
			elements.extend(self.browser.querySelectorAll("picture > source", parentElement, 30))
		else:
			elements = self.browser.querySelectorAll(cssSelector, parentElement, 30)

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

	def scrape(self, url: str, cssSelector: str, downloadRootPath: str, outputFilePath: str) -> None:
		"""
		해당 URL 주소의 웹페이지 내에세 이미지 스크래핑을 수행하는 트리거 또는 진입점

		:param url: 이동 및 이미지 스크래핑을 수행할 웹페이지의 URL 주소
		:param cssSelector: 이미지 요소의 CSS Selector (미지정 시 None)
		:param downloadRootPath: 스크래핑한 이미지를 저장할 디렉터리 경로
		:param outputFilePath: 스크래핑한 이미지의 URL을 저장할 JSON 파일 경로
		"""
		self.browser.goTo(url)

		if self.browser.isWired:
			collectedRequests = self.browser.getCollectedRequests()

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
		else:
			self.scrapeImageOfCurrentPage(self.browser.driver, cssSelector, downloadRootPath)
			self.browser.forEachIframes(None, self.scrapeImageOfCurrentPage, [cssSelector, downloadRootPath])

		if outputFilePath is not None and len(self.imgUrlList) > 0:
			with open(outputFilePath, "w") as outFile:
				json.dump(self.imgUrlList, outFile, indent=4)
				outFile.close()

		for imgUrl in self.imgUrlList:
			PrintUtil.printLog(imgUrl)

	def downloadImage(self, imgUrl: str, savePath: str) -> bool:
		"""
		해당 URL에 대한 이미지 다운로드 및 저장

		:param imgUrl: 다운받을 이미지 URL
		:param savePath: 다운받은 이미지 저장 경로
		"""
		isSuccess = False

		requests_cookies = {}
		cookies = self.browser.driver.get_cookies()
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
			imgElementList = self.browser.querySelectorAll("img", 20)
			if len(imgElementList) > 0:
				self.saveScreenshot(imgElementList[0], savePath)
				PrintUtil.printLog("downloadImage : " + savePath)
			else:
				PrintUtil.printLog("Failed to download file : code=" + str(response.status_code) + ", " + response.reason)
			self.browser.closeTab()

		return isSuccess

	def saveScreenshot(self, element: WebElement, savePath: str) -> None:
		if self.browser.saveElementPNGScreenshot(element, savePath):
			PrintUtil.printLog("Image saved successfully : " + savePath)
		else:
			PrintUtil.printLog("Unable to save image : " + savePath)