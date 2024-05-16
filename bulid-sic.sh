#!/bin/bash

source bin/activate
pyinstaller --onedir --clean -y --collect-datas=fake_useragent src/sic.py
./dist/sic/sic -h
deactivate