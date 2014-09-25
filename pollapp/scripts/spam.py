#!/usr/bin/env python
# Use this script to spam and get profit!
import argparse
import json
import pprint
import random
import sys

import requests

DEFAULT_HOST = "http://localhost:6543"
HEADERS = {"Content-Type": "application/json"}
DEFAULT_QUESTION = "Yay or Nay?"
DEFAULT_OPTIONS = "Yay,Nay,Maybe"


def random_ip():
    return "{}.{}.{}.{}".format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def make_url(host, parts):
    host = host.strip().strip("/")
    return "/".join([host] + parts)

def create_poll(name, options, host=None):
    url = make_url(host, ["polls"])
    data = {"name": name, "options": options}
    r = requests.post(url, data=json.dumps(data),
        headers=HEADERS)
    assert r.status_code == 201
    return r.json()["id"]

def create_vote(poll_id, option, ip_address, host=None):
    url = make_url(host, ["polls", poll_id, "vote"])
    data = {"option": option, "ip": ip_address}
    r = requests.post(url, data=json.dumps(data),
        headers=HEADERS)
    assert r.status_code == 201

def get_result(poll_id, host=None):
    url = make_url(host, ["polls", poll_id, "results"])
    r = requests.get(url)
    assert r.status_code == 200
    return r

def spam(name, options, total=100, host=None, config=None):
    poll_id = create_poll(name, options, host=host)
    groups = {}
    if config:
        # We expect to receive index:dup,uniq;index2:dup such form
        splited = config.split(";")
        for group in splited:
            index, nums = group.split(":")
            if "," not in nums:
                dup_range, unique_range = int(nums.split(",")[0]), 0
            else:
                dup_range, unique_range = nums.split(",")
            groups[index] = {"dup": int(dup_range),
                             "unique": int(unique_range)}
    else:
        # Otherwise, we will assume the first option gets
        # most of the votes with most duplicates
        # We will do 88 duplicates for option 0
        # with 10 more unique visitor for option 0.
        # That's 98 raw votes and 11 unique votes.
        # Remaining 2 will go to option 1 (all distinct)
        # and option 2 will have zero.
        groups = {0: {"dup": 88, "unique": 10},
                  1: {"dup": 0, "unique": 2},
                  2: {"dup": 0, "unique": 0}}

    for option, group in groups.items():
        if group["dup"] > 0:
            ip_address = random_ip()
            for i in xrange(0, group["dup"]):
                print("Spamming {} with duplicate #{}".format(option, i))
                create_vote(poll_id, option, ip_address, host=host)
                
        if group["unique"] > 0:
            for i in xrange(0, group["unique"]):
                ip_address = random_ip()
                print("Spamming {} with unique visitor #{}".format(option, i))
                create_vote(poll_id, option, ip_address, host=host)

    print("\nDone!Let's test.")
    pprint.pprint(
        get_result(poll_id, host=host).json(),
        indent=2
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spam votes")
    parser.add_argument("--host", action="store",
                       nargs='?', default=DEFAULT_HOST,
                       help="The server hostname (default: http://localhost:6543)")
    parser.add_argument("--name", action="store",
                       nargs='?', default=DEFAULT_QUESTION,
                       help="Name of the poll question (default: Yay or Nay?)")
    parser.add_argument("--options", action="store",
                       nargs='?', default=DEFAULT_OPTIONS,
                       help="Comma-separated options")
    parser.add_argument("--config", action="store",
                       help="Spam configuration. The format is index:dup[,unique].\
For example, 0:100,10;2:10 means for option 0 vote 100 times with the same IP \
address plus two more unique visitors (total of 110 votes for option 0 but there \
are only three unique votes. Option 1 is skipped (with zero vote) and for option \
2 only make 10 duplicate votes.By default, we make 100 total votes (option 0 \
gets 88 duplicates and 10 more unique votes; option 1 gets two unique votes; and \
option 3 gets zero vote.")

    args = parser.parse_args()
    spam(args.name, args.options,
        config=args.config,
        host=args.host)
