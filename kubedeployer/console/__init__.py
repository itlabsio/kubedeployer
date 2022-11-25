from functools import partial


write = partial(print, end="", flush=True)
writeln = partial(write, end="\n")

