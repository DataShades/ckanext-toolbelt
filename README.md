[![Tests](https://github.com/DataShades/ckanext-toolbelt/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-toolbelt/actions)

# ckanext-toolbelt

Collection of different entities that are useful sometimes.


## Requirements

| CKAN version    | Compatible? |
|-----------------|-------------|
| 2.8 and earlier | no          |
| 2.9             | yes         |
|                 |             |


## Decorators (`ckanext.toolbelt.decorators`)

### `Collector`

Creates a decorator that can collect functions and return them in a
dictionary. Originally designed for actions, auth functions, validators and
helpers.

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

---


## CLI

As soon as you've installed ckanext-toolbelt, it will register `ckan toolbelt`
route for CLI. You don't have to add `toolbelt` to the list of enabled
plugins. But depending on the list of enabled plugins, extra subroutes will be
added to the `ckan toolbelt` route.

Below are commands that do not depend on ckanext-toolbelt plugins. They are
available all the time or when some particular requirement is satisfied(in that
case, requirement itself is mentioned)

	make deps-makefile    Print to stdout basic Makefile for ckan-deps-installer
