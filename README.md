# spyder - A simple instagram comment scraper

This script scrapes instagram comment from a post which has a given id. For now, it only scrapes authors of comments and saves them in a file, one per line.

I wrote this script in an hurry for the sake of learning, so **this is not intended for production** and it could be very buggy. I'm not planning to return to this code soon, so bug fixing could require some time. Feel free to flag bugs and improvements opening an issue, I'll check them in my spare time.

If you use this, the responsibilty is all yours.

## How it works

Spyder will login to Instagram with specified user and drive Firefox browser to the intended post of the intended author. It will scrape the authors of comments under the post. Once it has finished, it will dump the authors in a text file.

The number of authors scraped depends on `MAX_LOAD_MORE_COMMENTS_CLICKS` param, which is the maximum number of times Spyder will click the "load more comments" button.

To avoid to piss off Instagram, between every step Spyder will wait a random amount of time between `WAIT_TIME_MIN` and `WAIT_TIME_MAX`.

Spyder uses some hardcoded xpaths and css class to locate elements in Instagram web pages. If Instagram changes some features of it's web pages, these elements will become quickly obsolete. So if the script is not running well you probably want to ckeck if these elements are up to date.

## Dependencies

This script requires `geckodriver` and a compatible Firefox version installed on your system. It also requires Selenium python api installed.

## Launch

Before you launch the script, you must set an environment variable called `GECKODRIVER_PATH` with the full path of geckodriver
`export GECKODRIVER_PATH=/full/path/to/geckodriver`.

To launch the script (in a Linux environment):

`$ ./main.py userScraper userScraped postId`

## Command line params

+ `userScraper`: Spyder will use this user to login, asking you for a password at runtime
+ `userScraped`: Owner of the post that will be scraped
+ `postId`: The id of the post, it is in the URL when you open an Instagram post from desktop. For example, in the URL `https://www.instagram.com/p/CMNb43kpenU/` the postId is `CMNb43kpenU`
