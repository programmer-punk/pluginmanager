# -*- coding: utf-8 -*-

"""

QGIST PLUGIN MANAGER
QGIS Plugin for Managing QGIS Plugins
https://github.com/qgist/pluginmanager

    qgist/pluginmanager/error.py: workbench exception types

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
# EXCEPTIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class QgistRepoError(Exception):
    pass

class QgistInstallFailed(Exception):
    pass

class QgistNotADirectoryError(NotADirectoryError):
    pass

class QgistNotAPluginDirectoryError(Exception):
    pass

class QgistMetaKeyError(KeyError):
    pass

# class QgistMetaRequirementError(Exception): # TODO see dtype_metadata
#     pass

class QgistMetaTxtError(Exception):
    pass

class QgistPluginIdCollisionError(Exception):
    pass
