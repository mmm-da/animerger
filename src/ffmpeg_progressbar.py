import re
import asyncio
from termcolor import colored
from alive_progress import alive_bar

async def _read_stream(stream, cb):  
    while True:
        line = await stream.readline()
        if line:
            cb(line)
        else:
            break

async def _stream_subprocess(cmd, stdout_cb, stderr_cb):  
    process = await asyncio.create_subprocess_exec(*cmd,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    await asyncio.wait([
        _read_stream(process.stdout, stdout_cb),
        _read_stream(process.stderr, stderr_cb)
    ])
    return await process.wait()


def execute(cmd:list, stdout_cb, stderr_cb):  
    loop = asyncio.get_event_loop()
    rc = loop.run_until_complete(
        _stream_subprocess(
            cmd,
            stdout_cb,
            stderr_cb,
    ))
    loop.close()
    return rc

# Global variables used in callbacks
total_duration = None
current_duration = None
stderr_log = []

def exec_with_progress(cmd:list,title='Title'):
    rc = 0
    with alive_bar(manual=True,title=title) as bar:
        total_duration_regex = r'Duration: (\d\d:\d\d:\d\d.\d\d).*' 
        progress_tick_regex = r'out_time=(\d\d:\d\d:\d\d\.\d\d).*' 
    
        def stdout_callback(line):
            global total_duration
            global current_duration
            result = re.search(progress_tick_regex,line.decode('utf-8').replace('\r\n', ''))
            if result:
                current_duration = result.group(1)
                current_duration = current_duration.replace(':', '')
                current_duration = current_duration.replace('.', '')
                bar(int(current_duration)/int(total_duration))

        def stderr_callback(line):
            global stderr_log
            global total_duration
            stderr_log.append(line.decode('utf-8'))
            if not total_duration:
                result = re.search(total_duration_regex,line.decode('utf-8'))
                if result:
                    total_duration = result.group(1)
                    total_duration = total_duration.replace(':', '')
                    total_duration = total_duration.replace('.', '')

        rc = execute(
            cmd,
            stdout_callback,
            stderr_callback
        )

        if not rc:
            bar(1)

    if rc:
        print(colored(f'Compile error: ffmpeg exited with code {rc}','red'))
        for line in stderr_log:
            print(colored('\t\t'+line,'red'))