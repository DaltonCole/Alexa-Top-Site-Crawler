mport scrapy
from tldextract import extract
import os
from urllib.request import urlopen
from urllib.parse import urlparse

# scrapy runspider driver.py

class MySpider(scrapy.Spider):
	name = 'javascriptScraper'
	allowed_domains = []#get_domain_names()
	start_urls = []#get_urls()
	
	# Dictionary of javascript scripts
	javascripts = {}
	max_samples = 1000

	def __init__(self, category='', **kwargs):
		self.start_urls = self.get_start_urls(kwargs['file'])
		self.allowed_domains = self.get_allowed_domains(kwargs['file'])
		self.file_to_open = kwargs['file']
		super().__init__(**kwargs)

	def parse(self, response):
		domain = extract(response.url).domain

		parsed_url = urlparse(response.url)
		url_without_path = parsed_url.scheme + '://' + parsed_url.netloc

		good_domain = False
		for url in self.allowed_domains:
			if domain in url:
				good_domain = True
				break
		if good_domain == False:
			return

		if domain not in self.javascripts:
			self.javascripts[domain] = set()

		for script in response.xpath('//script/text()').getall():
			if len(self.javascripts[domain]) < self.max_samples:
				self.javascripts[domain].add(script)

		for src in response.xpath('//script/@src').getall():
			if len(self.javascripts[domain]) < self.max_samples:
				potato = src

				if src.startswith('//'):
					src = 'http://' + src[2:]

				if src.startswith('/') or src.startswith('..'):
					src = url_without_path + '/' + src

				try:
					html = urlopen(src).read().decode('utf-8')
					self.javascripts[domain].add(html)
				except Exception as e:
					print(e)

		for href in response.xpath('//a/@href').getall():
			if len(self.javascripts[domain]) < self.max_samples:
				yield scrapy.Request(response.urljoin(href), self.parse)

	def closed(self, reason):
		# For each website
		for site, scripts in self.javascripts.items():
			site = 'scripts/{}'.format(site)
			# Make directory if it does not already exist
			if not os.path.exists(site):
				os.makedirs(site)

			# For each script
			for index, script in enumerate(scripts):
				with open('{}/{}.js'.format(site, index), 'w') as f:
					f.write(script)
		
		# Delete file that was used
		try:
			os.remove(self.file_to_open)
		except OSError:
			pass

		print('FINISHED {}'.format(self.allowed_domains))

	def get_allowed_domains(self, file):
		urls = []
		with open(file, 'r') as f:
			for line in f:
				urls.append(line.strip())
		return urls

	def get_start_urls(self, file):
		urls = []
		with open(file, 'r') as f:
			for line in f:
				urls.append('http://www.' + line.strip())
		return urls
