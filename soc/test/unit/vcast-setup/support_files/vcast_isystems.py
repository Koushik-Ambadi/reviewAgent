import time
import sys
import binascii
import shutil
# sys.path.append('C:\Python26\Lib\site-packages')
import isystem.connect as ic

# ------------------------------------------------------------------------------
# Parameter 1 --> Full path to the winIdea workspace file (e.g. autoliv.xjrf)
# Parameter 2 --> Full path to the executable (.elf) file
# ------------------------------------------------------------------------------
def executeTest():
    workspaceFile = sys.argv[1]
    #example: workspaceFile = "SDMDemo.xjrf"
    print('workSpaceFile path is: ' + workspaceFile)
     
    shutil.copyfile(sys.argv[2],"vcast.elf")
    elfFile = sys.argv[2]
    #example: elfFile = "SDMDemo_Boot.elf"
    print('elfFile path is:       ' + elfFile)

    # Prepare the ConnectionMigration
    connectionMgr = ic.ConnectionMgr()
    connectionMgr.connectMRU('')
    dbg = ic.CDebugFacade(connectionMgr)
    workspaceCtrl = ic.CWorkspaceController(connectionMgr)
    workspaceCtrl.closeDiscard()

    # Open specific workspace
    # The workspace should define a single target configuration
    workspaceCtrl.open(workspaceFile)

    loader_contr = ic.CLoaderController(connectionMgr)
    loader_contr.clearDownloadList(0)
    loader_contr.addToDownloadList(0,elfFile,False,"")

    dbg.download()

    try:
        dbg.deleteAll()
    except:
        print("Exception deleting all breakpoints!")

    dbg.setBP("vCAST_END")
    try:
        dbg.setBP("vcastHaltDebugger")
    except:
        print("Could not find symbol vcastHaltDebugger!!  Please define VCAST_OUTPUT_VIA_DEBUGGER")
        
    print("Creating Test Results (VCAST_STDOUT.DAT file)")
    outFile = open("VCAST_STDOUT.DAT","w", encoding="utf-8")

    print("Starting Test")
    while True:
        dbg.run()
        dbg.waitUntilStopped()

        print("Breakpoint hit")

        # Pre-Define local variables to 
        # ensure we have the correct data types
        vcast_output_buffer_end = 0
        vcast_output_buffer_value = 0

        evalResult = dbg.evaluate(ic.IConnectDebug.fRealTime,"vcast_output_buffer_end")
        vcast_output_buffer_end = evalResult.getInt()
        print("Output Buffer contains: " + str(vcast_output_buffer_end) + " characters")

        variableAddr = dbg.getVariableAddress("vcast_output_buffer")

        print("address of vcast_output_buffer = " + str(variableAddr.getAddress()))
        
        vcast_data = dbg.readMemory(ic.IConnectDebug.fRealTime, variableAddr.getMemArea(),
                                    variableAddr.getAddress(), vcast_output_buffer_end, 1)
         
        for byte in vcast_data:
            # This if statement fixes an issue where the debugger
            # was reading twice the amount of data that was requested
            if byte == 0:
                break
            if byte in range (0,255):
                outFile.write (chr(byte))
            else: 
                print("Out of range char value read [" + byte + "]")

        print("vCAST_END = " + str(dbg.getFunctionAddress("vCAST_END").getAddress()))
        print("vcastHaltDebugger = " + str(dbg.getFunctionAddress("vcastHaltDebugger").getAddress()))
        print("Current Program Counter = " + str(dbg.getCPUStatus().getExecutionPoint()))
        if dbg.getFunctionAddress("vCAST_END").getAddress() == dbg.getCPUStatus().getExecutionPoint():
            break

    print("End of test Reached")
    outFile.write("   ")
    outFile.close()
    connectionMgr.disconnect(ic.IConnect.dfCloseServerUnconditional | ic.IConnect.dfCloseAutoSaveNone)

#calling the program
if __name__ == "__main__":
    # The default Windows encoding on Python 3.7 is cp1252, which is undesired.
    encoding = 'utf-8'
    import sys
    try:
        if sys.stdout.encoding.lower() != encoding:
            sys.stdout.reconfigure(encoding=encoding)
        if sys.stderr.encoding.lower() != encoding:
            sys.stderr.reconfigure(encoding=encoding)
    except AttributeError:
        pass

    executeTest()
