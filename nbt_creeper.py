from nbt import nbt
import os

def processFile(file, last, remove = False):
    print(file)
    structure = nbt.NBTFile(file, 'rb')

    # The second list in structure is the list of all blocks in the structure, 3 is the palette
    spawnpoints = findCommandBlocks(structure[2], "function game:default/create_zombie_spawnpoint")
    shopItems = findCommandBlocks(structure[2], "function game:shops/create_item_point")
    shopkeepers = findCommandBlocks(structure[2], "function game:shops/create_shopkeeper")
    upgrade = findUpgrade(structure[2])

    air = findAir(structure[3])
    if remove:
        deleteblocks(air, spawnpoints, structure, last)
        deleteblocks(air, shopItems, structure, last)
        deleteblocks(air, shopkeepers, structure, last)
        deleteblocks(air, [upgrade], structure, last)

    with open(file.replace(".nbt", ".json"), 'w') as f:
        
        f.write("{\n")
        f.write("\t\"spawnpoints\": [\n")
        for i in range(len(spawnpoints)):
            f.write("\t\t{\"x\": " + str(spawnpoints[i][0]) + ", \"y\": " + str(spawnpoints[i][1]) + ", \"z\": " + str(spawnpoints[i][2]) + "}")
            if i != len(spawnpoints) - 1:
                f.write(",\n")
            else:
                f.write("\n")
        f.write("\t],\n")

        f.write("\t\"shopItems\": [\n")
        for i in range(len(shopItems)):
            f.write("\t\t{\"x\": " + str(shopItems[i][0]) + ", \"y\": " + str(shopItems[i][1]) + ", \"z\": " + str(shopItems[i][2]) + "}")
            if i != len(shopItems) - 1:
                f.write(",\n")
        f.write("\n\t],\n")

        f.write("\t\"shopkeepers\": [\n")
        for i in range(len(shopkeepers)):
            f.write("\t\t{\"x\": " + str(shopkeepers[i][0]) + ", \"y\": " + str(shopkeepers[i][1]) + ", \"z\": " + str(shopkeepers[i][2]) + "}")
            if i != len(shopkeepers) - 1:
                f.write(",\n")
        f.write("\n\t],\n")

        f.write("\t\"upgrade\": {")
        if upgrade[0] != -1:
            f.write("\n\t\t\"x\": " + str(upgrade[0]) + ", \"y\": " + str(upgrade[1]) + ", \"z\": " + str(upgrade[2]) + ",\n")
            f.write("\t\t\"element\": \"" + str(upgrade[3]) + "\"\n\t")
        f.write("}\n")
        f.write("}")
        
        f.close()

def findCommandBlocks(blocks, command):
    coordList = []
    for i in range(len(blocks)):
        if len(blocks[i].tags[0]) >= 5 and blocks[i].tags[0][4].value == command:
            pos = blocks[i].tags[1]
            coordList.append((pos[0].value, pos[1].value, pos[2].value))

    return coordList

# air is the found air id. poslist is a list of positions to replace with air.
def deleteblocks(air, poslist, structure, last):
    for i in range(len(structure[2])):
        if (len(structure[2][i]) == 3):
            x = structure[2][i][1][0]
            y = structure[2][i][1][1]
            z = structure[2][i][1][2]
            for j in range(len(poslist)):
                if (x.value == poslist[j][0]) and (y.value == poslist[j][1]) and (z.value == poslist[j][2]):
                    structure[2][i][2].value = air;

    structure.write_file("./modified_structures/"+last.split('/')[-1])

# Finds the pallete id # of air 
def findAir(pallete):
    for i in range(len(pallete)):
        if (len(pallete[i].tags) == 1 and str(pallete[i].tags) == "[minecraft:air]"):
            return i;
            
# The upgrade command block (if it exists) will have "function game:mechanics/upgrade/create/<element>_upgrade_spot"
def findUpgrade(blocks):
    for i in range(len(blocks)):
        if len(blocks[i].tags[0]) >= 5 and str(blocks[i].tags[0][4].value).startswith("function game:mechanics/upgrade/create/"):
            pos = blocks[i].tags[1]
            element = blocks[i].tags[0][4].value.split("/")[-1].split("_")[0]
            return (pos[0].value, pos[1].value, pos[2].value, element)

    return (-1, -1, -1, "none")

if __name__ == "__main__":
    last = "./structures/ai1_windmills.nbt"
    for filename in os.listdir("./structures"):
        if (not filename.endswith(".nbt")):
            continue
        file_path = "./structures/"+filename
        processFile(file_path, last, True)
        last = filename
                                                                             
