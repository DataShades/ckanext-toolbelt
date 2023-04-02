# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [0.3.0](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.17...v0.3.0) (2023-04-02)


### ⚠ BREAKING CHANGES

* update `make` command

### Features

* `make config pyproject` detects plugin name and writes output to pyproject.toml ([7dcfb39](https://github.com/DataShades/ckanext-toolbelt/commit/7dcfb39e127a76dbe1d16b4739eba7a7c8b6a905))
* fdt_sqlalchemy supports flask-sqlalchemy 3.0 ([c31923d](https://github.com/DataShades/ckanext-toolbelt/commit/c31923dcdb6fc6cb521dc66575dff73adfa1bfff))
* pin deps-installer to ckan v2.10 ([7c71766](https://github.com/DataShades/ckanext-toolbelt/commit/7c717669bab85e0d982bf3044e3fc68fab7f27b2))
* update `make` command ([717556d](https://github.com/DataShades/ckanext-toolbelt/commit/717556dcfabc0a859505b67c31a6e405dd7374bf))

## [0.3.0](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.17...v0.3.0) (2023-04-02)


### ⚠ BREAKING CHANGES

* update `make` command

### Features

* `make gh-action pypi-publish` ([038df5b](https://github.com/DataShades/ckanext-toolbelt/commit/038df5b26bf2a746ba80c15b3383509dfe07930f))
* `make gh-action` route ([2b8c9a5](https://github.com/DataShades/ckanext-toolbelt/commit/2b8c9a5ccb6eb5de8afaf1da325d63bb5b89a131))
* `make pyproject` detects plugin name and writes output to pyproject.toml ([7dcfb39](https://github.com/DataShades/ckanext-toolbelt/commit/7dcfb39e127a76dbe1d16b4739eba7a7c8b6a905))
* fdt_sqlalchemy supports flask-sqlalchemy 3.0 ([c31923d](https://github.com/DataShades/ckanext-toolbelt/commit/c31923dcdb6fc6cb521dc66575dff73adfa1bfff))
* pin deps-installer to ckan v2.10 ([7c71766](https://github.com/DataShades/ckanext-toolbelt/commit/7c717669bab85e0d982bf3044e3fc68fab7f27b2))
* update `make` command ([717556d](https://github.com/DataShades/ckanext-toolbelt/commit/717556dcfabc0a859505b67c31a6e405dd7374bf))

### [0.2.17](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.16...v0.2.17) (2023-03-11)


### Features

* add ruff config ([17841f4](https://github.com/DataShades/ckanext-toolbelt/commit/17841f4ad3dc266b6291f20dd2487c11c5701910))

### [0.2.16](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.15...v0.2.16) (2023-03-06)


### Features

* toolbelt_fdt_sqlalchemy plugin ([f70a044](https://github.com/DataShades/ckanext-toolbelt/commit/f70a04488d81e537ba2a725c8f390110c99ad684))

### [0.2.15](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.14...v0.2.15) (2023-03-06)


### Features

* toolbelt_fdt_scroll plugin ([bcac80e](https://github.com/DataShades/ckanext-toolbelt/commit/bcac80eff34d98bcd4822492a820b5b41a43d9a7))

### [0.2.14](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.13...v0.2.14) (2023-03-03)


### Features

* `make pyright-config` command ([ab93df7](https://github.com/DataShades/ckanext-toolbelt/commit/ab93df746ac0b64d0cb58c57d8f5b88c74681139))
* add cascade_organization_updates plugin ([9fe713e](https://github.com/DataShades/ckanext-toolbelt/commit/9fe713ef6030c3e7be83ea11f21f30e644b1ba66))
* make pyproject / make config-readme ([8b28deb](https://github.com/DataShades/ckanext-toolbelt/commit/8b28deb11a173f6049bdf61ab34943974e9b47c3))

### [0.2.13](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.12...v0.2.13) (2023-02-02)


### Bug Fixes

* another fix of hierarchy search ([1776b61](https://github.com/DataShades/ckanext-toolbelt/commit/1776b615b2f1c018e9de1fee4a3bcd6d57e8bdd8))

### [0.2.12](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.11...v0.2.12) (2023-02-02)


### Bug Fixes

* fix search by non-id parent ([2733b53](https://github.com/DataShades/ckanext-toolbelt/commit/2733b53c1e6fa2799e47fde500c5fdc673b38118))

### [0.2.11](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.10...v0.2.11) (2023-02-02)


### Features

* allow referencing any field in hierarchy ([af687be](https://github.com/DataShades/ckanext-toolbelt/commit/af687be783345a1a8bcb8d80f0fe6b6557bb57e1))

### [0.2.10](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.9...v0.2.10) (2023-02-01)


### Bug Fixes

* fix parent depth for package_hierarchy ([2123ef1](https://github.com/DataShades/ckanext-toolbelt/commit/2123ef1d3a027d829bfd1c9cd20570720c7103d8))

### [0.2.9](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.8...v0.2.9) (2023-02-01)


### Bug Fixes

* use better name for package_hierarchy config options ([d5337c2](https://github.com/DataShades/ckanext-toolbelt/commit/d5337c2f7c4a1f572be50e3ef9c6a87098377e3f))

### [0.2.8](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.7...v0.2.8) (2023-02-01)


### Features

* add utils.hierarchy module ([cb7dbfb](https://github.com/DataShades/ckanext-toolbelt/commit/cb7dbfb75a38a3102ebc02c58bcc544376e7301d))

### [0.2.7](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.6...v0.2.7) (2023-02-01)


### Features

* add utils.structures.Node ([8bdec35](https://github.com/DataShades/ckanext-toolbelt/commit/8bdec3505e3684f16992a779ce61d59f54e51cee))

### [0.2.6](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.5...v0.2.6) (2022-11-28)


### Features

* add SelectOption type ([6597943](https://github.com/DataShades/ckanext-toolbelt/commit/65979436f241e65f0409e6eb5627bc8de23b8343))

### [0.2.4](https://github.com/DataShades/ckanext-toolbelt/compare/v0.2.3...v0.2.4) (2022-08-28)


### Features

* add `utils.config_getter` ([8d44503](https://github.com/DataShades/ckanext-toolbelt/commit/8d44503915e49c0f116ea582145e908d57e76be2))


### Bug Fixes

* do not delete alembic_version of plugins ([6af6f64](https://github.com/DataShades/ckanext-toolbelt/commit/6af6f64ed8f08df7c7aecab402d55f6d502b4649))
