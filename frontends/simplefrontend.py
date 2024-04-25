from state import State
from filters import Filter, FilterMaker, LengthFilterMin, LengthFilterExact, LengthFilterMax, ContainsFilterMaker, PositionFilterMaker, PatternFilterMaker, RegexpFilterMaker, MorseFilterMaker
import re
from dictmanager import normalizeStreets, normalizeToAscii, DictSpecification

_RUN_EXIT = 0
_RUN_MAIN = 1
_RUN_DICTS = 2
_RUN_GROUPS = 3

PRETTYWIDTH = 300
DISPLAY_COLUMNS = 8

FILTERS: list[FilterMaker] = [LengthFilterExact, LengthFilterMax, LengthFilterMin, ContainsFilterMaker, PositionFilterMaker, PatternFilterMaker, MorseFilterMaker, RegexpFilterMaker]
NORMALIZERS = {"Prepropress strees names": normalizeStreets,
               "Normalize Umlauts et al.": normalizeToAscii}

def wait_for_enter():
    input("Press enter to continue.")

class SimpleFrontEnd:
    def __init__(self):
        pass


    @classmethod
    def pretty_print_dict(cls, d: list[str]):
        if len(d) == 0:
            print("***NO ENTRY MATCHES THE FILTERS***")
        elif len(d) <= 10:
            for entry in d:
                print(entry)
        else:
            max_len = max([len(entry) for entry in d]) + 3
            words_per_column = PRETTYWIDTH // max_len
            # print(max_len, words_per_column)
            # wait_for_enter()
            if words_per_column == 0:
                words_per_column = 1
            for index in range(len(d)):
                sep = ""
                if index % words_per_column == words_per_column-1:
                    sep = "\n"
                print("{0:<{width}}".format(d[index], width=max_len), end=sep)
            print("\n\n", end="")



    @classmethod
    def continue_read_number(cls, read_input: str, message: str) -> int | None:
        assert len(read_input) >= 1
        if len(read_input) == 1:
            read_input = input(message)
        else:
            read_input = read_input[1:]
        if len(read_input) == 0:
            return None
        try:
            read_number = int(read_input)
        except ValueError as e:
            print(f"Invalid input {e} is not a number.\nAborting.")
            return None
        if read_number < 0:
            print(f"Negative number {read_number} is not meaningful.\nAborting.")
            return None
        return read_number


    @classmethod
    def get_filter_index(cls, state: State, read_input: str) -> int | None:
        read_number = cls.continue_read_number(read_input, "Input index of filter: ")
        if read_number is None:
            return None
        if not (1 <= read_number <= len(state.selected_filters)):
            print(f"Number {read_number} out of range.\nAborting.")
            return None
        return read_number

    @classmethod
    def get_dict_index(cls, state: State, read_input: str) -> int | None:
        if len(state.dict_specs) == 0:
            print("No dictionaries loaded")
            return None
        if len(read_input) == 1 and len(state.dict_specs) == 1:
            return 1
        read_number = cls.continue_read_number(read_input, "Input index of dictionary: ")
        if read_number is None:
            return None
        if not (1 <= read_number <= len(state.dict_specs)):
            print(f"Number {read_number} out of range. Aborting")
            return None
        return read_number


    def command_print(self, state: State, read_input: str):
        dict_index = self.get_dict_index(state, read_input)
        if dict_index is None:
            return
        self.pretty_print_dict(state.filtered_dicts[dict_index - 1])
        wait_for_enter()

    def command_save(self, state: State, read_input: str):
        dict_index = self.get_dict_index(state, read_input)
        if dict_index is None:
            return
        filename = input("Please enter filename: ")
        with open(filename, "w") as f:
            for word in state.filtered_dicts[dict_index - 1]:
                f.write(word + "\n")
        input("Success. Please press enter to continue.")

    def run_main(self, state: State) -> int:
        while True:
            state.validate()
            state.sort_filters()
            self.report_status(state)

            print("\n\t\t***  Please select command: ***\n")
            if not state.active:
                print("a: Start evaluating filters", end="\t")
            else:
                print("a: Stop evaluating filters", end="\t")
            print("r: Remove filter", end="\t\t")
            print("t: (de)activate filter", end="\n")
            print("d: Manage dictionaries", end="\t\t")
            print("g: Manage fuzzyness groups", end="\t")
            print("j: Make filters fuzzy", end="\n")

            if state.active:
                print("p: Print candidates", end="\t\t")
                print("s: Save candidates to file", end="\n")

            print("Add filter:")
            for i in range(len(FILTERS)):
                print(f"    f{i+1}: {FILTERS[i]}")

            print("x: Exit", end="\n")

            read_input = input()
            if len(read_input) == 0:
                continue

            match read_input[0].lower():
                case 'x':
                    return _RUN_EXIT
                case 'a':
                    if state.active:
                        state.make_inactive()
                    else:
                        state.make_active()
                case 'r':
                    filter_index = self.get_filter_index(state, read_input)
                    if filter_index is None:
                        continue
                    state.delete_filter(filter_index)

                case 't':
                    filter_index = self.get_filter_index(state, read_input)
                    if filter_index is None:
                        continue
                    state.toggle_filter(filter_index)

                case 'd':
                    return _RUN_DICTS
                case 'g':
                    return _RUN_GROUPS
                case 'j':
                    max_errors = self.continue_read_number(read_input, "Enter the number of deviations allowed for the filters")
                    if max_errors is None:
                        continue
                    state.set_max_errors(max_errors)

                case 'p' if state.active:
                    self.command_print(state, read_input)

                case 's' if state.active:
                    self.command_save(state, read_input)

                case 'f':
                    read_input = read_input[1:]
                    try:
                        read_num = int(read_input)
                    except ValueError as e:
                        print("Invalid input")
                        wait_for_enter()
                        continue
                    if not (1 <= read_num <= len(FILTERS)):
                        print("Invalid input")
                        wait_for_enter()
                        continue
                    new_fil_maker = FILTERS[read_num-1]
                    new_fil = filter_from_FilterMaker(new_fil_maker)
                    if new_fil is None:
                        continue
                    state.add_filter(new_fil)

                case _:
                    print(f"unrecognized input: {read_input}")

    def run_dict(self, state: State):
        while True:
            state.validate()
            state.sort_filters()
            self.report_status(state)
            print("\n\t\t***  Please select command: ***\n")
            if not state.active:
                print("a: Start evaluating filters", end="\t")
            else:
                print("a: Stop evaluating filters", end="\t")
            print("r: Remove dict", end="\t\t\t")
            print("t: (de)activate dict", end="\n")
            print("f: Manage filters", end="\t\t")
            print("g: Manage fuzzyness groups", end="\t")
            print("d: Add dict", end="\n")

            if state.active:
                print("p: Print candidates", end="\t\t")
                print("s: Save candidates to file", end="\n")

            print("x: Exit", end="\n")

            read_input = input()
            if len(read_input) == 0:
                continue
            match read_input[0].lower():
                case 'a':
                    if state.active:
                        state.make_inactive()
                    else:
                        state.make_active()
                case "x":
                    return _RUN_EXIT
                case "f":
                    return _RUN_MAIN
                case "g":
                    return _RUN_GROUPS
                case 'p' if state.active:
                    self.command_print(state, read_input)
                case 's' if state.active:
                    self.command_save(state, read_input)
                case 't':
                    dict_index = self.get_dict_index(state, read_input)
                    if dict_index is None:
                        continue
                    state.toggle_dict(dict_index)
                case 'r':
                    dict_index = self.get_dict_index(state, read_input)
                    if dict_index is None:
                        continue
                    state.delete_dict(dict_index)
                case 'd':
                    fn = input("Please enter filename: ")
                    i = 1
                    print("Select normalization")
                    for normdesc, n in NORMALIZERS.items():
                        print(f"    {i}: {normdesc}")
                        i+=1
                    sel = input("Please enter number: ")
                    try:
                        sel_index = int(sel)
                        assert 1 <= sel_index <= len(NORMALIZERS)
                    except Exception as E:
                        print(f"Error {E}\nAborting.")
                        continue
                    selected_normalizer = list(NORMALIZERS.values())[sel_index-1]
                    new_spec = DictSpecification(fn, normalizer=selected_normalizer)
                    state.add_dict(new_spec)

                case _:
                    print(f"unrecognized input: {read_input}")



    def run(self, state: State):
        runner = _RUN_MAIN
        while True:
            if runner == _RUN_EXIT:
                break
            elif runner == _RUN_MAIN:
                runner = self.run_main(state)
            elif runner == _RUN_DICTS:
                runner = self.run_dict(state)
            elif runner == _RUN_GROUPS:
                print("This feature is not implemented yet.")
                wait_for_enter()
                runner = _RUN_MAIN
            else:
                raise RuntimeError("Unknown runner")



    @staticmethod
    def printseps(i: int = 80):
        print("-"*i)

    def report_status(self, state: State):
        # state.sort_filters()
        # state.compute_filtered_dicts()
        # state.validate()
        print("\n\n")
        self.printseps()
        print("\t\t\t *** STATUS ***")
        self.printseps()
        if not state.active:
            print("***Evaluation of filters is currently turned off***")
            self.printseps()
        print("Currently loaded dictionaries:")
        for i in range(len(state.dict_specs)):
            s = f"    {i+1}: {state.unfiltered_dicts[i]}"
            unfilteredsize = state.unfiltered_dicts[i].size
            filteredsize = len(state.filtered_dicts[i])
            if not state.active or not state.unfiltered_dicts[i].is_active:
                # s += f" ({unfilteredsize} entries)"
                pass
            else:
                s += f" ({filteredsize} out of {unfilteredsize} many entries pass the filters)"
            print(s)
        self.printseps()
        if len(state.selected_filters) == 0:
            print("No filters selected")
        else:
            print("Currently selected filters:")
            grouplabel = 65
            index = 1
            fils_by_gp = state.filter_by_group
            for gp in fils_by_gp.keys():
                if gp is state.StrictGroup:
                    pass
                elif gp is state.DefaultGroup:
                    if gp.max_errors != 0:
                        print(f"    The following filters are fuzzily matched, allowing a total of {gp.max_errors} deviations.")
                else:
                    print(f"    {chr(grouplabel)}: The following filters are fuzzily matched, allowing a total of {gp.max_errors} deviations.")
                    grouplabel+=1
                    if len(fils_by_gp[gp]) == 0:
                        print(f"        **NO FILTERS IN THIS GROUP**")
                for fil in fils_by_gp[gp]:
                    print(f"        {index}: {fil}")
                    index += 1
        self.printseps()

def filter_from_FilterMaker(fm: FilterMaker) -> Filter | None:
    gen = fm.create_filter_protocol()
    x = next(gen)
    try:
        while True:
            if x is None:
                return None
            if isinstance(x, Filter):
                return x
            prompt: str = x[0]
            t: type = x[1]
            read_input = input(prompt)
            if read_input == "":
                read_value = StopIteration
            else:
                try:
                    read_value = t(read_input)
                except ValueError as e:
                    print(f"Error reading input {e}\nAborting.")
                    return None
            x = gen.send(read_value)
    except Exception as e:
        print(f"Error: {e}\nAborting.")
        return None