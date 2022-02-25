import re

def timeStringConvert(string: str):
    """

    Parameters:
        string: The string which should get converted to the time units. (e.g. '2d 4h 6m 7s')

    Returns: A ``dict`` which the keys are 'days', 'hours', 'minutes', 'seconds' and the value is either a ``int`` or ``None``.
    """

    timeDict: dict = {}

    days = re.search("\d+d", string)
    hours = re.search("\d+h", string)
    minutes = re.search("\d+m", string)
    seconds = re.search("\d+s", string)

    if days is not None:
        timeDict['days'] = int(days.group(0).strip('d'))
    else:
        timeDict['days'] = None

    if hours is not None:
        timeDict['hours'] = int(hours.group(0).strip('h'))
    else:
        timeDict['hours'] = None

    if minutes is not None:
        timeDict['minutes'] = int(minutes.group(0).strip('m'))
    else:
        timeDict['minutes'] = None

    if seconds is not None:
        timeDict['seconds'] = int(seconds.group(0).strip('s'))
    else:
        timeDict['seconds'] = None

    return timeDict

string = "213d 4h 123m"
timeDict: dict = timeStringConvert(string)
print(timeDict)
