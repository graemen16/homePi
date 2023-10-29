# purge older camera files from server
your_id=${USER}-on-${HOSTNAME}
echo "$your_id"

#keep files for last xx days
DAYS_KEPT=21
echo "Keeping $DAYS_KEPT days of files"

THISDAY=$(date +%s)
DAYSTODAY=$(($THISDAY/(3600*24)))
# echo $DAYSTODAY

mydir1="/mnt/GigaStore/FTP/Cameras/Camera_rear_right"
mydir2="/mnt/GigaStore/FTP/Cameras/Camera_rear_left"
echo $mydir
# ls $mydir
df -m /mnt/GigaStore

for mydir in $mydir1 $mydir2; do 
	echo $mydir

	for dirname in $mydir/*; do
#		echo $dirname
		dirbasename=$(basename "$dirname")
		if [ -d "$dirname" ]; then
			dirdate=$(date -d "$dirbasename" +%s)
			dirdatedays=$(($dirdate/(3600*24)))
			dirage=$((-$dirdatedays+$DAYSTODAY))
	#		echo "$dirbasename is a directory $dirage old"
			if [ "$dirage" -gt "$DAYS_KEPT" ]; then
				echo "Deleting $dirbasename, $dirage days old"
	#			chmod -R 755 "$dirname"
				rm -r "$dirname"
			fi
		fi
	done
done