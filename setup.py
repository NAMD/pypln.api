# -*- coding:utf-8 -*-
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(name='pypln.api',
      version='0.1.1',
      author=('Álvaro Justen <alvarojusten@gmail.com>',
              'Flávio Amieiro <flavioamieiro@gmail.com>'),
      author_email='pypln@googlegroups.com',
      url='https://github.com/NAMD/pypln.api',
      description="Pythonic library to access PyPLN's Web interface",
      zip_safe=True,
      packages=find_packages(),
      namespace_packages=['pypln'],
      install_requires=['requests'],
      test_suite='nose.collector',
      license='GPL3',
)
