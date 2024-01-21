import re
word = "Server3"
digits = ''.join(re.findall(r'\d',word))
print(digits)