"""
BrowserManager v1.0.1

* Required libraries (with versions)
- selenium 4.19.0
- selenium-wire 5.1.0
- fake_useragent 1.5.1
"""

import selenium

from typing import List, Callable, Tuple, Any

from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, WebDriverException
from seleniumwire import webdriver as seleniumwire_webdriver
from seleniumwire.request import Request
from fake_useragent import UserAgent
from urllib.parse import urljoin

class BrowserManager:
	"""
	셀레니움 크롬 브라우저 관리자 (추후 모듈화를 위해 셀레니움 관련 로직은 최대한 여기에서만 수행)
	"""
	def __init__(self, isHeadless: bool, isWired: bool, verbose: bool = True):
		"""
		:param isHeadless: 백그라운드 실행 여부
		:param isWired: selenium-wire 실행 여부
		:param verbose: 콘솔창 로그 출력 여부
		"""
		self.isHeadless: bool = isHeadless
		self.isWired: bool = isWired
		self.verbose: bool = verbose
		self.collectedRequests: List[Request] = list()

		self.options: ChromiumOptions = None

		if self.isWired:
			self.options = seleniumwire_webdriver.ChromeOptions()
		else:
			self.options = webdriver.ChromeOptions()
		
		if self.isHeadless:
			self.options.add_argument("--headless=new")
			self.printLog("* Option : headless mode")

		self.options.add_argument("--remote-debugging-pipe")
		self.options.add_argument("--start-maximized")

		userAgent: str = UserAgent().random
		self.options.add_argument("user-agent=" + userAgent)
		self.printLog("* User-Agent : " + userAgent)

		#selenium-wire로 실행 시 SSL 이슈를 피하기 위한 처절한 분투의 결과물
		if self.isWired:
			self.options.add_argument("--ignore-certificate-errors")
			self.options.add_argument("--ignore-ssl-errors")
			self.driver = seleniumwire_webdriver.Chrome(options=self.options, seleniumwire_options={})
			self.printLog("* Option : use seleniumwire instead of selenium")
		else:
			self.driver = webdriver.Chrome(options=self.options)
			self.printLog("* Option : use selenium")

		WebDriverWait(self.driver, 20)

		self.printLog("Start Chrome")

	def printLog(self, log: str) -> None:
		"""
		로그 출력

		:param log: 로그 메시지
		"""
		if self.verbose:
			print(log)

	def getCurrentLocation(self) -> str:
		"""
		현재 브라우저의 주소 위치를 반환

		:return: 현재 URL
		"""
		return self.driver.current_url

	def goTo(self, url: str, timeout: float = 20) -> None:
		"""
		해당 URL로 이동 및 selenium-wire를 통한 request 수집

		:param url: 이동할 URL
		:param timeout: 전체 페이지 로드 최대 대기 시간
		"""
		self.driver.get(url)
		self.driver.implicitly_wait(timeout)
		if self.isWired:
			for request in self.driver.requests:
				if request.response:
					self.collectedRequests.append(request)
		self.printLog("Goto : " + url)

	def goToNewTab(self, url: str):
		"""
		새 탭에서 해당 URL로 이동

		:param url: 이동할 URL
		"""
		self.driver.switch_to.new_window("tab")
		self.goTo(url)

	def getCollectedRequests(self) -> List[Request]:
		"""
		selenium-wire를 통해 수집한 request 목록을 반환

		:return: 기 수집된 request 목록
		"""
		return self.collectedRequests

	def initCollectedRequests(self) -> None:
		"""
		selenium-wire request 목록 초기화
		"""
		if self.isWired:
			self.collectedRequests.clear()
			del self.driver.requests

	def waitUntil(self, cssSelector: str, timeout: float) -> List[WebElement]:
		"""
		현재 페이지 내 지정한 CSS Selector에 해당하는 요소들의 리스트를 대기 후 반환

		:param cssSelector: 웹페이지 내 요소를 지정할 CSS Selector
		:param timeout: 지정한 웹페이지 요소에 대한 최대 로드 대기 시간
		:return: 해당 CSS Selector에 대한 웹페이지 요소 리스트
		"""
		try:
			return WebDriverWait(self.driver, timeout).until(
				EC.presence_of_all_elements_located(( By.CSS_SELECTOR, cssSelector ))
			)
		except TimeoutException:
			pass

		return list()

	def querySelectorAll(self, cssSelector: str, parentElement: EC.WebDriverOrWebElement, timeout: float = 20) -> List[WebElement]:
		"""
		현재 페이지 내 지정한 부모 요소 내 CSS Selector에 해당하는 요소들의 리스트를 반환

		:param cssSelector: 웹페이지 내 요소를 지정할 CSS Selector
		:param parentElement: 탐색 기준 부모 요소 (최상위인 WebDriver도 가능)s
		:param timeout: 지정한 웹페이지 요소에 대한 최대 로드 대기 시간
		:return: 해당 CSS Selector에 대한 웹페이지 요소 리스트
		"""
		retList: List[WebElement] = None
		if type(parentElement) == WebElement:
			try:
				parentElement.find_elements(By.CSS_SELECTOR, cssSelector)
			except NoSuchElementException:
				retList = list()
		else:
			retList = self.waitUntil(cssSelector, timeout)
		return retList

	def forEachIframes(self, parentIframe: WebElement, iframeParamCallback: Callable[Tuple[WebElement, Any], None], extraParams: List[Any] = []) -> None:
		"""
		현재 페이지 내 iframe들을 재귀적으로 전수 탐색

		:param parentIframe: 탐색 기준 부모 iframe (최상위 페이지에 대해서는 None)
		:param iframeParamCallback: 각 iframe에 대한 callback (iframe을 기본 인자로 둠)
		:param extraParams: callback에 대한 추가 파라미터
		"""
		iframes: List[WebElement] = None
		if parentIframe is None:
			iframes = self.querySelectorAll("iframe", self.driver)
		else:
			iframes = self.querySelectorAll("iframe", parentIframe)
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
				self.printLog("Excluded an iframe element : cannot retrieve 'src' attribute")

	def getAttribute(self, element: WebElement, attrName: str) -> str:
		"""
		해당 웹페이지 요소에 대한 HTML 속성값을 반환

		:param element: 웹페이지 요소
		:param attrName: 값을 가져올 속성명
		:return: 해당 속성값
		"""
		try:
			return element.get_dom_attribute(attrName)
		except NoSuchElementException:
			pass
		except StaleElementReferenceException:
			pass
		return None

	def saveElementPNGScreenshot(self, element: WebElement, savePath: str) -> bool:
		"""
		해당 웹페이지 요소의 브라우저 내 모습을 캡쳐하여 PNG 이미지 파일로 저장

		:param element: 캡쳐할 웹페이지 요소
		:param savePath: 캡쳐 이미지 저장 경로
		:return: 캡쳐 및 저장 성공 여부
		"""
		if element is None:
			return False
		try:
			return element.screenshot(savePath)
		except WebDriverException:
			pass
		return False

	def closeTab(self):
		"""
		goToNewTab으로 생성한 브라우저 탭 종료
		"""
		self.driver.close()

	def exitBrowser(self):
		"""
		셀레니움 크롬 브라우저 종료
		"""
		self.driver.quit()