Changelog
=========

# UNRELEASED

## Changed
- License changed from MIT to Hippocratic.

## Added
- `events.instrument()` added as a decorator you can use to instrument a single function call.
- Official support for python 3.8.


# 0.5.1 - 2019-10-21

## Changed
- Before 0.5.0 flask-events would silently ignore being used outside the app context. With 0.5.0
  that changed to a hard failure, which makes some use cases more convulated without much benefit.
  The pre-0.5.0 behavior has been restored, with a logged warning that it's being used outside of
  an app context.


# 0.5.0 - 2019-10-19

## Removed
- Support for python 3.4.

## Added
- You can turn on opt-in anonymization of IPs in the default context by setting
  `EVENTS_ANONYMIZE_IPS` to `True` (default settings), or a dict with the keys `ipv4_mask` and
  `ipv6_mask` to customize the masks used.


# 0.4.0 - 2019-02-23

## Added
- celery tasks can now be instrumented too! Use `.init_celery_app` instead of `.init_app` to
  automatically instrument all celery tasks.


# 0.3.0 - 2018-07-13

## Fixed
- The logfmt outlet now formats 0 correctly (previously it would be empty string),0 and outputs
  True/False in lowercase, and by default formats floats with four digits.

## Added
- If running on Heroku and the `runtime-dyno-metadata` labs feature is enabled the release version
  and slug commit will be included by default.
- Added `handler` by default which is the qualified path to the function that handled the request.


# 0.2.0 - 2018-07-10

## Added
- `Events.add_all` to set data that should be included with all requests.


# 0.1.0 - 2018-07-09

First release!
