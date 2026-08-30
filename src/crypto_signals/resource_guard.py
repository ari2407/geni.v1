"""Device budget guard. Pauses ecosystem upgrades, never the signal safety gate."""
from __future__ import annotations
from dataclasses import dataclass
import os
import shutil

@dataclass(frozen=True)
class ResourceStatus:
    cpu_load: float | None
    memory_used: float | None
    disk_used: float
    pause_upgrades: bool

class ResourceGuard:
    def __init__(self, max_cpu_load: float = .85, max_memory: float = .85, max_disk: float = .90):
        self.max_cpu_load, self.max_memory, self.max_disk = max_cpu_load, max_memory, max_disk

    def status(self, path: str = ".") -> ResourceStatus:
        load = (os.getloadavg()[0] / max(1, os.cpu_count() or 1)) if hasattr(os, "getloadavg") else None
        memory = None
        try:
            values = {}
            for line in open("/proc/meminfo"):
                key, value = line.split(":", 1)
                values[key] = int(value.split()[0])
            memory = 1 - values["MemAvailable"] / values["MemTotal"]
        except (OSError, KeyError, ValueError):
            pass
        usage = shutil.disk_usage(path)
        disk = usage.used / usage.total
        pause = disk >= self.max_disk or (load is not None and load >= self.max_cpu_load) or (memory is not None and memory >= self.max_memory)
        return ResourceStatus(load, memory, disk, pause)

    def allow_upgrade(self, path: str = ".") -> bool:
        return not self.status(path).pause_upgrades
