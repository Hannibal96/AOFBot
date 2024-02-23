import glob


def extract_hand(file_name):
    hand = -1
    with open(file_name, "r") as f:
        for line in f:
            if "# Hand" in line:
                hand = int(line.split(":")[1])
    return hand


if __name__ == "__main__":
    total = 0
    date_time_start = [2024, 2, 16, 0, 0 ,0]
    for file in glob.glob("*.log"):
        _, date, time = file.split(".")[0].split("_")
        date = date.split("-")
        time = time.split("-")
        date = [int(v) for v in date]
        time = [int(v) for v in time]
        date_time = date+time
        hand = extract_hand(file)
        if hand == -1:
            continue
        if date_time > date_time_start:
            total += hand
        print(f"{file}: {hand}, {total}")

    print(f"Total: {total}")


