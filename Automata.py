from prettytable import PrettyTable

class FiniteAutomaton:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.start_state = set()
        self.accept_states = set()
        self.transitions = {}

    def add_state(self, state):
        self.states.add(state)

    def add_symbol(self, symbol):
        self.alphabet.add(symbol)

    def add_start_state(self, start_state):
        self.start_state.add(start_state)

    def add_accept_state(self, accept_state):
        self.accept_states.add(accept_state)

    def add_transition(self, from_state, symbol, to_state):
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        if symbol not in self.transitions[from_state]:
            self.transitions[from_state][symbol] = set()
        self.transitions[from_state][symbol].add(to_state)

    def to_truth_table(self):
        table = PrettyTable()
        table.field_names = ["State"] + sorted(self.alphabet)

        for state in sorted(self.states):
            if state in self.start_state and state in self.accept_states:
                row = ["<--> " + state]
            elif state in self.accept_states:
                row = ["<-- " + state]
            elif state in self.start_state:
                row = ["--> " + state]
            else:
                row = [state]
            transitions = self.transitions.get(state, {})
            for symbol in sorted(self.alphabet):
                next_states = transitions.get(symbol, "-")
                row.append(" ".join(next_states) if next_states != "-" else "-")

            table.add_row(row)

        return table
    
    def complete(fa):
        if fa.is_complete():
            return fa

        sink_state = "p"
        fa.add_state(sink_state)

        for state in fa.states:
            transitions = fa.transitions.get(state, {})
            for symbol in fa.alphabet:
                if symbol not in transitions:
                    fa.add_transition(state, symbol, sink_state)

        for symbol in fa.alphabet:
            fa.add_transition(sink_state, symbol, sink_state)

        return fa

    
    def standardize(fa):
        if fa.is_standard():
            return fa
        
        new_start_state = "q0_new"
        fa.add_state(new_start_state)

        # Ajouter des transitions du nouvel état initial vers chaque état initial d'origine avec les mêmes symboles
        for start_state in fa.start_state:
            transitions = fa.transitions.get(start_state, {})
            for symbol, next_states in transitions.items():
                for next_state in next_states:
                    fa.add_transition(new_start_state, symbol, next_state)

        # Mettre à jour l'état initial pour être le nouvel état initial
        fa.start_state = {new_start_state}

        return fa



    
    def is_deterministic(self):
        for state, transitions in self.transitions.items():
            for symbol in self.alphabet:
                if transitions.get(symbol) is None:
                    return False
        return True

    def is_complete(self):
        for state in self.states:
            if state not in self.transitions:
                return False
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]:
                    return False
        return True

    def is_standard(self):
        return len(self.start_state) == 1
            

    def fa_type(self):
        fa_type = []
        if self.is_deterministic():
            fa_type.append("deterministic")
        if self.is_complete():
            fa_type.append("complete")
        if self.is_standard():
            fa_type.append("standard")
        return " ".join(fa_type) if fa_type else "not recognized"


def read_fa_from_file(filename):
    fa = FiniteAutomaton()
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("States:"):
                    states = line[7:].strip().split()
                    for state in states:
                        fa.add_state(state)
                elif line.startswith("Alphabet:"):
                    alphabet = line[9:].strip().split()
                    for symbol in alphabet:
                        fa.add_symbol(symbol)
                elif line.startswith("Start:"):
                    start_state = line[6:].strip().split()
                    for state in start_state:
                        fa.add_start_state(state)
                elif line.startswith("Accept:"):
                    accept_states = line[7:].strip().split()
                    for state in accept_states:
                        fa.add_accept_state(state)
                elif line.startswith("Transitions:"):
                    for line in file:
                        if line.strip() == "":
                            break
                        from_state, symbol, to_state = line.strip().split()
                        fa.add_transition(from_state, symbol, to_state)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    return fa


# Example usage
fa = read_fa_from_file("fa.txt")
print(fa.to_truth_table())
print(fa.fa_type())
fa.standardize()
print(fa.to_truth_table())
print(fa.fa_type())
fa.complete()
print(fa.to_truth_table())
print(fa.fa_type())