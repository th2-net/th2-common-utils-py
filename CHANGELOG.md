# Release notes

## 1.6.3

* Add backward compatibility for `create_event_id` function
* Update workflows

## 1.6.2

* Fix event body creation

## 1.6.1

* Added vulnerabilities scanning workflow

## 1.6.0

* Updated `th2-grpc-common` minimal version to `3.12.0`.
* Optimized `create_event_id()` function. Now Event IDs are equal to UUID (created once per run lifecycle) plus increasing counter.
* Fixed creation of Event body. Now format is always correct (byte representation of JSON).
* Optimized serialization of data to Event body using faster library for JSON ([orjson](https://github.com/ijl/orjson))

## 1.5.0

* Added the ability to create sorted `TreeTable` (ordered by default).
* Added `dict_values_to_value_filters` and `dict_to_metadata_filter` functions (can be used to create `PreFilter` object from *th2-grpc-check1*).

## 1.4.3

* Fixed memory leak.

## 1.4.2

* Fixed conversion of `Direction` field of `message_metadata`.

## 1.4.1

* Changed `metadata` conversion in `message_to_dict` function.

## 1.4.0

* Added `json_to_message` function.


## 1.3.0

* Changed structure of `message_filter` and `metadata_filter` fields in `dict_to_root_message_filter` function.