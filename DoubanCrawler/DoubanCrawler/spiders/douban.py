import scrapy
from scrapy import Request, Selector

import json
from ..items import DoubancrawlerItem, DoubanCommentItem


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    movieUrl = 'https://movie.douban.com/subject/{id}/'
    commentUrl = 'https://movie.douban.com/subject/{id}/comments?start=0&limit=20&status=P&sort=new_score'
    start_urls = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=1,10&tags=%E7%94%B5%E5%BD%B1&start={page}'

    def start_requests(self):
        for i in range(25, 30):
            yield Request(self.start_urls.format(page=i*20), callback=self.parse)

    def parse(self, response):
        moviesData = json.loads(response.text)
        moviesList = moviesData.get('data')
        if moviesList:
            for movie in moviesList:
                movieId = movie.get('id')
                title = movie.get('title')
                directors = movie.get('directors')
                casts = movie.get('casts')
                cover = movie.get('cover')
                rate = movie.get('rate')
                star = movie.get('star')
                url = movie.get('url')
                if movieId and title and directors and casts and cover and rate and star and url:
                    movie_map = {
                        'movieId': int(movieId), 'title': title,  'directors': directors,
                        'casts': casts, 'rate': float(rate),  'cover': cover
                    }
                    yield Request(self.movieUrl.format(id=movieId), callback=self.parse_film, meta={'movie': movie_map})

    def parse_film(self, response):
        selector = Selector(response)

        types = selector.xpath('//*[@property="v:genre"]/text()').extract()
        try:
            year = selector.xpath(
                '//*[@id="content"]/h1/span[2]/text()').extract()[0][1:5]
            duration = selector.xpath(
                '//span[@property="v:runtime"]/text()').extract()[0]
            rating_num = selector.xpath(
                '//span[@property="v:votes"]/text()').extract()[0]
            region = selector.xpath(
                '//*[@id="info"]').re('制片国家/地区:</span>\s(.*)<br>')[0]
        except IndexError:
            duration = 0
            year = None
            rating_num = 0
            region = None
        if duration and year and rating_num and region:
            movie_map = response.meta.get('movie')
            movieId = movie_map['movieId']
            movie_map['year'] = year
            movie_map['duration'] = duration
            movie_map['rating_num'] = rating_num
            movie_map['region'] = region
            movie_map['types'] = types
            movie_item = DoubancrawlerItem()
            for key, value in movie_map.items():
                if key == 'casts':
                    s = '/'
                    value = s.join(value)
                if key == 'types':
                    s = '/'
                    value = s.join(value)
                if key == 'directors':
                    if len(value) > 1:
                        value = '|'.join(value)
                    else:
                        value = value[0]
                movie_item[key] = value
            yield movie_item
            yield Request(self.commentUrl.format(id=movieId), callback=self.parse_comment, meta={'movieId': movieId})

    def parse_comment(self, response):
        selector = Selector(response)
        movie = response.meta.get('movieId')
        username = selector.xpath('//*[@id="comments"]//h3/span[2]/a/text()')
        avatar = selector.xpath('//*[@id="comments"]//a/img/@src')
        rate = selector.xpath('//*[@id="comments"]//h3/span[2]/span[2]/@class')
        time = selector.xpath('//*[@id="comments"]//h3/span[2]/span[3]/text()')
        content = selector.xpath('//*[@id="comments"]//p/span/text()')
        for i in range(len(rate)):
            rate[i] = rate[i].extract()
            if rate[i] == 'allstar50 rating':
                rate[i] = 5
            elif rate[i] == 'allstar40 rating':
                rate[i] = 4
            elif rate[i] == 'allstar30 rating':
                rate[i] = 3
            elif rate[i] == 'allstar20 rating':
                rate[i] = 2
            elif rate[i] == 'allstar10 rating':
                rate[i] = 1
            elif rate[i] == 'allstar00 rating':
                rate[i] = 0
            else:
                rate[i] = -1

        for i in range(len(username)):
            comments_item = DoubanCommentItem()
            comments_item['movie'] = movie
            try:
                comments_item['username'] = str(username[i].extract())
                comments_item['avatar'] = str(avatar[i].extract())
                comments_item['time'] = str(time[i].extract()).strip()
                comments_item['rate'] = rate[i]
                comments_item['content'] = str(content[i].extract()).strip()
            except IndexError:
                comments_item['time'] = '2000-01-01'
                comments_item['rate'] = -1
            yield comments_item
