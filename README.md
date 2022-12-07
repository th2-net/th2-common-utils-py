# th2-common-utils-py (2.0.0)
Python library with useful functions for **developers and QA needs**. Check the [Wiki](https://github.com/th2-net/th2-common-utils-py/wiki) for instructions and examples.

## Installation
```
pip install th2-common-utils
```

## Release notes

### 2.0.0
Moved to books&pages (grpc v4)

* Added `create_event_batch` function.

### 1.6.0

* Updated `th2-grpc-common` minimal version to `3.12.0`.
* Optimized `create_event_id()` function.
* Optimized `create_event_body()` function (migrated to **orjson** library).

### 1.5.0

* Added the ability to create sorted `TreeTable` (ordered by default).
* Added `dict_values_to_value_filters` and `dict_to_metadata_filter` functions (can be used to create `PreFilter` object from *th2-grpc-check1*).

### 1.4.3

* Fixed memory leak.

### 1.4.2

* Fixed conversion of `Direction` field of `message_metadata`.

### 1.4.1

* Changed `metadata` conversion in `message_to_dict` function.

### 1.4.0

* Added `json_to_message` function.


### 1.3.0

* Changed structure of `message_filter` and `metadata_filter` fields in `dict_to_root_message_filter` function.
