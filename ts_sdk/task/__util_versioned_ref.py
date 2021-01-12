from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class VersionedRef:
    composite: Optional[str] = None
    namespace: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None

    def __init__(self, composite=None, namespace=None, name=None, version=None):
        """Converts this VersionedRef into canonical form
        
        After a call to this function, the composite field matches the
        other three fields. The function raises an exception if the
        field values are inconsistent.
        """

        if composite is None:
            self.namespace, self.name, self.version = namespace, name, version
            self.composite = f"{namespace}/{name}:{version}"
            return

        m = re.fullmatch("(.*)/(.*):(.*)", composite)
        if m is None:
            raise ValueError("versioned ref doesn't match namespace/name:version")
        self.composite = composite
        self.namespace, self.name, self.version = m.groups()

        if namespace is not None and namespace != self.namespace:
            raise ValueError("inconsistent namespace")
        if name is not None and name != self.name:
            raise ValueError("inconsistent name")
        if version is not None and version != self.version:
            raise ValueError("inconsistent version")
