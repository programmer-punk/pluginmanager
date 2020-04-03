# -*- coding: utf-8 -*-

"""

QGIST PLUGIN MANAGER
QGIS Plugin for Managing QGIS Plugins
https://github.com/qgist/pluginmanager

    qgist/pluginmanager/dtype_index.py: Repository index data type

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
# IMPORT (Internal)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .const import (
    CONFIG_KEY_ALLOW_DEPRECATED,
    CONFIG_KEY_ALLOW_EXPERIMENTAL,
    )
from .backends import backends
from .dtype_plugin import dtype_plugin_class
from .dtype_settings import dtype_settings_class

from ..error import (
    QgistTypeError,
    QgistValueError,
    )
from ..util import tr

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: INDEX
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class dtype_index_class:
    """
    Index of repositories

    Mutable.
    """

    def __init__(self, config):

        if not isinstance(config, dtype_settings_class):
            raise QgistTypeError(tr('"config" must be a "dtype_settings_class" object.'))

        self._config = config
        self._repos = [] # From high to low priority
        self._plugins = {} # Individual plugins, not their releases

        self._allow_deprecated = self._config.str_to_bool(self._config[CONFIG_KEY_ALLOW_DEPRECATED])
        self._allow_experimental = self._config.str_to_bool(self._config[CONFIG_KEY_ALLOW_EXPERIMENTAL])

    def __repr__(self):

        return f'<index ({id(self):x}) repos={self.len_repos:d} plugins={self.len_plugins:d}>'

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PROPERTIES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @property
    def repos(self):
        return (repo for repo in self._repos)

    @property
    def len_repos(self):
        return len(self._repos)

    @property
    def plugins(self):
        return (plugin for plugin in self._plugins.values())

    @property
    def len_plugins(self):
        return len(self._plugins)

    @property
    def allow_deprecated(self):
        return self._allow_deprecated
    @allow_deprecated.setter
    def allow_deprecated(self, value):
        if not isinstance(value, bool):
            raise QgistTypeError(tr('value is not bool'))
        self._allow_deprecated = value
        self._config[CONFIG_KEY_ALLOW_DEPRECATED] = self._config.bool_to_str(value)

    @property
    def allow_experimental(self):
        return self._allow_experimental
    @allow_experimental.setter
    def allow_experimental(self, value):
        if not isinstance(value, bool):
            raise QgistTypeError(tr('value is not bool'))
        self._allow_experimental = value
        self._config[CONFIG_KEY_ALLOW_EXPERIMENTAL] = self._config.bool_to_str(value)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MANAGEMENT: REPOSITORIES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def add_repo(self, repo_type, method, *args, **kwargs):
        "Initialize and add repository based on type, method and arbitrary parameters"

        if not isinstance(repo_type, str):
            raise QgistTypeError(tr('"repo_type" must be a str.'))
        if repo_type not in backends.keys():
            raise QgistValueError(tr('"repo_type" is unknown.'))
        if not isinstance(method, str):
            raise QgistTypeError(tr('"method" must be a str.'))

        repository_class = backends[repo_type].dtype_repository_class

        if method not in (item[5:] for item in dir(repository_class) if item.startswith('from_')):
            raise QgistValueError(tr('"method" is unknown.'))

        repo = getattr(repository_class, f'from_{method:s}')(*args, **kwargs) # TODO: Catch user abort
        self._repos.append(repo) # Add to list at the end, i.e. with lowers priority

    def change_repo_priority(self, repo_id, direction):
        "Repository can be moved up (lower priority) or down (higher priority) by one"

        if not isinstance(direction, int):
            raise QgistTypeError(tr('"direction" must be a str.'))
        if direction not in (1, -1):
            raise QgistValueError(tr('"direction" must either be 1 or -1.'))

        repo = self.get_repo(repo_id)
        index = self._repos.index(repo)

        if self.len_repos < 2:
            return
        if index == 0 and direction == -1:
            return
        if index == (self.len_repos - 1) and direction == 1:
            return

        self._repos[index + direction], self._repos[index] = self._repos[index], self._repos[index + direction]

    def get_repo(self, repo_id):
        "Get repository by id (if id is present)"

        if not isinstance(repo_id, str):
            raise QgistTypeError(tr('"repo_id" must be a str.'))
        if len(repo_id) == 0:
            raise QgistValueError(tr('"repo_id" must not be empty.'))
        if repo_id not in (repo.id for repo in self._repos):
            raise QgistValueError(tr('"repo_id" is unknown. There is no such repository.'))

        return {repo.id: repo for repo in self._repos}[repo_id]

    def remove_repo(self, repo_id):
        "Remove repository by id (if id is present)"

        repo = self.get_repo(repo_id)
        repo.remove()
        self._repos.remove(repo)

    def refresh_repos(self):
        "Reload index of every repo"

        for repo in self._repos:
            repo.refresh()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MANAGEMENT: PLUGINS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def add_plugin(self, plugin):

        if not isinstance(plugin, dtype_plugin_class):
            raise QgistTypeError(tr('"plugin" is not a plugin'))
        if plugin.id in self._plugins.keys():
            raise QgistValueError(tr('"plugin" can not be added - it is already in dict'))

        self._plugins[plugin.id] = plugin

    def get_plugin(self, plugin_id):

        if not isinstance(plugin_id, str):
            raise QgistTypeError(tr('"plugin_id" must be a str.'))
        if len(plugin_id) == 0:
            raise QgistValueError(tr('"plugin_id" must not be empty.'))
        if plugin_id not in self._plugins.keys():
            raise QgistValueError(tr('"plugin_id" is unknown. There is no such plugin.'))

        return self._plugins[plugin_id]

    # def remove_plugin(self, plugin_id):
    #
    #     pass

    def get_all_installed_plugins(self):
        "Currently installed plugins"

        return (plugin for plugin in self._plugins.values() if plugin.installed)

    def get_all_available_plugins(self):
        "Available plugins, compatible to QGIS version"

        return (plugin for plugin in self._plugins.values() if plugin.available)
