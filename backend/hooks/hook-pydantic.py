"""PyInstaller hook for Pydantic v2 support."""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all pydantic submodules
hiddenimports = collect_submodules('pydantic')
hiddenimports += collect_submodules('pydantic_core')

# Ensure critical pydantic_core modules are included
hiddenimports += [
    'pydantic_core._pydantic_core',
    'pydantic.deprecated.decorator',
    'pydantic.deprecated.json',
]

# Collect data files (if any)
datas = collect_data_files('pydantic')
datas += collect_data_files('pydantic_core')
