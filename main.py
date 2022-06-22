from enum import Enum
import string

valid_input_currency = [5, 10, 25, 100, 200, 500, 1000, 2000, 5000, 10000]

valid_change_currency = [5, 10, 25, 100, 200]

valid_purchase_items = {"Candy Bar": 200, "Chips": 150, "Soda": 100}

main_menu_options = ["Add Funds", "Purchase Item", "Return Change"]

# Pre-defined error messages
INVALID_INPUT_MESSAGE = "Invalid input given. {} is not a valid input"
INSUFFICIENT_FUNDS_MESSAGE = (
    "Insufficient Funds, please change your selection or add more funds."
)
RETURN_CHANGE_PROMPT = "Press y to confirm, any other button to return to the Main Menu"


# Just an enum for the easy indication of current screen
class VENDING_SCREEN(Enum):
    MAIN_MENU = 0
    ADD_FUNDS = 1
    PURCHASE_ITEM = 2
    RETURN_CHANGE = 3


# So instead of hard coding nice looking menu pages, just generate them from the above arrays and lists
screen_prompts = {
    VENDING_SCREEN.MAIN_MENU: "~ Main Menu ~\n\n%s"
    % "\n".join(
        ["{}: {}".format(index, value) for index, value in enumerate(main_menu_options)]
    ),
    VENDING_SCREEN.ADD_FUNDS: "~ Adding Funds ~\n\n%s"
    % "\n".join(
        [
            "{}: ${:.2f}".format(index, value / 100)
            for index, value in enumerate(valid_input_currency)
        ]
    ),
    VENDING_SCREEN.PURCHASE_ITEM: "~ Purchase Item ~\n\n%s"
    % "\n".join(
        [
            "{}: {} - ${:.2f}".format(index, value, valid_purchase_items[value] / 100)
            for index, value in enumerate(valid_purchase_items)
        ]
    ),
    VENDING_SCREEN.RETURN_CHANGE: "~ Return Change ~\n\n" + RETURN_CHANGE_PROMPT,
}


class MachineState:
    screen: VENDING_SCREEN
    exit_program: bool
    user_message: string
    current_stored_value: int

    def __init__(self):
        self.screen = VENDING_SCREEN.MAIN_MENU
        self.exit_program = False
        self.current_stored_value = 0
        self.user_message = ""

    # Main machine loop code
    def run_vending_machine(self):
        while not self.exit_program:
            inp = self.gather_input()
            self.process_input(inp)

    # TODO Since this is assuming regular currency, a greedy algorithm works, but ideally this would use some sort of DP approach if we were looking for least # of coins
    @staticmethod
    def get_change(current_value):
        res = {}
        for return_coin in sorted(valid_change_currency, reverse=True):
            res[return_coin] = current_value // return_coin
            current_value -= res[return_coin] * return_coin
        return res

    # Just a default pretty print of the change returning
    @staticmethod
    def print_change(change_dict):
        print("\n~~~ CHANGE RETURNED ~~~")
        for return_coin in change_dict:
            if change_dict[return_coin] > 0:
                print(
                    "${:.2f} -> {}".format(return_coin / 100, change_dict[return_coin])
                )
        print("~~~ CHANGE RETURNED ~~~")

    # Gathering and processing human input for machine interaction
    def gather_input(self):
        print()
        if self.user_message != None:
            # For any time the machine wants to prompt the user with information (i.e. error message) it will get displayed here and cleared
            print(self.user_message)
            self.user_message = None
        inp = input(
            screen_prompts[self.screen]
            + ("\nb: Back" if self.screen != VENDING_SCREEN.MAIN_MENU else "")
            + "\nx: Exit\n"
            + "Current change in the system: ${:.2f}\n".format(
                self.current_stored_value / 100
            )
            + "\nEnter Selection: "
        )
        return inp.lower()  # Always cleaning the input

    # Hard coded x/b for exits and main menu returns. If there was more time a reasonable history for multi-level depth pages makes sense as opposed to hard sending back to main
    def process_input(self, inp):
        if inp == "x":
            self.exit_program = True
        elif inp == "b":
            self.screen = VENDING_SCREEN.MAIN_MENU
        else:
            screen_functions[self.screen](self, inp)

    # Section defining the functionality of each page of the machine
    def run_main_menu(self, inp):
        try:
            # A bit of a hack to navigate, alowing -1 to TECHNICALLY be valid, but it sends it back to the main menu without error message
            self.screen = VENDING_SCREEN(int(inp) + 1)
        except:
            self.user_message = INVALID_INPUT_MESSAGE.format(inp)

    def run_add_funds(self, inp):
        try:
            self.current_stored_value += valid_input_currency[int(inp)]
        except:
            self.user_message = INVALID_INPUT_MESSAGE.format(inp)

    def run_purchase_items(self, inp):
        try:
            item_selection = list(valid_purchase_items.keys())[int(inp)]
            item_selection_price = valid_purchase_items[item_selection]
            if self.current_stored_value < item_selection_price:
                # The user doesnt have the funds necessary, boot them back out, and tell them that. Probably should add "you need X more to purchase" but that seems excessive
                self.user_message = INSUFFICIENT_FUNDS_MESSAGE
            else:
                # Since the purchase was successful, remove the price of the item from their cash stack and prmpt for change or not
                self.current_stored_value -= item_selection_price
                print(
                    "Purchased {} for ${:.2f}".format(
                        item_selection, item_selection_price / 100
                    )
                )
                print(
                    "There is ${:.2f} remaining in the machine".format(
                        self.current_stored_value / 100
                    )
                )
                # Another slight hack, since the run_return_change function only ~does anything~ when the input is 'y', just piggy back off that and use it verbatum without changing screens
                self.run_return_change(input("Return Change?\n" + RETURN_CHANGE_PROMPT))
        except:
            self.user_message = INVALID_INPUT_MESSAGE.format(inp)

    def run_return_change(self, inp):
        if inp == "y":
            MachineState.print_change(
                MachineState.get_change(self.current_stored_value)
            )
            self.current_stored_value = 0
        self.screen = VENDING_SCREEN.MAIN_MENU


# linking the screens to their intended functionality
screen_functions = {
    VENDING_SCREEN.MAIN_MENU: MachineState.run_main_menu,
    VENDING_SCREEN.ADD_FUNDS: MachineState.run_add_funds,
    VENDING_SCREEN.PURCHASE_ITEM: MachineState.run_purchase_items,
    VENDING_SCREEN.RETURN_CHANGE: MachineState.run_return_change,
}

if __name__ == "__main__":
    ms = MachineState()
    ms.run_vending_machine()
