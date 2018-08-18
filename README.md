# cspd-blotter
A simple Django project to scrape and collect [Colorado Springs Police Department blotter items](http://www.springsgov.com/units/police/policeblotter.asp).

## Running the project locally

- Install Python 3.x and [pipenv](https://docs.pipenv.org/) if you haven't already.
- I'm using an environment variable for the Django secret key called ... `DJANGO_SECRET_KEY`.
- Clone or [download and unzip](https://github.com/cjwinchester/cspd-blotter/archive/master.zip) this repo
- `cd` into the directory
- `pipenv --three install`
- `pipenv shell`
- `python manage.py migrate`
- To run the management command that scrapes the website: `python manage.py scrape` (maybe [change the headers](https://github.com/cjwinchester/cspd-blotter/blob/master/blotter/management/commands/scrape.py#L15-L19) to reflect your information first?)