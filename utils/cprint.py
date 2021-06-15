from colorama import Fore, Style, init

init(convert=True)


def cprint(*messages, success=False, error=False, info=False, symbol=True, carriage=True, to_print=True, flush=False, end='\n'):
    messages_list = list(map(str, messages))
    message = " ".join(messages_list)
    fmessage = '\r' if carriage else ''

    if success:
        fmessage += f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}{'[+] ' if symbol else ''}{message} {Style.RESET_ALL}"
    elif error:
        fmessage += f"{Style.BRIGHT}{Fore.LIGHTRED_EX}{'[-] ' if symbol else ''}{message} {Style.RESET_ALL}"
    elif info:
        fmessage += f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}{'[i] ' if symbol else ''}{message} {Style.RESET_ALL}"
    else:
        fmessage += message

    if to_print:
        print(fmessage, flush=flush, end=end)
    else:
        return fmessage
