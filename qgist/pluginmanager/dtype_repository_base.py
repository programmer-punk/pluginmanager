# -*- coding: utf-8 -*-

"""

QGIST PLUGIN MANAGER
QGIS Plugin for Managing QGIS Plugins
https://github.com/qgist/pluginmanager

    qgist/pluginmanager/dtype_repository.py: Repository data type

    Copyright (C) 2017-2020 QGIST project <info@qgist.org>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU General Public License
Version 2 ("GPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
https://github.com/qgist/pluginmanager/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT (Python Standard Library)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import Generator, Iterator

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT (Internal)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .const import CONFIG_GROUP_MANAGER_REPOS
from .backends import backends
from .dtype_pluginrelease_base import dtype_pluginrelease_base_class
from .dtype_settings import (
    dtype_settings_group_class,
    dtype_settings_class,
    )

from ..error import (
    QgistNotImplementedError,
    QgistValueError,
    QgistTypeError,
    )
from ..util import tr

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class dtype_repository_base_class:
    """
    # Repo

    This is abstract class representing a repository.
    From this, classes for repo types (i.e. plugin sources) are derived.

    Mutable.
    """

    _repo_type = None

    def __init__(self,
        repo_id, name, active, protected, plugin_releases,
        config_group
        ):

        if not isinstance(repo_id, str):
            raise QgistTypeError(tr('"repo_id" must be a str.'))
        if len(repo_id) == 0:
            raise QgistValueError(tr('"repo_id" must not be empty.'))
        if not isinstance(name, str):
            raise QgistTypeError(tr('"name" must be a str.'))
        if len(name) == 0:
            raise QgistValueError(tr('"name" must not be empty.'))
        if not isinstance(active, bool):
            raise QgistTypeError(tr('"active" must be a bool.'))
        if not isinstance(protected, bool):
            raise QgistTypeError(tr('"protected" must be a bool.'))
        if not any((isinstance(plugin_releases, dtype) for dtype in (Generator, Iterator, list, tuple))):
            raise QgistTypeError(tr('"plugin_releases" must be any of the floowing: list, tuple, generator, iterator.'))
        plugin_releases = list(plugin_releases)
        if not all((isinstance(release, dtype_pluginrelease_base_class) for release in plugin_releases)):
            raise QgistTypeError(tr('All releases must be plugin releases.'))
        if not isinstance(config_group, dtype_settings_group_class):
            raise QgistTypeError(tr('"config_group" must be a "dtype_settings_group_class" object.'))

        self._id = repo_id # unique
        self._name = name # TODO: enable translations!
        self._active = active
        self._protected = protected
        self._plugin_releases = plugin_releases

        self._config_group = config_group

    def __repr__(self):

        return (
            '<repository '
            f'id="{self._id:s}" name="{self._name:s}" type="{self._repo_type:s}" '
            f'plugin_releases={len(self):d} '
            f'protected={"yes" if self._protected else "no":s} '
            f'active={"yes" if self._active else "no":s}'
            '>'
            )

    def __len__(self):

        return len(self._plugin_releases)

    def __contains__(self, test_release):

        if not isinstance(test_release, dtype_pluginrelease_base_class):
            raise QgistTypeError(tr('"release" must be a release'))

        return any((
            release == test_release
            for release in self._plugin_releases
            ))

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PROPERTIES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise QgistTypeError(tr('New value of "name" must be a str.'))
        if len(value) == 0:
            raise QgistValueError(tr('New value of "name" must not be empty.'))
        self._name = value

    @property
    def active(self):
        return self._active

    @property
    def protected(self):
        return self._protected

    @property
    def plugin_releases(self):
        return (release for release in self._plugin_releases)

    @property
    def repo_type(self):
        return self._repo_type

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PROPERTIES: STUBS FOR SPECIALS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @property
    def url(self):
        raise QgistNotImplementedError()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MANAGEMENT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def refresh(self):
        "Refresh index, i.e. reload metadata from remote source"

        raise QgistNotImplementedError()

    def remove(self):
        "Run cleanup actions e.g. in config before repo is removed"

        raise QgistNotImplementedError()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HELPER STATIC & CLASS METHODS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @classmethod
    def get_repo_config_groups(cls, config):

        if not isinstance(config, dtype_settings_class):
            raise QgistTypeError(tr('"config" must be a "dtype_settings_class" object.'))

        repotype_group = config.get_group(CONFIG_GROUP_MANAGER_REPOS).get_group(cls._repo_type)

        return (
            repotype_group.get_group(repo_id)
            for repo_id in repotype_group.keys_root()
            )

    @classmethod
    def find_plugins(cls, config, protected, plugin_modules):
        raise QgistNotImplementedError()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PRE-CONSTRUCTOR
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @classmethod
    def from_default(cls, config):
        raise QgistNotImplementedError()

    @classmethod
    def from_directory(cls, config, path, writeable = False):
        raise QgistNotImplementedError()

    @classmethod
    def from_userinput(cls, config):
        raise QgistNotImplementedError()

    @classmethod
    def from_config(cls, config):
        raise QgistNotImplementedError()
