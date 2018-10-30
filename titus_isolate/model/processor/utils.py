from functools import reduce

from titus_isolate.model.processor.core import Core
from titus_isolate.model.processor.cpu import Cpu
from titus_isolate.model.processor.package import Package
from titus_isolate.model.processor.thread import Thread

DEFAULT_PACKAGE_COUNT = 2
DEFAULT_CORE_COUNT = 4
DEFAULT_THREAD_COUNT = 2
DEFAULT_TOTAL_THREAD_COUNT = DEFAULT_PACKAGE_COUNT * DEFAULT_CORE_COUNT * DEFAULT_THREAD_COUNT


def get_empty_threads(threads):
    return [t for t in threads if not t.is_claimed()]


def get_emptiest_core(package):
    emptiest_core = package.get_cores()[0]
    curr_empty_thread_count = len(emptiest_core.get_empty_threads())

    for core in package.get_cores()[1:]:
        new_empty_thread_count = len(core.get_empty_threads())
        if new_empty_thread_count > curr_empty_thread_count:
            emptiest_core = core
            curr_empty_thread_count = new_empty_thread_count

    return emptiest_core


def is_cpu_full(cpu):
    empty_threads = reduce(list.__add__, [p.get_empty_threads() for p in cpu.get_packages()])
    return len(empty_threads) == 0


def get_cpu(
        package_count=DEFAULT_PACKAGE_COUNT,
        cores_per_package=DEFAULT_CORE_COUNT,
        threads_per_core=DEFAULT_THREAD_COUNT):

    packages = []
    for p_i in range(package_count):

        cores = []
        for c_i in range(cores_per_package):
            cores.append(
                Core(c_i, __get_threads(p_i, c_i, package_count, cores_per_package, threads_per_core)))

        packages.append(Package(p_i, cores))

    return Cpu(packages)


def __get_threads(package_index, core_index, package_count, core_count, thread_count):
    threads = []
    for row_index in range(thread_count):
        offset = row_index * package_count * core_count
        index = offset + package_index * core_count + core_index
        threads.append(Thread(index))

    return threads


# Workloads
def get_workload_ids(cpu):
    return set([thread.get_workload_id() for thread in cpu.get_threads() if thread.is_claimed()])


def get_packages_with_workload(cpu, workload_id):
    return [package for package in cpu.get_packages() if is_on_package(package, workload_id)]


def is_on_package(package, workload_id):
    return len(get_threads_with_workload(package, workload_id)) > 0


def get_threads_with_workload(core, workload_id):
    return [thread for thread in core.get_threads() if thread.get_workload_id() == workload_id]