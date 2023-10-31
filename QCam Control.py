# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 13:08:39 2023

@author: c.hages
"""

import sys
import os
import ctypes

import numpy as np
import matplotlib.pyplot as plt

from qcam import Camera
from mono import Mono

from calibration import get_position

def frame_to_image(frame):
    """
    Convert frame buffer to image array
    Windows doesn't like it (i.e. throws a fatal exception)
    when this takes place in qcam.py for some reason!
    """
    # First we need to cast the void pointer to a pointer to a char array
    pBuffer = ctypes.cast(frame.pBuffer, ctypes.POINTER(ctypes.c_char * frame.size))
    
    # Then we create a numpy array from the buffer
    image_data = np.frombuffer(pBuffer.contents, dtype=np.uint8)
    
    # Now reshape it into the correct shape
    image = image_data.reshape(frame.height, frame.width)
    return image

if __name__ == "__main__":
    
    try:
        # Create a camera object
        camera = Camera()
        cameraOpened = camera.connect_to_camera()
        mono = Mono()
        
        # =============================================================================
        # Code to get/send paramters to Camera
        # =============================================================================
        
        if cameraOpened:
            result, model = camera.get_camera_model()
            if result != 0:  # Replace with your actual success value
                print(f"Failed to get camera model with error {result}")
            else:
                print(f"Camera model: {model}")
    
            # Display Info & Parameters
            camera.setup_camera()
            print(list(camera.info.values()))
            print(list(camera.parameters.values()))
            for name, param in camera.parameters.items():
                print(f"For parameter {name}: min_value is {param.min_value}, max_value is {param.max_value}")

            bkg = np.loadtxt("bkg.txt").astype(int)[:, 1]
            out_path = r"."

            camera.set_camera_param("Exposure", int(5 * 1e6))  # replace 1000 with the desired exposure value
            camera.set_camera_param("Gain", 1023)  # replace 1000 with the desired exposure value
            camera.set_camera_param("Binning", 2)  # replace 1000 with the desired exposure value
            camera.retrieve_parameters()
            print(list(camera.parameters.values()))
            
            y0 = 150
            y1 = 300
            
            for wl in np.arange(450, 1050, 5):
                print(wl)
                mono.set_wavelength(wl)
                frame = camera.grab_frame()
                image = frame_to_image(frame)
                
                x = get_position(wl, image.shape[1], grating_no=1, binning=2)

                integral = np.sum(image[y0:y1], axis=0).astype(int)
                integral -= bkg

                if wl in [0, 500, 600, 700, 800, 900, 1000]:
                    plt.figure(wl)
                    plt.imshow(image, cmap='rainbow')
                    plt.axhline(y0, color='r')
                    plt.axhline(y1, color='r')
                    
                    plt.figure(wl+1)
                    plt.plot(x, integral)
                    plt.ylabel("Counts")
                    plt.xlabel("WL [nm]")

                np.savetxt(os.path.join(out_path, f"{wl}.txt"), np.vstack((x, integral)).T, header="WL [nm]\tCounts", fmt='%.3f', delimiter="\t")
                #np.savetxt("bkg.txt", np.vstack((x, integral)).T, header="WL [nm]\tCounts", fmt="%.3f", delimiter="\t")
            # mono.set_wavelength(10)
            # frame = camera.grab_frame()
            # image = frame_to_image(frame)

            # plt.figure(1)
            # plt.imshow(image, cmap='rainbow')
        
    except SystemExit:
        print("An error occurred, exiting...")

        
    finally:
        mono.close()
        if cameraOpened:
            # Close the camera
            result = camera.close_camera()
            if result != 0:  # Replace with your actual success value
                print(f"Camera closing failed with error {result}")
                sys.exit(1)     
            print("Camera closed successfully")
        if 'camera' in locals():  # Check if camera was defined before trying to release the driver
            camera.release_driver()
            print("Driver released")        