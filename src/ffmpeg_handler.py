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


def execute(cmd, stdout_cb, stderr_cb):  
    loop = asyncio.get_event_loop()
    rc = loop.run_until_complete(
        _stream_subprocess(
            cmd,
            stdout_cb,
            stderr_cb,
    ))
    loop.close()
    return rc

if __name__ == '__main__':  
    with alive_progress.alive_bar(0) as bar:
        execute(
            ['ffmpeg', '-i', '/home/mda/Downloads/video2.mp4', '-vf', 'fps=5', '-vsync', '0', '/home/mda/Downloads/s4/%d.png'],
            lambda x: print("STDOUT: %s" % x),
            lambda x: bar(),
        )