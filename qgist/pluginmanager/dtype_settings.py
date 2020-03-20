# -*- coding: utf-8 -*-

"""

QGIST PLUGIN MANAGER
QGIS Plugin for Managing QGIS Plugins
https://github.com/qgist/pluginmanager

    qgist/pluginmanager/dtype_settings.py: Settings data type

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
# IMPORT (External Dependencies)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtCore import QDate

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT (Internal)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .const import CONFIG_DELIMITER
from ..config import config_class
from ..error import (
    QgistTypeError,
    QgistValueError,
    )
from ..util import tr

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: SETTINGS MAIN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class dtype_settings_class:
    """
    Transparent wrapper around QgsSettings - so it can be exchanged (for testing etc)
    Class enables redundant storage of settings: Into QgsSettings *and* config_class.
    When read, data from QgsSettings is preferred.
    When written, data goes first into config_class, second into QgsSettings.

    Mutable.
    """

    def __init__(self, config, try_qgis_settings = True):

        if not isinstance(config, config_class):
            raise QgistTypeError(tr('config must be an instance of config_class'), self)
        if not isinstance(try_qgis_settings, bool):
            raise QgistTypeError(tr('try_qgis_settings must be a bool'), self)

        self._config = config

        self._qgis_settings = None
        if try_qgis_settings:
            self._load_qgis_settings()

    def __repr__(self):

        return f'<settings ({id(self):x})>'

    def _load_qgis_settings(self):

        try:
            from qgis.core import QgsSettings
        except ModuleNotFoundError:
            QgsSettings = None

        self._settings = QgsSettings() if QgsSettings is not None else None

    def __getitem__(self, name):

        setting = self._settings.value(name) if self._settings is not None else None

        if setting is None:
            return self._config[name]
        return self._convert_qt_to_python(setting)

    def __setitem__(self, name, value):

        self._config[name] = value # does internal validity and type checks etc

        self._settings.setValue(name, value)

    def get(self, name, default):
        "dict get"

        setting = self._settings.value(name) if self._settings is not None else None

        if setting is None:
            return self._config.get(name, default)
        return self._convert_qt_to_python(setting)

    def get_group(self, root):
        "get group by root"

        if not isinstance(root, str):
            raise QgistTypeError(tr('root is not str'), self)
        if len(root) == 0:
            raise QgistValueError(tr('root must not be empty'), self)

        return _dtype_settings_group_class(self, root)

    def keys(self):
        "dict keys generator"

        keys = self._settings.allKeys() if self._settings is not None else None

        if keys is not None:
            return (key for key in keys) # keys is a list, should be a generator/iterator
        return self._config.keys()

    def keys_root(self):
        "dict keys generator - at root"

        return (item for item in set((
            key.split(CONFIG_DELIMITER, 1)[0]
            for key in self.keys()
            )))

    @staticmethod
    def _convert_qt_to_python(data):

        if config_class.check_value(data): # valid Python/JSON data type
            return data

        if isinstance(data, QDate):
            return data.toPyDate().isoformat() # returns date-time iso string

        raise QgistTypeError(tr('unknown data type from QGIS settings'), 'settings')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: SETTINGS GROUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class _dtype_settings_group_class:
    """
    Mimics QgsSettings.beginGroup & QgsSettings.endGroup, just without the change of state

    Mutable.
    """

    def __init__(self, settings, root):

        if not isinstance(settings, dtype_settings_class):
            raise QgistTypeError(tr('settings must be an instance of config_class'), self)
        if not isinstance(root, str):
            raise QgistTypeError(tr('root must be a str'), self)
        if len(root) == 0:
            raise QgistValueError(tr('root must not be empty'), self)

        self._settings = settings
        self._root = root
        self._base = self._root + CONFIG_DELIMITER
        self._base_len = len(self._base)

    def __repr__(self):

        return f'<settings group (attached to {id(self._settings):x}, root "{self._root:s}")>'

    def __getitem__(self, name):

        if not isinstance(name, str):
            raise QgistTypeError(tr('name is not str'), self)
        if len(name) == 0:
            raise QgistValueError(tr('name must not be empty'), self)

        return self._settings[self._base + name]

    def __setitem__(self, name, value):

        if not isinstance(name, str):
            raise QgistTypeError(tr('name is not str'), self)
        if len(name) == 0:
            raise QgistValueError(tr('name must not be empty'), self)

        self._settings[self._base + name] = value

    def get(self, name, default):
        "dict get"

        if not isinstance(name, str):
            raise QgistTypeError(tr('name is not str'), self)
        if len(name) == 0:
            raise QgistValueError(tr('name must not be empty'), self)

        return self._settings.get(self._base + name, default)

    def get_group(self, root):
        "get group by root"

        if not isinstance(root, str):
            raise QgistTypeError(tr('root is not str'), self)
        if len(root) == 0:
            raise QgistValueError(tr('root must not be empty'), self)

        return type(self)(self._settings, self._base + root)

    def keys(self):
        "dict keys generator"

        return (item for item in set((
            key[self._base_len:]
            for key in self._settings.all_keys()
            if key.startswith(self._base) and len(key) > self._base_len
            )))

    def keys_root(self):
        "dict keys generator - at root"

        return (item for item in set((
            key[self._base_len:].split(CONFIG_DELIMITER, 1)[0]
            for key in self._settings.all_keys()
            if key.startswith(self._base) and len(key) > self._base_len
            )))
