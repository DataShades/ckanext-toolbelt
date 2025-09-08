.DEFAULT_GOAL := help
.PHONY = help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


changelog:  ## compile changelog
	git cliff --output CHANGELOG.md $(if $(bump),--tag $(bump))


test_config = test.ini
test-server:  ## start server for frontend testing
	yes | ckan -c $(test_config) db clean
	ckan -c $(test_config) db upgrade
	yes | ckan -c $(test_config) sysadmin add admin password=password123 email=admin@test.net
	ckan -c $(test_config) run -t
