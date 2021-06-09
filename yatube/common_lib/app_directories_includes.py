"""
Wrapper for loading templates from "templates/includes" directories in
INSTALLED_APPS packages.
"""

import os

from django.template.loaders.filesystem import Loader as FilesystemLoader
from django.template.utils import get_app_template_dirs


class Loader(FilesystemLoader):

    def get_dirs(self):
        return get_app_template_dirs(os.path.join("templates", "includes"))
