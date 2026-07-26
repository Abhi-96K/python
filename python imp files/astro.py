from datetime import datetime, timedelta
import swisseph as swe

# Set up birth date
birth_date = datetime(2005, 10, 13)
location_lat = 19.155  # Majalgaon latitude
location_lon = 76.215  # Majalgaon longitude
timezone = 5.5  # IST (UTC+5:30)

# Start from 00:00 to 23:59 on the birth date
start_time = datetime(2005, 10, 13, 0, 0)
end_time = datetime(2005, 10, 13, 23, 59)
step = timedelta(minutes=5)

# Constants for Moon and Aquarius range
AQUARIUS_START = 300.0  # 0 deg Aquarius = 300 deg in zodiac
AQUARIUS_END = 330.0    # 30 deg Aquarius = 330 deg in zodiac

# Find all time ranges where Moon is in Aquarius
moon_in_aqua_times = []

current_time = start_time
while current_time <= end_time:
    julday = swe.julday(current_time.year, current_time.month, current_time.day,
                        current_time.hour + current_time.minute/60 - timezone)
    moon_pos = swe.calc_ut(julday, swe.MOON)[0][0]

    if AQUARIUS_START <= moon_pos < AQUARIUS_END:
        moon_in_aqua_times.append(current_time)

    current_time += step

# Convert to continuous intervals
from itertools import groupby

# Group by consecutive time steps (every 5 minutes)
intervals = []
if moon_in_aqua_times:
    group = [moon_in_aqua_times[0]]
    for t in moon_in_aqua_times[1:]:
        if (t - group[-1]) == step:
            group.append(t)
        else:
            intervals.append((group[0], group[-1]))
            group = [t]
    intervals.append((group[0], group[-1]))  # Add last group

# Print intervals
for start, end in intervals:
    print(f"Moon in Aquarius from {start.time()} to {end.time()} IST")
