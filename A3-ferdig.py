from socket import *

states = ["disconnected", "connected", "authorized"]
TCP_PORT = 1300  # TCP port used for communication
SERVER_HOST = "localhost"  # Set this to either hostname (domain) or IP address of the chat server

current_state = "disconnected"
must_run = True
client_socket = None  # type: socket


def quit_application():
    global must_run
    must_run = False


def send_command(command, arguments):
    global client_socket
    msg = str(command)
    if arguments == '' or arguments == None:
        msg += '\n'
    else:
        msg += ' ' + str(arguments) + '\n'
    client_socket.send(msg.encode())


def get_servers_response():
    newline_received = False
    message = ""
    while not newline_received:
        character = client_socket.recv(1).decode()
        if character == '\n':
            newline_received = True
        elif character == '\r':
            pass
        else:
            message += character
    return message


def connect_to_server():
    global client_socket
    global current_state
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect(("datakomm.work", 1300))
        current_state = 'connected'
    except IOerror as e:
        print('Error happened:', e)
        client_socket.close()
    send_command('async', None)
    response = get_servers_response()
    if response == 'modeok':
        print('Success!! Connected.')
    else:
        print("CONNECTION NOT IMPLEMENTED!")


def disconnect_from_server():
    global client_socket
    global current_state
    try:
        client_socket.close()
        current_state = 'disconnected'
    except IOError as e:
        print('Error happened:', e)
        print('You are already disconnected.')


def login():
    global current_state
    current_state = 'connected'
    username = str(input('Enter username: '))
    send_command('login', username)
    # print(get_servers_response())
    response = get_servers_response()
    if response == 'loginok':
        print('Welcome: ' + username)
        current_state = 'authorized'
    elif response == 'loginerr username already in use':
        print("Username already in use, try again.")
        login()
    elif response == 'loginerr incorrect username format':
        print("Wrong format, try again.")
        login()


def public_mld():
    mld = str(input("Enter public message: "))
    send_command('msg', mld)
    response = get_servers_response().split()
    if response[0] == 'msgerror':
        print(get_servers_response)


def priv_mld():
    global current_state
    current_state = 'authorized'
    pmld = str(input('Enter username followed by the message: '))
    send_command('privmsg', pmld)
    response = get_servers_response().split()
    if response[0] == 'msgerr':
        print(get_servers_response())
    else:
        print('Message was sent privately')


def user_list():
    global users
    send_command("users", None)
    respons = get_servers_response().split()
    if respons[0] == "users":
        respons.pop(0)
        print("List of Users:")
        [print(f"#{index + 1} {user}") for index, user in enumerate(respons)]
    return


def les_inbox():
    while True:
        send_command('inbox', None)
        innhold_innboks = get_servers_response()
        split_innhold = innhold_innboks.split()
        if innhold_innboks == 'inbox 0':
            print('Inbox is empty.')
            break
        elif split_innhold[0] == 'privmsg' or split_innhold[0] == 'msg':
            print(innhold_innboks)
        elif split_innhold[0] == 'msgok':
            pass


def get_joke():
    send_command("joke", None)
    joke_list = get_servers_response().split()
    joke_list.pop(0)
    joke = ''
    for i in range(0, len(joke_list)):
        joke += joke_list[i] + ' '
    print(joke)


"""
    The list of available actions that the user can perform
    Each action is a dictionary with the following fields:
    description: a textual description of the action
    valid_states: a list specifying in which states this action is available
    function: a function to call when the user chooses this particular action. The functions must be defined before
                the definition of this variable
    """

available_actions = [
    {
        "description": "Connect to a chat server",
        "valid_states": ["disconnected"],
        "function": connect_to_server
    },
    {
        "description": "Disconnect from the server",
        "valid_states": ["connected", "authorized"],
        "function": disconnect_from_server
    },
    {
        "description": "Authorize (log in)",
        "valid_states": ["connected", "authorized"],
        "function": login
    },
    {
        "description": "Send a public message",
        "valid_states": ["connected", "authorized"],
        "function": public_mld
    },
    {
        "description": "Send a private message",
        "valid_states": ["authorized"],
        "function": priv_mld
    },
    {
        "description": "Read messages in the inbox",
        "valid_states": ["connected", "authorized"],
        "function": les_inbox
    },
    {
        "description": "See list of users",
        "valid_states": ["connected", "authorized"],
        "function": user_list
    },
    {
        "description": "Get a joke",
        "valid_states": ["connected", "authorized"],
        "function": get_joke
    },
    {
        "description": "Quit the application",
        "valid_states": ["disconnected", "connected", "authorized"],
        "function": quit_application
    },
]


def run_chat_client():
    """ Run the chat client application loop. When this function exists, the application will stop """

    while must_run:
        print_menu()
        action = select_user_action()
        perform_user_action(action)
    print("Thanks for watching. Like and subscribe! 👍")


def print_menu():
    """ Print the menu showing the available options """
    print("==============================================")
    print("What do you want to do now? ")
    print("==============================================")
    print("Available options:")
    i = 1
    for a in available_actions:
        if current_state in a["valid_states"]:
            # Only hint about the action if the current state allows it
            print("  %i) %s" % (i, a["description"]))
        i += 1
    print()


def select_user_action():
    """
    Ask the user to choose and action by entering the index of the action
    :return: The action as an index in available_actions array or None if the input was invalid
    """
    number_of_actions = len(available_actions)
    hint = "Enter the number of your choice (1..%i):" % number_of_actions
    choice = input(hint)
    # Try to convert the input to an integer
    try:
        choice_int = int(choice)
    except ValueError:
        choice_int = -1

    if 1 <= choice_int <= number_of_actions:
        action = choice_int - 1
    else:
        action = None

    return action


def perform_user_action(action_index):
    """
    Perform the desired user action
    :param action_index: The index in available_actions array - the action to take
    :return: Desired state change as a string, None if no state change is needed
    """
    if action_index is not None:
        print()
        action = available_actions[action_index]
        if current_state in action["valid_states"]:
            function_to_run = available_actions[action_index]["function"]
            if function_to_run is not None:
                function_to_run()
            else:
                print("Internal error: NOT IMPLEMENTED (no function assigned for the action)!")
        else:
            print("This function is not allowed in the current system state (%s)" % current_state)
    else:
        print("Invalid input, please choose a valid action")
    print()
    return None


# Entrypoint for the application. In PyCharm you should see a green arrow on the left side.
# By clicking it you run the application.
if __name__ == '__main__':
    run_chat_client()
