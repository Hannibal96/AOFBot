def squeeze_name(name):
    _, color, number, _, sb, _, bb = name.split()
    return color + "_" + number + "_" + bb
