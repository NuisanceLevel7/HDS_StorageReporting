

echo "Collecting Array Info"
call hicommandcli getstoragearray subtarget=LogicalUnit lusubinfo=LDEV -f xml -o C:\Users\IZR\Documents\outfiles\logicalunit.xml
call hicommandcli getstoragearray subtarget=pool -f xml -o C:\Users\IZR\Documents\outfiles\pool.xml
call hicommandcli getstoragearray -f xml -o C:\Users\IZR\Documents\outfiles\arrays.xml
echo "Collecting Host Info"
call hicommandcli GetHost -o C:\Users\IZR\Documents\outfiles\hosts.txt
call hicommandcli gethostinfo -o C:\Users\IZR\Documents\outfiles\hostinfo.txt

