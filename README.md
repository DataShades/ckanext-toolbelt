# ckanext-toolbelt

Collection of different tools for daily use.


## Requirements

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | yes         |
| 2.10         | yes         |
| master       | yes         |


## Content

* [Decorators](#decorators)
  * [Collector](#collector)
  * [Cache](#cache)
* [Plugins](#plugins)
* [CLI](#cli)
* [Misc](#misc)


## Decorators (`ckanext.toolbelt.decorators`)

### `Collector`

Creates a decorator that collects functions and returns them in a
dictionary. Originally designed for actions, auth functions, validators and
helpers.

:information_source: CKAN v2.10 has `tk.blanket` module. It does the same
things in a bit different manner.

Can be used as decorator. Call `Collector.get_collection` when you need
dictionary with names of helpers mapped to helper functions

	helper = Collector()

	@helper
	def func():
		pass

	###
    # ITemplateHelpers
	def get_helpers(self):
		return helper.get_collection()

`Collector.split` allows you to visually separate decorator from the method,
that returns collection

	action, get_actions = Collector().split()

	@action
	def func():
		pass

	###
    # IActions
	def get_actions(self):
		return get_actions()

If you want your functions prefixed by the plugin name, provide this prefix as
a first argument to the `Collector`'s constructor. If particular items must
remain unprefixed, you can specify what name to use, when decorating an item


	validator, get_validators = Collector("toolbelt").split()

	@validator
	def func():
		"""I am toolbelt_func
		"""
		pass

	@validator("custom_func")
	def func():
		"""I am custom_func
		"""
		pass

	###
    # IValidators
	def get_validators(self):
		return get_validators()


[Back to content](#content)

### `Cache`

Cache for functions.

	Cache()
	def func(v):
	    return v * v

By default, cache is based on:

* module, where function is defined
* name of the function
* positional arguments
* named arguments

That means that following two invocations cached separately:

	func(10)
	func(v=10)

Cached data stored in redis as a JSON serialized structure. In order to use
different serializers, you can specify `dumper` and `loader` parameters when
creating `Cache` instance. Any function that accepts single value and returns
`str` or `bytes` can be used as a `dumper`. Any function that accepts `str` or
`bytes` and returns unserialized value can be used as loader.

	from pickle import dumps, loads

	@Cache(dumper=dumps, loader=loads)
	def func(v):
	    return v

As mentioned before, cache key computed using module, name of the function and
parameters. It can be changed by passing a function as `key` argument to the
`Cache` constructor. Expected signature is `key_strategy(func, *args,
**kwargs)`.

	# this function will be called only once, because cache key is based on its name.
	# And name will never change. Unless you change it
	@Cache(key=lambda f, *a, **k: f.__name__)
	def func(v):
	    return v

Cache duration(in seconds) can be configured via `duration` parameter of the
constructor(which can be a callable that returns comuted duration).

	cache = Cache(duration=3600)

	@cache
	def func(v):
	    return v + v

[Back to content](#content)

---

## Plugins

### `toolbelt_fdt_sqlalchemy`

Adapter for
[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/). Enables
SQLAlchemy panel on FlaskDebugToolbar. You have to install `flask-sqlalchemy`
extra to use this plugin:

```sh
pip install 'ckanext-toolbelt[flask-sqlalchemy]'
```

### `toolbelt_cascade_organization_updates`

Reindex all organization's datasets when organization updated. Requires
background worker.

### `toolbelt_composite_groups` / `toolbelt_composite_organizations`

Enable repeating subfields(ckanext-scheming) for organization and group schemas


[Back to content](#content)
---

## CLI

As soon as you've installed ckanext-toolbelt, it will register `ckan toolbelt`
route for CLI. You don't have to add `toolbelt` to the list of enabled
plugins.

Depending on the active plugins, extra subroutes may be added to the `ckan
toolbelt` route.

In addition, there is global `ctb` command that allows to use this package
without CKAN installed or without CKAN config file. But in this way some of
commands (`search-index` for example) are not available, because they use CKAN
core. `ctb` alias exists for setting up the CKAN or extensions and running
generic services, that do not rely on CKAN instance.


Global commands, available via `ctb` and `ckan toolbelt` routes:

```sh
# create a generic configuration. Supported types:
# * deps-makefile  CKAN dependency manager
# * pre-commit     Pre-commit
# * pyproject      pyproject.toml
# * gulp-sass      gulpfile.js with SASS configuration
make config <type>

# create a configuration for GitHub Action. Supported types:
# * pypi-publish    Publish package to PyPI when vX.Y.Z tag added.
# * release-please  Create a PR that compiles changelog and publishes GitHub release.
# * test            Test workflow.
make gh-action <type>

# Generate parts of README.md
# Supported types:
# * config  Print declared config options for the given plugins.
make readme <type>

# Start mail server that will catch outcomming mails.
dev mail-server
```

Commands that depends on CKAN core and available only via `ckan toolbelt`
route:
```sh

# Drop packages that are only in search index but not in DB.
search-index clear-missing

# Clean the DB, optionally keeping data in the given tables.
db clean --yes [-k user] [-k group] [-k ...]
```

[Back to content](#content)

---

## Misc

### `ckanext.toolbelt.utils.cache`
#### `DontCache`
#### `Cache`

### `ckanext.toolbelt.utils.fs`
#### StaticPath

No-op wrapper around filepath that can be used as a context manager:
```python
with StaticPath("/tmp/x.txt") as path:
    with open(path) as src:
        ...
# nothing is changed
```

#### RemovablePath

Context manager that removes file on exit:
```python
with RemovablePath("/tmp/x.txt") as path:
    with open(path) as src:
        ...
# /tmp/x.txt is removed
```

#### `path_to_resource(res_dict, max_size=0)`

Returns a filepath for a resource.

If resource is stored locally, return StaticPath. If resource stored remotely,
download it to /tmp and return RemovablePath. Remote resources with size
exceeding `max_size` are not downloaded and empty StaticPath returned.

Example:
```python
with path_to_resource(resource) as path:
    with open(path) as src:
        print(src.read())
```


### `ckanext.toolbelt.utils.scheming`
#### `get_validation_schema`

### `ckanext.toolbelt.utils.structures`
#### `Node`

### `ckanext.toolbelt.utils.hierarchy`
#### `Node`
#### `Strategy`
#### `ParentReference`
#### `package_hierarchy`


[Back to content](#content)
