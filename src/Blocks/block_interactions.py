from mcpi.minecraft import Minecraft as mc
import csv
import numpy as np

class BlockInterface():
    def __init__(self, block_path=None, connect=True):
        if connect:
            self.client = mc.create()
        else:
            self.client = None
            
        # Read in block list
        self.blocklist = None
        self.blockmap = None
        if not block_path is None:
            self.blocklist, self.blockmap = self.__read_in_blocks(block_path)
        
    def connect(self):
        self.client = mc.create()
    
    def read_block(self, x, y, z, verbose=False):
        if verbose:
            block = self.client.getBlockWithData(x, y, z)
            return (block.id, block.data)
        else:
            return self.client.getBlock(x, y, z)


    def read_blocks(self, start_coords, end_coords):
            # Read a cube of blocks
            assert type(start_coords) == list or type(end_coords) == list
            assert len(start_coords) == 3 and len(end_coords) == 3
            
            return self.client.getBlocks(
            start_coords[0],
            start_coords[1],
            start_coords[2],
            end_coords[0],
            end_coords[1],
            end_coords[2]
            )
    
    
    def read_blocks_np(self, start_coords, end_coords, listid=True):
        # Read a cube of blocks
        assert type(start_coords) == list or type(end_coords) == list
        assert len(start_coords) == 3 and len(end_coords) == 3

        # Sort coordinates 
        start_coords, end_coords = self.__sort_coordinates(start_coords, end_coords)

        # Get coordinate vector
        diff = [abs(end_coords[i]-start_coords[i])+1 for i in range(len(start_coords))]
        if listid:
            blocks = np.zeros(shape=(diff[1], diff[0], diff[2])).astype(int)
        else:
            blocks = np.zeros(shape=(diff[1], diff[0], diff[2])).astype(str)
        # Iterate over y element
        for yi, y in enumerate(range(start_coords[1], start_coords[1] + diff[1])):
            # Iterate over x element
            for xi, x in enumerate(range(start_coords[0], start_coords[0] + diff[0])):
                # Iterate over z element
                arspace = blocks[yi][xi]
                for zi, z in enumerate(range(start_coords[2], start_coords[2] + diff[2])):
                    block = self.read_block(x, y, z, True)
                    strblock = str(block[0])
                    if not block[1] == 0:
                        strblock += f"^{block[1]}"

                    if listid:
                        arspace[zi] = self.blockmap[
                            strblock
                        ]
                    else:
                        arspace[zi] = strblock
        return blocks                    


    def place_block_id(self, x, y, z, blockid, subblock=0):
        return self.client.setBlock(x, y, z, blockid, subblock) 
    

    def place_block_str(self, x, y, z, strblock):
        assert type(strblock) == str
        if "^" in strblock:
            id, subblock = strblock.split("^")
            id, subblock = int(id), int(subblock)
            self.place_block_id(x, y, z, id, subblock)
            return
        else:
            self.place_block_id(x, y, z, blockid=int(strblock))    


    def place_blocks(self, start_coords, end_coords, blockid, subblock):
        assert type(start_coords) == list or type(end_coords) == list
        assert len(start_coords) == 3 and len(end_coords) == 3

        return self.client.setBlocks(
            start_coords[0],
            start_coords[1],
            start_coords[2],
            end_coords[0],
            end_coords[1],
            end_coords[2],
            blockid,
            subblock
        )

    def place_blocks_np(self, blocks, x0=0, y0=-60, z0=0, isblocklist=True):
        assert len(blocks.shape) == 3
        if map:
            assert not self.blocklist is None 
            
        for yi, y in enumerate(blocks):
            for xi, x in enumerate(y):
                for zi, z in enumerate(x):
                    if isblocklist:
                        if type(z) is not int:
                            # try cast to int
                            z = int(z)
                        z = self.blocklist[z]
                    else:
                        z = str(z)
                    
                    self.place_block_str(x0+xi, y0+yi, z0+zi, strblock=z)
                    

        

    def __read_in_blocks(self, path):
        out = []
        lookup = {}
        with open(path, "r") as fs:
            reader = csv.reader(fs)
            for ri, row in enumerate(reader):
                out.append(row[1])
                lookup[row[1]] = ri
        # Remap some lookup values
        remap = [64, 71, 193, 194, 195, 196, 197, 17, 162, 53, 67, 108,\
            109, 114, 128, 134, 135, 136, 156, 163, 164, 180, 203]        
        for id in remap:
            mpp = lookup[f"{id}"]
            for i in range(20):
                lookup[f"{id}^{i}"] = mpp
        
        return out, lookup

    def __sort_coordinates(self, a, b):
        return [min(ai, bi) for ai, bi in zip(a, b)], \
            [max(ai, bi) for ai, bi in zip(a, b)]
            
                
                
    def save_np(self, arr:np.array, path:str):
        with open(path, "w+") as fs:
            wr = csv.writer(fs)
            wr.writerow(arr.shape)
            for y in arr:
                for z in y:
                    wr.writerow(z)
    
    def read_np(self, path:str) -> np.array:
        with open(path, "r") as fs:
            rd = csv.reader(fs)
            shape = ()
            arr = None
            rowy = 0
            rowx=0
            for i, row in enumerate(rd):
                if not i:
                    shape = tuple([int(s) for s in row])
                    arr = np.zeros(shape=shape).astype(int).astype(str)
                else:
                    arr[rowy][rowx] = row
                    rowx += 1
                    if rowx > (shape[1] - 1):
                        rowx = 0
                        rowy += 1
        return arr