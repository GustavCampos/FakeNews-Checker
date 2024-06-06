def calc_progress(cur_value: int, end_value: int, size=20) -> str:
    proportion = cur_value / end_value
    
    equals = "=" * round(size * proportion)
    spaces = " " * (size - len(equals))
    progress_bar = "[" + equals + spaces + "]"
    
    return f"{progress_bar} {cur_value}/{end_value} {proportion * 100:2.2f}%"