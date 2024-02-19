from string import ascii_uppercase as ascii
from typing import Optional


class MenuError(Exception):
    """Exceptions raised for errors in the Menu class."""
    def __init__(self, message):
        super().__init__(message)


class Menu:
    """Provides an interactive menu interface in the console.

    Allows adding, removing, and displaying menu options with associated callback functions.
    Supports both numerical and alphabetical selection input, and can optionally loop until
    explicitly exited."""
    def __init__(self, title: Optional[str] = "", header: Optional[str] = "", prompt: Optional[str] = "Choice", loop_menu: Optional[bool] = False, alfa: Optional[bool] = False):
        self.menu_options = []
        self.title = title
        self.header = header
        self.prompt = prompt
        self.loop_menu = loop_menu
        self.alfa = alfa
        self.changed = False
        self.menu = "" # Saves menu between displays

    def display(self):
        if len(self.menu_options) == 0:
            raise MenuError("No menu options defined. Add some options first")
        
        if self.changed:
            self._generate_menu()
            self.changed = False

        while True:
            print(self.menu)
            self._input()
            
            if not self.loop_menu:
                break 
            
    def add_option(self, option_text, callback, index = None):
        if not callable(callback):
            raise MenuError(f"Object ('{callback}') of the menu option ('{option_text}') is not a callable object. Ensure that it's callable and passed correctly.")
        
        if index is None:
            self.menu_options.append((option_text, callback))
        else:
            self.menu_options.insert(index, (option_text, callback))    

        self.changed = True
    
    def remove_option(self, index):
        if 0 <= index < len(self.menu_options):
            self.menu_options.pop(index)
            self.changed = True
        else:
            raise MenuError(f"No menu item exists at index {index}.")
        
    def exit(self):
        self.loop_menu = False
        print()
        
    def _generate_menu(self):
        gen_menu = ""

        if self.title:
            gen_menu += f"\n\n-=-=-=-=-= {self.title} =-=-=-=-=-=-"
        
        if self.header:
            gen_menu += f"\n\n{self.header}\n"

        for i, option in enumerate(self.menu_options):
            gen_menu += f"\n{i + 1}. {option[0]}" if not self.alfa else f"\n{ascii[i]}. {option[0]}"
        
        gen_menu += "\n"
        self.menu = gen_menu
    
    def _input(self):
        while True:
            try:
                choice = input(f"{self.prompt}: ")
                
                if self.alfa:
                    option = ascii.index(choice.upper())
                else:
                    option = int(choice) - 1

                if 0 <= option <= len(self.menu_options) - 1:
                    _, callback = self.menu_options[option]
                    callback()
                    break

                else:
                    raise ValueError

            except ValueError:
                if not self.alfa:
                    print(f"\nEnter a number between 1-{len(self.menu_options)}\n")
                else:
                    print(f"\nEnter a value between A-{ascii[len(self.menu_options) - 1]}\n")
    
    def _interactive_input(self):
        pass


def main():
    title = "EXAMPLE-PROGRAM"
    header = "A menu!"
    prompt = "Choice"
    loop = False # Defaults to False
    alfa = True # Defaults to False

    argument_example = "\nArgument passed!"
    menu = Menu(title, header, prompt, loop, alfa)
    menu.add_option("Cool stuff", callback_example)
    menu.add_option("Crazy stuff", callback_example)
    menu.add_option("Amazing stuff", lambda: callback_example(argument_example)) # Use lambda to pass functions with arguments
    menu.add_option("Exit", menu.exit)
    menu.display()


def callback_example(message = "\nDoing something!"):
    print(message)


if __name__ == "__main__":
    main()

# Returvärden i anropande funktion?
# Custom exit kriterier?
# Funktion för undermenyer, childklasser?
# Funktion för att välja "[x]. Alternativ" där "x" är en markering som går att styra upp/ned med piltangenterna