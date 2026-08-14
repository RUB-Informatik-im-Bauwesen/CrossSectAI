#-------------------------------------------------------------------------------
# Program version Allplan Bridge 2023-1-7
# Database version 1.00
#-------------------------------------------------------------------------------

#---------------------------------------------------------------------------
# Cross sections
#---------------------------------------------------------------------------

CSECTIONS BEGIN
	
	CSECTION "Tapered T Girder"
		
		TEXT   ""
		
		CVARS BEGIN
			
			VAR         "P3"               $P3                    LENGTH  ""
			VAR         "P4"               $P4                    LENGTH  ""
			VAR         "P5"               $P5                    LENGTH  ""
			VAR         "P6"               $P6  				  LENGTH  ""	
			VAR         "P7_h"          [expr {$P7 / 2.0}]     LENGTH  ""
			VAR         "P8"               $P8                    LENGTH  ""
			
		CVARS END
		
		CLINES BEGIN
			
			ZAXIS       "Zloc"              0.00000      0.00000
			YAXIS       "Yloc"              0.00000     90.00000
			
			PARALLEL    "L1"           "P7_h"      POS  LINE   "Yloc"
			PARALLEL    "L2"           "P7_h"      NEG  LINE   "Yloc"
			PARALLEL    "L3"           "P8"           POS  LINE   "L1"
			PARALLEL    "L4"           "P8"           NEG  LINE   "L2"
			PARALLEL    "L5"           "P6"           POS  LINE   "L3"
			PARALLEL    "L6"           "P6"           NEG  LINE   "L4"
			PARALLEL    "L7"           "P3"           NEG  LINE   "Zloc"
			PARALLEL    "L8"           "P4"           NEG  LINE   "L7"
			PARALLEL    "L9"           "P5"           NEG  LINE   "L8"
			
		CLINES END
		
		CBOUNDARIES BEGIN
			
			BOUNDARY "Boundary Line 1"
				
				POINTS BEGIN
					
					BPOINT       1  LSECT   "L5"    "Zloc"
					BPOINT       2  LSECT   "Zloc"  "Yloc"
					BPOINT       3  LSECT   "L6"    "Zloc"
					BPOINT       4  LSECT   "L6"    "L7"
					BPOINT       5  LSECT   "L4"    "L8"
					BPOINT       6  LSECT   "L2"    "L9"
					BPOINT       7  LSECT   "L9"    "Yloc"
					BPOINT       8  LSECT   "L1"    "L9"
					BPOINT       9  LSECT   "L3"    "L8"
					BPOINT      10  LSECT   "L5"    "L7"
					
				POINTS END
				
			BOUNDARY END
			
		CBOUNDARIES END
		
		CUNITS BEGIN
			
			SBEAM       1    LSECT     "Zloc"    "Yloc"
			
			SBEAM       1    BOUNDARY  "Boundary Line 1"
			
		CUNITS END
		
	CSECTION END
	
CSECTIONS END
	
