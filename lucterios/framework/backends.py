# -*- coding: utf-8 -*-
'''
Django setting adaptater to Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2022 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from django.contrib.auth.backends import ModelBackend, UserModel


class EmailModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        if password is None:
            return
        try:
            if username is not None:
                user = UserModel._default_manager.get_by_natural_key(username)
            elif email is not None:
                user = UserModel._default_manager.get(email=email, is_active=True)
            else:
                return
        except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
