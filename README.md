## Poll App in Pyramid

### Getting started

```
git clone https://github.com/yeukhon/poll-app
virtualenv poll-app-env
source poll-app-env/bin/activate
cd poll-app
pip install -r requirements.txt
python setup.py develop
nosetests .
```

Tests should now passed! Copy and edit production.ini (or whichever
INI file you use) with the right database configuration. Then
create the schema and launch the server:

```
cp configurations/production.ini.example production.ini
<edit INI file>
initialize_pollapp_db production.ini
gunicorn --paste production.ini -w 2 -t 3600
```

Next, let's make a couple requests.

```python
import requests
import json

url1 = "http://localhost:6543/polls"
headers = {"content-type": "application/json"}

data1 = {"name": "Hello World", "options": "yes,no,maybe"}

r1 = requests.post(url1, data=json.dumps(data1), headers=headers)

# <Response [201]>
# r.json()
# {u'id': u'0bb469ba-446f-11e4-9ffa-080027880ca6'}

url2 = "/".join(url1, str(r.json()["id"]), "vote")
data2 = {"option": 0, "ip": "127.0.0.1"}
# Bob voted option 1 for 4 times!
for i in range(0, 4):
    r2 = requests.post(url2, data=json.dumps(data2), headers=headers)
    # <Response [201]>
    # r2.json()
    # {u'status': u'Ok'}


# Alice, Eve also voted
data3 = {"option": 0, "ip": "127.0.0.2"}
r2 = requests.post(url2, data=json.dumps(data3), headers=headers)
data3 = {"option": 0, "ip": "127.0.0.3"}
r2 = requests.post(url2, data=json.dumps(data3), headers=headers)

# Finally, John voted for option 1
data3 = {"option": 1, "ip": "127.0.0.5"}
r2 = requests.post(url2, data=json.dumps(data3), headers=headers)

url3 = "/".join([url1, str(r.json()["id"]), "results"])
r3 = requests.get(url3)
# <Response [200]>
# r3.json()
#[{u'votes': 6, u'unique_votes': 3, u'name': u'yes'},
# {u'votes': 1, u'unique_votes': 1, u'name': u'no'},
# {u'votes': 0, u'unique_votes': 0, u'name': u'maybe'}]

```

### Spambot stress test

You can use ``pollapp/scripts/spam.py`` to spam votes.

```
python spam.py --name="Yay or Nay or Maybe?" \
--options="Yay,Nay,Maybe" --config="0:5,1;1:0,2"

```

This command will:

* creates a new poll with the given options
* option 0 will get 5 duplicate votes, and 1 additional unique vote
(total of 6 votes and 2 unique votes)
* option 1 will get 0 duplicate votes and 2 additional unique vote
(total of 2 vote and 2 unique vote)
* option 3 will get 0 vote

The ``;`` separates the configuration among options.

The result from the server is also displayed:

```
Done!Let's test.
[ { u'name': u'Yay', u'unique_votes': 2, u'votes': 6},
  { u'name': u'Nay', u'unique_votes': 2, u'votes': 2},
  { u'name': u'Maybe', u'unique_votes': 0, u'votes': 0}]
```

You can play with the command line ``./pollapp/scripts/spam.py --help``.
By default, without any specific configuration, 100 votes will
be casted across three options [dup/unique] (option 0 gets 88/10),
option 1 gets 0/2 and option 3 gets 0/0)

I've tested my raw SQL up to 46,000 duplicates (roughly 6 minutes
of insertions....).

### Specifications:

``POST /polls``: Create a new poll.
Returns a JSON object with one key `id`, the ID of the new poll.
POST arguments are:

* name: name of poll to create
* options: comma separated list of poll options

``POST /polls/<id>/vote``: Vote on a poll. POST arguments are:
* option: Zero-based index of option to vote on
* ip: IP address of voter. Use this argument instead of actual
remote IP to make testing easier

``GET /polls/<id>/results:`` Get poll results. Returns a JSON list
of objects, each with the keys:
* name: Name of the option
* votes: Raw number of votes on the option
* unique_votes: Unique number of IP addresses that voted on the option

Poll list and choice list views are not necessary, but may help with testing.


### Database models

* Polls:

    * id (PK)
    * question
    * created_on

* PullOptions

    * id (PK)
    * poll_id
    * poll (reference object, lazy)
    * text

* PollResponses

    * id (PK)
    * ip_address
    * voted_on
    * choice_id
    * choice (reference obejct, lazy)

### Play on SQLFiddle

I spent a great deal of time on SQLFiddle to work on
the SQL statement (yep, I suck at writing SQL queries!).

[SQLFiddle](http://sqlfiddle.com/#!15/ec5c9/41/0)
