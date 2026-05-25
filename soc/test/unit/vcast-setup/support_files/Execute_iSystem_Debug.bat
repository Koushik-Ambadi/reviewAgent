rem Command Line is winIDEA.exe SDMDemo.xjrf <<name of harness executable>>
rem In the .xjrf file, I set the download file to be vcast.elf, so we copy
rem the actual download file into that name to make the debugger happy!
copy %3 vcast.elf
%1 %2