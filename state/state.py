from typing import Tuple, Union
from dictmanager import DictSpecification, UnfilteredDict
from filters import Filter, apply_filter_groups, FilterWithGroup, Group

class State:
    dict_specs: list[DictSpecification]
    filtered_dicts: list[list[str]]
    unfiltered_dicts: list[UnfilteredDict]

    active: bool

    selected_filters: list[FilterWithGroup]
    groups: list[Group]  # excluding the DefaultGroup
    DefaultGroup: Group
    StrictGroup: Group

    def __init__(self, dict_specs: list[DictSpecification], selected_filters: list[FilterWithGroup] = None, error_limit: int = 0, do_eval: bool = False, groups: list[Group] = None):
        """
        Initialize the state using the given dict specification and the selected set of filters.
        NOTE: This does not actually run the filters (to allow users to deactivate filters in case of error / too slow execution)
        """
        self.dict_specs = dict_specs
        self.unfiltered_dicts = [UnfilteredDict(spec) for spec in dict_specs]
        self.filtered_dicts = [[] for _ in dict_specs]  # default to ensure invariant that is has the right length.
        self.active = do_eval
        self.DefaultGroup = Group(error_limit)
        self.StrictGroup = Group(0)

        if groups is None:
            self.groups = []
        else:
            self.groups = groups

        if selected_filters is None:
            self.selected_filters = []
        else:
            self.selected_filters = selected_filters[:]
            for f in self.selected_filters:
                if f.g is None:
                    if f.f.allow_errors:
                        f.g = self.DefaultGroup
                    else:
                        f.g = self.StrictGroup

        self.sort_filters()
        self.compute_filtered_dicts()
        self.validate()

    def validate(self):
        assert len(self.dict_specs) == len(self.filtered_dicts)
        assert len(self.dict_specs) == len(self.unfiltered_dicts)
        assert self.DefaultGroup is not None
        for fil in self.selected_filters:
            assert fil.g in self.groups or fil.g is self.DefaultGroup or fil.g is self.StrictGroup
            if fil.f.allow_errors:
                assert fil.g is not self.StrictGroup
            else:
                assert fil.g is self.StrictGroup
        assert self.StrictGroup.max_errors == 0

    @property
    def filter_by_group(self) -> dict[Group, list[Filter]]:
        """
        Returns the list of filters, sorted by group (as a dict)
        """
        d = {self.StrictGroup: [], self.DefaultGroup: []}
        for g in self.groups:
            d[g] = []
        for fg in self.selected_filters:
            d[fg.g] += [fg.f]
        return d

    def make_active(self):
        self.active = True
        self.compute_filtered_dicts()

    def make_inactive(self):
        self.active = False
        self.compute_filtered_dicts()

    def compute_filtered_dicts(self):
        """
        runs all active filters on all dicts
        """

        if self.active:
            self.filtered_dicts = [apply_filter_groups(self.filter_by_group, unfiltered_dict.L) for unfiltered_dict in self.unfiltered_dicts]
        else:
            self.filtered_dicts = [[] for _ in self.unfiltered_dicts]

    def reload(self):
        """
        reloads all dicts and runs all filters on all dicts
        """
        for u in self.unfiltered_dicts:
            u.reload()
        self.compute_filtered_dicts()

    def activate_dict(self, i: int):
        """
        activates the i'th (1-indexed) input dict
        """
        assert i >= 1
        assert i <= len(self.dict_specs)
        self.dict_specs[i-1].make_active()
        self.unfiltered_dicts[i-1].make_active()
        if self.active:
            self.filtered_dicts[i-1] = apply_filter_groups(self.filter_by_group, self.unfiltered_dicts[i-1].L)

    def deactivate_dict(self, i: int):
        """
        activates the i'th (1-indexed) input dict
        """
        assert i >= 1
        assert i <= len(self.dict_specs)
        self.dict_specs[i-1].make_inactive()
        self.unfiltered_dicts[i-1].make_inactive()
        self.filtered_dicts[i-1] = []  # Do this unconditionally

    def toggle_dict(self, i: int):
        assert 1 <= i <= len(self.dict_specs)
        if self.unfiltered_dicts[i-1].is_active:
            self.deactivate_dict(i)
        else:
            self.activate_dict(i)

    def delete_dict(self, i: int):
        """
        deletes the i'th (1-indexed) input dict
        """
        assert i >= 1
        assert i <= len(self.dict_specs)
        del self.dict_specs[i-1]
        del self.unfiltered_dicts[i-1]
        del self.filtered_dicts[i-1]

    def add_dict(self, new_dict_spec):
        """
        Adds new dict and evaluates all active filters on it.
        """
        self.dict_specs += [new_dict_spec]
        new_unfiltered_dict = UnfilteredDict(new_dict_spec)
        self.unfiltered_dicts += [new_unfiltered_dict]
        self.compute_filtered_dicts()

    def add_filter(self, new_filter: Union[Filter, FilterWithGroup]):
        """
        Adds the new filter and evaluates it.
        """
        if isinstance(new_filter, Filter):
            if new_filter.allow_errors:
                new_filter = FilterWithGroup(new_filter, self.DefaultGroup)
            else:
                new_filter = FilterWithGroup(new_filter, self.StrictGroup)
        assert isinstance(new_filter, FilterWithGroup)
        self.selected_filters += [new_filter]
        self.sort_filters()
        self.compute_filtered_dicts()  # could simplify by only computing current

    def delete_filter(self, i: int):
        """
        Removes the i'th filter (1-indexed)
        """
        assert 1 <= i <= len(self.selected_filters)
        del self.selected_filters[i-1]
        self.compute_filtered_dicts()


    def toggle_filter(self, i: int):
        """
        toggles activity of the i'th filter (1-indexed)
        """
        assert 1 <= i <= len(self.selected_filters)
        self.selected_filters[i - 1].toggle_active()
        self.compute_filtered_dicts()
    def activate_filter(self, i: int):
        """
        Activates the i'th filter (1-indexed)
        """
        assert 1 <= i <= len(self.selected_filters)
        self.selected_filters[i-1].make_active()
        self.compute_filtered_dicts()

    def deactivate_filter(self, i: int):
        """
        Deactivates the i'th filter (1-indexed)
        """
        assert 1 <= i <= len(self.selected_filters)
        self.selected_filters[i-1].make_inactive()
        self.compute_filtered_dicts()

    def sort_filters(self):
        d = self.filter_by_group
        for gp in d.keys():
            d[gp].sort(key=lambda x: x.priority)
        # self.selected_filters.sort(key=lambda x: x.f.priority)
        new_filter_list = [FilterWithGroup(fil, self.StrictGroup) for fil in d[self.StrictGroup]]
        new_filter_list += [FilterWithGroup(fil, self.DefaultGroup) for fil in d[self.DefaultGroup]]
        for gp in self.groups:
            new_filter_list += [FilterWithGroup(fil, gp) for fil in d[gp]]
        self.selected_filters = new_filter_list
        self.validate()

    def add_group(self, max_errors):
        new_group = Group(max_errors)
        self.groups += [new_group]


    def delete_group(self, i: int):
        """
        Deletes the i'th group (1-indexed)
        """
        assert 1 <= i <=len(self.groups)
        gp = self.groups[i-1]
        for fil in self.selected_filters:
            if fil.g is gp:
                fil.g = self.DefaultGroup
        del self.groups[i-1]
        self.validate()
        self.compute_filtered_dicts()

    def add_filter_to_group(self, filter_index: int, group_index: int):
        assert 1 <= filter_index <= len(self.selected_filters)
        assert 1 <= group_index <= len(self.groups)
        assert self.selected_filters[filter_index-1].f.allow_errors
        self.selected_filters[filter_index-1].g = self.groups[group_index-1]
        self.validate()
        self.sort_filters()
        self.validate()
        self.compute_filtered_dicts()

    def remove_filter_from_group(self, filter_index: int):
        assert 1 <= filter_index <= len(self.selected_filters)
        assert self.selected_filters[filter_index-1].g is not self.StrictGroup
        self.selected_filters[filter_index-1].g = self.DefaultGroup
        self.validate()
        self.sort_filters()
        self.validate()
        self.compute_filtered_dicts()

    def set_max_errors(self, max_errors: int = 0):
        # We actually modify the existing object, because comparison is done via "is"
        self.DefaultGroup.max_errors = max_errors
        self.compute_filtered_dicts()
