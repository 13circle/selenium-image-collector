import selenium

from typing import List

from urllib.parse import urljoin
from seleniumwire import webdriver as seleniumwire_webdriver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, WebDriverException

from util.PrintUtil import PrintUtil

class BrowserManager:
	def __init__(self, isHeadless: bool, isWired: bool):
		defaultUserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

		self.isWired = isWired
		if self.isWired:
			self.options = seleniumwire_webdriver.ChromeOptions()
		else:
			self.options = webdriver.ChromeOptions()

		self.options.add_argument("--remote-debugging-pipe")
		self.options.add_argument("--start-maximized")
		self.options.add_argument("user-agent=" + defaultUserAgent)

		if isHeadless:
			self.options.add_argument("--headless=new")

		if self.isWired:
			self.options.add_argument("--ignore-certificate-errors")
			self.options.add_argument("--ignore-ssl-errors")
			self.driver = seleniumwire_webdriver.Chrome(options=self.options, seleniumwire_options={})
			WebDriverWait(self.driver, 20)
		else:
			self.driver = webdriver.Chrome(options=self.options)

		self.collectedRequests = list()

		PrintUtil.printLog("Chrome started")

	def getWebDriver(self) -> WebDriver:
		return self.driver

	def getCurrentLocation(self) -> str:
		return self.driver.current_url

	def goTo(self, url: str):
		self.driver.get(url)
		self.driver.implicitly_wait(30)
		if self.isWired:
			for request in self.driver.requests:
				if request.response:
					self.collectedRequests.append(request)
		PrintUtil.printLog("Goto : " + url)

	def goToNewTab(self, url: str):
		self.driver.switch_to.new_window("tab")
		self.goTo(url)

	def getCollectedRequests(self):
		if self.isWired:
			return self.collectedRequests
		return None

	def initCollectedRequests(self):
		if self.isWired:
			self.collectedRequests.clear()
			del self.driver.requests

	def waitUntil(self, cssSelector: str, timeout: float) -> List[WebElement]:
		try:
			return WebDriverWait(self.driver, timeout).until(
				EC.presence_of_all_elements_located(( By.CSS_SELECTOR, cssSelector ))
			)
		except TimeoutException:
			pass

		return list()

	def querySelectorAll(self, parentElement: EC.WebDriverOrWebElement, cssSelector: str) -> List[WebElement]:
		elements: List[WebElement] = None
		try:
			elements = parentElement.find_elements(By.CSS_SELECTOR, cssSelector)
		except NoSuchElementException:
			elements = list()
		return elements

	def forEachIframes(self, parentIframe: WebElement, iframeParamCallback: callable, extraParams: List[any] = []):
		iframes: List[WebElement] = None
		if parentIframe is None:
			iframes = self.querySelectorAll(self.driver, "iframe")
		else:
			iframes = self.querySelectorAll(parentIframe, "iframe")
		for index, iframe in enumerate(iframes):
			src = None
			try:
				src = iframe.get_attribute("src")
			except StaleElementReferenceException:
				pass

			if src is not None and type(src) is str:
				if not src.startswith("http") or src.startswith("/") and not src.startswith("//"):
					src = urljoin(self.driver.current_url, src)

				self.driver.switch_to.frame(index)

				params: list = [iframe]
				params.extend(extraParams)

				iframeParamCallback(*params)

				self.forEachIframes(iframe, iframeParamCallback, extraParams)
				self.driver.switch_to.parent_frame()
			else:
				PrintUtil.printLog("Excluded an iframe element : cannot retrieve 'src' attribute")

	def getAttribute(self, element: WebElement, attrName: str) -> str:
		try:
			return element.get_dom_attribute(attrName)
		except NoSuchElementException:
			pass
		except StaleElementReferenceException:
			pass
		return None

	def saveElementPNGScreenshot(self, element: WebElement, savePath: str) -> bool:
		if element is None:
			return False
		try:
			return element.screenshot(savePath)
		except WebDriverException:
			pass
		return False

	def closeTab(self):
		self.driver.close()

	def exitBrowser(self):
		self.driver.quit()