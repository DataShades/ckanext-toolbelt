.DEFAULT_GOAL := help
.PHONY = help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$$$' $$(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$$$1, $$$$2}'


changelog:  ## compile changelog
	git changelog -c conventional -o CHANGELOG.md $(if $(bump),-B $(bump))

test-server:  ## start server for frontend testing
ifeq ($(dirty-server),)
	yes | ckan -c test.ini db clean
	ckan -c test.ini db upgrade
	yes | ckan -ctest.ini sysadmin add admin password=password123 email=admin@test.net
else
	ckan -c test.ini run -t
endif

test-frontend:  ## run e2e tests
	pytest -m playwright

typecheck:  ## Run typechecker
	npx pyright --pythonpath="$$(which python)"
