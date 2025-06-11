#-------------------------------------------------------------------------------
# Program version Allplan Bridge 2023-1-7
# Database version 1.00
#-------------------------------------------------------------------------------

	
#---------------------------------------------------------------------------
# Cross sections
#---------------------------------------------------------------------------

CSECTIONS BEGIN
	
	CSECTION "Slab Girder"
		
		TEXT   ""
		
		CVARS BEGIN
			
			VAR         "Parameter3"                       $P3  				LENGTH  ""
			VAR         "Parameter4"                       $P4  				LENGTH  ""
			VAR         "Parameter6"                       $P6  				LENGTH  ""
			VAR         "Parameter7_half"            	   [expr {$P7 / 2.0}]  	LENGTH  ""
			
		CVARS END
		
		CLINES BEGIN
			
			ZAXIS       "Zloc"              0.00000      0.00000
			YAXIS       "Yloc"              0.00000     90.00000
			
			PARALLEL    "L1"           "Parameter7_half"      POS  LINE   "Yloc"
			PARALLEL    "L2"           "Parameter7_half"      NEG  LINE   "Yloc"
			PARALLEL    "L3"           "Parameter6"           POS  LINE   "L1"
			PARALLEL    "L4"           "Parameter6"           NEG  LINE   "L2"
			PARALLEL    "L7"           "Parameter3"           NEG  LINE   "Zloc"
			PARALLEL    "L8"           "Parameter4"           NEG  LINE   "L7"
			
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

