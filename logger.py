import logging
import datetime
import re


card_symbol_mapping = {
    '\u2663': 'C',  # Example: ANSI encoding for clubs symbol
    '\u2660': 'S',  # Example: ANSI encoding for spades symbol
    '\u2665': 'H',  # Example: ANSI encoding for hearts symbol
    '\u2666': 'D',  # Example: ANSI encoding for diamonds symbol
}


def ansi_to_plain(text):
    ansi_pattern = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
    plain_text = ansi_pattern.sub('', text)
    return plain_text


def custom_print(*args, **kwargs):
    log_message = ' '.join(map(str, args))

    plain = ansi_to_plain(log_message)
    for ansi_code, unicode_symbol in card_symbol_mapping.items():
        plain = plain.replace(ansi_code, unicode_symbol)

    logging.info(plain)
    built_in_print(log_message, **kwargs)


built_in_print = print
print = custom_print


current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"./runs_logs/logger_{formatted_datetime}.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
