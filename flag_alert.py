import requests
from typing import Tuple
import time
import os

CBI_API = "https://api.community-boating.org/api/flag-history-recent"
WEBHOOK_URL = os.environ['WEBHOOK_URL']
FLAG_DICT = {
    "R": ":large_red_square:", 
    "Y": ":large_yellow_square:", 
    "G": ":large_green_square:",
    "C": ":flag_down:",
}
INTERVAL = 60 * int(os.environ['INTERVAL_MINS']) # seconds

def notifyHereTag(newFlag: str) -> str:
    if newFlag == "Y" or newFlag == "R":
        return "<!here>"
    return ""

def parseResponse(response: dict) -> Tuple[str, str]:
    """
    Case 1 (should never happen unless dock staff initiate flag change len(rows)
    times in the span of INTERVAL seconds):
    | x x x x x x x x x x x |
    
    Case 2 (captures change):
    x x | x x x x x x x x x |

    Case 3 (most frequent):
    x x x x x x x x x x x | | 

    """
    now = time.time()
    rows = response['data']['rows']

    for row in rows:
        print(row[0], time.ctime(row[1]), time.ctime(now))

    outsideIntervalIdx = 0
    while (outsideIntervalIdx < len(rows) and 
        rows[outsideIntervalIdx][1] >= now - INTERVAL):
        outsideIntervalIdx += 1

    # Case 3
    if outsideIntervalIdx == 0:
        return rows[outsideIntervalIdx][0], ""

    # Case 1
    if outsideIntervalIdx == len(rows):
        return rows[-1][0], rows[0][0]

    # Case 2
    return rows[outsideIntervalIdx][0], rows[0][0]

def main() -> str:
    # Retrieve flag-change-history from CBI API
    response = requests.get(CBI_API)
    prevFlag, newFlag = parseResponse(response.json())

    message = ""
    # POST to webhook URL to send Slack message
    if newFlag and prevFlag != newFlag:
        message = (f"Flag just changed from  {FLAG_DICT[prevFlag]}  to " + 
        f"{FLAG_DICT[newFlag]}\t{notifyHereTag(newFlag)}")  
        response = requests.post(WEBHOOK_URL, json={"text": message})
    
    return message

if __name__ == '__main__':
    main()