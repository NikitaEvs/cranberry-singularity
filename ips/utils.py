import sys
import traceback


def warn_tb(error, warning=False, cut=2, file=sys.stderr):
    level = "Предупреждение" if warning else "Ошибка"
    stack = (
        traceback.extract_stack()[:-cut]
        if cut
        else traceback.extract_stack()
    )
    print("".join(traceback.format_list(stack)) +
          f"{level}: {error}", file=file, flush=True)
