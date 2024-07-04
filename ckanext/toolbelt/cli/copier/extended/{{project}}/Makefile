###############################################################################
#                             requirements: start                             #
###############################################################################
ckan_tag = ckan-2.10.4

ext_list = \
	admin-panel \
	collection \
	comments \
	editable-config \
	files flakes \
	googleanalytics \
	let-me-in \
	officedocs or-facet \
	pdfview pygments \
	resource-indexer \
	scheming search-tweaks spatial \
	toolbelt \
	unfold \
	vip-portal \
	xloader


remote-admin-panel = https://github.com/mutantsan/ckanext-admin-panel commit 999183a
remote-collection = https://github.com/DataShades/ckanext-collection.git tag v0.2.0a0
remote-comments = https://github.com/DataShades/ckanext-comments.git tag v0.3.2a0
remote-editable-config = https://github.com/ckan/ckanext-editable-config tag v0.0.6
remote-files = https://github.com/DataShades/ckanext-files.git tag v1.0.0a0
remote-flakes = https://github.com/DataShades/ckanext-flakes.git tag v0.4.5
remote-let-me-in = https://github.com/mutantsan/ckanext-let-me-in tag v1.0.1
remote-officedocs = https://github.com/jqnatividad/ckanext-officedocs tag v1.1.0
remote-or-facet = https://github.com/DataShades/ckanext-or_facet tag v0.1.1
remote-pdfview = https://github.com/ckan/ckanext-pdfview.git tag 0.0.8
remote-pygments = https://github.com/mutantsan/ckanext-pygments commit f4287bb
remote-resource-indexer = https://github.com/DataShades/ckanext-resource_indexer.git tag v0.4.1
remote-scheming = https://github.com/ckan/ckanext-scheming tag release-3.0.0
remote-spatial = https://github.com/ckan/ckanext-spatial tag v2.1.1
remote-search-tweaks = https://github.com/dataShades/ckanext-search-tweaks tag v0.6.1
remote-toolbelt = https://github.com/DataShades/ckanext-toolbelt.git tag v0.4.14
remote-unfold = https://github.com/mutantsan/ckanext-unfold.git tag v1.0.2
remote-vip-portal = https://github.com/DataShades/ckanext-vip-portal.git tag v0.2.5a1
remote-xloader = https://github.com/ckan/ckanext-xloader.git tag 1.0.1
remote-googleanalytics = https://github.com/ckan/ckanext-googleanalytics.git tag v2.4.0

package_extras-remote-googleanalytics = requirements
package_extras-remote-files = opendal,libcloud
package_extras-remote-resource-indexer = pdf

###############################################################################
#                              requirements: end                              #
###############################################################################

_version = master

-include deps.mk

prepare:  ## download CDM rules
	curl -O https://raw.githubusercontent.com/DataShades/ckan-deps-installer/$(_version)/deps.mk

vendor:  ## Copy vendor libraries from node_modules/ to assets directory
	cp node_modules/showdown/dist/showdown.js ckanext/{{ project }}/assets/vendor
	cp node_modules/daterangepicker/daterangepicker.{js,css} ckanext/{{ project }}/assets/vendor
	cp node_modules/daterangepicker/moment.min.js ckanext/{{ project }}/assets/vendor
	cp node_modules/slick-carousel/slick/slick.min.js ckanext/{{ project }}/assets/vendor
	cp node_modules/htmx.org/dist/htmx.js ckanext/{{ project }}/assets/vendor
	cp node_modules/hyperscript.org/dist/_hyperscript.js ckanext/{{ project }}/assets/vendor/hyperscript.js
	cp node_modules/overlayscrollbars/styles/overlayscrollbars.css ckanext/{{ project }}/assets/vendor
	cp node_modules/overlayscrollbars/browser/overlayscrollbars.browser.es6.js ckanext/{{ project }}/assets/vendor/overlayscrollbars.js

typecheck:  ## Run typechecker
	pyright --pythonpath $(which python)


changelog:  ## compile changelog
	git changelog -c conventional -o CHANGELOG.md $(if $(bump),-B $(bump))

test-server:  ## start server for frontend testing
	yes | ckan -c test.ini db clean
	ckan -c test.ini db upgrade
	yes | ckan -ctest.ini sysadmin add admin password=password123 email=admin@test.net
	ckan -c test.ini run -t
