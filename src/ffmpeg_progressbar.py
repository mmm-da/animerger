import asyncio
import alive_progress

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


def parse_ffmpeg_output(line):
    print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',line)
    stdout_callback = lambda x: print(f"STDERR: {x}") 

stdout_callback = parse_ffmpeg_output

def exec_with_progress(cmd:list):
    execute(
        cmd,
        lambda x: print(f"STDOUT: {x}"),
        stdout_callback,
    )

exec_with_progress(
    [
        'ffmpeg',
    ]
)