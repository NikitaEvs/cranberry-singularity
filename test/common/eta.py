import ips

data = ips.buffer()
print(data)

if data == ["johnny", "johnny"]:
    ips.exit_with("yes papa?")
elif data == "eating sugar?":
    ips.exit_with("yes papa")
elif data == "telling a lie?":
    ips.exit_with("no papa")
elif data == "open your mouth":
    ips.exit_with(["ha", "Ha", "ha"])
else:
    raise KeyError("where's my papa?")
