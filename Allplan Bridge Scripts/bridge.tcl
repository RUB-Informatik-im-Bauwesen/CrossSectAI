#-------------------------------------------------------------------------------
# Program version Allplan Bridge 2023-1-7
# Database version 1.00
#-------------------------------------------------------------------------------

# Directory where the template scripts and variable file are located
set base_dir "C:/Users/Benedikt/Desktop/Allplan_Scripts/"


# Load the variables
set variable_filename "variables.tcl"
set variable_filepath $base_dir$variable_filename

source $variable_filepath


# Load template type
if {$template_type == 0} {
    set template_filename "slab_girder.tcl"
	set cross_section_name "Slab Girder"
} elseif {$template_type == 1} {
	set template_filename "t_girder.tcl"
	set cross_section_name "T Girder"
} else {
    set template_filename "tapered_t_girder.tcl"
	set cross_section_name "Tapered T Girder"
}

set template_filepath $base_dir$template_filename



ABM BEGIN
	
	#---------------------------------------------------------------------------
	# General project settings
	#---------------------------------------------------------------------------
	
	PROJECT BEGIN
		
		UNIT       SETDB ANGLED     "\[deg\]"    ""      "Degree to Radians"
		UNIT       SETDB ANGLE      "\[rad\]"    ""      "Radians"
		UNIT       SETDB LCROSSD    "\[m\]"      ""      "Meter"
		UNIT       SETDB LCROSS     "\[m\]"      ""      "Meter"
		UNIT       SETDB LSTRUCTD   "\[m\]"      ""      "Meter"
		UNIT       SETDB LSTRUCT    "\[m\]"      ""      "Meter"
		UNIT       SETDB STATION    "\[m\]"      ""      "Meter"
		UNIT       SETDB TEMP       "\[°C\]"     ""      "Celsius for temperature "
		UNIT       SETDB AREINF     "\[cm²\]"    ""      "Square Centimeter to Square Meter"
		UNIT       SETDB ASTRAND    "\[mm²\]"    ""      "Square Millimeter to Square Meter"
		UNIT       SETDB EMOD       "\[N/mm²\]"  ""      "Stress to Kilonewton per Square Meter"
		UNIT       SETDB STRESS     "\[N/mm²\]"  ""      "Stress to Kilonewton per Square Meter"
		UNIT       SETDB FORCE      "\[kN\]"     ""      "Kilonewton"
		UNIT       SETDB MOMENT     "\[kNm\]"    ""      "Kilonewton Meter"
		UNIT       SETDB DEVIATION  "\[rad/m\]"  ""      "Radian per Meter"
		UNIT       SETDB LSMALL     "\[mm\]"     ""      "Millimeter to Meter"
		UNIT       SETDB GAMMA      "\[kN/m³\]"  ""      "Specific weight Kilonewton per Meter³"
		UNIT       SETDB ACC        "\[m/s²\]"   ""      "Acceleration Meter per Second²"
		
		PORIGIN                 0.000                0.000
		RADIUS+    LEFT
		SERVICE    ROAD
		
		#-----------------------------------------------------------------------
		# Recalculation settings (analysis)
		#-----------------------------------------------------------------------
		
		RECALCULATION BEGIN
			
			STRUCTURE BEGIN
				
				ANALYSISMODEL                 OFF
				OPTION   BEAMSHEARDEF         ON
				
			STRUCTURE END
			
		RECALCULATION END
		
	PROJECT END
	
	#---------------------------------------------------------------------------
	# Axes definition
	#---------------------------------------------------------------------------
	
	AXES BEGIN
		
		AXIS "Axis 1" BEGIN
			
			BIMPLUS         "" ""
			
			SSLOPE          ASC
			SBEGIN                           0
			
			PLAN BEGIN
				
				POINT       ABS                   0               0               0
				LINE        DS                   15
				
			PLAN END
			
			PROFILES BEGIN
				
				PROFILE "Gradient" ACTIVE BEGIN
					
					SCALE       10
					
					POLYGON BEGIN
						
						POINT            0.000000     0.000000
						POINT           15.000000     0.000000
												
					POLYGON END
					
				PROFILE END
				
			PROFILES END
			
		AXIS END
		
	AXES END
	
	#---------------------------------------------------------------------------
	# Calculator - Formulas, Functions, Tables 
	#---------------------------------------------------------------------------
	
	CALC BEGIN
		
	CALC END
	
	#---------------------------------------------------------------------------
	# Cross sections
	#---------------------------------------------------------------------------
	
	source $template_filepath
		
	#---------------------------------------------------------------------------
	# Model structure
	#---------------------------------------------------------------------------
	
	STRUCTURE BEGIN
		
		GIRDER "Girder 1" BEGIN
			
			TEXT            ""
			REFAXIS         "Axis 1"
			CSPLANE         NORMAL
			SBEGIN                 0.000000
			
			STATIONS BEGIN
				
				SLOCAL s001            0.000000    BEAM
				SLOCAL s002            5.000000    BEAM
				SLOCAL s003           10.000000    BEAM
				SLOCAL s004           15.000000    BEAM
				
			STATIONS END
			
			SPOINT            s001              CSECTION   "" $cross_section_name
			SPOINT      [XFTS s002   s003   1]  CSECTION   $cross_section_name
			SPOINT            s004              CSECTION   $cross_section_name ""
			
			SPOINT      [XFTS s001   s004   1]  ZROTATE    0.00000
			
			SPOINT      [XFTS s001   s004   1]  YROTATE    0.00000
			
			
			SPOINT      [XFTS s001   s004   1]  NODE       "1"               0   STEP     0
			
			SPOINT      [XFTS s001   s003   1]  BEAM       "1"               0   STEP     0
			
			SPOINT      [XFTS s001   s003   1]  MATERIAL   "1"          ""
			
			SPOINT      [XFTS s001   s003   1]  GROUP      "1"          ""
			
			GRILLAGE "OFF" BEGIN
				
				MATERIAL         ""
				GROUP            ""
				CSECTION         ""                0.00000
				ELEMS                 0      0
				
			GRILLAGE END
			
		GIRDER END
		
		#-----------------------------------------------------------------------
		# Geometrical positions of structural members
		#-----------------------------------------------------------------------
		
		GPOSITIONS BEGIN
			
		GPOSITIONS END
		
		#-----------------------------------------------------------------------
		# Topological connections of structural members (Analysis)
		#-----------------------------------------------------------------------
		
		CONNECTIONS BEGIN
			
			
		CONNECTIONS END
		
	STRUCTURE END
	
ABM END
