import argparse

from fake_useragent import UserAgent

from util.PrintUtil import PrintUtil
from util.CLIHandler import CLIHandler
from crawler.BrowserManager import BrowserManager
from crawler.ImageScraper import ImageScraper

def main() -> None:
	"""
	selenium-image-collector 메인 함수
	"""
	# CLI 매개변수 파싱
	cliHander = CLIHandler(argparse.ArgumentParser())
	cliHander.parseArgs()

	# 주요 매개변수 할당
	url: str = cliHander.getArg("url")							# 이미지를 가져올 URL
	silent: bool = cliHander.getArg("silent")					# 로그 출력 숨김 여부
	headless: bool = cliHander.getArg("headless")				# 셀레니움 크롬 브라우저 백그라운드 실행 여부
	wired: bool = cliHander.getArg("wired")						# selenium-wire HTTP request 캡쳐 수행 여부
	downPath: str = cliHander.getArg("DownloadPath")			# 이미지 저장 경로 (디렉터리)
	outputFilePath: str = cliHander.getArg("OutputFilePath")	# 이미지 URL 목록 저장 경로 (JSON 파일)
	cssSelector: str = cliHander.getArg("CSSSelector")			# 이미지 요소의 CSS Selector

	# 로그 출력 여부 설정
	PrintUtil.isPrintable = not silent

	# 셀레니움 크롬 브라우저 초기화 및 실행
	browserManager = BrowserManager(headless, wired, PrintUtil.isPrintable)

	# 이미지 웹 스크래퍼 초기화
	imageScraper = ImageScraper(browserManager)

	# 이미지 스크래핑 시작
	imageScraper.scrape(url, cssSelector, downPath, outputFilePath)

	# 셀레니움 크롬 브라우저 종료
	browserManager.exitBrowser()

if __name__ == '__main__':
	main()