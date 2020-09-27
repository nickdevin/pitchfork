from pitchfork.items import PitchforkItem
from scrapy import Spider, Request
import re

class PitchforkSpider(Spider):
	name = 'pitchfork_spider'
	allowed_urls = ['https://www.pitchfork.com']
	start_urls = ['https://pitchfork.com/reviews/albums/']


	def parse(self, response):

		#get link to each review on a single page
		review_urls = response.xpath('//a[@class = "review__link"]/@href').extract()
		review_urls = ['https://www.pitchfork.com' + url for url in review_urls]
		for url in review_urls:
			yield Request(url = url, callback = self.parse_reviews_page)

		#total number of pages of reviews is not visible to user
		#if page number in URL exceeds last actual page of reviews, get 404 error and return True
		too_many_pages = bool(response.xpath('//div[@class = "error-page__heading"]/text()').extract_first())
		
		#proceed through pages of reviews until 404 error is reached
		try:
			page_number = int(re.findall('\d+', response.url)[0])
		except:
			page_number = 1

		if not too_many_pages:
			next_page = 'https://pitchfork.com/reviews/albums/?page=' + str(page_number + 1)
			yield Request(url = next_page, callback = self.parse)


	def parse_reviews_page(self, response):
		
		#get artist name
		artist = response.xpath('//ul[@class = "artist-links artist-list single-album-tombstone__artist-links"]//text()').extract_first()
		
		#get album title
		album = response.xpath('//h1[@class = "single-album-tombstone__review-title"]/text()').extract_first()
		
		#get record labels
		label = '|'.join(set(response.xpath('//ul[@class = "labels-list single-album-tombstone__meta-labels"]//text()').extract()))
		
		#get review date
		review_date = response.xpath('//time[@class = "pub-date"]/@datetime').extract_first()
		
		#get album release year
		#leave as strings for now as there are some unusual entries, e.g. '1981/2015' for an album that has been reissued
		year = response.xpath('//span[@class = "single-album-tombstone__meta-year"]/text()').extract()
		try:
			#if year is not blank, return it
			year = list(filter(lambda s: re.search('\d', s), year))[0]
		except:
			#otherwise impute with year from review_date
			year = review_date.split('-')[0]
		
		#get review score (out of 10.0)
		score = float(response.xpath('//span[@class = "score"]/text()').extract_first())
		
		#get name of author of review
		reviewer = response.xpath('//a[@class = "authors-detail__display-name"]/text()').extract_first()
		
		#get genres of album
		genre = '|'.join(response.xpath('//ul[@class = "genre-list genre-list--before"]//text()').extract())
		
		#get text of review
		#some reviews have unwanted text at the end, e.g. legal disclaimers, advertisements for other features on website
		#this unwanted text is removed
		review_text = response.xpath('//div[@class = "contents dropcap"]//text()').extract()
		strings_to_remove = ['Buy:', 'Pitchfork earns a commission', 'Catch up every Saturday']
		to_drop_strings = list(filter(lambda s: any([t in s for t in strings_to_remove]), review_text))
		try:
			review_end = to_drop_strings.index(False)
			review_text = review_text[review_end]
		except:
			pass
		review_text = ''.join(review_text)

		#does the album have the distinction 'best new music?'
		best_new_music = response.xpath('//p[@class = "bnm-txt"]//text()').extract_first() == 'Best new music'

		#does the album have the distinction 'best new reissue?'
		best_new_reissue = response.xpath('//p[@class = "bnm-txt"]//text()').extract_first() == 'Best new reissue'

		
		item = PitchforkItem()
		item['artist'] = artist
		item['album'] = album
		item['label'] = label
		item['year'] = year
		item['score'] = score
		item['reviewer'] = reviewer
		item['genre'] = genre
		item['review_text'] = review_text
		item['review_date'] = review_date
		item['best_new_music'] = best_new_music
		item['best_new_reissue'] = best_new_reissue

		yield item