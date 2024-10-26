from slowbeast.symexe.options import SEOptions
from slowbeast.symexe.threads.configuration import Unfolding, Configuration
from slowbeast.symexe.threads.interpreter import SymbolicInterpreter
from slowbeast.symexe.threads.state import TSEState


class PORSymbolicInterpreter(SymbolicInterpreter):

    def __init__(self, P, ohandler=None, opts: SEOptions = SEOptions()) -> None:
        print("Initiating the UPOR executor")
        super().__init__(P, ohandler, opts)
        self.bot_state = TSEState.createBottom()
        self.unfolding = Unfolding()

    def get_extended_states(self) -> TSEState:
        pass

    def get_enabled_states(self) -> TSEState:
        pass

    def run(self) -> int:
        self.prepare()
        self.bot_state = self.initial_states()[0]
        self.unfolding.events[0] = self.bot_state
        self.running_config = Configuration()
    
    def explore(self, current_config: Configuration, 
                avoiding_config: Configuration, 
                assisting_config: Configuration ) -> None:
        """ DFS exploring and creating possible configurations."""
        self.master_state.extend(self.executing_state.get_extented_instructions())
        
        enabled_in_c = self.executing_state.get_enabled_instructions()
        if enabled_in_c.len() == 0 \
            or enabled_in_c is None:
            return
        
        state_a = self.get_assisting_state()
        if state_a is None:
            exec_instruction = enabled_in_c[0]
        else:
            for e in state_a.trace:
                if e in enabled_in_c:
                    exec_instruction = e
                    break
        assert exec_instruction is not None, "event not chosen properly in Explore"
        
        
        
    
                    
    # Set C
    def get_executing_state(self) -> TSEState:
        pass

    # Set A in the algorithm
    def get_assisting_state(self) -> TSEState:
        pass

    # Set D
    def get_avoiding_state(self) -> TSEState:
        pass

    # Set U
    def get_master_state(self) -> TSEState:
        pass

    # Set G
    def get_deletable_states(self) -> TSEState:
        pass