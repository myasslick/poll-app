## Poll App in Pyramid

Specifications:

POST /polls : Create a new poll. Returns a JSON object with one key `id`, the ID of the new poll. POST arguments are:
* name: name of poll to create
* options: comma separated list of poll options
  POST /polls/<id>/vote : Vote on a poll. POST arguments are:
* option: Zero-based index of option to vote on
* ip: IP address of voter. Use this argument instead of actual remote IP to make testing easier
GET /polls/<id>/results: Get poll results. Returns a JSON list of objects, each with the keys:
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

