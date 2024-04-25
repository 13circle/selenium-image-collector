import argparse

from util.PrintUtil import PrintUtil
from util.CLIHandler import CLIHandler
from crawler.BrowserManager import BrowserManager
from crawler.ImageScraper import ImageScraper

def main():
	"""
	selenium-image-collector 메인 함수
	"""
	# CLI 매개변수 파싱
	cliHander = CLIHandler(argparse.ArgumentParser())
	cliHander.parseArgs()

	# 로그 출력 여부 설정
	PrintUtil.isPrintable = not bool(cliHander.getArg("silent"))

	# 셀레니움 크롬 브라우저 초기화 및 실행
	browserManager = BrowserManager(cliHander.getArg("headless"), cliHander.getArg("wired"))

	# 이미지 웹 스크래퍼 초기화
	imageScraper = ImageScraper(browserManager)

	# 주요 매개변수 할당
	url = cliHander.getArg("url")						# 이미지를 가져올 URL
	downPath = cliHander.getArg("DownloadPath")			# 이미지 저장 경로 (디렉터리)
	outputFilePath = cliHander.getArg("OutputFilePath")	# 이미지 URL 목록 저장 경로 (JSON 파일)

	# 이미지 스크래핑 시작
	imageScraper.scrape(url, downPath, outputFilePath)

	# 셀레니움 크롬 브라우저 종료
	browserManager.exitBrowser()

main()