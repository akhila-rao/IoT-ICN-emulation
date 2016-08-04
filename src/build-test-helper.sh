#!/bin/bash

# A helper script to build specific targets.
# It prints either 'ok', 'warning' or 'failed' depending on the outcome of the
# build. The output of the build is stored in /tmp/$LOG_FNAME. If the build
# failed, the modified file $TARGET_FNAME is stored in /tmp/$TARGET_FNAME.$LOG_FNAME.
#
# Parameters (passed in environment variables):
# 	LOG_FNAME	Name of the logfile to write to.
#	MAKE_TARGETS	Targets that need to be built.
#	MAKE_VARS	Variable-value pairs that are sent to the Makefile.
#	MODIFIY_FNAME	Name of the file to change #defines.
#	SET_VARS	#define variables that need to be defined.
#	UNSET_VARS	#define variables that need to be unset.
#	PKT_FORMAT	Name of the packet format to test. If this variable is
#			set, the packet format tests are executed instead of
#			the normal build.

# Undefining all environment variables in this invocation (build variables are passed as MAKE_VARS)
unset USE_KRNL
unset USE_FRAG
unset USE_NFN
unset USE_SIGNATURES

if [ -n "$MODIFIY_FNAME" ]; then
    # Backup
    cp "$MODIFIY_FNAME" "$MODIFIY_FNAME.bak"

    # Define variables that are commented out
    for VAR in $SET_VARS; do
        #  echo "Defining $VAR..."
        sed -e "s!^\s*//\s*#define $VAR!#define $VAR!" "$MODIFIY_FNAME" > "$MODIFIY_FNAME.sed"
        mv "$MODIFIY_FNAME.sed" "$MODIFIY_FNAME"
    done

    # Comment already defined variables
    for VAR in $UNSET_VARS; do
        #  echo "Unsetting $VAR..."
        sed -e "s!^\s*#define $VAR!// #define $VAR!" "$MODIFIY_FNAME" > "$MODIFIY_FNAME.sed"
        mv "$MODIFIY_FNAME.sed" "$MODIFIY_FNAME"
    done
fi

# Print work
printf "%-30s [..]" "$LOG_FNAME"

RC="ok"
if [ -n "$PKT_FORMAT" ]; then
    make -j$NO_CORES -C util ccn-lite-pktdump > "/tmp/$LOG_FNAME.log" 2>&1
    if [ $? -ne 0 ]; then
        RC="fail"
    else
        rm -f "/tmp/$LOG_FNAME.log"
        FNAMES=`find ../test/$PKT_FORMAT -iname "*.$PKT_FORMAT"`
        for FNAME in $FNAMES; do
            echo "### ccn-lite-pktdump < $FNAME" >> "/tmp/$LOG_FNAME.log"
            ./util/ccn-lite-pktdump < $FNAME >> "/tmp/$LOG_FNAME.log" 2>&1
            if [ $? -ne 0 ]; then
                RC="fail"
            fi
            echo "" >> "/tmp/$LOG_FNAME.log"
        done
    fi
else
    # Build and log output
    make -j$NO_CORES -k $MAKE_VARS $MAKE_TARGETS > "/tmp/$LOG_FNAME.log" 2>&1
    if [ $? -ne 0 ]; then
        RC="fail"
    fi

    # Replace backup
    if [ -n "$MODIFIY_FNAME" ]; then
        cp "$MODIFIY_FNAME" "/tmp/$MODIFIY_FNAME.$LOG_FNAME"
        mv "$MODIFIY_FNAME.bak" "$MODIFIY_FNAME"
    fi
fi

# Print status
if [ $RC = "ok" ]; then
    if ! grep --quiet -i "warning" "/tmp/$LOG_FNAME.log"; then
        echo $'\b\b\b\b[\e[1;32mok\e[0;0m]'
    else
        echo $'\b\b\b\b\b\b\b\b\b[\e[1;33mwarning\e[0;0m]'
    fi
    exit 0
else
    echo $'\b\b\b\b\b\b\b\b[\e[1;31mfailed\e[0;0m]'
    exit 1
fi
