#!/bin/bash

function backup() 
{

	DATE=$(date +%Y%m%d)
	HEURE=$(date +%H%M)
	SRC="$1"
	REAL=$(readlink -f "$SRC")
	BACKUP=~/backup/${DATE}_${HEURE}${REAL}
	BACKUPDIR="$(dirname "$BACKUP")"

	if [[ -d $SRC ]] || [[ -f $SRC ]]; then
	         mkdir -p "${BACKUPDIR}"
	         echo "Creating backup directory ${BACKUPDIR}/ for $SRC" 
		 for f in "$@"
	         do
	                 cp -r "${f}" "${BACKUPDIR}"/
	         done
	else
	         echo "${SRC} is invalid"
	         exit 1
	fi
} 


function helpme()
{
	echo "cpb <FILE|DIR> // Create backup"
	echo "cpb <DIR1> <FILE1> <DIR Z> <FILE Y> // Multiples backups"
	echo "cpb --search <FILE|DIR> // Search a file"
	echo "cpb --list // List all backups"
}

function listbackupfiles()
{
	ls -laR ~/backup/
}

function searchfiles()
{
	if [ "$1" = "" ]; then
		helpme
	else
		find ~/backup/ -name "*$1*"
	fi
}

case "$1" in
	"--help") helpme ;;
	"--list") listbackupfiles ;;
	"--search") searchfiles $2 ;;
	*) for i in ${@} ; do backup $i; done ;;
esac

exit 0
