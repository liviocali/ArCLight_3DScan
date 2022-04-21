MYPATH="/data/LRS/acl_teststand/3dscan/data_files/"

cat $1 | while read LINE;
do
	FNAME=${LINE: -29}
	FULLPATH="$MYPATH$FNAME"
	echo "Converting "$FNAME
	/home/daq/software/AFIViewer/build/ADC64Viewer -g 0 -f $FULLPATH -m x > /dev/null

	INNAME=${FNAME: -21}
	echo $INNAME
	OUTNAME=$(ls -rt | tail -n 1)
	echo $OUTNAME
	while ! [[ "$OUTNAME" == *"$INNAME"* ]];
	do
  		echo "File not converted, retry."
		/home/daq/software/AFIViewer/build/ADC64Viewer -g 0 -f $FULLPATH -m x > /dev/null
		OUTNAME=$(ls -rt | tail -n 1)	
	done
	if ! [[ "$OUTNAME" == *"$FNAME"* ]]; then
		mv $OUTNAME "rlog_$FNAME.root"
	fi
done
