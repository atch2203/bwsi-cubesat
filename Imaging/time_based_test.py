from time import sleep
# import imaging_stage_one as phase1

#take pic + process --> 2 seconds
#sleep time --> 8 seconds
#Angle order: 0-60-120-180-240-300-30-90-150-210-270-330
#big leap from 300 to 30 degrees 

# phase1.set_user_values("rhea", 100/258.49564793241683, 271, 45)
# print(phase1.capture_image)


time = 0
zzz = 4
sleep(2) #idle --> focus camera
input('Press enter to start imaging: ')
print("started")







for pic in range(0,4,1):
    #take pic 
    sleep(zzz)
    time+=zzz+2
    print("time:", " ", time)
    sleep(zzz)
    time+=zzz
    print("time:", " ", time)

#take pic at 300 degrees
sleep(13) #jump from 300 degrees to 30

for image in range(0,6,1):
    #take pic
    sleep(zzz)
    time+=zzz+2
    print("time:", " ", time)
    sleep(zzz)
    time+=zzz
    print("time:", " ", time)

