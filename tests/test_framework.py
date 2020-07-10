# establish nice colors to output for test results
class bcolors:
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


# called by each test case
def test(cond, test_name, subtext=""):
    if cond:
        print(f"Test {test_name} {bcolors.OKGREEN}Passed{bcolors.ENDC}", end="")
    else:
        print(f"Test {test_name} {bcolors.FAIL}Failed{bcolors.ENDC}", end="")
    if subtext != "":
        print(f": {subtext}", end="")
    print()
    return int(cond == False)
