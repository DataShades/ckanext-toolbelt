## Example:
# make prepare; make full-upgrade
#
## or
# make prepare; make sync install
#
## `make prepare` installs/updates code for all other make-rules. It's
## recommended to execute it periodicatlly, to pull the lates version of CDM.
#
## `make full-upgrade` synchronizes and installs CKAN, dependencies and current
## extension.
#
## `make sync install` synchronizes and installs only dependencies. CKAN and
## current extension are ignored.
#
## Add `develop=1` to install dev-requirements.txt alongside with the normal
## requirements.
#
## Any extension can be synchronized/installed individually:
# make sync-EXT install-EXT
#
## If `remote-EXT` definition is present, extension is pulled from the
## specified source. If you are running `make sync-EXT install-EXT` and there
## is no `remote-EXT` line, CDM makes an attempt to pull the extension from
## master branch of `https://github.com/ckan/ckanext-EXT`. Most likely, such
## extension does not exist. But git will think that you are pulling from
## private repository and may ask your credentials or just say that you don't
## have permissions to read from this repo.

###############################################################################
#                             requirements: start                             #
###############################################################################
# CKAN core supports this short syntax. But internally it's unfolds into
## remote-ckan = https://github.com/ckan/ckan tag ckan-2.10.4
# if you want to use CKAN fork or specific commit, use this full specification
ckan_tag = ckan-2.11.2

# items from this list are installed by `make full-upgrade` and `make sync
# install`. If you specify remote, but did not added extension to this list, it
# won't be installed. If you add SOMETHING to this list, but did not specify
# remote, SOMETHING is pulled from `https://github.com/ckan/ckanext-SOMETHING
# branch master`
ext_list = \
	admin-panel \
	charts collection cloudstorage comments \
    dcat \
	editable-config \
	files flakes \
	ingest \
	geoview googleanalytics \
    hierarchy harvest \
	let-me-in \
	officedocs or-facet \
	pdfview pygments \
	resource-indexer \
	scheming search-tweaks spatial saml syndicate \
	security \
	toolbelt \
	unfold \
	vip-portal \
	xloader

# information about extension source. Format is `ALTERNATIVE-NAME = URL TYPE
# REF`, where
#
# * ALTERNATIVE: `remote` by default, but can be any string
#
# * NAME: name of extension. Must be exactly the same as value from `ext_list`
#
# * URL: repo URL. GitHub, BitBucket, GitLab or even SSH URL
#
# * TYPE: type of reference specified by the next part. One of: branch, commit, tag
#
# * REF: commit hash, branch name, tag name, depending on TYPE value. Prefer tags
remote-admin-panel = https://github.com/DataShades/ckanext-admin-panel commit 999183a
# dev is an alternative. You can install it via `make full-upgrade
# alternative=dev`. Any other prefix can be used instead of `dev`.
dev-admin-panel = https://github.com/DataShades/ckanext-admin-panel branch master

remote-cloudstorage = https://github.com/DataShades/ckanext-cloudstorage.git tag v0.3.2
remote-charts = https://github.com/DataShades/ckanext-charts.git tag v1.6.0
remote-collection = https://github.com/DataShades/ckanext-collection.git tag v0.2.0a0
remote-comments = https://github.com/DataShades/ckanext-comments.git tag v0.3.2a0
remote-dcat = https://github.com/ckan/ckanext-dcat.git tag v2.2.0
remote-editable-config = https://github.com/ckan/ckanext-editable-config tag v0.0.6
remote-files = https://github.com/DataShades/ckanext-files.git tag v1.0.0a3
remote-flakes = https://github.com/DataShades/ckanext-flakes.git tag v0.4.5
remote-geoview = https://github.com/ckan/ckanext-geoview.git tag v0.1.0
remote-googleanalytics = https://github.com/ckan/ckanext-googleanalytics.git tag v2.4.0
remote-harvest = https://github.com/ckan/ckanext-harvest.git tag v1.5.6
remote-hierarchy = https://github.com/ckan/ckanext-hierarchy.git tag v1.2.1
remote-ingest = https://github.com/DataShades/ckanext-ingest.git tag v1.4.2
remote-let-me-in = https://github.com/DataShades/ckanext-let-me-in tag v1.0.1
remote-officedocs = https://github.com/jqnatividad/ckanext-officedocs tag v1.1.0
remote-or-facet = https://github.com/DataShades/ckanext-or_facet tag v0.1.1
remote-pdfview = https://github.com/ckan/ckanext-pdfview.git tag 0.0.8
remote-pygments = https://github.com/DataShades/ckanext-pygments commit f4287bb
remote-resource-indexer = https://github.com/DataShades/ckanext-resource_indexer.git tag v0.4.1
remote-saml = https://github.com/DataShades/ckanext-saml.git tag v0.3.3
remote-scheming = https://github.com/ckan/ckanext-scheming tag release-3.0.0
remote-search-tweaks = https://github.com/dataShades/ckanext-search-tweaks tag v0.6.1
remote-security = https://github.com/data-govt-nz/ckanext-security tag 4.1.1

remote-spatial = https://github.com/ckan/ckanext-spatial tag v2.1.1
remote-syndicate = https://github.com/DataShades/ckanext-syndicate tag v2.2.2
remote-toolbelt = https://github.com/DataShades/ckanext-toolbelt.git tag v0.4.24
remote-unfold = https://github.com/DataShades/ckanext-unfold.git tag v1.0.2
remote-vip-portal = https://github.com/DataShades/ckanext-vip-portal.git tag v0.2.5a1
remote-xloader = https://github.com/ckan/ckanext-xloader.git tag 2.0.0

# extras installed with the extension. Produce `pip install
# 'ckanext-googleanalytics[requirements]'`-like instructions.
package_extras-remote-googleanalytics = requirements
package_extras-remote-files = opendal,libcloud
package_extras-remote-resource-indexer = pdf



###############################################################################
#                              requirements: end                              #
###############################################################################

# version of CDM pulled during `make-prepare`. Use version tag to prevent
# undesirable udates
_version = master

# import all rules defined in `deps.mk`. This file will be pulled by `make prepare`
-include deps.mk

prepare:  ## download CDM rules
	curl -O https://raw.githubusercontent.com/DataShades/ckan-deps-installer/$(_version)/deps.mk
