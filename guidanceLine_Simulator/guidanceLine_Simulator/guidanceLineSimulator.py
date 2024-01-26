#!C://Users/nthorson2/AppData/Local/Programs/Python/Python38/python.exe

import math
import shapely
from shapely.geometry import LineString
import geopandas as gpd
from geographiclib.geodesic import Geodesic
import logging

def generateDuplicateFeature():
    location = 'generate feature start'
    try:
        inputBool = False
        while inputBool == False:
            fileInput = input("Enter the Input File Path(including file name): ")
            if fileInput.lower() != 'exit':
                if fileInput != '':
                    inputBool = True
                else:
                    print("No Input File Location Provided!")
            else:
                exit()
                
        #read dataset
        location = 'read dataset'
        dataset = gpd.read_file(fileInput)
        
        if dataset.geometry[0].geom_type == 'LineString':        
            lineTypeBool = False
            while lineTypeBool == False:
                circleTrackLine = input("\n" + "Is the Guidance Line a CircleTrack Line? (y/n): ")
                if circleTrackLine.lower() == 'y' or circleTrackLine.lower() == 'yes':
                    offsetDir = 'left'
                    offsetGenDir = 'Outward'
                    circleTrackBool = True
                    lineTypeBool = True
                elif circleTrackLine.lower() == 'n' or circleTrackLine.lower() == 'no':
                    #determine heading
                    location = 'determine heading'
                    circleTrackBool = False
                    heading, bearing = determineLineHeading(dataset)
                    print("\n" + 'line heading: ' + repr(heading) + '°' + "\n")
                    
                    location = 'line offset direction'
                    offsetBool = False
                    while offsetBool == False:    
                        if bearing == 'North' or bearing == 'South':
                            userSelect = str(input("Enter Direction of Offset (ie 'east' or 'west'): "))
                        elif bearing == 'West' or bearing == 'East':
                            userSelect = str(input("Enter Direction of Offset (ie 'north' or 'south'): "))
                        elif bearing == 'NorthWest' or bearing == 'SouthEast':
                            userSelect = str(input("Enter Direction of Offset (ie 'northeast' or 'southwest'): "))
                        elif bearing == 'NorthEast' or bearing == 'SouthWest':
                            userSelect = str(input("Enter Direction of Offset (ie 'northwest' or 'southeast'): "))
                        
                        if userSelect != '':
                            if userSelect.lower() != 'exit':
                                offsetDir, offsetGenDir, offsetBool = lineOffsetDirection(bearing, userSelect)
                            else:
                                exit()
                        else:
                            print('user must enter a selection')
                        
                        if offsetDir == 'Invalid Selection!':   #user chose an invalid selection, re-initiate loop
                            print('Invalid Selection!')
                    
                    lineTypeBool = True
                else:
                    offsetBool = False
                    print('No Line Type Input, Please Input Yes or No')
                  
            orgwidthBool = False
            while orgwidthBool == False:
                orgSwathWidth = input("\n" + 'Original Line Swath Width to nearest Whole Number: ')
                if orgSwathWidth.lower() != 'exit':
                    if orgSwathWidth.isdigit():
                        if isinstance(int(orgSwathWidth),int):
                            orgSwathWidth = int(orgSwathWidth)
                            orgwidthBool = True
                        else:
                            print("Value must be a Whole Number!")
                    else:
                        print("Value must be a Whole Number!")
                else:
                    exit()
            
            distanceBool = False
            while distanceBool == False:
                print("\n" + 'Enter Line Generation Distance to nearest Whole Number') 
                distance = input('note - distance value and swath width value will determine number of lines generated : ')
                if distance.lower() != 'exit':
                    if distance.isdigit():
                        if isinstance(int(distance),int):
                            distance = int(distance)
                            distanceBool=True
                        else:
                            print("Value must be a Whole Number!")
                    else:
                        print("Value must be a Whole Number!")
                else:
                    exit()
            
            deswidthBool = False
            while deswidthBool == False:
                desiredSwathWidth = input("\n" + 'Desired Swath Width for Offset to nearest Whole Number: ')
                if desiredSwathWidth.lower() != 'exit':
                    if desiredSwathWidth.isdigit():
                        if isinstance(int(desiredSwathWidth), int):
                            desiredSwathWidth = int(desiredSwathWidth)
                            deswidthBool = True
                        else:
                            print("Value must be a Whole Number!")
                    else:
                        print("Value must be a Whole Number!")
                else:
                    exit()
                    
            outputBool = False
            while outputBool == False:
                fileOutput = input("\n" + "Enter the Output File Path (including new file name): ")
                if fileOutput.lower() != 'exit':
                    if fileOutput != '':
                        outputBool = True
                    else:
                        print("No Output File Location Provided!")
                else:
                    exit()
                    
            #fileInput = 'C://Users/nthorson2/Documents/test_Shp/Main_ln_20ft_nad83.shp'
            #fileInput = 'C://Users/nthorson2/Documents/test_Shp/Main_ln_40ft_nad83.shp'
            #fileOutput = 'C://Users/nthorson2/Documents/test_Shp/geoJSON/main_ln_20ft_nad83.geojson'
            # C:/Users/nthorson2/Documents/PythonScripts/testData/Input/guidanceLine/3514_circleTrack_Input/3514_C_EndRows_14G_ln.shp


# NOTE:     Circletrack lines require an inward shift, regardless of whether the desired swath width is equal to the
#           original swath width. Circle track lines fall on the edge of the implement (not in the center of the pass),
#           therefore they must be shifted inward to get onto what would be considered normal row traffic. 

# NOTE:     Shapely is currently throwing an deprecation warning message after each iteration. 
#           This warning is due to code being utilized in the geopandas libary residing in the geometry
#           portion of a geodataframe. Geopandas will need to update thier geodataframes code regarding
#           geometry.coords (utilzing a numpy array instead of shapely.coords) in order to mantain 
#           compatibility with shapely 2.0 (currently using shapely 1.8)
 


        #calculate number of features to be offset -
        #   calculated from swath width(User Input) &
        #   provided distance (User Input)
        #   ie swath width = 20'ft ; distance = 1260'ft
        #       1260/20 = 63 passes ; loop 62 times
            location = 'calculate number of features to be offset'
            offset = desiredSwathWidth
            newFeatureCount = math.ceil(distance / desiredSwathWidth)
           
        #calculate circle track offset distance and direction -
        #   calculated using half the original swath width
        #   and then set to shift inward towards the center point
            if circleTrackBool == True:
                circleTrackShiftDist = orgSwathWidth / 2
                circleTrackShiftDir = 'right'
            
            if orgSwathWidth == desiredSwathWidth:
                    firstOffset = 0
            else:
                firstOffset = abs(desiredSwathWidth - orgSwathWidth) / 2
            
        #calculate the last pass offset - 
        #   determined using the result of the total distance
        #   divided by the desired swath width. This value is 
        #   then used to determine the shift distance and direction
            if isinstance((distance/desiredSwathWidth),float):
                lastOffset = (newFeatureCount - (distance/desiredSwathWidth)) * desiredSwathWidth
                if offsetGenDir == 'North':
                    lastShiftDir = 'South'
                elif offsetGenDir == 'South':
                    lastShiftDir = 'North'
                elif offsetGenDir == 'East':
                    lastShiftDir = 'West'
                elif offsetGenDir == 'West':
                    lastShiftDir = 'East'
                elif offsetGenDir == 'NorthEast':
                    lastShiftDir = 'SouthWest'
                elif offsetGenDir == 'NorthWest':
                    lastShiftDir = 'SouthEast'
                elif offsetGenDir == 'SouthEast':
                    lastShiftDir = 'NorthWest'
                elif offsetGenDir == 'SouthWest':
                    lastShiftDir = 'NorthEast'
                elif offsetGenDir == 'Outward':
                    lastShiftDir = 'Inward'
            else:
                lastOffset = 0
                lastShiftDir = 'no shift'
                
        #request direction of offset (North, South, East, or West) - 
        #   determine direction of travel for line 
        #   based on coordinate progression through
        #   geometry array, and create new line
        #   accordingly 
            location = 'set first offset'                
            offsetDir = offsetDir.lower()
            offset = abs(offset)
            firstOffset = abs(firstOffset)

        #check file projection
            location = 'check projection'
            nad83_EPSG = 'epsg:26852'
            wgs84_EPSG = 'epsg:4326'
            if dataset.crs != nad83_EPSG:
                datasetNAD83 = dataset.to_crs(nad83_EPSG)
            else:
                datasetNAD83 = dataset
        
            location = 'offset features'
            #select first feature of dataset
            featureList = list(datasetNAD83.geometry[0].coords)
            #newDataset = dataset
            newDataset = gpd.GeoDataFrame(columns=datasetNAD83.columns)
          #offset first circleTrack line
            if circleTrackBool == True:
                lineOffset = circleTrackShiftDist
                featureOffsetDir = circleTrackShiftDir
                newFeature = offsetFeatureLine(featureList,lineOffset,featureOffsetDir,0)
                featureList = list(newFeature['geometry'].coords)

          #loop through range and generate new features
            for i in range(newFeatureCount):
                location = 'offset feature loop'
                lineOffset = offset
                featureOffsetDir = offsetDir
                newLine = True
                if firstOffset != 0 and i == 0:
                    lineOffset = firstOffset #re-assign lineOffset value
                    if desiredSwathWidth < orgSwathWidth:
                        if offsetDir.lower() == 'right':
                            featureOffsetDir = 'left'
                        elif offsetDir.lower() == 'left':
                            featureOffsetDir = 'right'
                            
                elif i == 0:
                    if desiredSwathWidth==orgSwathWidth and circleTrackBool == True:
                        newDataset.loc[i]=newFeature
                    
                    newLine = False
                    
                elif i == (newFeatureCount - 1):
                    lineOffset = offset - lastOffset 
                    
                if newLine == True:    
                  #pass feature vertice coordinates to offset procedure
                    location = 'offset feature line'
                    newFeature = offsetFeatureLine(featureList,lineOffset,featureOffsetDir,i)
                  #add row to dataset (memory only)
                    newDataset.loc[i]=newFeature
                  #set featurelist to newly created line
                    featureList = list(newDataset.geometry[i].coords)
                    location = 'offset feature line print'
            
        #transformDataset
            location = 'transform dataset to wgs84'
            newDataset.set_crs(nad83_EPSG,inplace=True)
            #newDataset.set_crs(epsg=26852,inplace=True)
            newDataset = newDataset.to_crs(wgs84_EPSG)
        #create new shapefile
            location = 'write out new shapefile'
            newDataset.to_file(fileOutput,driver="Shapefile") #write dataset to shapefile
            
            if circleTrackBool == True:
                shift = circleTrackShiftDist - firstOffset
                shiftDir = 'Inward'
            else:
                shift = firstOffset
                shiftDir = offsetGenDir
            
            lastPass = newFeatureCount - 1
            
            
            #return True     #this return can be anything to confirm completion
            print("\n" + 'file sucessfully created')
            print("\n" + 'Shift: ' + repr(shift) + "'ft")
            print('Shift Direction: ' + shiftDir)
            print("\n" + 'Last Pass: ' + repr(newFeatureCount - 1))
            print('Last Pass Shift: ' + repr(lastOffset) + "'ft")
            print('Last Pass Shift Direction: ' + lastShiftDir)
            input("\n" + 'hit any key to exit')
            exit()
        else:
            print('Error! Input Dataset is not a Polyline or Line type Shapefile dataset')
        
        
        
    except Exception as e:
        print("\n" + repr(e)+"\n")
        print('location - ' + location + "\n")
        input('hit any key to exit')
        logging.error(e)
        

def lineOffsetDirection(bearing,selection):
    offsetDir = ''          #used for parallel_offset function ; right or left
    offsetGenDir = ''       #used as an end product deliverable description ; North South East West
    offsetBool = False      #used to end parent loop iterations
    
    if bearing == 'North' or bearing == 'South':
        if selection.lower()=='e' or selection.lower()=='east':
            offsetGenDir = 'East'
            if bearing == 'North':
                offsetDir = 'right'
                offsetBool = True
            elif bearing == 'South':
                offsetDir = 'left'
                offsetBool = True
        elif selection.lower()=='w' or selection.lower()=='west' :
            offsetGenDir = 'West'
            if bearing == 'North':
                offsetDir = 'left'
                offsetBool = True
            elif bearing == 'South':
                offsetDir = 'right'
                offsetBool = True
        else:
            offsetDir = 'Invalid Selection!'
            offsetBool = False
    elif bearing == 'West' or bearing == 'East':
        if selection.lower()=='n' or selection.lower()=='north':
            offsetGenDir = 'North'
            if bearing == 'West':
                offsetDir = 'right'
                offsetBool = True
            elif bearing == 'East':
                offsetDir = 'left'
                offsetBool = True
        elif selection.lower()=='s' or selection.lower()=='south':
            offsetGenDir = 'South'
            if bearing == 'West':
                offsetDir = 'left'
                offsetBool = True
            elif bearing == 'East':
                offsetDir = 'right'
                offsetBool = True
        else:
            offsetDir = 'Invalid Selection!'
            offsetBool = False
    elif bearing == 'NorthWest' or bearing == 'SouthEast':
        if selection.lower()=='ne' or selection.lower()=='northeast':
            offsetGenDir = 'NorthEast'
            if bearing == 'NorthWest':
                offsetDir = 'right'
                offsetBool = True
            elif bearing == 'SouthEast':
                offsetDir = 'left'
                offsetBool = True
        elif selection.lower()=='sw' or selection.lower()=='southwest':
            offsetGenDir = 'SouthWest'
            if bearing == 'NorthWest':
                offsetDir = 'left'
                offsetBool = True
            elif bearing == 'SouthEast':
                offsetDir = 'right'
                offsetBool = True
        else:
            offsetDir = 'Invalid Selection!'
            offsetBool = False
    elif bearing == 'NorthEast' or bearing == 'SouthWest':
        if selection.lower()=='nw' or selection.lower()=='northwest':
            offsetGenDir = 'NorthWest'
            if bearing == 'NorthEast':
                offsetDir = 'left'
                offsetBool = True
            elif bearing == 'SouthWest':
                offsetDir = 'right'
                offsetBool = True
        elif selection.lower()=='se' or selection.lower()=='southeast':
            offsetGenDir = 'SouthEast'
            if bearing == 'NorthEast':
                offsetDir = 'right'
                offsetBool = True
            elif bearing == 'SouthWest':
                offsetDir = 'left'
                offsetBool = True
        else:
            offsetDir = 'Invalid Selection!'
            offsetBool = False
            
    return offsetDir, offsetGenDir, offsetBool
 
def offsetFeatureLine(featureList,offset,offsetDir,cnt):
  #line offset
    geoArr = []
    for feat in featureList:
        geoArr.append((feat[0],feat[1]))
      
    #set linestring
    line = LineString(geoArr)
    offsetLine = line.parallel_offset(
                                    offset,
                                    offsetDir,  #direction = 'right' or 'left'
                                    join_style=1
                                  )
    if offsetDir == 'right':
        revLineArr = []
        for i in range(len(offsetLine.coords)):
            index = len(offsetLine.coords)-(i+1)
            revLineArr.append(offsetLine.coords[index])
        
        #print(revLineArr)
        newLine = LineString(revLineArr)
    else:
        newLine = offsetLine
    newFeature = {"id":cnt,"geometry":newLine}

    return newFeature
    
def offsetFeaturePoint(featureList):
#WORK IN PROGRESS!!!!   
  #point offset
    newFeature = []
    newVertice = {}
    cnt = 0
    for inst in featureList:
        if (cnt % 2) == 0:
          #cnt is even and represents x axis
            oldX = inst[cnt]
            newX = oldX #plus some calculation to offset feature vertice
        else:
          #cnt is odd and represents y axis
            oldY = inst[cnt]
            newY = oldY #plus some calculation to offset feature vertice
        
        newVertice.update({newX:newY})
        cnt = cnt + 1    
        
    newFeature.append(newVertice)

def determineLineHeading(dataset):
    
    if dataset.crs != 'epsg:4326':
        dataset = dataset.to_crs('epsg:4326')
    
    lastI = len(dataset.geometry[0].coords)-1
    strtLat = dataset.geometry[0].coords[0][1]
    strtLon = dataset.geometry[0].coords[0][0]
    endLat = dataset.geometry[0].coords[lastI][1]
    endLon = dataset.geometry[0].coords[lastI][0]
    
    #latConst = 1/364000    #latitude feet per 1 degree of variance
    #lonConst = 1/288200    #longitude feet per 1 degree of variance
    
    heading = Geodesic.WGS84.Inverse(strtLat,strtLon,endLat,endLon)['azi1']
    
    if heading < 0:
        heading = 360 - abs(heading)
    
    if heading < 22.5 or heading > 337.5:
        bearing = 'North'
    elif heading > 22.5 and heading < 67.5:
        bearing = 'NorthEast'
    elif heading > 67.5 and heading < 112.5:
        bearing = 'East'
    elif heading > 112.5 and heading < 157.5:
        bearing = 'SouthEast'
    elif heading > 157.5 and heading < 202.5:
        bearing= 'South'
    elif heading > 202.5 and heading < 247.5:
        bearing = 'SouthWest'
    elif heading > 247.5 and heading < 292.5:
        bearing = 'West'
    elif heading > 292.5 and heading < 337.5:
        bearing = 'NorthWest'

    return heading, bearing
    
            
if __name__ == "__main__":
     generateDuplicateFeature()

