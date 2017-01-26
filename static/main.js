/**
 * AUTHOR:  Daniel Welsh, Dalia Al-Shahrabi
 * DESC:    Map origin names to actual names and links.
 * DATE:    26/01/2017
 */

var origin_map =
    {
        'bbc-news': {
            "name": "BBC News",
            "link": "http://www.bbc.co.uk/news"
        },
        'the-huffington-post': {
            "name": 'The Huffington Post',
            "link": "http://www.huffingtonpost.co.uk"
        },
        'cnn': {
            "name": 'CNN',
            "link": "http://edition.cnn.com"
        },
        'daily-mail': {
            "name": "Daily Mail",
            "link": "http://www.dailymail.co.uk/"
        },
        'national-geographic': {
            "name": "National Geographic",
            "link": "http://www.nationalgeographic.com"
        },
        'independent': {
            "name": "The Independent",
            "link": "http://www.independent.co.uk"
        },
        'the-guardian-uk': {
            "name": "The Guardian",
            "link": "https://www.theguardian.com/uk"
        },
        'the-new-york-times': {
            "name": "The New York Times",
            "link": "https://www.nytimes.com"
        },
        'the-telegraph': {
            "name": "The Telegraph",
            "link": "http://www.telegraph.co.uk"
        },
        'the-economist': {
            "name": "The Economist",
            "link": "http://www.economist.com"
        }
    };

$('.origin').each(function (ix) {

    var origin_inf = origin_map[$(this).find('a').text()];

    $(this).find('a').text(origin_inf['name']);
    $(this).find('a').attr('href', origin_inf['link']);
});