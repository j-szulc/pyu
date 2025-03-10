# def zfill_list(lst, width=None, fillchar="0"):
#     result = [str(l) for l in lst]
#     width = width or len(max(result, key=len))
#     return [l + (width - len(l))*fillchar for l in result]

def chunk_while(predicate, iterable):
    current = []
    for value in iterable:
        if predicate(current + [value]):
            current.append(value)
            continue
        if current:
            yield current
        current = [value]
    if current:
        yield current

def chunk_by_size(iterable, max_size):
    yield from chunk_while(lambda chunk: sum(map(len, chunk)) <= max_size, iterable)