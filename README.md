# Django Test Tutorial

[![badge](https://img.shields.io/travis/seporaitis/django-tutorial-tests/master.svg)](https://travis-ci.org/seporaitis/django-tutorial-tests/builds)

## What is this?

This is the standard Django tutorial application with some extra
tests.

## Why is it here?

High level: provide examples of testing Django views, especially GET &
POST requests, using Django test `Client` and Django `RequestFactory`.

The top-level difference between the two is that `Client` creates and
runs the request starting at low-level HTTP, to middleware, to view,
and returns the response object with the context, used to render
template.

On the other hand, `RequestFactory` returns request object that can be
then used to test view function as a black-box, with exactly known
inputs, testing for specific outputs.

Although both have their purpose, request factory based tests are much
faster than client, as can be observed by cloning this repository and
running `tox`:

``` shell
$ tox -- polls.tests.test_views_with_request_factory
... output ...
Ran 6 tests in 0.034s
```

``` shell
$ tox -- polls.tests.test_views_with_client
... output ...
Ran 10 tests in 0.205s
```

## More reading:

* [Django test `Client`](https://docs.djangoproject.com/en/dev/topics/testing/tools/)
* [Django `RequestFactory`](https://docs.djangoproject.com/en/1.11/topics/testing/advanced/#the-request-factory)
