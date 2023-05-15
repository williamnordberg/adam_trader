from datetime import datetime

timestamp = 1684083913177 / 1000.0  # Convert from milliseconds to seconds
dt_object = datetime.fromtimestamp(timestamp)

print(dt_object)