import scrapy

class DoubancrawlerItem(scrapy.Item):
    table = 'movie'
    movieId = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
    directors = scrapy.Field()
    casts = scrapy.Field()
    region = scrapy.Field()
    types = scrapy.Field()
    duration = scrapy.Field()
    rate = scrapy.Field()
    cover = scrapy.Field()
    star = scrapy.Field()
    rating_num = scrapy.Field()


class DoubanCommentItem(scrapy.Item):
    table = 'movie_comment'
    movie = scrapy.Field()
    username = scrapy.Field()
    avatar = scrapy.Field()
    rate = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()

