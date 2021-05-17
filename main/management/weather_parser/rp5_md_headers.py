def get_header(phpsessid, browser):
    rp5 = {
        'Chrome': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '99',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={phpsessid}; extreme_open=false; tab_wug=1; tab_metar=1; i=76755%7C79514%7C35519'
                      f'%7C79520%7C9228; iru=76755%7C79514%7C35519%7C79520%7C9228; ru=%D0%A2%D1%83%7C%D0%A3%D1%80%D0%B0'
                      f'%D0%BB%D0%BE%D0%B2%D0%BA%D0%B0%7C%D0%A3%D1%88%D0%B0%D0%BA%D0%BE%D0%B2%D0%BE%7C%D0%A7%D0%B0%D0'
                      f'%B3%D0%BE%D1%8F%D0%BD%7C%D0%A8%D0%B8%D0%BC%D0%B0%D0%BD%D0%BE%D0%B2%D1%81%D0%BA; '
                      f'last_visited_page=http%3A%2F%2Frp5.md%2F%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%A8%D0'
                      f'%B8%D0%BC%D0%B0%D0%BD%D0%BE%D0%B2%D1%81%D0%BA%D0%B5; tab_synop=2; format=csv; f_enc=utf; '
                      f'lang=ru',
            'Host': 'rp5.md',
            'Origin': 'https://rp5.md',
            'Referer': 'https://rp5.md/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/90.0.4430.212 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        },
        'Firefox': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Content-Length': '108',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'tab_synop=2; __utma=176139873.1504441056.1621024648.1621024648.1621191032.2; '
                      f'__utmz=176139873.1621024648.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); cto_bundle='
                      f'ZzKsdl9lZEFyNlVtQmhuQk84QXNmdHliRXVvcVEzTml3QXpxaE5WeVB0dDJMcFp4TmZzU1ZmTlhIcEpIWiUyQmRmaiUy'
                      f'QmVVUnF3RWEyMnNuSHRzTnF1NmhGekV4Y3B3R2FEMjRwNUIybFlFNXFuQU02NWxiNm5mSXhXNVZ2cUJmUjVVQ1VjT1h'
                      f'XajBJWXBYRXBEUzRydloxNW55R2lRJTNEJTNE; PHPSESSID={phpsessid}; format=xls; f_enc=ansi; '
                      f'__utmb=176139873.1.10.1621191032; __utmc=176139873; __utmt=1; located=1; lang=ru',
            'Host': 'rp5.md',
            'Origin': 'https://rp5.md',
            'Referer': 'https://rp5.md/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'X-Requested-With': 'XMLHttpRequest'
        },
        'Opera': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '99',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={phpsessid}; __utma=176139873.33261936.1621191456.1621191456.1621191456.1; '
                      f'__utmc=176139873; __utmz=176139873.1621191456.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd='
                      f'(none); __utmt=1; __utmb=176139873.1.10.1621191456; located=1; lang=ru; tab_synop=2; '
                      f'format=csv; f_enc=utf',
            'Host': 'rp5.md',
            'Origin': 'https://rp5.md',
            'Referer': 'https://rp5.md/',
            'sec-ch-ua': '"Chromium";v="90", "Opera";v="76", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/90.0.4430.93 Safari/537.36 OPR/76.0.4017.123 (Edition Yx)',
            'X-Requested-With': 'XMLHttpRequest'
        },
        'InternetExplorer': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU',
            'Cache-Control': 'no-cache',
            'Connection': 'Keep-Alive',
            'Content-Length': '99',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={phpsessid}; tab_synop=2; format=csv; f_enc=utf; __utma=176139873.190604176.1621191767.1621191767.1621191767.1; __utmb=176139873.1.10.1621191767; __utmc=176139873; __utmz=176139873.1621191767.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; located=1; lang=ru',
            'Host': 'rp5.md',
            'Referer': 'https://rp5.md/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'X-Requested-With': 'XMLHttpRequest'
        },
        'Edge': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '99',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={phpsessid}; __utma=176139873.1653315065.1621192064.1621192064.1621192064.1; '
                      f'__utmc=176139873; __utmz=176139873.1621192064.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd='
                      f'(none); __utmt=1; __utmb=176139873.1.10.1621192064; located=1; cto_bundle=hLaULV9ONHpCS2xs'
                      f'Qk5OJTJGV2NlbkFUZWR4JTJCQkYxbk5ZeDZjNW9vb3Vjc1U2WWlpTWZlbFhTJTJCUVEySGI3Z2k0WTBmZUNQMjclMk'
                      f'JrWm9raFhIMkJhb0NEYkdSdm9DUEF4NFJpc1dXZEw0UTA3YW9yb0Z3JTNE; lang=ru; tab_synop=2; format=csv; '
                      f'f_enc=utf',
            'Host': 'rp5.md',
            'Origin': 'https://rp5.md',
            'Referer': 'https://rp5.md/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.62',
            'X-Requested-With': 'XMLHttpRequest'
        },
        'Yandex': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '99',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={phpsessid}; __utma=176139873.1612331330.1621192377.1621192377.1621192377.1; '
                      f'__utmc=176139873; __utmz=176139873.1621192377.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd='
                      f'(none); __utmt=1; __utmb=176139873.1.10.1621192377; located=1; lang=ru; tab_synop=2; '
                      f'format=csv; f_enc=utf',
            'Host': 'rp5.md',
            'Origin': 'https://rp5.md',
            'Referer': 'https://rp5.md/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Yandex";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/90.0.4430.41 YaBrowser/21.5.0.582 Yowser/2.5 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
    }
    return rp5[browser]
