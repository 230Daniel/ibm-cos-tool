import asyncio
import run
from run import run_command, run_commands_in_batches, clear_command_log

# The file to write command output to (useful for debugging)
COMMAND_LOG_FILE = "command_log.txt"


def configure():
    global COMMAND_LOG_FILE
    run.configure(COMMAND_LOG_FILE)


async def main():
    configure()
    clear_command_log()


if __name__ == '__main__':
    asyncio.run(main())
