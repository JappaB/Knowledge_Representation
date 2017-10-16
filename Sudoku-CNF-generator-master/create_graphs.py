import matplotlib.pyplot as plt
import csv
import numpy as np

table = {}

with open('data-table-backup.csv', 'r') as csv_file:
    FIELD_NAMES = ['id', 'givens', 'agility', 'used', 'seconds', 'variables', 'n_phases', 'conflicts', 'level', 'MB', 'limit', 'learned', 'original']

    data_table = csv.reader(csv_file, delimiter=';')

    for row in data_table:
        if row[0] == 'id' : continue

        conflicts = int(row[7])
        n_givs = int(row[1])

        if n_givs not in table:
            table[n_givs] = [conflicts]
        else:
            table[n_givs].append(conflicts)

std_dev = [np.std(table[key]) for key in sorted(table.keys())]
avg = [np.mean(table[key]) for key in sorted(table.keys())]
median = [np.median(table[key]) for key in sorted(table.keys())]

plt.plot(sorted(table.keys()), avg, color="green", label='mean')

plt.plot(sorted(table.keys()), median, label='median')
plt.xlabel("Number of givens")
plt.ylabel("Conflicts")

plt.legend()
plt.show()

# plt.plot(sorted(table.keys()), std_dev)
# plt.xlabel("Number of givens")
# plt.ylabel("Standard Deviation")
# plt.show()


# plt.xlabel("Number of givens")
# plt.ylabel("Mean")
# plt.show()