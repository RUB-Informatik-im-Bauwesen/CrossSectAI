#---------------------------------------------------------------------------
# Cross sections
#---------------------------------------------------------------------------

CSECTIONS BEGIN
	
	CSECTION "Slab Girder"
		
		TEXT   ""
		
		CVARS BEGIN
			
			VAR         "P3"                       $P3  				LENGTH  ""
			VAR         "P4"                       $P4  				LENGTH  ""
			VAR         "P6"                       $P6  				LENGTH  ""
			VAR         "P7_h"            	   [expr {$P7 / 2.0}]  	LENGTH  ""
			
		CVARS END
		
		CLINES BEGIN
			
			ZAXIS       "Zloc"              0.00000      0.00000
			YAXIS       "Yloc"              0.00000     90.00000
			
			PARALLEL    "L1"           "P7_h"      POS  LINE   "Yloc"
			PARALLEL    "L2"           "P7_h"      NEG  LINE   "Yloc"
			PARALLEL    "L3"           "P6"           POS  LINE   "L1"
			PARALLEL    "L4"           "P6"           NEG  LINE   "L2"
			PARALLEL    "L7"           "P3"           NEG  LINE   "Zloc"
			PARALLEL    "L8"           "P4"           NEG  LINE   "L7"
			
		CLINES END
		
		CBOUNDARIES BEGIN
			
			BOUNDARY "Boundary Line 1"
				
				POINTS BEGIN
					
					BPOINT       1  LSECT   "L3"    "Zloc"
					BPOINT       2  LSECT   "L4"    "Zloc"
					BPOINT       3  LSECT   "L4"    "L7"
					BPOINT       4  LSECT   "L2"    "L8"
					BPOINT       5  LSECT   "L1"    "L8"
					BPOINT       6  LSECT   "L3"    "L7"
					
				POINTS END
				
			BOUNDARY END
			
		CBOUNDARIES END
		
		CUNITS BEGIN
			
			SBEAM       1    LSECT     "Zloc"    "Yloc"
			
			SBEAM       1    BOUNDARY  "Boundary Line 1"
			
		CUNITS END
		
	CSECTION END
	
CSECTIONS END

