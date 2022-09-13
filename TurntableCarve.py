
# import mayavi.mlab as mlab
import matplotlib.pyplot as plt
import subprocess
from sys import platform
from PIL import Image
import numpy as np
import open3d as o3d


def CarveIt(V_in, P, mask, VolWidth, VolHeight, VolDepth):
    # Write output exchange file
    out = open('carveInput.dat', 'wb')

    sY = V_in.shape[0]
    sX = V_in.shape[1]
    sZ = V_in.shape[2]

    smY = mask.shape[0]
    smX = mask.shape[1]

    width = VolWidth
    height = VolHeight
    depth = VolDepth

    data = np.array([sX, sY, sZ], dtype='uint32')
    out.write(data.tobytes())
    out.write(V_in.tobytes('A'))
    out.write(P.tobytes('F'))

    data = np.array([smX, smY], dtype='uint32')
    out.write(data.tobytes())
    out.write(mask.tobytes('F'))

    data = np.array([width, height, depth], dtype='float64')
    out.write(data.tobytes())
    out.close()

    # Execute
    if platform == "win32":
        execPrefix = "CarveIt.exe"
    else:
        execPrefix = "./CarveIt.o"

    p = subprocess.Popen(execPrefix + " carveInput.dat carveResult.dat", shell=True)
    p.wait()

    # Read input exchange file
    V_in = np.fromfile('carveResult.dat', dtype='uint8')
    return V_in.reshape((sY, sX, sZ), order='F')


def TurntableCarve(fn, cam, V, imageLength, imageWidth, show3D):
    # Reconstruct volume of an object from its projection masks acquired using
    # a turntable setup
    #
    # Input:
    # fn: describes names of input mask files
    # cam: camera properties
    # V: describes the reconstruction volume, i.e. a cuboid-shaped region
    #
    # Output:
    # vol_in_mm3: volume of the reconstructed object in mm^3

    # # perform volume carving on mask images
    # volume_in_mm3 = TurntableCarve(fnmask,cam,tool,V);
    ###################################################################

    V.dx = V.VolWidth / V.sX  # voxelsize in X-direction
    V.dy = V.VolHeight / V.sY  # voxelsize in Y-direction
    V.dz = V.VolDepth / V.sZ  # voxelsize in Z-direction
    V.Voxels = [V.sY, V.sX, V.sZ]  # number of voxels in volume
    V.vol = np.ones(tuple(V.Voxels), np.uint8)  # solid filled volume

    # print info
    print('** Analyzing images -- Carving  **')

    # loop images for carving
    NumImgs = len(fn.number)  # number of images
    for i in range(NumImgs):
        # print a point to show progress
        if i % 9 == 0:
            print(".")

        # get the mask in array
        mask = ReadImage(fn, i)

        # calculate projection matrix for this image
        P = ProjectionMatrix(cam, i, imageLength, imageWidth)

        # draw the volume outline as box in mask image
        # projectVolBox(P,mask,V,10); # uncomment to see the projected volume boxes

        # do the carving with a c implementation
        V.vol = CarveIt(V.vol, P, mask, V.VolWidth, V.VolHeight, V.VolDepth)

        # alternatively do the carving in Python -- very slow!
        # V.vol = Carve(V.vol,P,mask,V.VolWidth,V.VolHeight,V.VolDepth)

    # show the reconstructed object
    if show3D:
        # save surface points
        saveSurfacePoints(V.vol)
        # showModel(V, 1)
        Display3DModel()

    # calculate the final volume of the object
    vol_in_mm3 = np.sum(V.vol) * V.dx * V.dy * V.dz
    return vol_in_mm3


##########################################################
# get the imageArray(mask)
def ReadImage(fn, idx):
    imgfilename = fn.base + ("%04d" % fn.number[idx]) + fn.extension
    img = Image.open(imgfilename)  # get the image
    img = np.array(img.getdata()).reshape(img.size[0], img.size[1])  # convert to array
    return img


def saveSurfacePoints(data):
    pointCLoud = []
    for x in range(len(data)):
        for y in range(len(data[x])):
            for z in range(len(data[x][y])):
                # shell (surface)
                if isEdgePoint(data, x, y, z):
                    subData = [x, y, z, 37, 100, 100]
                    subData = np.array(subData)
                    pointCLoud.append(subData)
    np.savetxt("surfacePoints.txt", pointCLoud)


# to check whether the point is on the surface or not.
def isEdgePoint(data, x, y, z):
    if data[x][y][z] == 1:
        if (data[x - 1][y][z] == 0 or data[x + 1][y][z] == 0
                or data[x][y - 1][z] == 0 or data[x][y + 1][z] == 0
                or data[x][y][z - 1] == 0 or data[x][y][z + 1] == 0):
            return True


def Display3DModel():
    point_cloud = np.loadtxt("./surfacePoints.txt", skiprows=1)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud[:, :3])
    pcd.colors = o3d.utility.Vector3dVector(point_cloud[:, 3:6] / 255)
    pcd.estimate_normals()

    # make  all normals point outwards
    countOfNeighbors = 10
    pcd.orient_normals_consistent_tangent_plane(countOfNeighbors)

    print('run Poisson surface reconstruction')
    with o3d.utility.VerbosityContextManager(
            o3d.utility.VerbosityLevel.Debug) as cm:
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=8)

    # smooth the surface of the model (mesh filter)
    mesh_out = mesh.filter_smooth_simple(number_of_iterations=5)
    mesh_out.compute_vertex_normals()  # add normal of the triangle, otherwise, is not 3D.
    o3d.visualization.draw_geometries([mesh_out])
    # print(mesh_out)
    o3d.io.write_triangle_mesh("./res.stl", mesh_out)  # save to stl file

##########################################################
# show the reconstructed volume as isosurface
# def showModel(Vin, currentfigurenum):
#     mlab.figure(currentfigurenum, bgcolor=(1, 1, 1), fgcolor=(1, 1, 1))
#     mlab.clf()
#
#     p = mlab.contour3d(Vin.vol, color=(1, 0, 0))
#     mlab.text(0.05, 0.95, 'Please close the window to continue calculations.', color=(0, 0, 0), width=0.9)
#     mlab.text(0.3, 0.05, 'Rotate using click&drag', color=(0, 0, 0), width=0.4)
#
#     c_scene = mlab.get_engine().current_scene
#     # c_scene.scene.light_manager.light_mode = 'vtk'
#     c_scene.scene.camera.position = [0, 0, -128]
#     c_scene.scene.camera.view_up = [-1, 0, 0]
#     c_scene.scene.render()
#     mlab.show()
#     return p


##########################################################
# draw a box in the mask image to show, where the reconstruction
# region is located
def projectVolBox(P, mask, V, currentfigurenum):
    fig = plt.figure(figsize=(6, 3.2))

    ax = fig.add_subplot(111)
    ax.set_title('projectedVolBox')
    plt.imshow(mask)
    ax.set_aspect('equal')
    # plt.colorbar(orientation='vertical')

    ## corner points of a cube, centered at the origin of the world coord
    ## system. Homogeneous coords.
    x = V.VolWidth / 2
    y = V.VolHeight / 2
    z = V.VolDepth / 2
    Q1 = np.array([x, y, z, 1]).reshape((1, 4))
    q1 = P * Q1.transpose()
    q1 = q1 / q1[2]

    Q2 = np.array([x, y, -z, 1]).reshape((1, 4))
    q2 = P * Q2.transpose()
    q2 = q2 / q2[2]

    Q3 = np.array([x, -y, z, 1]).reshape((1, 4))
    q3 = P * Q3.transpose()
    q3 = q3 / q3[2]

    Q4 = np.array([x, -y, -z, 1]).reshape((1, 4))
    q4 = P * Q4.transpose()
    q4 = q4 / q4[2]

    Q5 = np.array([-x, y, z, 1]).reshape((1, 4))
    q5 = P * Q5.transpose()
    q5 = q5 / q5[2]

    Q6 = np.array([-x, y, -z, 1]).reshape((1, 4))
    q6 = P * Q6.transpose()
    q6 = q6 / q6[2]

    Q7 = np.array([-x, -y, z, 1]).reshape((1, 4))
    q7 = P * Q7.transpose()
    q7 = q7 / q7[2]

    Q8 = np.array([-x, -y, -z, 1]).reshape((1, 4))
    q8 = P * Q8.transpose()
    q8 = q8 / q8[2]

    plt.plot([float(q1[0]), float(q2[0])], [float(q1[1]), float(q2[1])])
    plt.plot([float(q1[0]), float(q3[0])], [float(q1[1]), float(q3[1])])
    plt.plot([float(q1[0]), float(q5[0])], [float(q1[1]), float(q5[1])])
    plt.plot([float(q2[0]), float(q4[0])], [float(q2[1]), float(q4[1])])
    plt.plot([float(q2[0]), float(q6[0])], [float(q2[1]), float(q6[1])])
    plt.plot([float(q3[0]), float(q4[0])], [float(q3[1]), float(q4[1])])
    plt.plot([float(q3[0]), float(q7[0])], [float(q3[1]), float(q7[1])])
    plt.plot([float(q4[0]), float(q8[0])], [float(q4[1]), float(q8[1])])
    plt.plot([float(q5[0]), float(q6[0])], [float(q5[1]), float(q6[1])])
    plt.plot([float(q5[0]), float(q7[0])], [float(q5[1]), float(q7[1])])
    plt.plot([float(q6[0]), float(q8[0])], [float(q6[1]), float(q8[1])])
    plt.plot([float(q7[0]), float(q8[0])], [float(q7[1]), float(q8[1])])
    plt.show()


##########################################################
# calculate projection matrix P from given camera and image nformation
def ProjectionMatrix(cam, i, imageLength, imageWidth):
    # principal point in image
    p = [imageLength / 2, imageWidth / 2]    # the width is not 200, so adjust the Y of p.

    # Z = f*(M/m), FocalLength is f/m, m in [mm/pix], 1/M is PixPerMMAtZ
    f = cam.FocalLengthInMM * cam.PixPerMMSensor
    Z = f / cam.PixPerMMAtZ  # distance of rotation axis, i.e. origin of world coords.
    X = 0
    Y = 0

    K = np.matrix([[f, 0, p[0]], [0, f, p[1]], [0, 0, 1]])  # calibration matrix
    c = np.cos(cam.alpha[i] / 180.0 * np.pi)
    s = np.sin(cam.alpha[i] / 180.0 * np.pi)
    R = np.matrix([[c, 0, -s], [0, 1, 0], [s, 0, c]])  # rotation matrix
    t = [X, Y, -Z]  # translation vector, where camera is in world coords

    tT = np.matrix(t).transpose()
    P = K * np.matrix(np.concatenate((R, -tT), axis=1))
    return P


##########################################################
# Dummy class for storage
class Object(object):
    pass
