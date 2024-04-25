from typing import Callable
from abc import ABC, abstractmethod

class Filter(ABC):
    """
    Filter that can be used to filter a given list of strings
    This is mostly a container / ABC to unify the backend
    """

    allow_errors: bool  # whether the filter allows "fuzzy" matching
    priority: int  # priority of the filter. Lower priority filters get applied first. This is purely for efficiency. Default = 0
    display: str  # display this to the user
    active: bool  # is the filter active

    def __init__(self, *, allow_errors: bool = False, priority: int = 0, display: str, active: bool = True):
        self.allow_errors = allow_errors
        self.priority = priority
        self.display = display
        self.active = active

    def __str__(self) -> str:
        s: str = self.display
        if not self.active:
            s+=" (inactive)"
        return s

    def make_active(self):
        self.active = True

    def make_inactive(self):
        self.active = False

    def toggle_active(self):
        self.active = not self.active

    @abstractmethod
    def apply(self, input_list: list[str]) -> list[str]:
        """
        apply the filter to the given input list.
        NOTE: The output list must be a new mutable object that does not track the input.
        """
        raise NotImplementedError

    def apply_with_errors(self, input_list: list[str], *, max_errors: int = 0) -> list[list[str]]:
        """
        apply the filer to the given input list
        Outputs a sequence L[0], ..., L[max_errors] of disjoint lists where each L[i] is the result of
        applying the filter while allowing i errors.
        """
        ret: list[list[str]] = [[] for _ in range(max_errors+1)]
        ret[0] = self.apply(input_list)
        return ret

def from_error_count(input_list: list[str], *, max_errors: int, fun: Callable[[str], int]) -> list[list[str]]:
    """
    from_error_count is an implementation for apply_with_errors from a callable fun(str) -> Number of errors
    where fun(s) == -1 means "discard"
    """
    output_lists = [[] for _ in range(max_errors+1)]
    for input_string in input_list:
        num_errs = fun(input_string)
        if num_errs == -1:
            continue
        if num_errs > max_errors:
            continue
        assert 0 <= num_errs <= max_errors
        output_lists[num_errs] += [input_string]
    return output_lists


class Group:
    max_errors: int
    def __init__(self, max_errors: int):
        self.max_errors = max_errors


class FilterWithGroup:
    f: Filter
    g: Group
    def __init__(self, f: Filter, g: Group = None):
        self.f = f
        self.g = g

    def make_active(self):
        self.f.make_active()

    def make_inactive(self):
        self.f.make_inactive()

    def toggle_active(self):
        self.f.toggle_active()

def apply_filters(filters: list[Filter], input_list: list[str], *, max_errors: int = 0) -> list[str]:
    """
    apply all each filter among filters that is active on the given input list, allowing a total of max_errors errors.
    """

    out: list[list[str]] = [[] for _ in range(max_errors+1)]
    out[0] = input_list[:]

    # out[i] contains all elements from the input_list that so far succeeded with i total errors

    for individual_filter in filters:
        if individual_filter.active:
            new_out = [[] for _ in range(max_errors+1)]
            for i in range(max_errors+1):
                filter_res = individual_filter.apply_with_errors(out[i], max_errors=max_errors-i)
                for j in range(max_errors-i+1):
                    new_out[i+j] += filter_res[j]
            out = new_out[:]
    ret = []
    for i in range(max_errors+1):
        ret += out[i]
    return ret

def apply_filter_groups(filters_by_group: dict[Group, list[Filter]], input_list: list[str]) -> list[str]:
    out = input_list[:]
    for gp, list_of_filters in filters_by_group.items():
        out = apply_filters(list_of_filters, out, max_errors=gp.max_errors)
    return out


class SimpleFilter(Filter):
    def __init__(self, fun, display: str, *, priority: int = 0):
        super().__init__(allow_errors=False, priority=priority, display=display, active=True)
        self.fun = fun

    def apply(self, input_list: list[str]) -> list[str]:
        return [x for x in input_list if self.fun(x)]

class BinaryFilter(Filter):
    def __init__(self, fun, display: str, *, priority: int = 0):
        super().__init__(allow_errors=True, display=display, priority=priority, active=True)
        self.fun = fun


    def apply(self, input_list: list[str]) -> list[str]:
        return [x for x in input_list if self.fun(x)]

    def apply_with_errors(self, input_list: list[str], *, max_errors: int = 0) -> list[list[str]]:
        assert max_errors >= 0
        if max_errors == 0:
            return [self.apply(input_list)]
        out = [[] for _ in range(max_errors+1)]
        fun = self.fun
        for s in input_list:
            if fun(s):
                out[0] += [s]
            else:
                out[1] += [s]
        return out



class FilterMaker(ABC):
    description: str

    def __init__(self, *, description: str, **kwargs):
        self.description = description

    def __str__(self):
        return self.description

    @abstractmethod
    def create_filter_protocol(self):
        pass

# This could be function (taking description, prompts, conditions and initializeFilter as arguments)
# Making it a class is just syntactic suger to write it more nicely.
class FilterMakerMaker(ABC):
    description: str = None
    prompts: dict[str, type] = None
    conditions: list[Callable] = None
    num_args: int = 0

    @classmethod
    def make_FilterMaker(cls) -> FilterMaker:
        class NewFilterMaker(FilterMaker):
            assert cls.description is not None
            if cls.prompts is None:
                cls.prompts = []
            if cls.conditions is None:
                cls.conditions = [None for _ in cls.prompts.keys()]
            assert len(cls.prompts) == len(cls.conditions)
            
            def create_filter_protocol(self):
                args: list = []
                i = 0
                for prompt, t in cls.prompts.items():
                    next_arg = yield prompt, t
                    if next_arg is StopIteration:
                        break
                    if cls.conditions[i] is not None:
                        cls.conditions[i](next_arg)  # may raise exception
                    args += [next_arg]
                    i += 1
                if len(args) < cls.num_args:
                    yield None
                else:
                    yield cls.initializeFilter(*args)
                raise StopIteration

            def __init__(self, *, description: str, **kwargs):
                super().__init__(description=description, **kwargs)

        return NewFilterMaker(description=cls.description)

    @classmethod
    @abstractmethod
    def initializeFilter(cls, *args) -> Filter:
        pass

