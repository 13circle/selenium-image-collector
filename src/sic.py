import argparse

from util.PrintUtil import PrintUtil
from util.CLIHandler import CLIHandler
from crawler.BrowserManager import BrowserManager
from crawler.ImageScraper import ImageScraper

def main():
	cliHander = CLIHandler(argparse.ArgumentParser())
	cliHander.parseArgs()

	PrintUtil.isPrintable = not bool(cliHander.getArg("silent"))

	browserManager = BrowserManager(cliHander.getArg("headless"), cliHander.getArg("wired"))
	imageScraper = ImageScraper(browserManager)

	url = cliHander.getArg("url")
	downPath = cliHander.getArg("DownloadPath")
	outputFilePath = cliHander.getArg("OutputFilePath")
	imageScraper.scrape(url, downPath, outputFilePath)

	browserManager.exitBrowser()

main()