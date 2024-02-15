from aiogram.types import BotCommand



commands = [
    BotCommand(
        command='start',
        description='start a bot'
    ),
    # BotCommand(
    #     command='addTask',
    #     description='Add a new task'
    # ),
    BotCommand(
        command='allTasks',
        description='Show all tasks'
    ),
    BotCommand(
        command='allWords',
        description='Show all words'
    ),
    BotCommand(
        command='getWord',
        description='Get a word'
    ),

]
