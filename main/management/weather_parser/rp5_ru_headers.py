def get_header(phpsessid, browser) -> dict:
    rp5 = {
        'Chrome': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '99',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={phpsessid}; __utmc=66441069; located=1; extreme_open=false; format=xls; f_enc=ansi;'
                      f' _ga=GA1.2.1087305705.1637171587; tab_synop=3; __utma=66441069.1087305705.1637171587.16414678'
                      f'78.1641479713.10; __utmz=66441069.1641479713.10.3.utmcsr=yandex|utmccn=(organic)|utmcmd=organ'
                      f'ic; __utmt=1; is_adblock=1; i=3609%7C3609%7C3609; iru=3609%7C3609%7C3609; ru=%D0%99%D0%BE%D1%'
                      f'88%D0%BA%D0%B0%D1%80-%D0%9E%D0%BB%D0%B0%7C%D0%99%D0%BE%D1%88%D0%BA%D0%B0%D1%80-%D0%9E%D0%BB%D'
                      f'0%B0%7C%D0%99%D0%BE%D1%88%D0%BA%D0%B0%D1%80-%D0%9E%D0%BB%D0%B0; last_visited_page=http%3A%2F%2'
                      f'Frp5.ru%2F%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%99%D0%BE%D1%88%D0%BA%D0%B0%D1%80-%D'
                      f'0%9E%D0%BB%D0%B5; __utmb=66441069.4.10.1641479713; lang=ru; cto_bundle=Onyb519SaDc3NVJqUW9hcU'
                      f'00dHNDcEsyMTZwZmtMRzJ6SU9YZ1RCbUdyVyUyQnRmRHJuakxHZDk1V1AlMkJNOWREbTFqRnVaakdBT21Jbml5ZXNKa3R'
                      f'MTHpwRSUyRjd6d2RrVXJlVWNpdyUyRlk3UGVvRGJYV0FQVmV3WFJRVWhweUZCd2hjN3AxWXFvbGFZeU45MERxYiUyQmdU'
                      f'cnJsUmN2WlJRJTNEJTNE',
            'Host': 'rp5.ru',
            'Origin': 'https://rp5.ru',
            'Referer': 'https://rp5.ru/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'Windows',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/96.0.4664.110 Safari/537.36X-Requested-With: XMLHttpRequest',
            'X-Requested-With': 'XMLHttpRequest'},
        'Firefox': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Content-Length': '157',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'tab_synop=2; __utma=66441069.787260057.1615713964.1618399838.1641480120.4; cto_bundle=TCQkIF9lZ'
                      f'EFyNlVtQmhuQk84QXNmdHliRXVnJTJGeUxBRDc3TVVVRjFTdHRiJTJCcyUyRkFyd1BUOTJPVVl3JTJGZ1ZtZXYlMkZNbTJL'
                      f'QlZxeXlGYW5qJTJCUDJPd2xBcjk4biUyQmY4d3hsRlF0ZzhZOU01RHBiOHJsQ1pPVWxwQkhMZDMlMkZJaUYwYTJpNEgxVVh'
                      f'nZnFNV3REU0s3ZlNzS0U5aHdUbUpnJTNEJTNE; extreme_open=false; __gads=ID=8c18f2d64afa91f2-22c846691'
                      f'5bb00f9:T=1618399837:RT=1618399837:S=ALNI_MY3hQkYRVTh3Y2OwwZGFs-dJxR9kA; tab_metar=1; is_adbloc'
                      f'k=0; PHPSESSID={phpsessid}; i=3609; iru=3609; ru=%D0%99%D0%BE%D1%88%D0%BA%D0%B0%D1%80-%D0%9E%D0'
                      f'%BB%D0%B0; last_visited_page=http%3A%2F%2Frp5.ru%2F%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_'
                      f'%D0%99%D0%BE%D1%88%D0%BA%D0%B0%D1%80-%D0%9E%D0%BB%D0%B5; __utmb=66441069.4.10.1641480120; __ut'
                      f'mc=66441069; __utmz=66441069.1641480120.4.1.utmcsr=yandex.ru|utmccn=(referral)|utmcmd=referral'
                      f'|utmcct=/; __utmt=1; format=csv; f_enc=utf; lang=ru',
            'Host': 'rp5.ru',
            'Origin': 'https://rp5.ru',
            'Referer': 'https://rp5.ru/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'X-Requested-With': 'XMLHttpRequest'
        },
        'Opera': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '98',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={phpsessid}; __utmc=66441069; extreme_open=false; __gads=ID=641633653496891c-2277e3e'
                      f'c16bb0088:T=1618400457:RT=1618400457:S=ALNI_MbOXRCZKZ-4xFvhddq-wLOB1LoVIA; located=1; __utma=66'
                      f'441069.2058564896.1618400458.1625578832.1641480511.5; __utmz=66441069.1641480511.5.1.utmcsr=(di'
                      f'rect)|utmccn=(direct)|utmcmd=(none); __utmt=1; __utmb=66441069.1.10.1641480511; lang=ru; tab_sy'
                      f'nop=2; format=csv; f_enc=utf',
            'Host': 'rp5.ru',
            'Origin': 'https://rp5.ru',
            'Referer': 'https://rp5.ru/',
            'sec-ch-ua': '"Chromium";v="96", "Opera";v="82", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.'
                          '0.4664.110 Safari/537.36 OPR/82.0.4227.43 (Edition Yx)',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'Edge': {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '98',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={phpsessid}; __utma=66441069.1737022037.1641481207.1641481207.1641481207.1; __utmc=66'
                      f'441069; __utmz=66441069.1641481207.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1;'
                      f' __utmb=66441069.1.10.1641481207; located=1; cto_bundle=92H8Ql9ONHpCS2xsQk5OJTJGV2NlbkFUZWR4JTJ'
                      f'CS0J2S0RPUVcxQm1xbFh6aEVhR1BvQ2FWdG4lMkJlaGt2aGF0QVJkTEdaV0x5OEg1NTVrJTJGSlk2TmtyMktES2psaUppbj'
                      f'hJU3pRNnRDeTZaU0I0djl0S0JUdG10QXFxRG5YSSUyRmwzUCUyQkt6bDhYQzJSVlhkYmtUMmJreGFsREZsc0VUSHclM0QlM'
                      f'0Q; lang=ru; tab_synop=2; format=csv; f_enc=utf',
            'Host': 'rp5.ru',
            'Origin': 'https://rp5.ru',
            'Referer': 'https://rp5.ru/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0'
                          '.4664.110 Safari/537.36 Edg/96.0.1054.62',
            'X-Requested-With': 'XMLHttpRequest',
        },
    }
    return rp5[browser]
