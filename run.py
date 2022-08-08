import asyncio
import math
from datetime import datetime
from typing import List

global COMMAND_LOG_FILE


def configure(command_log_file: str):
    global COMMAND_LOG_FILE
    COMMAND_LOG_FILE = command_log_file


async def run_command(command: List[str]) -> str:
    start = datetime.now()
    stdout, stderr = await _run_command(command)
    finish = datetime.now()

    seconds_taken = round((finish - start).total_seconds(), 3)
    _write_to_command_log(f"---SINGLE COMMAND---\n\n"
                          f"Started: {start.strftime('%Y-%m-%d %H:%M:%S')}\n"
                          f"Finished: {finish.strftime('%Y-%m-%d %H:%M:%S')}\n"
                          f"Took {seconds_taken} seconds\n\n"
                          f"command: {command}\n"
                          f"stdout: {stdout}\n"
                          f"stderr: {stderr}\n\n")

    return stdout.decode("utf-8")


async def run_commands_in_batches(commands: List[List[str]], batch_size: int) -> List[str]:
    batches = math.ceil(len(commands) / batch_size)
    results = []
    for batch_num in range(0, batches):
        batch_start_index = batch_num * batch_size
        batch_end_index = batch_start_index + batch_size
        commands_in_batch = commands[batch_start_index:batch_end_index]

        results.extend(
            await _run_command_batch(commands_in_batch))

        if batch_num + 1 < batches:
            print(f"   {round(((batch_num + 1) / batches) * 100)}% complete...")

    print("   done")
    return results


async def _run_command(command: List[str]) -> (bytes, bytes):
    program = command[0]
    args = command[1:]

    process = await asyncio.create_subprocess_exec(
        program,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    return await process.communicate()


async def _run_command_batch(commands: List[List[str]]) -> List[str]:
    tasks = []
    for command in commands:
        tasks.append(
            asyncio.create_task(
                _run_command(command)))

    start = datetime.now()
    await asyncio.gather(*tasks)
    finish = datetime.now()

    seconds_taken = round((finish - start).total_seconds(), 3)
    command_log_output = [
        f"---NEW BATCH---\n\n"
        f"Commands: {len(commands)}\n"
        f"Started: {start.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Finished: {finish.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Took {seconds_taken} seconds\n\n"]

    results = []
    for i in range(len(tasks)):
        stdout, stderr = tasks[i].result()
        results.append(stdout.decode("utf-8"))
        command_log_output.append(f"command: {commands[i]}\n"
                                  f"stdout: {stdout}\n"
                                  f"stderr: {stderr}\n\n")

    _write_to_command_log(*command_log_output)

    return results


def clear_command_log():
    global COMMAND_LOG_FILE

    f = open(COMMAND_LOG_FILE, 'w')
    f.close()


def _write_to_command_log(*lines: str) -> None:
    global COMMAND_LOG_FILE

    f = open(COMMAND_LOG_FILE, 'a')
    f.writelines(lines)
    f.close()
