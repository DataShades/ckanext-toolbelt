###############################################################################
#                             requirements: start                             #
###############################################################################
ckan_tag = ckan-2.10.0
ext_list = dcat

remote-dcat = https://github.com/ckan/ckanext-dcat.git branch master

###############################################################################
#                              requirements: end                              #
###############################################################################

_version = master

-include deps.mk

prepare:
	curl -O https://raw.githubusercontent.com/DataShades/ckan-deps-installer/$(_version)/deps.mk
