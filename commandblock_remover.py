from nbt import nbt
import os

def processFile(file, remove = False):
    structure = nbt.NBTFile(file, 'rb')
    structure.tags.sort(key = lambda tag: tag.name)
    air = findAir(structure[3])

    # structure[1] is a list of all blocks in the structure
    spawnpoints = findCommandBlocks(structure[1], "function game:default/create_zombie_spawnpoint", remove, air, structure, file)
    shopItems = findCommandBlocks(structure[1], "function game:shops/create_item_point", remove, air, structure, file)
    shopkeepers = findCommandBlocks(structure[1], "function game:shops/create_shopkeeper", remove, air, structure, file)
    upgrade = findUpgrade(structure[1], remove, air, structure)

    # printing structure results
    info = os.path.basename(file) + "| Spawnpoints: " + str(len(spawnpoints)) + " | Shop items: " + str(len(shopItems)) + " | Shopkeepers: "+str(len(shopkeepers)) + " | Upgrade: " + str(upgrade[3]) + " | "
    print(info, end='')

    # create new file with removed command blocks
    structure.write_file(file.replace("/structures/","/modified_structures/"))

    # creating the json file with all spawnpoints, shop items, shopkeepers, and upgrade locations
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

# search pallete for the air id
def findAir(pallete):
    for i in range(len(pallete)):
        if (len(pallete[i].tags) == 1 and str(pallete[i].tags) == "[minecraft:air]"):
            return i;

def findCommandBlocks(blocks, command, remove, air, structure, file):
    coordList = []
    
    # Determining where to look for the command
    commandLocation = 5

    for i in range(len(blocks)):
        blocks[i].tags.sort(key = lambda tag: tag.name)

        # some blocks contain additional tags, so make sure we look in the right spot for the command 
        if str(blocks[i][0].tags[0].name) == "conditionMet":
            commandLocation = 4

        if str(blocks[i][0].tags[0].name) in ("UpdateLastExecution", "conditionMet") and blocks[i].tags[0][commandLocation].value == command:
            pos = blocks[i].tags[1]
            coordList.append((pos[0].value, pos[1].value, pos[2].value))
            if (not remove):
                continue

            structure[1][i][2].value = air
    
    return coordList

# The upgrade command block (if it exists) will have "function game:mechanics/upgrade/create/<element>_upgrade_spot"
def findUpgrade(blocks, remove, air, structure):
    commandLocation = 5

    for i in range(len(blocks)):

        if str(blocks[i][0].tags[0].name) == "conditionMet":
            commandLocation = 4

        if str(blocks[i][0].tags[0].name) in ("UpdateLastExecution", "conditionMet") and str(blocks[i].tags[0][commandLocation].value).startswith("function game:mechanics/upgrade/create/"):
            pos = blocks[i].tags[1]
            element = blocks[i].tags[0][commandLocation].value.split("/")[-1].split("_")[0]
            if (not remove):
                continue
            # set block to air.
            structure[1][i][2].value = air;
            return (pos[0].value, pos[1].value, pos[2].value, element)

    return (-1, -1, -1, "none")    

if __name__ == "__main__":
    
    numOfFiles = len(os.listdir("./structures"))
    num = 0;
    total = 0;
    
    for filename in os.listdir("./structures"):
        if (not filename.endswith(".nbt")):
            continue
        file_path = "./structures/"+filename
        processFile(file_path, True)
        num+=1
        total+=1
        percentage = round(((num/numOfFiles)*100), 2)
        print(str(percentage)+"%")

    print("Finished processing "+str(total)+" files.")