* Dev Stacks
1. argparse
- CLI 인터페이스 argument 유틸 적용
- argument 입력 유효성 검증 및 도움말 기능 적용
- 상황별 크롤링을 위한 옵션화
2. seleniumwire
- selenium 기반의 네트워크 패킷 수집 라이브러리
- 페이지 내에서 최초 로드된 HTML DOM 이외에 동적으로 생성되어 접근 불가한 미디어를 직접 URL로 접근
3. selenium screenshot 함수
- URL로 직접 접근이 불가한 이미지의 경우 해당 DOM 요소에 대한 스크린샷을 추출, png 이미지로 저장
4. pyinstaller
- 파이썬 스크립트를 실행파일로 빌드해주는 라이브러리
- 빌드 후 파이썬 가상환경에서 벗어나도 라이브러리 접근 가능
5. HTTPS 사이트들의 SSL 인증 오류 및 기타 보안 관련 이슈를 피하기 위한 처절한 분투
- selenium Chome 브라우저에 --ignore-certificate-error, --ignore-ssl-errors 적용
- 이외 수집 및 처리 불가한 URL 및 미디어에 대한 상황별 예외처리 구현
- User-Agent 헤더 디폴트 적용 (user-agent 옵션 적용)
6. filetype
- 웹 문서 및 데이터의 MIME 타입 및 파일 유형을 판단하는 라이브러리
- REST API를 통해 다운받은 미디어 바이너리를 분석하여 해당 데이터의 이미지 여부 및 이미지에 대한 확장자 판별

* Usage
- CLI 도움말 참조 (sic --help 또는 sic -h)