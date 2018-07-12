Changelog
=========

# UNRELEASED

## Fixed
- The logfmt outlet now formats 0 correctly (previously it would be empty string),0 and outputs
  True/False in lowercase, and by default formats floats with four digits.

## Added
- If running on Heroku and the `runtime-dyno-metadata` labs feature is enabled the release version
  and slug commit will be included by default.


# 0.2.0 - 2018-07-10

## Added
- `Events.add_all` to set data that should be included with all requests.


# 0.1.0 - 2018-07-09

First release!
