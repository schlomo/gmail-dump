# gmail-dump
Dump all Email from GMail via API (no IMAP). Very useful if your GMail administrator disabled IMAP for "security" reasons.

## Setup & Run

1. Clone this code, I tested it with Python 3
1. Go to [Google API Developer Console](https://console.developers.google.com/apis/credentials) and create a set of client credentials enabled for the [GMail API](https://developers.google.com/gmail/api/)
1. Download the credentials JSON and save as `client_secrets.json`
1. Install [Virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
1. Create virtualenv with `virtualenv -p python3 venv`
1. Activate virtualenv with `source venv/bin/activate`
1. Install [Google API Client Libraries](https://developers.google.com/api-client-library/python/) with `pip install google-api-python-client`
1. Run code with python gmail-dump.py.

On first run your browser should open up and ask for your Google Authorization. It will then download all Email into the maildir folder mail.

You can use [mutt](http://www.mutt.org/) like `mutt -f mail` to browse through the downloaded email.

## Caveats

* I use the message ID as file name for the mail files, it seems to work so far. Please report if you have a problem with that.
* This script just dumps the bare email and completely ignores any labels. Pull requests are welcome.

