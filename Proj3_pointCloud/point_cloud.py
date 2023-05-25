import numpy as np
import laspy

las = laspy.read("broken.las")

with open("statistics.txt", "w") as stats:
    points = f"Number of Points: {len(las)}.\n"
    data = np.reshape(las.xyz, (3, len(las)))
    box_dim = f"Cloud Boxes (xyz): [{data[0].max() - data[0].min() : .3f}, {data[1].max() - data[1].min() : .3f}, {data[2].max() - data[2].min() : .3f} ]."
    data = np.transpose(data)
    stats.writelines([points, box_dim])
    stats.write("\nLink to download file .las: https://mega.nz/file/xh43GLDC#TI9jgV56nCMGrFc7pUFy_84rYjtwRe7yd1ekyQx8v24")

out = laspy.LasData(las.header)
out.xyz = data
out.write("file.las")