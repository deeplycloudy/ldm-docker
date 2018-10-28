import os
import subprocess
import glob
import argparse
from datetime import datetime, timedelta
from time import sleep

def pqinsert(filename, container='ldm-prod'):
    
    pqcommand = ["pqinsert",  filename]
    # can also pqinsert with -p to custom-eliminate the whole path
    # -p productID  Assert product-ID as <productID>. Default is the
    #               filename. With multiple files, product-ID becomes
    #               <productID>.<seqno>

    
    # run command on docker (add -it for interactive)
    # command = "docker exec -d {0} {1}".format(container, pqcommand)
        
    print(pqcommand)
    output = subprocess.check_output(pqcommand, stderr=subprocess.STDOUT)
    # return output

def await_grid(grid_dir, scene_id, action):
    # Fetch the previous minute of data. Get one minute ago, and then round down
    # to the nearest minute
    dt1min = timedelta(0, 60)
    lastmin = datetime.now() - dt1min
    startdate = datetime(lastmin.year, lastmin.month, lastmin.day, 
                          lastmin.hour, lastmin.minute)
    enddate = startdate + dt1min
    
    # at most, wait a few minutes for the full minute to be available
    dropdead = lastmin + dt1min*5
    
    mode='M3'
    platform='G16'
    
    grid_path = os.path.join(grid_dir, startdate.strftime('%Y/%b/%d'))
    # "OR_GLM-L2-GLMC-M3_G16_s20181011100000_e20181011101000_c20181011124580.nc 
    # Won't know file created time.
    dataset_name = "OR_GLM-L2-GLM{4}-{0}_{1}_s{2}_e{3}_c*.nc".format(
        mode, platform, startdate.strftime('%Y%j%H%M%S0'),
        enddate.strftime('%Y%j%H%M%S0'), scene_id)
    expected_file = os.path.join(grid_path, dataset_name)

    while True:
        grid_files = glob.glob(expected_file)
        results = []
        if len(grid_files) > 0:
            # sleep(1) # mysterious wait lets file write complete
            for gf in grid_files:
                result = action(gf)
                results.append(result)
            return results
        elif datetime.now() > dropdead:
            # Return the empty list of files
            return results
        else:
            # Keep waiting
            print("Waiting for {0}".format(expected_file))
            sleep(2)
            continue

parse_desc = """ Watch for a GLM grid corresponding to the minute of data before
present, and insert it into the LDM Docker queue"""

def create_parser():
    parser = argparse.ArgumentParser(description=parse_desc)
    parser.add_argument('-g', '--grid_dir', metavar='directory',
        required=True, dest='grid_dir', action='store',
        help="Gridded data will be saved to this directory, in subdirectories" 
             "like /2018/Jul/04/")
    parser.add_argument('-c', '--scene', dest='scene', action='store',
        default='C',
        help="One of C, M1, M2, or F, matching the scene ID part of the"
             " filename")
    return parser

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    print(await_grid(args.grid_dir, args.scene, pqinsert))
