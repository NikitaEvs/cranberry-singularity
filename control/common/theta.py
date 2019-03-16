import ips

lines = [
    ["johnny", "johnny"],
    "eating sugar?",
    "telling a lie?",
    "open your mouth"
]

for line in lines:
    answer = ips.call("eta", line)
    print("<<<", line)
    print(">>>", answer)
