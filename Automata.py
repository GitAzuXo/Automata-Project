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
        table.field_names = [s.replace("Îµ", "ε") for s in table.field_names]

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
        
        new_start_state = "i"
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
    

    def epsilon_closure(self, state):
        closure = {state}  # Include the initial state in the closure
        stack = [state]    # Initialize a stack with the initial state

        # Perform depth-first search to find all states reachable via epsilon transitions
        while stack:
            current_state = stack.pop()
            transitions = self.transitions.get(current_state, {})
            epsilon_transitions = transitions.get('Îµ', set())  # Retrieve epsilon transitions
            for next_state in epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return closure

    
    def is_deterministic(self):
        for state, transitions in self.transitions.items():
            # Vérifier s'il y a plus d'une transition pour un symbole
            for symbol in self.alphabet:
                if symbol in transitions and len(transitions[symbol]) > 1:
                    return False
            # Vérifier s'il y a une transition vide
            if 'Îµ' in transitions:
                return False
        return True


    def determinize(self):
        if self.is_deterministic():
            return self

        new_fa = FiniteAutomaton()

        # Compute epsilon closures for all states
        epsilon_closures = {}
        for state in self.states:
            epsilon_closures[state] = self.epsilon_closure(state)

        # Compute epsilon closure of start state
        start_closure = self.epsilon_closure(next(iter(self.start_state)))

        # Initialize variables for the determinization process
        state_mapping = {frozenset(start_closure): 'q0'}
        queue = [frozenset(start_closure)]
        visited = set()

        while queue:
            current_states = queue.pop(0)
            visited.add(current_states)

            # Check if the current set of states is an accept state
            if any(state in self.accept_states for state in current_states):
                new_fa.add_accept_state(state_mapping[current_states])

            for symbol in self.alphabet:
                next_states = set()
                for state in current_states:
                    transitions = self.transitions.get(state, {})
                    if symbol in transitions:
                        next_states.update(transitions[symbol])  # Exclude epsilon transitions

                # Compute the epsilon closure of the next states
                next_states_epsilon = set()
                for state in next_states:
                    next_states_epsilon.update(epsilon_closures[state])

                if next_states_epsilon:
                    next_state_frozen = frozenset(next_states_epsilon)
                    if next_state_frozen not in state_mapping:
                        new_state_name = f'q{len(state_mapping)}'
                        state_mapping[next_state_frozen] = new_state_name
                        queue.append(next_state_frozen)
                        new_fa.add_state(new_state_name)
                        if any(state in self.accept_states for state in next_state_frozen):
                            new_fa.add_accept_state(new_state_name)

                    new_fa.add_transition(state_mapping[current_states], symbol, state_mapping[next_state_frozen])

        # Set the start state of the new automaton
        new_fa.add_start_state('q0')

        return new_fa





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
fa = read_fa_from_file("automatas/31.txt")
print(fa.to_truth_table())
print(fa.fa_type())
fa.standardize()
print(fa.to_truth_table())
print(fa.fa_type())
fa.complete()
print(fa.to_truth_table())
print(fa.fa_type())
fa.determinize()
print(fa.to_truth_table())
print(fa.fa_type())
