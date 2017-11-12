with open('recovered/arc/clusters/6.0.0_r1_acdc_clustered.rsf', encoding="utf8") as data_file:
    data = data_file.readlines()

cluster = set()
for line in data:
    cluster.add(line.split(" ")[1])
print(len(cluster))