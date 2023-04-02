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


## Decorators (`ckanext.toolbelt.decorators`)

### `Collector`

Creates a decorator that can collect functions and return them in a
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
SQLAlchemy panel on FlaskDebugToolbar. You have to install appropriate version
of `flask-sqlalchemy` to use this plugin:

| Environment                     | Version | Command                             |
|---------------------------------|---------|-------------------------------------|
| Flask 2.0(CKAN <= 2.10)         | 2.5     | `pip install flask-sqlalchemy~=2.5` |
| Flask 2.2(CKAN >= 2.11, master) | 3.0     | `pip install flask-sqlalchemy~=3.0` |

Note: `flask-sqlalchemy~=2.5` works with the latest CKAN version, so you can
always use the first line from the table above.

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
