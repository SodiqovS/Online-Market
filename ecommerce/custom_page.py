from typing import TypeVar

from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from fastapi_pagination.links import Page

T = TypeVar('T')

CustomPage = CustomizedPage[
    Page[T],
    UseParamsFields(size=10),  #
]
